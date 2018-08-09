import unittest
from unittest.mock import patch
import backend.settings as settings

class TestSettings(unittest.TestCase):

    @patch.dict('backend.settings.os.environ', {'DEPLOY_ENV': 'invalid'})
    def test_error_raised_on_bad_deploy_env(self):
        # with self.assertRaisesRegex(ValueError, "must be one of ['parity', 'ropsten', 'mainnet'] "):
        with self.assertRaisesRegex(ValueError, "must be one of"):
            settings.deploy_env()


    @patch.dict('backend.settings.os.environ', {'DEPLOY_ENV': 'ropsten'})
    def test_get_deploy_env_when_valid(self):
        self.assertEqual('ropsten', settings.deploy_env())

    def test_get_deploy_env_when_env_var_not_present(self):
        self.assertEqual('parity', settings.deploy_env())

    @patch.dict('backend.settings.os.environ', {'DEPLOY_ENV': 'mainnet'})
    def test_get_ethereum_private_key_on_mainnet_but_key_not_present_in_env(self):
        with self.assertRaisesRegex(KeyError, 'ETHEREUM_PRIVATE_KEY'):
            settings.ethereum_private_key()
