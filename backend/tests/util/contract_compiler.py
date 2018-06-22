import os
from solc import compile_files

class ContractCompiler:
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    contracts_root = os.path.join(backend_root, 'contracts')

    def __init__(self):
        self.contracts = None

    def compile_contracts(self):
        self.contracts = compile_files(self.get_contract_files())

    def get_contract_files(self):
        contracts = []

        for root, dirs, files in os.walk(self.contracts_root):
            for file in files:
                contracts.append(os.path.join(root, file))

        return contracts

    def get_contract_interface(self, contract_file_name, contract_name):
        if self.contracts is None:
            self.compile_contracts()

        contract_path = self.find_contract(contract_file_name)

        if contract_path is None:
            raise ValueError(f"contract {contract_file_name} doesn't exist")

        return self.contracts[f'{contract_path}:{contract_name}']

    def find_contract(self, contract_file_name):

        for root, dirs, files in os.walk(self.contracts_root):
            for file in files:
                if file == contract_file_name:
                    return os.path.join(root, contract_file_name)

        return None
