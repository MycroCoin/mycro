from django.test import TestCase, Client
import json
from backend.server.models import Project, ASC

PROJECT_NAME = 'mycro'
DAO_ADDRESS = '123'
GITHUB_ACCESS_TOKEN = 'fake'
ASC_ADDRESS = '456'

class TestProjectGraphQL(TestCase):
    def setUp(self):
        self._client = Client()
        self.project = Project.objects.create(repo_name=PROJECT_NAME, dao_address=DAO_ADDRESS)
        self.asc = ASC.objects.create(address=ASC_ADDRESS, project=self.project)

    def query(self, query: str, op_name: str = None, input: dict = None):
        '''
        Args:
            query (string) - GraphQL query to run
            op_name (string) - If the query is a mutation or named query, you must
                               supply the op_name.  For annon queries ("{ ... }"),
                               should be None (default).
            input (dict) - If provided, the $input variable in GraphQL will be set
                           to this value

        Returns:
            dict, response from graphql endpoint.  The response has the "data" key.
                  It will have the "error" key if any error happened.
        '''
        body = {'query': query}
        if op_name:
            body['operation_name'] = op_name
        if input:
            body['variables'] = {'input': input}

        resp = self._client.post('/graphql', json.dumps(body),
                                 content_type='application/json')
        jresp = json.loads(resp.content.decode())
        return jresp

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        '''
        Assert that the resp (as retuened from query) has the data from
        expected
        '''
        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertEqual(resp['data'], expected, 'Response has correct data')

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
        self.assertResponseNoErrors(resp, {'allProjects': [{'daoAddress': DAO_ADDRESS, 'repoName': PROJECT_NAME }]})

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
        self.assertResponseNoErrors(resp, {'allAscs': [{'address': ASC_ADDRESS}]})


    def test_create_project(self):
        Project.objects.filter().delete()
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(repoName: "{PROJECT_NAME}", daoAddress: "{DAO_ADDRESS}") {{
    newProject {{
      repoName
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {'createProject': {'newProject': {'repoName': PROJECT_NAME}}})

        all_projects = Project.objects.all()

        self.assertEqual(1, len(all_projects))
        self.assertEqual(PROJECT_NAME, all_projects[0].repo_name)


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
        self.assertResponseNoErrors(resp, {'project': {'repoName': PROJECT_NAME}})

    def test_get_project_by_name(self):
        resp = self.query(
            f'''
query {{
  project(repoName: "{PROJECT_NAME}") {{
    id
  }}
}}
            '''
        )
        self.assertResponseNoErrors(resp, {'project': {'id': "1"}})

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

        self.assertResponseNoErrors(resp, {'ascForProject': [{'project': {'repoName': PROJECT_NAME}}]})

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

        self.assertResponseNoErrors(resp, {'asc': {'address': ASC_ADDRESS}})

    def test_get_asc_by_address(self):
        resp = self.query(
            f'''
query {{
  asc(address: "{ASC_ADDRESS}") {{
     id
  }}
}}
            '''
        )

        self.assertResponseNoErrors(resp, {'asc': {'id': "1"}})

    def test_create_asc(self):
        ASC.objects.filter().delete()
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createAsc(address: "{ASC_ADDRESS}", projectId: "1")  {{
    newAsc {{
      address
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {'createAsc': {'newAsc': {'address': ASC_ADDRESS}}})

        all_ascs = ASC.objects.all()

        self.assertEqual(1, len(all_ascs))
        self.assertEqual(PROJECT_NAME, all_ascs[0].project.repo_name)
        self.assertEqual(ASC_ADDRESS, all_ascs[0].address)
