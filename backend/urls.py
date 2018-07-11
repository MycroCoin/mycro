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
from django.urls import path
from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
import os

from graphene_django.views import GraphQLView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

mycro_address = None
w3 = None
mycro_instance = None

# TODO figure out how to use app config
# Terrible fucking hack to deploy the Mycro contract and register listeners for it during server startup
# This file gets executed during all (?) of the manage.py subcommands so use os.environ and sys.argv to guard for when
# a certain env variable is available during the runserver subcommand
import sys
if "DEPLOY_MYCRO_DAO" in os.environ and 'runserver' in sys.argv:
    from backend.server.deploy import deploy_to_kaleido
    from backend.server.utils.contract_compiler import ContractCompiler
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    from backend.server.models import Project
    PROJECT_REGISTRATION_BEAT_NAME = "Detect Project Registration"
    MERGE_PR_BEAT_NAME = "Detect Merge Events"

    compiler = ContractCompiler()
    w3, (mycro_contract, mycro_address, mycro_instance) = deploy_to_kaleido(
        compiler.get_contract_interface('mycro.sol', 'MycroCoin'))

    Project.create_mycro_dao(mycro_address)
    schedule, created = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.SECONDS, )
    if not PeriodicTask.objects.filter(name=PROJECT_REGISTRATION_BEAT_NAME):
        PeriodicTask.objects.create(interval=schedule, name=PROJECT_REGISTRATION_BEAT_NAME,
                                    task='backend.server.tasks.process_registrations')
    if not PeriodicTask.objects.filter(name=MERGE_PR_BEAT_NAME):
        PeriodicTask.objects.create(interval=schedule, name=MERGE_PR_BEAT_NAME,
                                    task='backend.server.tasks.process_merges')

