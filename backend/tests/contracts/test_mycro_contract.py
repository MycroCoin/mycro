from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from backend.server.utils.deploy import _deploy_contract
import unittest
import backend.tests.testing_utilities.constants as constants


class TestMycro(unittest.TestCase):

    def setUp(self):

        # web3.py instance
        self.w3 = Web3(EthereumTesterProvider())

        contract_interface = constants.COMPILER.get_contract_interface("mycro.sol", "MycroCoin")
        self.mycro_contract, _, self.mycro_instance = _deploy_contract(self.w3, contract_interface)

    def test_give_initial_balance(self):
        balance = self.mycro_instance.balanceOf("0x364ca3F935E88Fbc9e041d2032F996CAc69452e6")

        self.assertEqual(self.mycro_instance.totalSupply(), balance)

    def test_register_project(self):
        project_address = self.w3.eth.accounts[1]
        event_filter = self.mycro_contract.events.RegisterProject.createFilter(
            argument_filters={'filter': {'event': 'RegisterProject'}}, fromBlock=0)

        self.mycro_instance.registerProject(project_address, transact={'from': self.w3.eth.accounts[0]})

        projects = self.mycro_instance.getProjects()
        self.assertEqual(project_address, projects[0])

        events = event_filter.get_new_entries()
        self.assertEqual(project_address, events[0]['args']['projectAddress'])
