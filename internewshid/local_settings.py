from __future__ import unicode_literals, absolute_import

import private_settings

DEBUG = True
ASSETS_DEBUG = DEBUG
ASSETS_AUTO_BUILD = DEBUG
DJANGOJS_DEBUG = DEBUG

DEPLOY_ENV = "localdev"
DEPLOY_ENV_NAME = "Local dev copy"
DEPLOY_ENV_COLOR = '#ff9900'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'internewshid',
        'USER': 'internewshid',
        'PASSWORD': private_settings.DB_PASSWORD,
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    }
}

EMAIL_HOST = 'localhost'
SITE_HOSTNAME = 'localhost:8000'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
