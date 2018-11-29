from unittest.mock import patch, MagicMock, ANY, call

import backend.tests.testing_utilities.constants as constants
from backend.server.models import Project, ASC, Wallet, BlockchainState
from backend.tests.mycro_django_test import MycroDjangoTest


class TestASCSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(repo_name=constants.PROJECT_NAME,
                                              dao_address=constants.PROJECT_ADDRESS, initial_balances=constants.CREATORS_BALANCES)
        self.asc = self.project.asc_set.create(address=constants.ASC_ADDRESS,
                                               project=self.project,
                                               reward=constants.REWARD,
                                               pr_id=constants.PR_ID)
        self.assertEqual(1, ASC.objects.count())

    def test_get_all_ascs(self):
        resp = self.query(
            '''
query {
  allAscs {
    address
  }
}
            '''
        )
        self.assertResponseNoErrors(resp, {
            'allAscs': [{'address': constants.ASC_ADDRESS}]})

    def test_get_asc_by_project_address(self):
        resp = self.query(
            f'''
query {{
  ascForProject(projectAddress: "{constants.PROJECT_ADDRESS}") {{
    project {{
        repoName
    }}
  }}
}}
            '''
        )

        self.assertResponseNoErrors(resp, {'ascForProject': [
            {'project': {'repoName': constants.PROJECT_NAME}}]})

    def test_get_asc_by_id(self):
        resp = self.query(
            f'''
query {{
  asc(ascId: "{self.asc.id}") {{
     address
  }}
}}
            '''
        )

        self.assertResponseNoErrors(resp,
                                    {'asc': {'address': constants.ASC_ADDRESS}})

    def test_get_asc_by_address(self):
        resp = self.query(
            f'''
query {{
  asc(address: "{constants.ASC_ADDRESS}") {{
     reward
     prId
  }}
}}
            '''
        )

        self.assertResponseNoErrors(resp, {'asc': {'reward': constants.REWARD, 'prId': constants.PR_ID}})

    def test_create_asc_project_doesnt_exist(self):
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createMergeAsc(daoAddress: "invalid dao address", rewardee: "{constants.REWARDEE}", reward: {constants.REWARD}, prId: 1)  {{
    asc {{
      address 
    }}
  }}
}}
""")

        self.assertErrorNoResponse(resp, "Project matching query")

    @patch('backend.server.schemas.asc.create_asc.delay')
    @patch('backend.server.schemas.asc.CreateMergeASC._validate_asc_creation')
    def test_create_asc(self, validate_mock: MagicMock, create_asc_task_mock: MagicMock):
        ASC.objects.filter().delete()
        self.assertEqual(0, self.project.asc_set.count())

        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createMergeAsc(daoAddress: "{constants.PROJECT_ADDRESS}", rewardee: "{constants.REWARDEE}", reward: {constants.REWARD},  prId: 1)  {{
    asc {{
      address 
      rewardee
      id
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {
            'createMergeAsc': {'asc': {'id': ANY,'address': '', 'rewardee': constants.REWARDEE}}})

        all_ascs = ASC.objects.all()

        self.assertEqual(1, len(all_ascs))
        self.assertEqual(constants.PROJECT_NAME, all_ascs[0].project.repo_name)
        self.assertEqual(BlockchainState.PENDING, BlockchainState(all_ascs[0].blockchain_state))
        self.assertEqual('', all_ascs[0].address)


        self.assertEqual(1, self.project.asc_set.count())
        validate_mock.assert_called_once()

        create_asc_task_mock.assert_called_once_with(int(resp['data']['createMergeAsc']['asc']['id']))

    def test_get_merge_asc_abi(self):
        resp = self.query("""
query {
    getMergeAscAbi
} 
        """)

        # basically just testing that nothing errors out
        # don't want to assert anything on the returned abi because that will make this test brittle
        self.assertNotIn('errors', resp)

    def test_create_asc_already_exists(self):
        resp = self.query(
            f"""
            mutation {{
              createMergeAsc(daoAddress: "{constants.PROJECT_ADDRESS}", rewardee: "{constants.REWARDEE}", reward: {constants.REWARD},  prId: {constants.PR_ID})  {{
                asc {{
                  address 
                }}
              }}
            }}
            """)

        self.assertErrorNoResponse(resp, 'already exists')

    @patch('backend.server.schemas.asc.github')
    @patch.dict('backend.settings.os.environ',
                {'GITHUB_TOKEN': constants.GITHUB_ACCESS_TOKEN,
                 'GITHUB_ORGANIZATION': constants.GITHUB_ORGANIZATION})
    def test_create_asc_no_open_pr(self, github_mock):
        pr_id = constants.PR_ID + 1

        open_pr = MagicMock()
        open_pr.number = pr_id + 1
        github_mock.get_pull_requests.return_value = [open_pr]

        resp = self.query(
            f"""
            mutation {{
              createMergeAsc(daoAddress: "{constants.PROJECT_ADDRESS}", rewardee: "{constants.REWARDEE}", reward: {constants.REWARD},  prId: {pr_id})  {{
                asc {{
                  address 
                }}
              }}
            }}
            """)

        self.assertErrorNoResponse(resp, 'open PR with')
        github_mock.get_pull_requests.assert_called_once_with(
            self.project.repo_name, constants.GITHUB_ORGANIZATION,
            constants.GITHUB_ACCESS_TOKEN, state='open')
