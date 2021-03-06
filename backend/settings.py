"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import dj_database_url
import os
import sys
import backend.constants as constants

IS_PROD = os.environ.get('PROD') == 'true'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '=*f9))56@c*dzlmm0%t@)v1=)d2*pbom51h+o7l%35xt92ya3t')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not IS_PROD

# URLs used to talk to the backend
ALLOWED_HOSTS = ['server', 'localhost']

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.github.GithubOAuth2',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend.server',
    'graphene_django',
    'django_celery_results',
    'django_celery_beat',
    'corsheaders',
    'social_django',
    'encrypted_model_fields',
]

AUTH_USER_MODEL = 'server.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_DB_NAME', 'postgres'),
        'USER': os.environ.get('DJANGO_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', ''),
        'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DJANGO_DB_PORT', '5432')
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Graphene config
GRAPHENE = {
    'SCHEMA': 'backend.schema.schema'
}

# Celery config
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')


# Who's allowed to talk to the backend
CORS_ORIGIN_WHITELIST = ('https://apps.mycrocoin.org:443') if IS_PROD else (
    'localhost:3000'
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT'
)

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

CSRF_TRUSTED_ORIGINS = (
    'localhost:3000',
    '127.0.0.1:3000',
)

CORS_ALLOW_CREDENTIALS = True

ALLOWED_DEPLOY_ENVS = ['parity', 'ropsten', 'rinkeby', 'mainnet']

SOCIAL_AUTH_PIPELINE = [
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # 'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
]

# Make sure this is set in production.
# TODO: we need a better story for enforcing variables in prod vs non-prod
FIELD_ENCRYPTION_KEY = os.environ.get("FIELD_ENCRYPTION_KEY", "p098ck9XEUuGrzMtk0z06afANmAQ3iKTujGtaPZwzBM=")


# Application config
# TODO change these from functions to constants
def deploy_env():
    deploy_env = os.environ.get('DEPLOY_ENV', 'parity')
    if deploy_env not in ALLOWED_DEPLOY_ENVS:
        raise ValueError(f'DEPLOY_ENV must be one of {ALLOWED_DEPLOY_ENVS} but is {deploy_env}')
    return deploy_env

def get_infura_api_key():
    return os.environ['INFURA_API_KEY']

def ethereum_private_key():
    env_var_name = 'ETHEREUM_PRIVATE_KEY'
    if deploy_env() == 'mainnet':
        # on mainnet we will never default to the dev key below
        return os.environ[env_var_name]
    else:
        # ----------- WARNING: DO NOT USE THIS PRIVATE KEY IN ANY PRODUCTION SENSE. NEVER PUT REAL ETH INTO THIS ACCOUNT
        return os.environ.get('ETHEREUM_PRIVATE_KEY', constants.DEFAULT_ETHEREUM_PRIVATE_KEY)

def parity_endpoint():
    return os.environ.get('PARITY_ENDPOINT', constants.DEFAULT_PARITY_ENDPOINT)

def github_token():
    return os.environ['GITHUB_TOKEN']

def github_organization():
    return os.environ['GITHUB_ORGANIZATION']

