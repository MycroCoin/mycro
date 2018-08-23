import backend.tests.testing_utilities.constants as constants
from backend.server.utils.deploy import _deploy_contract


def deploy_base_dao(w3=constants.W3,
                    symbol=constants.SYMBOL,
                    name=constants.NAME,
                    decimals=constants.DECIMALS,
                    totalSupply=constants.TOTAL_SUPPLY,
                    initalAddresses=constants.INITIAL_ADDRESSES,
                    initialBalances=constants.INITIAL_BALANCES):
    base_dao_interface = constants.COMPILER.get_contract_interface(
        "base_dao.sol", "BaseDao")
    return _deploy_contract(w3, base_dao_interface,
                            symbol,
                            name,
                            decimals,
                            totalSupply,
                            initalAddresses,
                            initialBalances)


def create_and_register_merge_module(base_dao_instance, w3=constants.W3):
    merge_module_interface = constants.COMPILER.get_contract_interface(
        "merge_module.sol", "MergeModule")
    merge_contract, merge_address, merge_instance = _deploy_contract(w3,
                                                                     merge_module_interface)
    base_dao_instance.registerModule(merge_address,
                                     transact={'from': w3.eth.accounts[0]})

    return merge_contract, merge_address, merge_instance


def create_and_propose_merge_asc(base_dao_instance, w3=constants.W3,
                                 rewardee=constants.REWARDEE,
                                 reward=constants.REWARD,
                                 pr_id=constants.PR_ID):
    asc_contract, asc_address, asc_instance = create_merge_asc(w3, rewardee,
                                                               reward, pr_id)

    base_dao_instance.propose(asc_address,
                              transact={'from': w3.eth.accounts[0]})

    return asc_contract, asc_address, asc_instance


def create_merge_asc(w3=constants.W3,
                     rewardee=constants.REWARDEE,
                     reward=constants.REWARD,
                     pr_id=constants.PR_ID):
    merge_asc_interface = constants.COMPILER.get_contract_interface(
        "merge_asc.sol", "MergeASC")

    return _deploy_contract(w3, merge_asc_interface,
                            rewardee, reward, pr_id)
