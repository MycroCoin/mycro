from backend.server.models import Project, ASC
from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.testing_utilities.constants as constants
from unittest.mock import patch
from backend.tests.testing_utilities.utils import *


class TestProjectSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(repo_name=constants.PROJECT_NAME,
                                              dao_address=constants.DAO_ADDRESS,
                                              is_mycro_dao=True)

    def test_get_all_projects(self):
        resp = self.query(
            '''
query {
  allProjects {
    repoName,
    daoAddress,
  }
}
            '''
        )
        self.assertResponseNoErrors(resp, {
            'allProjects': [{'daoAddress': constants.DAO_ADDRESS,
                             'repoName': constants.PROJECT_NAME}]})

    @patch('backend.server.utils.deploy.get_w3')
    @patch('backend.server.utils.github.create_repo')
    @patch('backend.settings.github_organization')
    def test_create_project(self, github_organization_mock, create_repo_mock, get_w3_mock):
        project_name = 'testing'
        dao_address = '0x1111111111111111111111111111111111111118'
        w3 = get_w3_mock.return_value
        w3.eth.waitForTransactionReceipt.return_value = {
            'contractAddress': dao_address}

        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(projectName: "{project_name}", creatorAddress: "{constants.DAO_ADDRESS}") {{
      projectAddress
  }}
}}
""")
        self.assertResponseNoErrors(resp, {
            'createProject': {'projectAddress': dao_address}})

        all_projects = Project.objects.all()

        self.assertEqual(2, len(
            all_projects))
        self.assertEqual(constants.PROJECT_NAME, all_projects[0].repo_name)
        self.assertEqual(project_name, all_projects[1].repo_name)

        # called twice for deployment and twice for registrations
        self.assertEqual(4,
                         get_w3_mock.return_value.eth.waitForTransactionReceipt.call_count)
        self.assertEqual(4, w3.eth.sendRawTransaction.call_count)

        create_repo_mock.assert_called_once_with(repo_name=project_name, organization=github_organization_mock.return_value)

    def test_create_project_mycro_dao_doesnt_exist(self):
        Project.objects.filter().delete()
        project_name = 'testing'

        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(projectName: "{project_name}", creatorAddress: "{constants.DAO_ADDRESS}") {{
      projectAddress
  }}
}}
""")
        self.assertErrorNoResponse(resp,
                                   "Could not find mycro dao. Cannot create new project.")

    def test_create_project_with_invalid_name(self):
        Project.objects.filter().delete()
        project_name = 'invalid name'

        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(projectName: "{project_name}", creatorAddress: "{constants.DAO_ADDRESS}") {{
      projectAddress
  }}
}}
""")
        self.assertErrorNoResponse(resp, "must match the regex")

    def test_get_project_by_id(self):
        resp = self.query(
            '''
query {
  project(id: "1") {
    repoName
  }
}
            '''
        )
        self.assertResponseNoErrors(resp, {
            'project': {'repoName': constants.PROJECT_NAME}})

    def test_get_project_by_name(self):
        resp = self.query(
            f'''
query {{
  project(repoName: "{constants.PROJECT_NAME}") {{
    id
  }}
}}
            '''
        )
        self.assertResponseNoErrors(resp, {'project': {'id': "1"}})

    @patch('backend.server.utils.deploy.get_w3')
    def test_get_balances(self, get_w3_mock):
        w3 = constants.W3
        get_w3_mock.return_value = w3

        dao_contract, dao_address, dao_instance = deploy_base_dao()
        self.project.dao_address = dao_address
        self.project.save()

        resp = self.query(
            '''
            query {
                project(id: "1") {
                    balances {
                        address,
                        balance
                    }
                }
            }'''
        )

        balances = resp['data']['project']['balances']
        balances = {balance['address']: balance['balance'] for balance in
                    balances}

        for expected_address, expected_balance in zip(
                constants.INITIAL_ADDRESSES, constants.INITIAL_BALANCES):
            self.assertEqual(expected_balance, balances[expected_address])

    @patch('backend.server.utils.deploy.get_w3')
    def test_get_threshold(self, get_w3_mock):
        w3 = constants.W3
        get_w3_mock.return_value = w3

        dao_contract, dao_address, dao_instance = deploy_base_dao()
        self.project.dao_address = dao_address
        self.project.save()

        resp = self.query(
            '''
            query {
                project(id: "1") {
                    threshold
                }
            }'''
        )

        self.assertResponseNoErrors(resp, {'project': {'threshold': 51}})

        # now, propose, vote and pass an ASC so that the threshold is raised
        # want to make sure this is being read from the blockchain
        create_and_register_merge_module(dao_instance)
        _, asc_address, _ = create_and_propose_merge_asc(dao_instance)
        dao_instance.vote(asc_address, transact={'from': constants.INITIAL_ADDRESSES[0]})
        dao_instance.vote(asc_address, transact={'from': constants.INITIAL_ADDRESSES[1]})

        resp = self.query(
            '''
            query {
                project(id: "1") {
                    threshold
                }
            }'''
        )

        self.assertResponseNoErrors(resp, {'project': {'threshold': (100 + constants.REWARD) // 2 + 1}})



    def test_get_ascs(self):
        ASC.objects.create(
            address=constants.ASC_ADDRESS,
            project=self.project,
            reward=constants.REWARD,
            rewardee=constants.REWARDEE)

        resp = self.query(
            '''
            query {
                project(id: "1") {
                    ascs {
                        address
                    }
                }
            }
            '''
        )

        self.assertResponseNoErrors(resp, {'project': {'ascs': [{'address': constants.ASC_ADDRESS}]}})



