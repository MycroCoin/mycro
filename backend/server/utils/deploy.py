from web3 import Web3, Account
from web3.providers import HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.contract import ConciseContract

import logging
import os
import backend.settings as settings

logger = logging.getLogger(__name__)

def deploy(contract_interface, *args, private_key=None, timeout=120):
    w3 = get_w3()
    contract, address, instance = _deploy_contract(w3, contract_interface, *args, private_key=private_key, timeout=timeout)

    return w3, contract, address, instance

def get_w3():
    deploy_env = settings.deploy_env()

    if deploy_env == 'parity':
        return _get_parity_w3()
    elif deploy_env == 'ropsten':
        return _get_ropsten_w3()
    else:
        raise EnvironmentError(f'{deploy_env} is an invalid value for DEPLOY_ENV')


def _get_ropsten_w3():
    return Web3(HTTPProvider(f'https://ropsten.infura.io/v3/{settings.get_infura_api_key()}'))

def _get_parity_w3():
    return Web3(HTTPProvider(settings.parity_endpoint()))

def get_event_filter_w3():
    if settings.deploy_env() == 'ropsten':
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
        # TODO make gas price based on the latest_block. Right now we can't do that because when using a private chain
        # during dev the latest_block the first time round is the genesis block and using it's gas limit messes things up
        # there's probably some way to detect if latest_block is genesis and putting some logic around that
        txn = contract_constructor.buildTransaction({'nonce': nonce, 'gas': 4000000, 'gasPrice': 21000000000})
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


