import graphene
from graphene import ObjectType
from backend.urls import mycro_address


class Query(ObjectType):
    mycro_dao = graphene.String()

    def resolve_mycro_dao(self, info):
        return mycro_address