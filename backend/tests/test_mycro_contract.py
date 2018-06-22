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
        self.contract_interface = self.compiler.get_contract_interface("mycro.sol", "MycroCoin")

        # web3.py instance
        self.w3 = Web3(EthereumTesterProvider())

        # Instantiate and deploy contract
        contract = self.w3.eth.contract(abi=self.contract_interface['abi'], bytecode=self.contract_interface['bin'])

        # Get transaction hash from deployed contract
        tx_hash = contract.deploy(transaction={'from': self.w3.eth.accounts[0]})

        # Get tx receipt to get contract address
        tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
        contract_address = tx_receipt['contractAddress']

        # Contract instance in concise mode
        abi = self.contract_interface['abi']
        contract_instance = self.w3.eth.contract(address=contract_address, abi=abi,ContractFactoryClass=ConciseContract)

        # Getters + Setters for web3.eth.contract object
        print('Contract value: {}'.format(contract_instance.totalSupply()))

    def test_lol(self):
        pass
