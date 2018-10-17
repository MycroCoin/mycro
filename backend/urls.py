"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
import os
import sys
import logging
import backend.settings as settings

from graphene_django.views import GraphQLView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
]

main_wallet = None


# TODO figure out how to use app config - we can clean all of this up if we get app config working
# Terrible fucking hack to deploy the Mycro contract and register listeners for it during server startup
# This file gets executed during all (?) of the manage.py subcommands so use os.environ and sys.argv to guard for when
# a certain env variable is available during the runserver subcommand
if 'runserver' in sys.argv:
    import backend.server.utils.deploy as deploy
    from backend.server.utils.contract_compiler import ContractCompiler
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    from backend.server.models import Project, Wallet

    MERGE_PR_BEAT_NAME = "Detect Merge Events"
    w3 = deploy.get_w3()

    # If no wallet exists in the db create it. If one exists, treat the one with
    # the lowest ID as the main wallet of this application
    if not Wallet.objects.filter():
        account = w3.eth.account.create('')
        private_key = account.privateKey.hex()
        Wallet.objects.create(private_key=private_key, address=account.address)

    # if the wallet isn't funded, fund it
    main_wallet = Wallet.objects.first()
    if deploy.get_wallet_balance(w3, main_wallet.private_key) < 1e18:
        deploy.transfer_between_accounts(w3, settings.ethereum_private_key(), main_wallet.private_key, 1)

    # TODO remove this when we no longer need to deploy the mycro contract on init
    # maybe we should hide this behind an env variable because this is useful for testing
    mycro_project = Project.objects.filter(is_mycro_dao=True)
    if len(mycro_project) == 0:
        compiler = ContractCompiler()
        _, mycro_contract, mycro_address, mycro_instance = deploy.deploy(
            compiler.get_contract_interface('mycro.sol', 'MycroCoin'), private_key=main_wallet.private_key, timeout=None)
        Project.create_mycro_dao(mycro_address, symbol=mycro_instance.symbol(), decimals=mycro_instance.decimals())
    elif len(mycro_project) > 1:
        raise ValueError("Shit there are two mycro DAOs")

    # Set up background tasks which monitor blockchain for events
    schedule, created = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.SECONDS, )
    if not PeriodicTask.objects.filter(name=MERGE_PR_BEAT_NAME):
        PeriodicTask.objects.create(interval=schedule, name=MERGE_PR_BEAT_NAME,
                                    task='backend.server.tasks.process_merges')

