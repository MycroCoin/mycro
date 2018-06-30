from web3 import Web3
from web3.providers import HTTPProvider
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.utils import deploy_contract
import logging
import sys
import os


def get_kaleido_username_password():
    user = os.environ.get("KALEIDO_USER", "u0savgvdua")
    password = os.environ.get("KALEIDO_PASSWORD")

    return user, password


def deploy_to_kaleido(contract_interface):
    user, password = get_kaleido_username_password()

    w3 = Web3(HTTPProvider(f"https://{user}:{password}@u0telyzine-u0lq1q8otp-rpc.us-east-2.kaleido.io"))

    return w3, deploy_contract(w3, contract_interface)


def deploy_to_ganache(contract_interface):
    w3 = Web3(HTTPProvider("HTTP://127.0.0.1:7545"))

    return w3, deploy_contract(w3, contract_interface)


def main():
    contract_compiler = ContractCompiler()
    contract_interface = contract_compiler.get_contract_interface("mycro.sol", "MycroCoin")

    mycro_instance = None
    try:
        w3, (mycro_contract, mycro_address, mycro_instance) = deploy_to_ganache(contract_interface)
        logging.info("Ganache deployment succeeded")
    except Exception as e:
        logging.warning("Ganache down")
        logging.warning(e)

    if mycro_instance is None:
        try:
            w3, (mycro_contract, mycro_address, mycro_instance) = deploy_to_kaleido(contract_interface)
            logging.info("Kaleido deployment succeeded")
        except Exception as e:
            logging.warning("Kaleido down")
            logging.warning(e)
            sys.exit(1)

    logging.info(f"Contract address is {mycro_address}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
