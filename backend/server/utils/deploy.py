from web3 import Web3
from web3.providers import HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.contract import ConciseContract

import logging
import os


def deploy(contract_interface, *args):
    w3 = get_w3()
    contract, address, instance = _deploy_contract(w3, contract_interface, *args)

    return w3, contract, address, instance

def get_w3():
    deployment_environment = os.environ['DEPLOY_ENV']
    if deployment_environment == 'ganache':
        return _get_ganache_w3()
    elif deployment_environment == 'kaleido':
        return _get_kaleido_w3()
    else:
        raise EnvironmentError(f'{deployment_environment} is an invalid value for DEPLOY_ENV')


def _deploy_contract(w3, contract_interface, *args):
    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Get transaction hash from deployed contract
    tx_hash = contract.constructor(*args).transact(transaction={'from': w3.eth.accounts[0]})

    # Get tx receipt to get contract address
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']

    # Contract instance in concise mode
    abi = contract_interface['abi']
    contract_instance = w3.eth.contract(address=contract_address, abi=abi,
                                        ContractFactoryClass=ConciseContract)

    return contract, contract_address, contract_instance


def _get_kaleido_username_password():
    user = os.environ.get("KALEIDO_USER", "u0g9fge43j")
    password = os.environ["KALEIDO_PASSWORD"]

    return user, password


def _get_kaleido_endpoint():
    user, password = _get_kaleido_username_password()

    return os.environ.get("KALEIDO_ENDPOINT",
                          f"https://{user}:{password}@u0a9n6r4oc-u0qutwl2df-rpc.us-east-2.kaleido.io")


def _get_ganache_endpoint():
    return os.environ.get("GANACHE_ENDPOINT", "http://127.0.0.1:7545")


def _get_ganache_w3():
    ganache_endpoint = _get_ganache_endpoint()
    logging.info(f"Connecting to {ganache_endpoint}")
    w3 = Web3(HTTPProvider(ganache_endpoint))

    return w3


def _get_kaleido_w3():
    kaleido_endpoint = _get_kaleido_endpoint()
    w3 = Web3(HTTPProvider(kaleido_endpoint))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)

    return w3


