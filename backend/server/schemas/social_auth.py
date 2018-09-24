import graphene
import graphql_social_auth


class Mutations(graphene.ObjectType):
    social_auth = graphql_social_auth.SocialAuthJWT.Field()

