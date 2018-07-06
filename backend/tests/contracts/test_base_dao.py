from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.utils import deploy_contract
from eth_tester.exceptions import TransactionFailed
import unittest

W3 = Web3(EthereumTesterProvider())
SYMBOL = 'lol'
NAME = 'lolcoin'
DECIMALS = 18
TOTAL_SUPPLY = 100
INITIAL_ADDRESS = '0x1111111111111111111111111111111111111111'
INITIAL_ADDRESSES = [W3.eth.accounts[7], W3.eth.accounts[8], W3.eth.accounts[9]]
INITIAL_BALANCES = [33, 33, 34]


class TestBaseDao(unittest.TestCase):

    def setUp(self):
        self.compiler = ContractCompiler()

        contract_interface = self.compiler.get_contract_interface("base_dao.sol", "BaseDao")
        _, _, self.dao_instance = deploy_contract(W3, contract_interface, SYMBOL, NAME, DECIMALS, TOTAL_SUPPLY,
                                                  INITIAL_ADDRESSES, INITIAL_BALANCES)

    def test_can_propose(self):
        asc_address = W3.eth.accounts[1]
        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})
        proposals = self.dao_instance.get_proposals()

        self.assertEqual(1, len(proposals))
        self.assertEqual(str(asc_address), proposals[0])

    def test_vote_fails_for_unproposed_asc(self):
        asc_address = W3.eth.accounts[1]

        with self.assertRaises(TransactionFailed):
            self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[0]})

    def test_vote_fails_when_voting_second_time(self):
        asc_interface = self.compiler.get_contract_interface("merge_asc.sol", "MergeASC")

        # passing dummy address for merge module
        _, asc_address, _ = deploy_contract(W3, asc_interface, W3.eth.accounts[0])

        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[0]})

        with self.assertRaises(TransactionFailed):
            self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[0]})

    def test_propose_same_asc_twice_fails(self):
        asc_address = W3.eth.accounts[1]

        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})

        with self.assertRaises(TransactionFailed):
            self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})

    def test_starting_balance(self):
        balance = self.dao_instance.balanceOf(W3.eth.accounts[7])

        self.assertEqual(33, balance)

    def test_register_module(self):
        module = W3.eth.accounts[1]

        self.dao_instance.registerModule(module, transact={'from': W3.eth.accounts[0]})

        self.assertTrue(self.dao_instance.isModuleRegistered(module))


    def test_vote_passes_threshold_executes_asc(self):
        asc_interface = self.compiler.get_contract_interface("merge_asc.sol", "MergeASC")
        merge_module_interface = self.compiler.get_contract_interface("merge_module.sol", "MergeModule")

        merge_contract, merge_address, merge_instance = deploy_contract(W3, merge_module_interface)
        _, asc_address, asc_instance = deploy_contract(W3, asc_interface, merge_address)

        event_filter = merge_contract.events.Merge.createFilter(argument_filters={'filter': {'event': 'Merge'}},
                                                                fromBlock=0)

        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[7]})

        self.assertEqual(0, len(event_filter.get_new_entries()))

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[8]})

        entries = event_filter.get_new_entries()

        self.assertEqual(1, len(entries))
        self.assertEqual(1, entries[0]["args"]["pr_id"])
