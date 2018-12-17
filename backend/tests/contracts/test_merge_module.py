import unittest

import backend.tests.testing_utilities.constants as constants
from backend.tests.testing_utilities.utils import deploy_contract


class TestMergeModule(unittest.TestCase):

    def setUp(self):
        self.w3 = constants.create_w3()
        self.merge_module_interface = constants.COMPILER.get_contract_interface(
            "merge_module.sol", "MergeModule")
        _, _, self.merge_module_instance = deploy_contract(self.w3,
                                                           self.merge_module_interface)

    def test_get_name(self):
        self.assertEqual(1, self.merge_module_instance.getCode())

    def test_merge_adds_to_list(self):
        self.merge_module_instance.merge(1, transact={
            'from': self.w3.eth.accounts[0]})

        self.assertEqual([1], self.merge_module_instance.pullRequestsToMerge())

    def test_merge_adds_same_pr_twice_if_asked(self):
        self.merge_module_instance.merge(1, transact={
            'from': self.w3.eth.accounts[0]})
        self.merge_module_instance.merge(1, transact={
            'from': self.w3.eth.accounts[0]})

        self.assertEqual([1, 1],
                         self.merge_module_instance.pullRequestsToMerge())
