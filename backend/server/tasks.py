# Create your tasks here
from github import Github
from celery import shared_task
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.deploy import get_w3
from web3 import Web3
from web3.providers import HTTPProvider
from backend.server.models import Project
import logging
from web3.contract import ConciseContract
import os


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
    w3 = get_w3()

    for project in projects:
        print(f"processing merges for project {project.repo_name}")
        if project.is_mycro_dao:
            print(f"{project.repo_name} is the mycro doa")
            continue

        print(f"building merge filters for {project.repo_name}")
        merge_filter = build_merge_event_filter(project, compiler, w3)

        events = merge_filter.get_all_entries()
        for event in events:
            print(f"########## merge event: {event}")
            pr_id = int(event['args']['pr_id'])
            logging.info(f"DAO {project.dao_address} with name {project.repo_name} wants to merge {pr_id}")

            # TODO revoke this
            token = os.environ['GITHUB_TOKEN']
            github = Github(token)

            org = github.get_organization('mycrocoin')
            repo = org.get_repo(project.repo_name)
            pr = repo.get_pull(pr_id)
            try:
                pr.merge()
            except:
                pass


@shared_task
def process_registrations():
    mycro_project = Project.get_mycro_dao()
    if mycro_project is None:
        return

    # TODO figure out how to cache the compiler, w3, interface, contract and listener
    compiler = ContractCompiler()
    w3 = get_w3()

    contract_interface = compiler.get_contract_interface('mycro.sol', 'MycroCoin')
    mycro_contract = w3.eth.contract(abi=contract_interface['abi'], address=mycro_project.dao_address)
    print(mycro_contract.functions.getProjects().call())

    project_registration_listener = mycro_contract.events.RegisterProject.createFilter(fromBlock=0)

    # TODO use get_new_entries instead
    events = project_registration_listener.get_all_entries()

    projects = set([project[0] for project in Project.objects.values_list('dao_address')])

    for event in events:
        print(f"event {event}")
        registered_project_address = event['args']['projectAddress']

        if registered_project_address not in projects:
            print("not previously found")
            base_dao_interface = compiler.get_contract_interface('base_dao.sol', 'BaseDao')
            base_dao_contract = w3.eth.contract(abi=base_dao_interface['abi'], address=registered_project_address,
                                                ContractFactoryClass=ConciseContract)
            repo_name = base_dao_contract.name()

            # TODO revoke this token once we've got some funding
            token = "da1f1b18405f9d8af8d878516f2b7883bbfd8451"
            github = Github(token)

            org = github.get_organization('mycrocoin')
            org.create_repo(name=repo_name, auto_init=True)
            Project.objects.create(repo_name=repo_name, dao_address=registered_project_address)


@shared_task
def print_stuff():
    # NB: this isn't used for anything meaningful but is helpful to keep around for playing around with celery
    # we should get rid of this once we're comfortable with how celery works
    print("1")
