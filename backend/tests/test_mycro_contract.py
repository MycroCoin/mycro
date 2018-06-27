from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from backend.src.utils.contract_compiler import ContractCompiler
from backend.src.utils.utils import deploy_contract
import unittest


class TestMycro(unittest.TestCase):

    def setUp(self):
        self.compiler = ContractCompiler()

        # web3.py instance
        self.w3 = Web3(EthereumTesterProvider())

        contract_interface = self.compiler.get_contract_interface("mycro.sol", "MycroCoin")
        _, _, self.mycro_instance = deploy_contract(self.w3, contract_interface)


    def test_can_propose(self):
        asc_address = self.w3.eth.accounts[1]
        self.mycro_instance.propose(asc_address, transact={'from': self.w3.eth.accounts[0]})
        proposals = self.mycro_instance.get_proposals()

        self.assertEqual(1, len(proposals))
        self.assertEqual(str(asc_address), proposals[0])

    def test_can_vote(self):
        asc_address = self.w3.eth.accounts[1]
        self.mycro_instance.vote(asc_address, transact={'from': self.w3.eth.accounts[0]})

        self.assertEqual(1, self.mycro_instance.get_num_votes(asc_address))

    def test_execute_asc(self):
        asc_interface = self.compiler.get_contract_interface("dummy_asc.sol", "DummyASC")

        _, asc_address, asc_instance = deploy_contract(self.w3, asc_interface)

        # should not fail
        self.mycro_instance.execute_asc(asc_address);
