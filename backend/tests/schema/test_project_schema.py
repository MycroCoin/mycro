from backend.server.models import Project, ASC
from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.util.constants as constants


class TestProjectSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(repo_name=constants.PROJECT_NAME, dao_address=constants.DAO_ADDRESS)

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
            'allProjects': [{'daoAddress': constants.DAO_ADDRESS, 'repoName': constants.PROJECT_NAME}]})


    def test_create_project(self):
        Project.objects.filter().delete()
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createProject(repoName: "{constants.PROJECT_NAME}", daoAddress: "{constants.DAO_ADDRESS}") {{
    newProject {{
      repoName
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {'createProject': {'newProject': {'repoName': constants.PROJECT_NAME}}})

        all_projects = Project.objects.all()

        self.assertEqual(1, len(all_projects))
        self.assertEqual(constants.PROJECT_NAME, all_projects[0].repo_name)

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
        self.assertResponseNoErrors(resp, {'project': {'repoName': constants.PROJECT_NAME}})

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
