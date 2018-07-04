from backend.server.models import Project, ASC
from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.util.constants as constants


class TestASCSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(repo_name=constants.PROJECT_NAME, dao_address=constants.DAO_ADDRESS)
        self.asc = ASC.objects.create(address=constants.ASC_ADDRESS, project=self.project)

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

    def test_create_asc(self):
        ASC.objects.filter().delete()
        # need to double up on braces because of f-strings
        resp = self.query(f"""
mutation {{
  createAsc(address: "{constants.ASC_ADDRESS}", projectId: "1")  {{
    newAsc {{
      address
    }}
  }}
}}
""")
        self.assertResponseNoErrors(resp, {'createAsc': {'newAsc': {'address': constants.ASC_ADDRESS}}})

        all_ascs = ASC.objects.all()

        self.assertEqual(1, len(all_ascs))
        self.assertEqual(constants.PROJECT_NAME, all_ascs[0].project.repo_name)
        self.assertEqual(constants.ASC_ADDRESS, all_ascs[0].address)
