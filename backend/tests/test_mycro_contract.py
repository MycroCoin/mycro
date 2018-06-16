import json
import web3

from web3 import Web3, HTTPProvider
from web3.providers.eth_tester import EthereumTesterProvider
from solc import compile_source, compile_files
from web3.contract import ConciseContract
import os


class ContractCompiler:
    backend_root = os.path.dirname(os.path.dirname(__file__))
    contracts_root = os.path.join(backend_root, 'contracts')

    def __init__(self):
        self.contracts = None

    def compile_contracts(self):
        self.contracts = compile_files(self.get_contract_files())

    def get_contract_files(self):
        contracts = []

        for root, dirs, files in os.walk(self.contracts_root):
            for file in files:
                contracts.append(os.path.join(root, file))

        return contracts

    def get_contract_interface(self, contract_file_name, contract_name):
        if self.contracts is None:
            self.compile_contracts()

        contract_path = self.find_contract(contract_file_name)

        if contract_path is None:
            raise ValueError(f"contract {contract_file_name} doesn't exist")

        return self.contracts[f'{contract_path}:{contract_name}']

    def find_contract(self, contract_file_name):

        for root, dirs, files in os.walk(self.contracts_root):
            for file in files:
                if file == contract_file_name:
                    return os.path.join(root, contract_file_name)

        return None


compiler = ContractCompiler()
contract_interface = compiler.get_contract_interface("mycro.sol", "MycroCoin")

# web3.py instance
w3 = Web3(EthereumTesterProvider())

# Instantiate and deploy contract
contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

# Get transaction hash from deployed contract
tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0]})

# Get tx receipt to get contract address
tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']

# Contract instance in concise mode
abi = contract_interface['abi']
contract_instance = w3.eth.contract(address=contract_address, abi=abi,ContractFactoryClass=ConciseContract)

# Getters + Setters for web3.eth.contract object
print('Contract value: {}'.format(contract_instance.totalSupply()))
