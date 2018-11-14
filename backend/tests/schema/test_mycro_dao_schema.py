from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.testing_utilities.constants as constants
from backend.server.models import Project
from graphql.error.located_error import GraphQLLocatedError


class TestMycroDaoSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()

    def test_return_none_when_not_created(self):
        resp = self.query("""
query {
  mycroDao
}
        """)
        self.assertResponseNoErrors(resp, {'mycroDao': None})

    def test_return_proper_address_when_created(self):
        Project.objects.create(dao_address=constants.PROJECT_ADDRESS, is_mycro_dao=True, initial_balances=constants.CREATORS_BALANCES)


        resp = self.query("""
query {
  mycroDao
}
        """)
        self.assertResponseNoErrors(resp, {'mycroDao': constants.PROJECT_ADDRESS})

    def test_raise_when_two_exist(self):
        Project.objects.create(dao_address=constants.PROJECT_ADDRESS, is_mycro_dao=True, initial_balances=constants.CREATORS_BALANCES)
        Project.objects.create(dao_address='fake address', is_mycro_dao=True, initial_balances=constants.CREATORS_BALANCES)


        # this query raises an error in the logs, it's ok
        resp = self.query("""
query {
  mycroDao
}
        """)
        self.assertErrorNoResponse(resp, 'Found 2 instances')
