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


class TransferError(Exception):
    pass


async def deploy_async(contract_interface, *args, private_key,
                       timeout=600):
    w3 = get_w3()
    contract, address, instance = _deploy_contract(w3, contract_interface,
                                                   *args,
                                                   private_key=private_key,
                                                   timeout=timeout)

    return w3, contract, address, instance


def deploy(contract_interface, *args, private_key, timeout=600):
    with get_or_create_event_loop() as loop:
        return loop.run_until_complete(
            deploy_async(contract_interface, *args, private_key=private_key,
                         timeout=timeout))


async def call_contract_function_async(contract_func, *args, private_key,
                                       timeout=600):
    w3 = get_w3()
    return _call_contract_func(w3, contract_func, *args,
                               private_key=private_key, timeout=timeout)


def call_contract_function(contract_func, *args, private_key, timeout=600):
    with get_or_create_event_loop() as loop:
        return loop.run_until_complete(
            call_contract_function_async(contract_func, *args,
                                         private_key=private_key,
                                         timeout=timeout))


def _call_contract_func(w3: Web3, contract_func, *args, private_key,
                        timeout=600):
    """
    Call a function on a contract
    :param w3: a w3 instance to use
    :param contract_func: a reference to a function on a web3.datatypes.Contract object
    :param args: arguments to pass the function
    :param private_key: the private key to use for mutating calls
    :param timeout: how long to wait for a transaction to be mined
    :return: a transaction receipt when mutating or the results of the function call when not mutating
    """
    if private_key is None:
        raise ValueError('Private key cannot be none')
    fund_account_if_needed(w3, settings.ethereum_private_key(), private_key)

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
    elif deploy_env == 'rinkeby':
        return _get_rinkeby_w3()
    else:
        raise EnvironmentError(
            f'{deploy_env} is an invalid value for DEPLOY_ENV')


def _get_ropsten_w3():
    logging.debug('Getting ropsten w3 through infura')
    return Web3(HTTPProvider(
        f'https://ropsten.infura.io/v3/{settings.get_infura_api_key()}'))


def _get_rinkeby_w3():
    logging.debug('Getting rinkeby w3 through infura')

    w3 = Web3(HTTPProvider(
        f'https://rinkeby.infura.io/v3/{settings.get_infura_api_key()}'))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    return w3


def _get_parity_w3():
    logging.debug('Getting parity w3')
    return Web3(HTTPProvider(settings.parity_endpoint()))


def _calculate_gas_limit(w3):
    """
    Sometimes this calculates an average value bigger than the current gasLimit
    picking a good gasLimit is really fucking hard.

    NOTE: this is untested and unused.

    TODO: clean/correct this unused tech debt
    :param w3:
    :return:
    """
    num_blocks = 0
    total_gas = 0
    block = w3.eth.getBlock('latest')
    while block and num_blocks < 50:
        total_gas += block.gasLimit
        num_blocks += 1
        block = w3.eth.getBlock(block.number - 1)

    avg_gas = int(total_gas / num_blocks)
    adjustment = int(avg_gas / 1024)
    adjusted = avg_gas - adjustment - 1
    return adjusted


def _build_transaction_dict(w3, private_key, gas=None, gas_price=None):
    acc = Account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(acc.address, 'pending')
    nonce = w3.eth.getTransactionCount(acc.address)
    latest_block = w3.eth.getBlock('latest')
    if not gas:
        gas = 7000000  # tech debt until we figure out how to always pick a good gas limit

    if not gas_price:
        gas_price = int(
            w3.eth.gasPrice * 1.1)  # add an additional 10% just to be safe

    return {'nonce': nonce, 'gas': gas, 'gasPrice': gas_price}


def _deploy_contract(w3, contract_interface, *args, private_key,
                     timeout=600):
    if private_key is None:
        raise ValueError('Private key cannot be none')

    fund_account_if_needed(w3, settings.ethereum_private_key(), private_key)

    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface['abi'],
                               bytecode=contract_interface['bin'])

    # Get transaction hash from deployed contract
    contract_constructor = contract.constructor(*args)
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
    contract = w3.eth.contract(address=contract_address,
                               abi=contract_interface['abi'])

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


def get_wallet_balance(w3: Web3, private_key: str) -> int:
    account = Account.privateKeyToAccount(private_key)
    return w3.eth.getBalance(account.address)


def transfer_between_accounts(w3: Web3,
                              source_private_key: str,
                              destination_private_key: str,
                              amount_in_wei: int) -> None:
    source_account = Account.privateKeyToAccount(source_private_key)
    destination_account = Account.privateKeyToAccount(destination_private_key)
    signed_txn = w3.eth.account.signTransaction(dict(
        nonce=w3.eth.getTransactionCount(source_account.address),
        gasPrice=int(w3.eth.gasPrice * 1.1),
        # increase by 10% just to be sure this will be included
        gas=3 * 21000,  # 3x normal transaction cost just to be safe
        to=destination_account.address,
        value=amount_in_wei
    ),
        source_private_key)

    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)


def fund_account_if_needed(w3: Web3,
                           source_private_key: str,
                           destination_private_key: str,
                           minimum_balance_in_destination: int = int(1e18)) -> None:
    source_balance: int = get_wallet_balance(w3, source_private_key)
    destination_balance: int = get_wallet_balance(w3, destination_private_key)
    topup_amount: int = minimum_balance_in_destination - destination_balance
    if destination_balance < minimum_balance_in_destination:
        if source_balance < minimum_balance_in_destination - destination_balance:
            raise TransferError(
                f'Source account does not have enough funds to balance the destination account. Source balance is {source_balance}. Destination balance is {destination_balance}')
        else:
            transfer_between_accounts(w3, source_private_key,
                                      destination_private_key, topup_amount)
