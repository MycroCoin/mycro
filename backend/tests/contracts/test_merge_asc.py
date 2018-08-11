from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.deploy import _deploy_contract
import unittest

W3 = Web3(EthereumTesterProvider())
REWARD = 10

class TestMergeAsc(unittest.TestCase):

    def setUp(self):
        self.compiler = ContractCompiler()

        contract_interface = self.compiler.get_contract_interface("merge_asc.sol", "MergeASC")
        _, _, self.merge_asc_instance = _deploy_contract(W3, contract_interface, W3.eth.accounts[1], REWARD, 1)

    def test_get_rewardee(self):

        # note: depends on the account used by _deploy_contract for the deployment
        self.assertEqual(W3.eth.accounts[1], self.merge_asc_instance.rewardee())
