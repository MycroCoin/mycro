from unittest.mock import patch, MagicMock, call, ANY

from backend.server.models import Project, ASC, Wallet, BlockchainState
from backend.tests.mycro_django_test import MycroDjangoTest
from backend.tests.testing_utilities.utils import *


class TestProjectSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(repo_name=constants.PROJECT_NAME,
                                              dao_address=constants.PROJECT_ADDRESS,
                                              is_mycro_dao=True, initial_balances=constants.CREATORS_BALANCES)

        self.assertEqual(1, Project.objects.count())

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
            'allProjects': [{'daoAddress': constants.PROJECT_ADDRESS,
                             'repoName': constants.PROJECT_NAME}]})

    @patch('backend.server.schemas.project.create_project')
    def test_create_project(self, create_project_mock):
        project_name = 'testing'

        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(projectName: "{project_name}", creatorAddress: "{constants.PROJECT_ADDRESS}") {{
      project {{
        daoAddress
        symbol
      }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {
            'createProject': {'project':{'daoAddress': '' , 'symbol': project_name[:3]}}})

        all_projects = Project.objects.all()
        new_project: Project = all_projects[1]

        self.assertEqual(2, len(
            all_projects))
        self.assertEqual(constants.PROJECT_NAME, all_projects[0].repo_name)
        self.assertEqual({constants.PROJECT_ADDRESS: 1000}, new_project.initial_balances)
        self.assertEqual(project_name, new_project.repo_name)
        self.assertEqual(BlockchainState.PENDING, new_project.blockchain_state)
        self.assertFalse(new_project.is_mycro_dao)
        self.assertEqual(project_name[:3], new_project.symbol)
        self.assertEqual(18, new_project.decimals)
        self.assertEqual('', new_project.dao_address)
        self.assertEqual('', new_project.merge_module_address)
        self.assertEqual(0, new_project.last_merge_event_block)

        create_project_mock.delay.assert_called_once()


    def test_create_project_mycro_dao_doesnt_exist(self):
        Project.objects.filter().delete()
        project_name = 'testing'

        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(projectName: "{project_name}", creatorAddress: "{constants.PROJECT_ADDRESS}") {{
      project {{
        id
      }}
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
  createProject(projectName: "{project_name}", creatorAddress: "{constants.PROJECT_ADDRESS}") {{
      project {{
        id
      }}
  }}
}}
""")
        self.assertErrorNoResponse(resp, "must match the regex")

    def test_get_project_by_id(self):
        resp = self.query(
            f'''
            query {{
                project(daoAddress: "{constants.PROJECT_ADDRESS}") {{
                    repoName
                }}
            }}
            '''
        )
        self.assertResponseNoErrors(resp, {
            'project': {'repoName': constants.PROJECT_NAME}})


    @patch('backend.server.utils.deploy.get_w3')
    def test_get_balances(self, get_w3_mock):
        w3 = constants.W3
        get_w3_mock.return_value = w3

        dao_contract, dao_address, dao_instance = deploy_base_dao()
        self.project.dao_address = dao_address
        self.project.save()

        resp = self.query(
            f'''
            query {{
                project(daoAddress: "{dao_address}") {{
                    balances {{
                        address,
                        balance
                    }}
                }}
            }}'''
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
            f'''
            query {{
                project(daoAddress: "{dao_address}") {{
                    threshold
                }}
            }}'''
        )

        self.assertResponseNoErrors(resp, {'project': {'threshold': 51}})

        # now, propose, vote and pass an ASC so that the threshold is raised
        # want to make sure this is being read from the blockchain
        create_and_register_merge_module(dao_instance)
        _, asc_address, _ = create_and_propose_merge_asc(dao_instance)
        dao_instance.vote(asc_address, transact={'from': constants.INITIAL_ADDRESSES[0]})
        dao_instance.vote(asc_address, transact={'from': constants.INITIAL_ADDRESSES[1]})

        resp = self.query(
            f'''
            query {{
                project(daoAddress: "{dao_address}") {{
                    threshold
                }}
            }}'''
        )

        self.assertResponseNoErrors(resp, {'project': {'threshold': (100 + constants.REWARD) // 2 + 1}})



    def test_get_ascs(self):
        ASC.objects.create(
            address=constants.ASC_ADDRESS,
            project=self.project,
            reward=constants.REWARD,
            rewardee=constants.REWARDEE)

        resp = self.query(
            f'''
            query {{
                project(daoAddress: "{constants.PROJECT_ADDRESS}") {{
                    ascs {{
                        address
                    }}
                }}
            }}
            '''
        )

        self.assertResponseNoErrors(resp, {'project': {'ascs': [{'address': constants.ASC_ADDRESS}]}})



