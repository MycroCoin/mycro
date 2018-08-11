from backend.server.models import Project, ASC
from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.testing_utilities.constants as constants
from unittest.mock import patch


class TestASCSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(repo_name=constants.PROJECT_NAME, dao_address=constants.DAO_ADDRESS)
        self.asc = ASC.objects.create(address=constants.ASC_ADDRESS, project=self.project, reward=constants.REWARD)

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
        self.assertResponseNoErrors(resp, {'allAscs': [{'address': constants.ASC_ADDRESS}]})

    def test_get_asc_by_project_id(self):
        resp = self.query(
            '''
query {
  ascForProject(projectId: "1") {
    project {
        repoName
    }
  }
}
            '''
        )

        self.assertResponseNoErrors(resp, {'ascForProject': [{'project': {'repoName': constants.PROJECT_NAME}}]})

    def test_get_asc_by_id(self):
        resp = self.query(
            '''
query {
  asc(ascId: "1") {
     address
  }
}
            '''
        )

        self.assertResponseNoErrors(resp, {'asc': {'address': constants.ASC_ADDRESS}})

    def test_get_asc_by_address(self):
        resp = self.query(
            f'''
query {{
  asc(address: "{constants.ASC_ADDRESS}") {{
     id
  }}
}}
            '''
        )

        self.assertResponseNoErrors(resp, {'asc': {'id': "1"}})

    def test_create_asc_project_doesnt_exist(self):
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createAsc(daoAddress: "invalid dao address", rewardee: "{constants.REWARDEE}", reward: {constants.REWARD}, prId: 1)  {{
    asc {{
      address 
    }}
  }}
}}
""")

        self.assertErrorNoResponse(resp, "Project matching query")

    @patch('backend.server.utils.deploy.get_w3')
    def test_create_asc(self, get_w3_mock):
        ASC.objects.filter().delete()
        w3 = get_w3_mock.return_value
        w3.eth.waitForTransactionReceipt.return_value = {'contractAddress': constants.ASC_ADDRESS}


        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createAsc(daoAddress: "{constants.DAO_ADDRESS}", rewardee: "{constants.REWARDEE}", reward: {constants.REWARD},  prId: 1)  {{
    asc {{
      address 
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {'createAsc': {'asc': {'address': constants.ASC_ADDRESS}}})

        all_ascs = ASC.objects.all()

        self.assertEqual(1, len(all_ascs))
        self.assertEqual(constants.PROJECT_NAME, all_ascs[0].project.repo_name)
        self.assertEqual(constants.ASC_ADDRESS, all_ascs[0].address)

        # called once for deployment and once for registration
        self.assertEqual(2, get_w3_mock.return_value.eth.waitForTransactionReceipt.call_count)
        self.assertEqual(2, w3.eth.sendRawTransaction.call_count)


    def test_get_merge_asc_abi(self):
        resp = self.query("""
query {
    getMergeAscAbi
} 
        """)

        # basically just testing that nothing errors out
        # don't want to assert anything on the returned abi because that will make this test brittle
        self.assertNotIn('errors', resp)
