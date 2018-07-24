import unittest
from unittest.mock import patch, MagicMock, call
import backend.server.utils.deploy as deploy
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider
from web3 import Account
import backend.settings as settings

PARITY_ENDPOINT = 'a.b.c'
INFURA_KEY = 'lol'
ETHEREUM_PRIAVTE_KEY = '0xlol'


class TestDeploy(unittest.TestCase):


    @patch.dict('backend.settings.os.environ', {'INFURA_API_KEY': INFURA_KEY})
    def test_get_ropsten_w3(self):
        w3 = deploy._get_ropsten_w3()

        self.assertIsInstance(w3.providers[0], HTTPProvider)
        self.assertIn(INFURA_KEY, w3.providers[0].endpoint_uri)

    def test_get_parity_endpoint_not_set(self):
        self.assertEqual('http://localhost:8545', settings.parity_endpoint())

    @patch.dict('backend.settings.os.environ', {'PARITY_ENDPOINT': PARITY_ENDPOINT})
    def test_get_parity_endpoint_set(self):
        self.assertEqual(PARITY_ENDPOINT, settings.parity_endpoint())

    @patch.dict('backend.settings.os.environ', {'PARITY_ENDPOINT': PARITY_ENDPOINT})
    def test_get_parity_w3(self):
        w3 = deploy._get_parity_w3()

        self.assertIsInstance(w3.providers[0], HTTPProvider)

        self.assertEqual(PARITY_ENDPOINT, w3.providers[0].endpoint_uri)

    @patch.dict('backend.settings.os.environ', {'DEPLOY_ENV': 'ropsten'})
    def test_event_filter_w3_env_is_ropsten(self):
        w3 = deploy.get_event_filter_w3()

        self.assertEqual(settings.parity_endpoint(), w3.providers[0].endpoint_uri)

    @patch.dict('backend.settings.os.environ', {'DEPLOY_ENV': 'parity'})
    def test_event_filter_w3_env_is_not_ropsten(self):
        w3 = deploy.get_event_filter_w3()

        self.assertEqual(settings.parity_endpoint(), w3.providers[0].endpoint_uri)


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
        txn.assert_called_once_with({'nonce': w3.eth.getTransactionCount.return_value, 'gas': 4000000, 'gasPrice': 21000000000})

        w3.eth.account.signTransaction.assert_called_once_with(txn.return_value, private_key)
        tx_hash = w3.eth.sendRawTransaction.return_value

        w3.eth.waitForTransactionReceipt.assert_called_once_with(tx_hash, timeout=10)
        
