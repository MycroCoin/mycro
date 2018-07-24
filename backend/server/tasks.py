from celery import shared_task
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.deploy import get_event_filter_w3
from web3 import Web3
from backend.server.models import Project
import logging
from web3.contract import ConciseContract
import backend.server.utils.github as github


def build_merge_event_filter(project: Project, compiler: ContractCompiler, w3: Web3):
    base_dao_interface = compiler.get_contract_interface('base_dao.sol', 'BaseDao')
    base_dao_contract = w3.eth.contract(abi=base_dao_interface['abi'], address=project.dao_address)

    merge_address = base_dao_contract.functions.getModuleByCode(1).call()

    merge_module_interface = compiler.get_contract_interface('merge_module.sol', 'MergeModule')
    merge_module_contract = w3.eth.contract(abi=merge_module_interface['abi'], address=merge_address)

    merge_listener = merge_module_contract.events.Merge.createFilter(fromBlock=0)

    return merge_listener


@shared_task
def process_merges():
    projects = Project.objects.filter()
    compiler = ContractCompiler()
    w3 = get_event_filter_w3()

    for project in projects:
        if project.is_mycro_dao:
            continue

        merge_filter = build_merge_event_filter(project, compiler, w3)

        events = merge_filter.get_all_entries()
        for event in events:
            pr_id = int(event['args']['pr_id'])
            logging.info(f"DAO {project.dao_address} with name {project.repo_name} wants to merge {pr_id}")

            # TODO get rid of this try catch
            # We can do this when we use get_new_entries but need this for now because we reattempt to merge PRs even
            # after they've been merged which results in an exception
            try:
                github.merge_pr(project.repo_name, pr_id)
            except Exception as e:
                logging.warning(f'PR {pr_id} for project {project.repo_name} could not be merged, probably because it already has been')
                logging.warning(e)


@shared_task
def process_registrations():
    mycro_project = Project.get_mycro_dao()
    if mycro_project is None:
        return

    # TODO figure out how to cache the compiler, w3, interface, contract and listener
    compiler = ContractCompiler()
    w3 = get_event_filter_w3()

    contract_interface = compiler.get_contract_interface('mycro.sol', 'MycroCoin')
    mycro_contract = w3.eth.contract(abi=contract_interface['abi'], address=mycro_project.dao_address)

    project_registration_listener = mycro_contract.events.RegisterProject.createFilter(fromBlock=0)

    # TODO use get_new_entries instead
    events = project_registration_listener.get_all_entries()

    projects = set([project[0] for project in Project.objects.values_list('dao_address')])

    for event in events:
        registered_project_address = event['args']['projectAddress']

        if registered_project_address not in projects:
            base_dao_interface = compiler.get_contract_interface('base_dao.sol', 'BaseDao')
            base_dao_contract = w3.eth.contract(abi=base_dao_interface['abi'], address=registered_project_address,
                                                ContractFactoryClass=ConciseContract)

            repo_name = base_dao_contract.name()
            github.create_repo(repo_name)

            Project.objects.create(repo_name=repo_name, dao_address=registered_project_address)


@shared_task
def print_stuff():
    # NB: this isn't used for anything meaningful but is helpful to keep around for playing around with celery
    # we should get rid of this once we're comfortable with how celery works
    print("1")
