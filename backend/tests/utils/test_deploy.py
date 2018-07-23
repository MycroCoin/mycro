import unittest
from unittest.mock import patch, MagicMock, call
import backend.server.utils.deploy as deploy
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider
from web3 import Account

PARITY_ENDPOINT = 'a.b.c'
INFURA_KEY = 'lol'
KALEIDO_USERNAME = 'kaleido'
KALEIDO_PASSWORD = 'pwd'
KALEIDO_ENDPOINT = 'a@b.c.x'
GANACHE_ENDPOINT = 'c@d.f.y'
ETHEREUM_PRIAVTE_KEY = '0xlol'


class TestDeploy(unittest.TestCase):

    def test_get_infura_key_not_set(self):
        self.assertIsNone(deploy.get_infura_api_key())

    @patch.dict('backend.server.utils.deploy.os.environ', {'INFURA_API_KEY': INFURA_KEY})
    def test_get_infura_key(self):
        self.assertEqual(INFURA_KEY, deploy.get_infura_api_key())

    @patch.dict('backend.server.utils.deploy.os.environ', {'INFURA_API_KEY': INFURA_KEY})
    def test_get_ropsten_w3(self):
        w3 = deploy._get_ropsten_w3()

        self.assertIsInstance(w3.providers[0], HTTPProvider)
        self.assertIn(INFURA_KEY, w3.providers[0].endpoint_uri)

    def test_get_parity_endpoint_not_set(self):
        self.assertEqual('http://localhost:8545', deploy.get_parity_endpoint())

    @patch.dict('backend.server.utils.deploy.os.environ', {'PARITY_ENDPOINT': PARITY_ENDPOINT})
    def test_get_parity_endpoint_set(self):
        self.assertEqual(PARITY_ENDPOINT, deploy.get_parity_endpoint())

    @patch.dict('backend.server.utils.deploy.os.environ', {'PARITY_ENDPOINT': PARITY_ENDPOINT})
    def test_get_parity_w3(self):
        w3 = deploy._get_parity_w3()

        self.assertIsInstance(w3.providers[0], HTTPProvider)

        self.assertEqual(PARITY_ENDPOINT, w3.providers[0].endpoint_uri)

    @patch.dict('backend.server.utils.deploy.os.environ', {'DEPLOY_ENV': 'ropsten'})
    def test_event_filter_w3_env_is_ropsten(self):
        w3 = deploy.get_event_filter_w3()

        self.assertEqual(deploy.get_parity_endpoint(), w3.providers[0].endpoint_uri)

    @patch.dict('backend.server.utils.deploy.os.environ', {'DEPLOY_ENV': 'ganache'})
    def test_event_filter_w3_env_is_not_ropsten(self):
        w3 = deploy.get_event_filter_w3()

        self.assertEqual(deploy._get_ganache_endpoint(), w3.providers[0].endpoint_uri)

    @patch.dict('backend.server.utils.deploy.os.environ',
                {'KALEIDO_USER': KALEIDO_USERNAME, 'KALEIDO_PASSWORD': KALEIDO_PASSWORD})
    def test_get_kaleido_username_password_both_set(self):
        self.assertEqual((KALEIDO_USERNAME, KALEIDO_PASSWORD), deploy._get_kaleido_username_password())

    @patch.dict('backend.server.utils.deploy.os.environ', {'KALEIDO_PASSWORD': KALEIDO_PASSWORD})
    def test_get_kaleido_username_password_only_password_set(self):
        self.assertEqual(('u0g9fge43j', KALEIDO_PASSWORD), deploy._get_kaleido_username_password())

    def test_get_kaleido_username_password_password_not_set(self):
        self.assertEqual(('u0g9fge43j', None), deploy._get_kaleido_username_password())

    @patch.dict('backend.server.utils.deploy.os.environ',
                {'KALEIDO_USER': KALEIDO_USERNAME, 'KALEIDO_PASSWORD': KALEIDO_PASSWORD})
    def test_kaleido_endpoint_not_set_in_env(self):
        endpoint = deploy._get_kaleido_endpoint()

        self.assertIn(KALEIDO_USERNAME, endpoint)
        self.assertIn(KALEIDO_PASSWORD, endpoint)

    @patch.dict('backend.server.utils.deploy.os.environ',
                {'KALEIDO_USER': KALEIDO_USERNAME, 'KALEIDO_PASSWORD': KALEIDO_PASSWORD,
                 'KALEIDO_ENDPOINT': KALEIDO_ENDPOINT})
    def test_get_kaleido_endpoint_username_password_endpoint_all_set_in_env(self):
        self.assertEqual(KALEIDO_ENDPOINT, deploy._get_kaleido_endpoint())

    def get_ganache_endpoint_not_set_in_env(self):
        self.assertEqual('http://127.0.0.1', deploy._get_ganache_endpoint())

    @patch.dict('backend.server.utils.deploy.os.environ', {'GANACHE_ENDPOINT': GANACHE_ENDPOINT})
    def test_get_ganache_endpoint_set_in_env(self):
        self.assertEqual(GANACHE_ENDPOINT, deploy._get_ganache_endpoint())


    @patch.dict('backend.server.utils.deploy.os.environ', {'GANACHE_ENDPOINT': GANACHE_ENDPOINT})
    def test_get_ganache_w3(self):
        w3 = deploy._get_ganache_w3()

        self.assertEqual(GANACHE_ENDPOINT, w3.providers[0].endpoint_uri)

    @patch.dict('backend.server.utils.deploy.os.environ', {'KALEIDO_ENDPOINT': KALEIDO_ENDPOINT})
    def test_get_kaleido_w3(self):
        w3 = deploy._get_kaleido_w3()

        self.assertEqual(KALEIDO_ENDPOINT, w3.providers[0].endpoint_uri)
        self.assertIn(geth_poa_middleware, w3.middleware_stack)

    def test_get_ethereum_private_key_not_set(self):
        with self.assertRaises(KeyError):
            deploy.get_private_key()

    @patch.dict('backend.server.utils.deploy.os.environ', {'ETHEREUM_PRIVATE_KEY': ETHEREUM_PRIAVTE_KEY})
    def test_get_ethereum_private_key(self):
           self.assertEqual(ETHEREUM_PRIAVTE_KEY, deploy.get_private_key())


    def test_deploy_contract_without_private_key(self):
        w3 = MagicMock()
        contract_interface = MagicMock()
        args = (1,)

        deploy._deploy_contract(w3, contract_interface, *args, private_key=None, timeout=10)

        contract_interface.__getitem__.assert_has_calls([call('abi'), call('bin'), call('abi')])

        w3.eth.contract.return_value.constructor.assert_called_with(*args)
        w3.eth.contract.return_value.constructor.return_value.transact.assert_called_once_with(transaction={'from': w3.eth.accounts[0]})

        tx_hash = w3.eth.contract.return_value.constructor.return_value.transact.return_value
        w3.eth.waitForTransactionReceipt.assert_called_once_with(tx_hash, timeout=10)

    @patch('backend.server.utils.deploy.Account')
    def test_deploy_contract_with_private_key(self, account_mock):
        w3 = MagicMock()
        contract_interface = MagicMock()
        args = (1,)
        private_key = 'abcde'
        account = MagicMock()
        account_mock.privateKeyToAccount.return_value = account

        deploy._deploy_contract(w3, contract_interface, *args, private_key=private_key, timeout=10)

        contract_interface.__getitem__.assert_has_calls([call('abi'), call('bin'), call('abi')])

        w3.eth.contract.return_value.constructor.assert_called_with(*args)
        account_mock.privateKeyToAccount.assert_called_once_with(private_key)

        txn = w3.eth.contract.return_value.constructor.return_value.buildTransaction
        txn.assert_called_once_with({'nonce': w3.eth.getTransactionCount.return_value, 'gas': w3.eth.getBlock.return_value.gasLimit, 'gasPrice': 21000000000})

        w3.eth.account.signTransaction.assert_called_once_with(txn.return_value, private_key)
        tx_hash = w3.eth.sendRawTransaction.return_value

        w3.eth.waitForTransactionReceipt.assert_called_once_with(tx_hash, timeout=10)
        
