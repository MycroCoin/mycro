from web3.contract import ConciseContract

import backend.tests.testing_utilities.constants as constants


def deploy_contract(w3, contract_interface, *args):
    # Instantiate contract
    contract = w3.eth.contract(abi=contract_interface['abi'],
                               bytecode=contract_interface['bin'])
    tx_hash = contract.constructor(*args).transact(
        transaction={'from': w3.eth.accounts[0]})

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']

    # Contract instance in concise mode
    abi = contract_interface['abi']
    contract_instance = w3.eth.contract(address=contract_address, abi=abi,
                                        ContractFactoryClass=ConciseContract)

    # need to recreate the contract now that we've successfully deployed and have a contract address
    contract = w3.eth.contract(address=contract_address,
                               abi=contract_interface['abi'])

    return contract, contract_address, contract_instance


def deploy_base_dao(w3,
                    symbol=constants.SYMBOL,
                    name=constants.NAME,
                    decimals=constants.DECIMALS,
                    totalSupply=constants.TOTAL_SUPPLY,
                    initalAddresses=constants.INITIAL_ADDRESSES,
                    initialBalances=constants.INITIAL_BALANCES):
    base_dao_interface = constants.COMPILER.get_contract_interface(
        "base_dao.sol", "BaseDao")
    return deploy_contract(w3, base_dao_interface,
                           symbol,
                           name,
                           decimals,
                           totalSupply,
                           initalAddresses,
                           initialBalances)


def create_and_register_merge_module(w3, base_dao_instance):
    merge_module_interface = constants.COMPILER.get_contract_interface(
        "merge_module.sol", "MergeModule")
    merge_contract, merge_address, merge_instance = deploy_contract(w3,
                                                                    merge_module_interface)
    base_dao_instance.registerModule(merge_address,
                                     transact={'from': w3.eth.accounts[0]})

    return merge_contract, merge_address, merge_instance


def create_and_propose_merge_asc(w3, base_dao_instance,
                                 rewardee=constants.REWARDEE,
                                 reward=constants.REWARD,
                                 pr_id=constants.PR_ID):
    asc_contract, asc_address, asc_instance = create_merge_asc(w3, rewardee,
                                                               reward, pr_id)

    base_dao_instance.propose(asc_address,
                              transact={'from': w3.eth.accounts[0]})

    return asc_contract, asc_address, asc_instance


def create_merge_asc(w3,
                     rewardee=constants.REWARDEE,
                     reward=constants.REWARD,
                     pr_id=constants.PR_ID):
    merge_asc_interface = constants.COMPILER.get_contract_interface(
        "merge_asc.sol", "MergeASC")

    return deploy_contract(w3, merge_asc_interface,
                           rewardee, reward, pr_id)
