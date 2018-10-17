from django.test import TestCase, Client
import json
from backend.server.models import Wallet
from backend.tests.testing_utilities.constants import WALLET_PRIVATE_KEY


class MycroDjangoTest(TestCase):
    """
    Base test case for all Django tests in the Mycro world
    """

    def setUp(self):
        self._client = Client()
        Wallet.objects.create(private_key=WALLET_PRIVATE_KEY, address='fake')


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

    def assertErrorNoResponse(self, resp: dict, msg):
        self.assertRegex(resp['errors'][0]['message'], msg)
        lol = 'lol'
