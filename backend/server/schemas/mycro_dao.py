import graphene
from graphene import ObjectType
import os


ENV_DAO_ADDRESS_KEY = "MYCRO_DAO_ADDRESS"

class Query(ObjectType):
    mycro_dao = graphene.String()

    def resolve_mycro_dao(self, info):
        return os.environ.get(ENV_DAO_ADDRESS_KEY, None)
