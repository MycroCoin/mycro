from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.util.constants as constants
import os
from backend.server.schemas.mycro_dao import ENV_DAO_ADDRESS_KEY


class TestMycroDaoSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        os.environ.pop(ENV_DAO_ADDRESS_KEY, None)

    def test_return_dao_address_from_env(self):
        os.environ[ENV_DAO_ADDRESS_KEY] = constants.DAO_ADDRESS
        resp = self.query("""
query {
  mycroDao
}
        """)
        self.assertResponseNoErrors(resp, {'mycroDao': constants.DAO_ADDRESS})

    def test_return_none_when_env_not_set(self):
        resp = self.query("""
query {
  mycroDao
}
        """)
        self.assertResponseNoErrors(resp, {'mycroDao': None})
