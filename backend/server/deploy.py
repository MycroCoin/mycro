from web3 import Web3
from web3.providers import HTTPProvider
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.utils import deploy_contract
from web3.middleware import geth_poa_middleware

import logging
import sys
import os


def get_kaleido_username_password():
    user = os.environ.get("KALEIDO_USER", "u0savgvdua")
    password = os.environ.get("KALEIDO_PASSWORD")

    return user, password

def get_kaleido_endpoint():
    user, password = get_kaleido_username_password()

    return os.environ.get("KALEIDO_ENDPOINT", f"https://{user}:{password}@u0a9n6r4oc-u0qutwl2df-rpc.us-east-2.kaleido.io")


def get_ganache_endpoint():
    return os.environ.get("GANACHE_ENDPOINT", "http://127.0.0.1:7545")


def deploy_to_kaleido(contract_interface):
    kaleido_endpoint = get_kaleido_endpoint()
    w3 = Web3(HTTPProvider(kaleido_endpoint))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)

    return w3, deploy_contract(w3, contract_interface)


def deploy_to_ganache(contract_interface):
    ganache_endpoint = get_ganache_endpoint()
    logging.info(f"Connecting to {ganache_endpoint}")
    w3 = Web3(HTTPProvider(ganache_endpoint))

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
