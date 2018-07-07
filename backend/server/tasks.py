# Create your tasks here
from celery import shared_task
from backend.server.utils.contract_compiler import ContractCompiler
from backend.server.utils.utils import deploy_contract
from backend.server.deploy import main

@shared_task
def deploy_mycro():
    main()

@shared_task
def print_stuff():
    print("1")

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

