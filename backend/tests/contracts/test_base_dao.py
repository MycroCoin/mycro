from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.deploy import _deploy_contract
from eth_tester.exceptions import TransactionFailed
import unittest
import backend.tests.testing_utilities.constants as constants

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
        self.base_dao_interface = constants.COMPILER.get_contract_interface("base_dao.sol", "BaseDao")
        self.dao_contract, self.dao_address, self.dao_instance = _deploy_contract(W3, self.base_dao_interface, SYMBOL,
                                                                                  NAME, DECIMALS,
                                                                                  TOTAL_SUPPLY,
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
        merge_asc_interface = constants.COMPILER.get_contract_interface("merge_asc.sol", "MergeASC")

        _, asc_address, _ = _deploy_contract(W3, merge_asc_interface, W3.eth.accounts[0], 15, constants.PR_ID)

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
        merge_module_interface = constants.COMPILER.get_contract_interface("merge_module.sol", "MergeModule")
        merge_contract, merge_address, merge_instance = _deploy_contract(W3, merge_module_interface)
        self.dao_instance.registerModule(merge_address, transact={'from': W3.eth.accounts[0]})

        dummy_module_interface = constants.COMPILER.get_contract_interface("dummy_module.sol", "DummyModule")
        _, dummy_module_address, _ = _deploy_contract(W3, dummy_module_interface)

        self.assertTrue(self.dao_instance.isModuleRegistered(merge_address))
        self.assertFalse(self.dao_instance.isModuleRegistered(dummy_module_address))

    def test_vote_passes_threshold_executes_asc(self):
        reward = 15

        merge_asc_interface = constants.COMPILER.get_contract_interface("merge_asc.sol", "MergeASC")
        merge_module_interface = constants.COMPILER.get_contract_interface("merge_module.sol", "MergeModule")

        merge_contract, merge_address, merge_instance = _deploy_contract(W3, merge_module_interface)
        _, asc_address, asc_instance = _deploy_contract(W3, merge_asc_interface, W3.eth.accounts[5], reward,
                                                        constants.PR_ID)

        event_filter = merge_contract.events.Merge.createFilter(argument_filters={'filter': {'event': 'Merge'}},
                                                                fromBlock=0)

        self.dao_instance.registerModule(merge_address, transact={'from': W3.eth.accounts[0]})
        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[7]})

        self.assertEqual(0, len(event_filter.get_new_entries()))

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[8]})

        entries = event_filter.get_new_entries()

        self.assertEqual(1, len(entries))
        self.assertEqual(constants.PR_ID, entries[0]["args"]["pr_id"])

        self.assertEqual(reward, self.dao_instance.balanceOf(W3.eth.accounts[5]))
        self.assertEqual(TOTAL_SUPPLY + reward, self.dao_instance.totalSupply())

        self.assertEqual([constants.PR_ID], merge_instance.pullRequestsToMerge())

    def test_vote_for_executed_asc_doesnt_do_raise_new_merge_event(self):
        reward = 15

        merge_asc_interface = constants.COMPILER.get_contract_interface("merge_asc.sol", "MergeASC")
        merge_module_interface = constants.COMPILER.get_contract_interface("merge_module.sol", "MergeModule")

        merge_contract, merge_address, merge_instance = _deploy_contract(W3, merge_module_interface)
        _, asc_address, asc_instance = _deploy_contract(W3, merge_asc_interface, W3.eth.accounts[5], reward,
                                                        constants.PR_ID)

        event_filter = merge_contract.events.Merge.createFilter(argument_filters={'filter': {'event': 'Merge'}},
                                                                fromBlock=0)

        self.dao_instance.registerModule(merge_address, transact={'from': W3.eth.accounts[0]})
        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[7]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[8]})

        entries = event_filter.get_new_entries()

        self.assertTrue(asc_instance.hasExecuted())
        self.assertEqual(1, len(entries))
        self.assertEqual(constants.PR_ID, entries[0]["args"]["pr_id"])

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[9]})
        entries = event_filter.get_new_entries()

        self.assertEqual(0, len(entries))

        self.assertEqual(reward, self.dao_instance.balanceOf(W3.eth.accounts[5]))

    def test_vote_threshold_updates_after_asc_executes(self):
        reward = 50

        merge_asc_interface = constants.COMPILER.get_contract_interface("merge_asc.sol", "MergeASC")
        merge_module_interface = constants.COMPILER.get_contract_interface("merge_module.sol", "MergeModule")

        merge_contract, merge_address, merge_instance = _deploy_contract(W3, merge_module_interface)
        self.dao_instance.registerModule(merge_address, transact={'from': W3.eth.accounts[0]})

        _, asc_address, asc_instance = _deploy_contract(W3, merge_asc_interface, W3.eth.accounts[5], reward,
                                                        constants.PR_ID)
        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[7]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[8]})

        self.assertEqual(TOTAL_SUPPLY + reward, self.dao_instance.totalSupply())

        # deploy new ASC
        _, asc_address, asc_instance = _deploy_contract(W3, merge_asc_interface, W3.eth.accounts[5], reward,
                                                        constants.PR_ID)
        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[7]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[8]})

        self.assertFalse(asc_instance.hasExecuted())

        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[9]})

        self.assertTrue(asc_instance.hasExecuted())

    def test_constructor_adds_to_transactors(self):
        self.assertEqual(INITIAL_ADDRESSES, self.dao_instance.getTransactors())

    def test_transfer_event_emitted_during_construction(self):
        event_filter = self.dao_contract.events.Transfer.createFilter(
            argument_filters={'filter': {'event': 'Transfer'}},
            fromBlock=0)

        events = event_filter.get_new_entries()

        self.assertEqual(3, len(events))

    def test_transfer_adds_to_transactors(self):
        event_filter = self.dao_contract.events.Transfer.createFilter(
            argument_filters={'filter': {'event': 'Transfer'}},
            fromBlock=0)
        # consume events emitted during construction
        event_filter.get_new_entries()

        # transfer 10 tokens to accounts[6] from accounts[7]
        self.dao_instance.transfer(W3.eth.accounts[6], 10, transact={'from': W3.eth.accounts[7]})

        self.assertEqual(10, self.dao_instance.balanceOf(W3.eth.accounts[6]))
        self.assertEqual(INITIAL_ADDRESSES + [W3.eth.accounts[6]], self.dao_instance.getTransactors())
        self.assertEqual(23, self.dao_instance.balanceOf(W3.eth.accounts[7]))
        self.assertEqual(1, len(event_filter.get_new_entries()))

    def test_transfer_from_adds_to_transactors(self):
        event_filter = self.dao_contract.events.Transfer.createFilter(
            argument_filters={'filter': {'event': 'Transfer'}},
            fromBlock=0)
        # consume events emitted during construction
        event_filter.get_new_entries()

        # approve accounts[6]
        num_tokens = 10
        self.dao_instance.approve(W3.eth.accounts[6], num_tokens, transact={'from': W3.eth.accounts[7]})

        self.dao_instance.transferFrom(W3.eth.accounts[7], W3.eth.accounts[6], num_tokens,
                                       transact={'from': W3.eth.accounts[6]})

        self.assertEqual(num_tokens, self.dao_instance.balanceOf(W3.eth.accounts[6]))
        self.assertEqual(INITIAL_ADDRESSES + [W3.eth.accounts[6]], self.dao_instance.getTransactors())
        self.assertEqual(23, self.dao_instance.balanceOf(W3.eth.accounts[7]))
        self.assertEqual(1, len(event_filter.get_new_entries()))

    def test_duplicate_account_in_transactors_when_balance_emptied_then_filled(self):
        self.dao_instance.transfer(W3.eth.accounts[8], 33, transact={'from': W3.eth.accounts[7]})
        self.dao_instance.transfer(W3.eth.accounts[7], 33, transact={'from': W3.eth.accounts[8]})

        self.assertEqual(INITIAL_ADDRESSES + [W3.eth.accounts[7]], self.dao_instance.getTransactors())

    def test_upgrade_symbol_not_the_same(self):
        __, __, new_dao_instance = _deploy_contract(W3, self.base_dao_interface, 'dif', NAME, DECIMALS,
                                                    TOTAL_SUPPLY,
                                                    INITIAL_ADDRESSES, INITIAL_BALANCES)

        # expected to not throw for now
        new_dao_instance.upgradeFrom(self.dao_address)

    def test_upgrade_name_not_the_same(self):
        __, __, new_dao_instance = _deploy_contract(W3, self.base_dao_interface, SYMBOL, 'dif', DECIMALS,
                                                    TOTAL_SUPPLY,
                                                    INITIAL_ADDRESSES, INITIAL_BALANCES)

        # expected to not throw for now
        new_dao_instance.upgradeFrom(self.dao_address)

    def test_upgrade_decimals_not_the_same(self):
        __, __, new_dao_instance = _deploy_contract(W3, self.base_dao_interface, SYMBOL, NAME, 1,
                                                    TOTAL_SUPPLY,
                                                    INITIAL_ADDRESSES, INITIAL_BALANCES)

        with self.assertRaises(TransactionFailed):
            new_dao_instance.upgradeFrom(self.dao_address)

    def test_upgrade_works_as_expected(self):
        # create, propose and vote for an ASC
        merge_asc_interface = constants.COMPILER.get_contract_interface("merge_asc.sol", "MergeASC")
        _, asc_address, _ = _deploy_contract(W3, merge_asc_interface, W3.eth.accounts[0], 15, constants.PR_ID)
        self.dao_instance.propose(asc_address, transact={'from': W3.eth.accounts[0]})
        self.dao_instance.vote(asc_address, transact={'from': W3.eth.accounts[0]})

        # create and register a module
        merge_module_interface = constants.COMPILER.get_contract_interface("merge_module.sol", "MergeModule")
        __, merge_address, __ = _deploy_contract(W3, merge_module_interface)
        self.dao_instance.registerModule(merge_address, transact={'from': W3.eth.accounts[0]})

        __, __, new_dao_instance = _deploy_contract(W3, self.base_dao_interface, SYMBOL, NAME, DECIMALS,
                                                    1,
                                                    [], [])
        new_dao_instance.upgradeFrom(self.dao_address, transact={'from': W3.eth.accounts[0]})

        self.assertEqual(new_dao_instance.name(), self.dao_instance.name())
        self.assertEqual(new_dao_instance.symbol(), self.dao_instance.symbol())
        self.assertEqual(new_dao_instance.decimals(), self.dao_instance.decimals())
        self.assertEqual(new_dao_instance.totalSupply(), self.dao_instance.totalSupply())
        self.assertEqual(new_dao_instance.threshold(), self.dao_instance.threshold())
        self.assertEqual(new_dao_instance.get_proposals(), self.dao_instance.get_proposals())
        self.assertEqual(new_dao_instance.getTransactors(), self.dao_instance.getTransactors())
        for transactor in self.dao_instance.getTransactors():
            self.assertEqual(new_dao_instance.balanceOf(transactor), self.dao_instance.balanceOf(transactor))

        for asc in self.dao_instance.get_proposals():
            self.assertEqual(new_dao_instance.get_asc_votes(asc), self.dao_instance.get_asc_votes(asc))

        self.assertNotEqual(new_dao_instance.getModuleByCode(1), self.dao_instance.getModuleByCode(1))
