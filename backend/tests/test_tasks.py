from unittest.mock import ANY, MagicMock, patch

import backend.server.tasks as tasks
import backend.tests.testing_utilities.constants as constants
import backend.tests.testing_utilities.utils as utils
from backend.server.models import (
    ASC, BlockchainState, ObjectDoesNotExist, Project, Transaction,
)
from backend.tests.mycro_django_test import MycroDjangoTest


class TestTasks(MycroDjangoTest):
    # TODO test process merges tasks

    def setUp(self):
        super().setUp()

    @patch('backend.server.tasks.StrictRedis.lock')
    @patch('backend.server.utils.deploy.Transaction')
    @patch('backend.server.utils.deploy.get_w3')
    @patch('backend.server.utils.github.create_repo')
    @patch('backend.settings.github_organization')
    def test_create_project_happy_case(self,
                                       github_organization_mock: MagicMock,
                                       create_repo_mock: MagicMock,
                                       get_w3_mock: MagicMock,
                                       transaction_mock: MagicMock,
                                       redis_lock_mock: MagicMock):
        Project.create_mycro_dao(constants.MYCRO_ADDRESS,
                                 constants.MYCRO_PROJECT_SYMBOL,
                                 constants.DECIMALS)
        project = Project.objects.create(symbol=constants.PROJECT_SYMBOL,
                                         repo_name=constants.PROJECT_NAME,
                                         decimals=constants.DECIMALS,
                                         initial_balances=constants.CREATORS_BALANCES)

        # TODO make this more of an integration test by using constants.W3 like the create_asc tests
        w3 = get_w3_mock.return_value
        w3.eth.waitForTransactionReceipt.return_value = {
            'contractAddress'  : constants.PROJECT_ADDRESS,
            'cumulativeGasUsed': 2,
            'gasUsed'          : 1,
            'blockNumber'      : 3,
            'status'           : 4}
        w3.eth.getBalance.return_value = int(10e18)

        tasks.create_project(project.pk)

        # two transactions, one for deploying and once for registering
        transaction_mock.objects.create.assert_any_call(
            wallet=self.wallet,
            hash=get_w3_mock.return_value.eth.sendRawTransaction.return_value.hex.return_value,
            value=ANY,
            chain_id=ANY,
            nonce=ANY,
            gas_limit=ANY,
            gas_price=ANY,
            data=ANY,
            to=ANY,
            contract_address=constants.PROJECT_ADDRESS,
            cumulative_gas_used=2,
            gas_used=1,
            block_number=3,
            status=4
        )

        # called twice for deployment and twice for registrations
        self.assertEqual(4,
                         get_w3_mock.return_value.eth.waitForTransactionReceipt.call_count)
        self.assertEqual(4, w3.eth.sendRawTransaction.call_count)

        create_repo_mock.assert_called_once_with(
            repo_name=constants.PROJECT_NAME,
            organization=github_organization_mock.return_value)

        project.refresh_from_db()
        self.assertEqual(constants.PROJECT_ADDRESS, project.dao_address)
        self.assertEqual(BlockchainState.COMPLETED, project.blockchain_state)
        self.assertNotEqual('', project.merge_module_address)

        redis_lock_mock.assert_called_once_with(tasks.REDIS_CREATE_CONTRACT_LOCK)

    @patch('backend.server.tasks.StrictRedis.lock')
    @patch('backend.server.utils.deploy.Transaction')
    @patch('backend.server.utils.deploy.get_w3')
    @patch('backend.server.utils.github.create_repo')
    @patch('backend.settings.github_organization')
    def test_create_project_project_does_not_exist(self,
                                                   github_organization_mock: MagicMock,
                                                   create_repo_mock: MagicMock,
                                                   get_w3_mock: MagicMock,
                                                   transaction_mock: MagicMock,
                                                   redis_lock_mock: MagicMock):
        # TODO make this more of an integration test by using constants.W3 like the create_asc tests
        with self.assertRaisesRegex(ObjectDoesNotExist, 'Project matching'):
            tasks.create_project(Project.objects.count() + 1)

        github_organization_mock.assert_not_called()
        create_repo_mock.assert_not_called()
        get_w3_mock.assert_not_called()
        transaction_mock.assert_not_called()
        redis_lock_mock.assert_called_once_with(tasks.REDIS_CREATE_CONTRACT_LOCK)

    @patch('backend.server.tasks.StrictRedis.lock')
    @patch('backend.server.utils.deploy.get_w3')
    def test_create_asc_happy_case(self,
                                   get_w3_mock: MagicMock,
                                   redis_lock_mock: MagicMock):
        get_w3_mock.return_value = constants.create_w3()
        _, project_address, _ = utils.deploy_base_dao(constants.create_w3())
        project = Project.objects.create(symbol=constants.PROJECT_SYMBOL,
                                         repo_name=constants.PROJECT_NAME,
                                         decimals=constants.DECIMALS,
                                         initial_balances=constants.CREATORS_BALANCES,
                                         dao_address=project_address)
        asc = ASC.objects.create(rewardee=constants.REWARDEE,
                                 reward=constants.REWARD,
                                 pr_id=constants.PR_ID,
                                 project=project,
                                 blockchain_state=BlockchainState.PENDING)

        tasks.create_asc(asc.id)

        asc.refresh_from_db()

        self.assertEqual(BlockchainState.COMPLETED, asc.blockchain_state)
        self.assertNotEqual('', asc.address)

        redis_lock_mock.assert_called_once_with(tasks.REDIS_CREATE_CONTRACT_LOCK)

        transactions = Transaction.objects.all()

        self.assertEqual(2, len(transactions))

    @patch('backend.server.tasks.StrictRedis.lock')
    @patch('backend.server.utils.deploy.get_w3')
    def test_create_asc_when_not_pending(self,
                                         get_w3_mock: MagicMock,
                                         redis_lock_mock: MagicMock):
        get_w3_mock.return_value = constants.create_w3()
        _, project_address, _ = utils.deploy_base_dao(constants.create_w3())
        project = Project.objects.create(symbol=constants.PROJECT_SYMBOL,
                                         repo_name=constants.PROJECT_NAME,
                                         decimals=constants.DECIMALS,
                                         initial_balances=constants.CREATORS_BALANCES,
                                         dao_address=project_address)
        asc = ASC.objects.create(rewardee=constants.REWARDEE,
                                 reward=constants.REWARD,
                                 pr_id=constants.PR_ID,
                                 project=project,
                                 blockchain_state=BlockchainState.STARTED)

        with self.assertRaisesRegex(AssertionError, 'pending'):
            tasks.create_asc(asc.id)

        asc.refresh_from_db()

        # state must not be modified
        self.assertEqual(BlockchainState.STARTED, asc.blockchain_state)
        self.assertEqual('', asc.address)

        redis_lock_mock.assert_called_once_with(tasks.REDIS_CREATE_CONTRACT_LOCK)

        transactions = Transaction.objects.all()

        self.assertEqual(0, len(transactions))

    @patch('backend.server.tasks.StrictRedis.lock')
    @patch('backend.server.utils.deploy.get_w3')
    def test_create_asc_that_has_address(self,
                                         get_w3_mock: MagicMock,
                                         redis_lock_mock: MagicMock):
        get_w3_mock.return_value = constants.create_w3()
        _, project_address, _ = utils.deploy_base_dao(constants.create_w3())
        project = Project.objects.create(symbol=constants.PROJECT_SYMBOL,
                                         repo_name=constants.PROJECT_NAME,
                                         decimals=constants.DECIMALS,
                                         initial_balances=constants.CREATORS_BALANCES,
                                         dao_address=project_address)
        asc = ASC.objects.create(rewardee=constants.REWARDEE,
                                 reward=constants.REWARD,
                                 pr_id=constants.PR_ID,
                                 project=project,
                                 blockchain_state=BlockchainState.PENDING,
                                 address=constants.ASC_ADDRESS)

        with self.assertRaisesRegex(AssertionError, 'address'):
            tasks.create_asc(asc.id)

        asc.refresh_from_db()

        # state must not be modified
        self.assertEqual(BlockchainState.PENDING, asc.blockchain_state)
        self.assertEqual(constants.ASC_ADDRESS, asc.address)

        redis_lock_mock.assert_called_once_with(tasks.REDIS_CREATE_CONTRACT_LOCK)

        transactions = Transaction.objects.all()

        self.assertEqual(0, len(transactions))
