from celery import shared_task
from backend.server.utils.contract_compiler import ContractCompiler
import backend.server.utils.deploy as deploy
from web3 import Web3
from backend.server.models import Project
import logging
from web3.contract import ConciseContract
import backend.server.utils.github as github
import backend.settings as settings


def get_merge_module_instance(project: Project, compiler: ContractCompiler, w3: Web3):
    base_dao_interface = compiler.get_contract_interface('base_dao.sol', 'BaseDao')
    base_dao_contract = w3.eth.contract(abi=base_dao_interface['abi'], address=project.dao_address)

    merge_address = base_dao_contract.functions.getModuleByCode(1).call()

    merge_module_interface = compiler.get_contract_interface('merge_module.sol', 'MergeModule')
    merge_module_contract = w3.eth.contract(abi=merge_module_interface['abi'], address=merge_address)

    return merge_module_contract


@shared_task
def process_merges():
    projects = Project.objects.filter()
    compiler = ContractCompiler()
    w3 = deploy.get_w3()

    for project in projects:
        if project.is_mycro_dao:
            continue
        logging.info(f"Looking for PRs for project {project.dao_address}")

        merge_contract = get_merge_module_instance(project, compiler, w3)

        logging.info(f"Found PRs: {merge_contract.functions.pullRequestsToMerge().call()}")
        for pr_id in merge_contract.functions.pullRequestsToMerge().call():
            logging.info(f"DAO {project.dao_address} with name {project.repo_name} wants to merge {pr_id}")

            # TODO get rid of this try catch
            # We can do this when we use get_new_entries but need this for now because we reattempt to merge PRs even
            # after they've been merged which results in an exception
            try:
                github.merge_pr(project.repo_name, pr_id, organization=settings.github_organization())
            except Exception as e:
                logging.warning(
                    f'PR {pr_id} for project {project.repo_name} could not be merged, probably because it already has been')
                logging.warning(e)


