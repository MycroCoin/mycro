import unittest
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.utils import deploy_contract

class TestMergeModule(unittest.TestCase):

    def setUp(self):
        self.compiler = ContractCompiler()
        self.w3 = Web3(EthereumTesterProvider())

        self.merge_module_interface = self.compiler.get_contract_interface("merge_module.sol", "MergeModule")
        _, _, self.merge_module_instance = deploy_contract(self.w3, self.merge_module_interface)


    def test_get_name(self):
        self.assertEqual("MergeModule", self.merge_module_instance.getName())