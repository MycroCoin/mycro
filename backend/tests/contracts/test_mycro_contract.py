from backend.server.utils.deploy import _deploy_contract
import unittest
import backend.tests.testing_utilities.constants as constants
from eth_tester.exceptions import TransactionFailed


class TestMycro(unittest.TestCase):

    def setUp(self):
        # web3.py instance

        self.contract_interface = constants.COMPILER.get_contract_interface(
            "mycro.sol", "MycroCoin")
        self.mycro_contract, self.mycro_address, self.mycro_instance = _deploy_contract(
            constants.W3,
            self.contract_interface)

    def test_give_initial_balance(self):
        balance = self.mycro_instance.balanceOf(
            "0x364ca3F935E88Fbc9e041d2032F996CAc69452e6")

        self.assertEqual(self.mycro_instance.totalSupply(), balance)

    def test_register_project(self):
        project_address = constants.W3.eth.accounts[1]
        event_filter = self.mycro_contract.events.RegisterProject.createFilter(
            argument_filters={'filter': {'event': 'RegisterProject'}},
            fromBlock=0)

        self.mycro_instance.registerProject(project_address, transact={
            'from': constants.W3.eth.accounts[0]})

        projects = self.mycro_instance.getProjects()
        self.assertEqual(project_address, projects[0])

        events = event_filter.get_new_entries()
        self.assertEqual(project_address, events[0]['args']['projectAddress'])

    def test_upgrade(self):
        # register a project with the original mycro dao
        project_address = constants.W3.eth.accounts[1]
        self.mycro_instance.registerProject(project_address, transact={
            'from': constants.W3.eth.accounts[0]})

        # create, propose and vote for an ASC
        merge_asc_interface = constants.COMPILER.get_contract_interface(
            "merge_asc.sol", "MergeASC")
        _, asc_address, _ = _deploy_contract(constants.W3, merge_asc_interface,
                                             constants.W3.eth.accounts[0], 15,
                                             constants.PR_ID)
        self.mycro_instance.propose(asc_address,
                                    transact={'from': constants.W3.eth.accounts[0]})

        # create a new mycro dao
        new_mycro_contract, new_mycro_address, new_mycro_instance = _deploy_contract(
            constants.W3, self.contract_interface)

        # we want to check if any RegisterProject events are emitted
        event_filter = new_mycro_contract.events.RegisterProject.createFilter(
            argument_filters={'filter': {'event': 'RegisterProject'}},
            fromBlock=0)

        # perform the upgrade
        new_mycro_instance.upgradeFrom(self.mycro_address, transact={
            'from': constants.W3.eth.accounts[0]})

        # want to make sure that BaseDao state is upgraded along the mycro specific state
        self.assertEqual(new_mycro_instance.get_proposals(),
                         self.mycro_instance.get_proposals())
        self.assertEqual(new_mycro_instance.getProjects(),
                         self.mycro_instance.getProjects())

        # Projects which are copied during an upgrade should emit an event
        self.assertEqual(1, len(event_filter.get_new_entries()))

    def test_cannot_upgrade_non_mycro_dao(self):
        __, __, new_mycro_instance = _deploy_contract(
            constants.W3, self.contract_interface)

        with self.assertRaises(TransactionFailed):
            new_mycro_instance.upgradeFrom(constants.W3.eth.accounts[1], transact={
                'from': constants.W3.eth.accounts[0]})
