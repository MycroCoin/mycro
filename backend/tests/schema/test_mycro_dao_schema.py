from backend.tests.mycro_django_test import MycroDjangoTest
import backend.tests.testing_utilities.constants as constants
import os


class TestMycroDaoSchema(MycroDjangoTest):

    def setUp(self):
        super().setUp()

    def test_return_none_when_not_set(self):
        resp = self.query("""
query {
  mycroDao
}
        """)
        self.assertResponseNoErrors(resp, {'mycroDao': None})
