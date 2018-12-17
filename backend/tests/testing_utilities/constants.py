from eth_tester import EthereumTester
from web3 import Account, Web3
from web3.providers.eth_tester import EthereumTesterProvider

import backend.constants as app_constants
from backend.server.utils.contract_compiler import ContractCompiler

COMPILER = ContractCompiler()


def create_w3():
    tester = EthereumTester()
    tester.add_account(app_constants.DEFAULT_ETHEREUM_PRIVATE_KEY)
    w3 = Web3(EthereumTesterProvider(ethereum_tester=tester))

    tester.send_transaction({'from': w3.eth.accounts[0],
                             'to'  : app_constants.DEFAULT_ETHEREUM_ADDRESS,
                             'gas' : 21000, 'value': int(10e18)})

    return w3


W3_ACCOUNTS = create_w3().eth.accounts

# hardcoded Ethereum addresses
PROJECT_ADDRESS = '0x1111111111111111111111111111111111111111'
REWARDEE = '0x1111111111111111111111111111111111111112'
MYCRO_ADDRESS = '0x1111111111111111111111111111111111111113'
INITIAL_ADDRESS = '0x1111111111111111111111111111111111111114'
ASC_ADDRESS = '0x1111111111111111111111111111111111111115'

MYCRO_PROJECT_NAME = 'mycro'
MYCRO_PROJECT_SYMBOL = 'myc'
PROJECT_NAME = 'foobar'
PROJECT_SYMBOL = PROJECT_NAME[:3]
GITHUB_ACCESS_TOKEN = 'fake'
GITHUB_ORGANIZATION = 'lolwut'
REWARD = 15
PR_ID = 11
SYMBOL = 'lol'
NAME = 'lolcoin'
DECIMALS = 18
CREATORS_BALANCES = {W3_ACCOUNTS[7]: 33, W3_ACCOUNTS[8]: 33, W3_ACCOUNTS[9]: 34}
INITIAL_BALANCES = list(CREATORS_BALANCES.values())
INITIAL_ADDRESSES = list(CREATORS_BALANCES.keys())
TOTAL_SUPPLY = sum(INITIAL_BALANCES)
WALLET = Account.privateKeyToAccount(
    'f49e1216edac9a5b0fab36f28037bfe8d5eb104b13f049b59decfac446e56ab4')  # default private key with a different final character (4 instead of 3)
TRANSACTION = {'gas': 10, 'nonce': 1, 'gasLimit': 10, 'data': '0x123abc'}
