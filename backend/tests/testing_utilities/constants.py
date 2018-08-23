from backend.server.utils.contract_compiler import ContractCompiler
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider

COMPILER = ContractCompiler()
W3 = Web3(EthereumTesterProvider())
PROJECT_NAME = 'mycro'
DAO_ADDRESS = '123'
GITHUB_ACCESS_TOKEN = 'fake'
ASC_ADDRESS = '456'
REWARDEE = '0x1111111111111111111111111111111111111112'
REWARD = 15
PR_ID = 11
SYMBOL = 'lol'
NAME = 'lolcoin'
DECIMALS = 18
TOTAL_SUPPLY = 100
INITIAL_ADDRESS = '0x1111111111111111111111111111111111111111'
INITIAL_ADDRESSES = [W3.eth.accounts[7], W3.eth.accounts[8], W3.eth.accounts[9]]
INITIAL_BALANCES = [33, 33, 34]
