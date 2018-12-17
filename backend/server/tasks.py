from celery import shared_task
from celery.utils.log import get_task_logger
from redis import StrictRedis
from web3 import Web3

import backend.server.utils.deploy as deploy
import backend.server.utils.github as github
import backend.settings as settings
from backend.server.models import Project, Wallet, BlockchainState, ASC
from backend.server.utils.contract_compiler import ContractCompiler

REDIS_CLIENT = StrictRedis.from_url(settings.CELERY_BROKER_URL)
REDIS_CREATE_CONTRACT_LOCK = 'create-contract-lock'
logger = get_task_logger(__name__)


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
        if project.blockchain_state != BlockchainState.COMPLETED:
            continue
        logger.info(f"Looking for PRs for project {project.dao_address}")

        merge_contract = get_merge_module_instance(project, compiler, w3)

        logger.info(f"Found PRs: {merge_contract.functions.pullRequestsToMerge().call()}")
        for pr_id in merge_contract.functions.pullRequestsToMerge().call():
            logger.info(f"DAO {project.dao_address} with name {project.repo_name} wants to merge {pr_id}")

            # TODO get rid of this try catch
            # We can do this when we use get_new_entries but need this for now because we reattempt to merge PRs even
            # after they've been merged which results in an exception
            try:
                github.merge_pr(project.repo_name, pr_id, organization=settings.github_organization())
            except Exception as e:
                logger.warning(
                    f'PR {pr_id} for project {project.repo_name} could not be merged, probably because it already has been')
                logger.warning(e)

@shared_task(bind=True)
def create_project(self, project_id: int) -> None:
    # TODO add mechanism to retry if anything in here fails
    # TODO there's lots of opportunity for failure in this function, we should be
    # more resilient

    logger.info(f'Attempting to get lock to create project {project_id}')

    # TODO extend to support locking based on wallets
    with REDIS_CLIENT.lock(REDIS_CREATE_CONTRACT_LOCK):
        logger.info(f'Acquired lock to create project {project_id}')
        project = Project.objects.get(pk=project_id)

        project.blockchain_state = BlockchainState.STARTED.value
        project.save()

        compiler = ContractCompiler()
        mycro_project = Project.get_mycro_dao()

        w3 = deploy.get_w3()

        contract_interface = compiler.get_contract_interface('mycro.sol',
                                                             'MycroCoin')
        mycro_contract = w3.eth.contract(abi=contract_interface['abi'],
                                         address=mycro_project.dao_address)

        base_dao_interface = compiler.get_contract_interface('base_dao.sol',
                                                             'BaseDao')
        merge_module_interface = compiler.get_contract_interface(
            'merge_module.sol', 'MergeModule')

        creators = []
        creator_balances = []
        logger.info(f'Project balances are {project.initial_balances}')
        for creator, balance in project.initial_balances.items():
            creators.append(creator)
            creator_balances.append(balance)

        total_supply = sum(creator_balances)

        # TODO add validation of project properties
        w3, dao_contract, dao_address, _ = deploy.deploy(base_dao_interface,
                                                         project.symbol,
                                                         project.repo_name,
                                                         project.decimals,
                                                         total_supply,
                                                         creators,
                                                         creator_balances,
                                                         private_key=Wallet.objects.first().private_key)

        _, _, merge_module_address, _ = deploy.deploy(merge_module_interface,
                                                      private_key=Wallet.objects.first().private_key)

        deploy.call_contract_function(
            dao_contract.functions.registerModule,
            merge_module_address,
            private_key=Wallet.objects.first().private_key)
        deploy.call_contract_function(
            mycro_contract.functions.registerProject,
            dao_address,
            private_key=Wallet.objects.first().private_key)


        project.blockchain_state = BlockchainState.COMPLETED.value
        project.dao_address = dao_address
        project.merge_module_address = merge_module_address
        project.save()

        github.create_repo(repo_name=project.repo_name,
                           organization=settings.github_organization())

    logger.info(f'Finished creating project {project_id}')

@shared_task(bind=True)
def create_asc(self, asc_id):

    logger.info(f'Attempting to get lock to create asc {asc_id}')

    with REDIS_CLIENT.lock(REDIS_CREATE_CONTRACT_LOCK):
        logger.info(f'Acquired lock to create asc {asc_id}')

        asc = ASC.objects.get(id=asc_id)

        assert asc.blockchain_state == BlockchainState.PENDING, "Blockchain state must be pending"
        assert not asc.address, "ASC must not already have an address"

        compiler = ContractCompiler()

        w3 = deploy.get_w3()
        base_dao_interface = compiler.get_contract_interface('base_dao.sol',
                                                             'BaseDao')
        dao_contract = w3.eth.contract(abi=base_dao_interface['abi'],
                                       address=asc.project.dao_address)

        asc_interface = compiler.get_contract_interface('merge_asc.sol',
                                                        'MergeASC')

        # we don't use the async method here because we can't parallelize
        # first the asc has to be deployed to get it's address then the address has to be registered
        # with the base dao
        _, _, asc_address, _ = deploy.deploy(asc_interface, asc.rewardee, asc.reward,
                                             asc.pr_id,
                                             private_key=Wallet.objects.first().private_key)

        deploy.call_contract_function(dao_contract.functions.propose,
                                      asc_address,
                                      private_key=Wallet.objects.first().private_key)

        asc.blockchain_state = BlockchainState.COMPLETED
        asc.address = asc_address
        asc.save()
