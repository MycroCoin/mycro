import json
import web3

from web3 import Web3, HTTPProvider
from web3.providers.eth_tester import EthereumTesterProvider
from web3.contract import ConciseContract
from backend.tests.util.contract_compiler import ContractCompiler
import unittest

class TestMycro(unittest.TestCase):

    def setUp(self):

        self.compiler = ContractCompiler()

        # web3.py instance
        self.w3 = Web3(EthereumTesterProvider())

        contract_interface = self.compiler.get_contract_interface("mycro.sol", "MycroCoin")
        _, _, self.mycro_instance = self._deploy_contract(contract_interface)

    def _deploy_contract(self, contract_interface):
        # Instantiate and deploy contract
        contract = self.w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

        # Get transaction hash from deployed contract
        tx_hash = contract.deploy(transaction={'from': self.w3.eth.accounts[0]})

        # Get tx receipt to get contract address
        tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
        contract_address = tx_receipt['contractAddress']

        # Contract instance in concise mode
        abi = contract_interface['abi']
        contract_instance = self.w3.eth.contract(address=contract_address, abi=abi,ContractFactoryClass=ConciseContract)

        return contract, contract_address, contract_instance


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

        _, asc_address, asc_instance = self._deploy_contract(asc_interface)

        # should not fail
        self.mycro_instance.execute_asc(asc_address);
