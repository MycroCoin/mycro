from web3 import Web3, Account
from web3.providers import HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.contract import ConciseContract

import logging
import os

logger = logging.getLogger(__name__)

def deploy(contract_interface, *args, private_key=None, timeout=120):
    w3 = get_w3()
    contract, address, instance = _deploy_contract(w3, contract_interface, *args, private_key=private_key, timeout=timeout)

    return w3, contract, address, instance

def get_w3():
    deployment_environment = os.environ['DEPLOY_ENV']
    if deployment_environment == 'ganache':
        return _get_ganache_w3()
    elif deployment_environment == 'kaleido':
        return _get_kaleido_w3()
    elif deployment_environment == 'ropsten':
        return _get_ropsten_w3()
    else:
        raise EnvironmentError(f'{deployment_environment} is an invalid value for DEPLOY_ENV')

def get_infura_api_key():
    return os.environ.get('INFURA_API_KEY', None)

def _get_ropsten_w3():
    api_key = get_infura_api_key()
    return Web3(HTTPProvider(f'https://ropsten.infura.io/v3/{api_key}'))

def get_parity_endpoint():
    return os.environ.get('PARITY_ENDPOINT', 'http://localhost:8545')

def _get_parity_w3():
    parity_endpoint = get_parity_endpoint()
    return Web3(HTTPProvider(parity_endpoint))

def get_event_filter_w3():
    deployment_environment = os.environ['DEPLOY_ENV']
    if deployment_environment == 'ropsten':
        return _get_parity_w3()
    else:
        return get_w3()


def _deploy_contract(w3, contract_interface, *args, private_key=None, timeout=120):
    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Get transaction hash from deployed contract
    contract_constructor = contract.constructor(*args)
    if private_key is None:
        tx_hash = contract.constructor(*args).transact(transaction={'from': w3.eth.accounts[0]})
    else:
        acc = Account.privateKeyToAccount(private_key)
        nonce = w3.eth.getTransactionCount(acc.address)
        latest_block = w3.eth.getBlock('latest')
        txn = contract_constructor.buildTransaction({'nonce': nonce, 'gas': latest_block.gasLimit, 'gasPrice': 21000000000})
        signed = w3.eth.account.signTransaction(txn, private_key)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

    # Get tx receipt to get contract address
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout)
    contract_address = tx_receipt['contractAddress']

    # Contract instance in concise mode
    abi = contract_interface['abi']
    contract_instance = w3.eth.contract(address=contract_address, abi=abi,
                                        ContractFactoryClass=ConciseContract)

    return contract, contract_address, contract_instance


def _get_kaleido_username_password():
    user = os.environ.get("KALEIDO_USER", "u0g9fge43j")
    password = os.environ.get("KALEIDO_PASSWORD")

    return user, password


def _get_kaleido_endpoint():
    user, password = _get_kaleido_username_password()

    return os.environ.get("KALEIDO_ENDPOINT",
                          f"https://{user}:{password}@u0a9n6r4oc-u0qutwl2df-rpc.us-east-2.kaleido.io")


def _get_ganache_endpoint():
    return os.environ.get("GANACHE_ENDPOINT", "http://127.0.0.1:7545")


def _get_ganache_w3():
    ganache_endpoint = _get_ganache_endpoint()
    logger.info(f"Connecting to {ganache_endpoint}")
    w3 = Web3(HTTPProvider(ganache_endpoint))

    return w3


def _get_kaleido_w3():
    kaleido_endpoint = _get_kaleido_endpoint()
    w3 = Web3(HTTPProvider(kaleido_endpoint))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)

    return w3

def get_private_key():
    return os.environ['ETHEREUM_PRIVATE_KEY']

