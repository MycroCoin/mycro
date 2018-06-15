import json
import web3

from web3 import Web3, HTTPProvider
from web3.providers.eth_tester import EthereumTesterProvider
from solc import compile_source
from web3.contract import ConciseContract
import os

def read_contract_file():
    backend_root = os.path.dirname(os.path.dirname(__file__))
    contracts_root = os.path.join(backend_root, 'contracts')
    with open(os.path.join(contracts_root, 'mycro.sol')) as f:
        source = f.read()

    return source

# Solidity source code
contract_source_code = read_contract_file()

compiled_sol = compile_source(contract_source_code) # Compiled source code
contract_interface = compiled_sol['<stdin>:MycroCoin']

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
