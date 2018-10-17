import unittest
from unittest.mock import patch, MagicMock, call, ANY
import backend.server.utils.deploy as deploy
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider
from web3 import Account
import backend.settings as settings
import backend.tests.testing_utilities.constants as constants
import asyncio

PARITY_ENDPOINT = 'a.b.c'
INFURA_KEY = 'lol'
ETHEREUM_PRIAVTE_KEY = '0xlol'


class TestDeploy(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

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

    def test_deploy_contract_without_private_key(self):
        w3 = MagicMock()
        w3.eth.getBalance.return_value = int(10e18)
        contract_interface = MagicMock()
        args = (1,)


        with self.assertRaisesRegex(ValueError, 'cannot be none'):
            deploy._deploy_contract(w3, contract_interface, *args, private_key=None,
                                                                           timeout=10)



    @patch('backend.server.utils.deploy.Account')
    def test_deploy_contract_with_private_key(self, account_mock):
        w3 = MagicMock()
        w3.eth.getBalance.return_value = int(10e18)
        latest_block = w3.eth.getBlock.return_value
        latest_block.gasLimit = 1024

        contract_interface = MagicMock()
        args = (1,)
        private_key = 'abcde'
        account = MagicMock()
        account_mock.privateKeyToAccount.return_value = account

        deploy._deploy_contract(w3, contract_interface, *args, private_key=private_key, timeout=10)

        contract_interface.__getitem__.assert_has_calls([call('abi'), call('bin'), call('abi')])

        w3.eth.contract.return_value.constructor.assert_called_with(*args)
        # account_mock.privateKeyToAccount.assert_called_once_with(private_key)
        self.assertEqual(3, account_mock.privateKeyToAccount.call_count)

        txn = w3.eth.contract.return_value.constructor.return_value.buildTransaction
        txn.assert_called_once_with(
            {'nonce': w3.eth.getTransactionCount.return_value, 'gas': 7000000, 'gasPrice': 1})

        w3.eth.account.signTransaction.assert_called_once_with(txn.return_value, private_key)
        tx_hash = w3.eth.sendRawTransaction.return_value

        w3.eth.waitForTransactionReceipt.assert_called_once_with(tx_hash, timeout=10)

    @patch('backend.server.utils.deploy.get_w3')
    def test_call_contract_func(self, get_w3_mock):
        w3 = get_w3_mock.return_value
        w3.eth.getBalance.return_value = int(10e18)

        private_key = settings.ethereum_private_key()
        timeout = 1
        contract = MagicMock()

        receipt = deploy.call_contract_function(contract.functions.registerProject,
                                                constants.DAO_ADDRESS,
                                                private_key=private_key, timeout=timeout)

        self.assertEqual(receipt, w3.eth.waitForTransactionReceipt.return_value)
        w3.eth.waitForTransactionReceipt.assert_called_once_with(w3.eth.sendRawTransaction.return_value,
                                                                 timeout=timeout)

        deploy.call_contract_function(contract.functions.registerProject, constants.DAO_ADDRESS,
                                      timeout=timeout, private_key=settings.ethereum_private_key())

        self.assertEqual(2, w3.eth.waitForTransactionReceipt.call_count)

    def test_transfer_between_accounts(self):
        source_account_key = constants.WALLET_PRIVATE_KEY
        destination_account_key = settings.ethereum_private_key()
        amount = 100
        w3 = MagicMock()
        destination_address = Account.privateKeyToAccount(destination_account_key)

        deploy.transfer_between_accounts(w3, source_account_key, destination_account_key, amount)

        w3.eth.account.signTransaction.assert_called_once_with(dict(nonce=ANY, gasPrice=ANY, gas=ANY, to=destination_address.address, value=amount), source_account_key)
        w3.eth.sendRawTransaction.assert_called_once_with(w3.eth.account.signTransaction.return_value.rawTransaction)
        w3.eth.waitForTransactionReceipt.assert_called_once_with(w3.eth.sendRawTransaction.return_value, timeout=120)

    @patch('backend.server.utils.deploy.get_wallet_balance')
    @patch('backend.server.utils.deploy.transfer_between_accounts')
    def test_fund_account_if_needed_happy_case(self, transfer_mock, get_balance_mock):
        get_balance_mock.side_effect = [int(10e18), 0]
        w3 = MagicMock()

        deploy.fund_account_if_needed(w3, 'lol', 'fake')

        transfer_mock.assert_called_once_with(w3, 'lol', 'fake', int(1e18))

    @patch('backend.server.utils.deploy.get_wallet_balance')
    @patch('backend.server.utils.deploy.transfer_between_accounts')
    def test_fund_account_source_doesnt_have_enough(self,transfer_mock,  get_balance_mock):
        get_balance_mock.side_effect = [0, 0]
        w3 = MagicMock()

        with self.assertRaisesRegex(deploy.TransferError, 'does not have enough'):
            deploy.fund_account_if_needed(w3, 'lol', 'fake')

        transfer_mock.assert_not_called()

    @patch('backend.server.utils.deploy.get_wallet_balance')
    @patch('backend.server.utils.deploy.transfer_between_accounts')
    def test_fund_account_source_destination_already_has_enough(self,transfer_mock,  get_balance_mock):
        get_balance_mock.side_effect = [0, int(10e18)]
        w3 = MagicMock()

        deploy.fund_account_if_needed(w3, 'lol', 'fake')

        transfer_mock.assert_not_called()
