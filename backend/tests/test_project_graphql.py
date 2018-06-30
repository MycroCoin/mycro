from django.test import TestCase, Client
import json
from backend.server.models import Project

PROJECT_NAME = 'mycro'
DAO_ADDRESS = '123'
GITHUB_ACCESS_TOKEN = 'fake'

class TestProjectGraphQL(TestCase):
    def setUp(self):
        self._client = Client()
        Project.objects.create(name=PROJECT_NAME, github_access_token=GITHUB_ACCESS_TOKEN, dao_address=DAO_ADDRESS)

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

    def test_login_mutation_successful(self):
        resp = self.query(
            '''
query {
  allProjects {
    name,
    daoAddress,
    githubAccessToken
  }
}
            '''
        )
        self.assertResponseNoErrors(resp, {'allProjects': [{'daoAddress': DAO_ADDRESS, 'name': PROJECT_NAME, 'githubAccessToken': GITHUB_ACCESS_TOKEN}]})


    def test_create_project(self):
        Project.objects.filter().delete()
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation maker {{
  createProject(repoName: "{PROJECT_NAME}", daoAddress: "{DAO_ADDRESS}", githubAccessToken:"{GITHUB_ACCESS_TOKEN}") {{
    newProject {{
      name
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {'createProject': {'newProject': {'name': PROJECT_NAME}}})

        all_projects = Project.objects.all()

        self.assertEqual(1, len(all_projects))
        self.assertEqual(PROJECT_NAME, all_projects[0].name)


    def test_get_project_by_id(self):
        resp = self.query(
            '''
query {
  project(id: "1") {
    name
  }
}
            '''
        )
        self.assertResponseNoErrors(resp, {'project': {'name': PROJECT_NAME}})

    def test_get_project_by_name(self):
        resp = self.query(
            f'''
query {{
  project(name: "{PROJECT_NAME}") {{
    id
  }}
}}
            '''
        )
        self.assertResponseNoErrors(resp, {'project': {'id': "1"}})
