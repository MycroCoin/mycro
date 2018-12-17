import unittest

from eth_tester.exceptions import TransactionFailed

from backend.tests.testing_utilities.utils import *


class TestMergeAsc(unittest.TestCase):

    def setUp(self):
        self.w3 = constants.create_w3()

    def test_get_rewardee(self):
        _, _, merge_asc_instance = create_merge_asc(self.w3)
        self.assertEqual(constants.REWARDEE, merge_asc_instance.rewardee())

    def test_get_reward(self):
        _, _, merge_asc_instance = create_merge_asc(self.w3)
        self.assertEqual(constants.REWARD, merge_asc_instance.reward())

    def test_upgrade_from_executed_asc_fails(self):
        __, __, dao_instance = deploy_base_dao(self.w3)
        create_and_register_merge_module(self.w3, dao_instance)
        __, asc_address, asc_instance = create_and_propose_merge_asc(self.w3,
                                                                     dao_instance)

        dao_instance.vote(asc_address,
                          transact={'from': constants.INITIAL_ADDRESSES[0]})
        dao_instance.vote(asc_address,
                          transact={'from': constants.INITIAL_ADDRESSES[1]})

        self.assertTrue(asc_instance.hasExecuted())

        __, __, new_asc_instance = create_merge_asc(self.w3)

        with self.assertRaises(TransactionFailed):
            new_asc_instance.upgradeFrom(asc_address, transact={
                'from': self.w3.eth.accounts[0]})

    def test_cannot_upgrade_already_executed_asc(self):
        __, __, dao_instance = deploy_base_dao(self.w3)
        create_and_register_merge_module(self.w3, dao_instance)
        __, asc_address, asc_instance = create_and_propose_merge_asc(self.w3,
                                                                     dao_instance)

        dao_instance.vote(asc_address,
                          transact={'from': constants.INITIAL_ADDRESSES[0]})
        dao_instance.vote(asc_address,
                          transact={'from': constants.INITIAL_ADDRESSES[1]})

        self.assertTrue(asc_instance.hasExecuted())

        __, new_asc_address, __ = create_merge_asc(self.w3)

        with self.assertRaises(TransactionFailed):
            asc_instance.upgradeFrom(new_asc_address, transact={
                'from': self.w3.eth.accounts[0]})

    def test_upgrade_merge_asc_happy_case(self):
        rewardee = '0x1111111111111111111111111111111111111114'
        reward = 21
        pr_id = 13

        __, __, dao_instance = deploy_base_dao(self.w3)
        create_and_register_merge_module(self.w3, dao_instance)
        __, asc_address, asc_instance = create_and_propose_merge_asc(self.w3,
                                                                     dao_instance,
                                                                     rewardee=rewardee,
                                                                     reward=reward,
                                                                     pr_id=pr_id)

        __, __, new_asc_instance = create_merge_asc(self.w3)

        self.assertNotEqual(new_asc_instance.rewardee(),
                            asc_instance.rewardee())
        self.assertNotEqual(new_asc_instance.reward(), asc_instance.reward())
        self.assertNotEqual(new_asc_instance.prId(), asc_instance.prId())

        new_asc_instance.upgradeFrom(asc_address, transact={
            'from': self.w3.eth.accounts[0]})

        self.assertEqual(rewardee, new_asc_instance.rewardee())
        self.assertEqual(reward, new_asc_instance.reward())
        self.assertEqual(pr_id, new_asc_instance.prId())
