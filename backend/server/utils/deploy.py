from web3 import Web3, Account
from backend.server.utils.contract_compiler import ContractCompiler
from web3.providers import HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.contract import ConciseContract

import logging
import os
import backend.settings as settings
import asyncio
from contextlib import contextmanager

logger = logging.getLogger(__name__)


async def deploy_async(contract_interface, *args, private_key=None, timeout=120):
    w3 = get_w3()
    contract, address, instance = _deploy_contract(w3, contract_interface, *args, private_key=private_key,
                                                   timeout=timeout)

    return w3, contract, address, instance


def deploy(contract_interface, *args, private_key=None, timeout=120):
    with get_or_create_event_loop() as loop:
        return loop.run_until_complete(
            deploy_async(contract_interface, *args, private_key=private_key, timeout=timeout))


async def call_contract_function_async(contract_func, *args, private_key=None, timeout=120):
    w3 = get_w3()
    return _call_contract_func(w3, contract_func, *args, private_key=private_key, timeout=timeout)


def call_contract_function(contract_func, *args, private_key=None, timeout=120):
    with get_or_create_event_loop() as loop:
        return loop.run_until_complete(
            call_contract_function_async(contract_func, *args, private_key=private_key, timeout=timeout))


def _call_contract_func(w3: Web3, contract_func, *args, private_key=None, timeout=600):
    """
    Call a function on a contract
    :param w3: a w3 instance to use
    :param contract_func: a reference to a function on a web3.datatypes.Contract object
    :param args: arguments to pass the function
    :param private_key: the private key to use for mutating calls
    :param timeout: how long to wait for a transaction to be mined
    :return: a transaction receipt when mutating or the results of the function call when not mutating
    """

    # TODO: this has been unittested but it not integration tested, it would be good to set that up
    if private_key is not None:
        transaction_dict = _build_transaction_dict(w3, private_key)

        txn = contract_func(*args).buildTransaction(transaction_dict)
        signed = w3.eth.account.signTransaction(txn, private_key)

        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout)

        return tx_receipt
    else:
        return contract_func(*args).call()


def get_w3():
    deploy_env = settings.deploy_env()
    logging.debug(f'Deploy env is {deploy_env}')

    if deploy_env == 'parity':
        return _get_parity_w3()
    elif deploy_env == 'ropsten':
        return _get_ropsten_w3()
    else:
        raise EnvironmentError(f'{deploy_env} is an invalid value for DEPLOY_ENV')


def _get_ropsten_w3():
    logging.debug('Getting ropsten w3 through infura')
    return Web3(HTTPProvider(f'https://ropsten.infura.io/v3/{settings.get_infura_api_key()}'))


def _get_parity_w3():
    logging.debug('Getting parity w3')
    return Web3(HTTPProvider(settings.parity_endpoint()))


def _build_transaction_dict(w3, private_key, gas=None, gasPrice=5000000000):
    acc = Account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(acc.address)
    latest_block = w3.eth.getBlock('latest')
    if not gas:
        gas = latest_block.gasLimit

        # the gasLimit must be at least one adjustment unit less than the latest
        # block gasLimit
        adjustment = int(latest_block.gasLimit / 1024)
        gas -= adjustment
        gas -= 1 # just for good measure in case there's an off by 1 with the adjustment

    # TODO make gas price based on the latest_block. Right now we can't do that because when using a private chain
    # during dev the latest_block the first time round is the genesis block and using it's gas limit messes things up
    # there's probably some way to detect if latest_block is genesis and putting some logic around that
    return {'nonce': nonce, 'gas': gas, 'gasPrice': gasPrice}


def _deploy_contract(w3, contract_interface, *args, private_key=None, timeout=600):
    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Get transaction hash from deployed contract
    contract_constructor = contract.constructor(*args)
    if private_key is None:
        tx_hash = contract.constructor(*args).transact(transaction={'from': w3.eth.accounts[0]})
    else:
        transaction_dict = _build_transaction_dict(w3, private_key)
        txn = contract_constructor.buildTransaction(transaction_dict)
        signed = w3.eth.account.signTransaction(txn, private_key)

        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

    # Get tx receipt to get contract address
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout)
    contract_address = tx_receipt['contractAddress']

    # Contract instance in concise mode
    abi = contract_interface['abi']
    contract_instance = w3.eth.contract(address=contract_address, abi=abi,
                                        ContractFactoryClass=ConciseContract)

    # need to recreate the contract now that we've successfully deployed and have a contract address
    contract = w3.eth.contract(address=contract_address, abi=contract_interface['abi'])

    return contract, contract_address, contract_instance


@contextmanager
def get_or_create_event_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError as e:
        loop = asyncio.new_event_loop()

    try:
        yield loop
    finally:
        loop.close()

def _get_contract(address, filename, contract_name):
    compiler = ContractCompiler()
    w3 = get_w3()

    interface = compiler.get_contract_interface(filename, contract_name)
    contract = w3.eth.contract(abi=interface['abi'], address=address)

    return contract

def get_dao_contract(dao_address):
    return _get_contract(dao_address, 'base_dao.sol', 'BaseDao')

def get_asc_contract(asc_address):
    return _get_contract(asc_address, 'base_asc.sol', 'BaseASC')
