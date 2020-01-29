from __future__ import absolute_import, unicode_literals

import collections
import json
import warnings
from copy import deepcopy
from os import path

import private_settings

warnings.filterwarnings(
    'ignore',
    module='floppyforms',
    message='Unable to import floppyforms.gis'
)

BASE_DIR = path.abspath(path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = private_settings.SECRET_KEY

ADMINS = (
    ('Aptivate internewshid team', 'internewshid-team@aptivate.org'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'donotreply@internewshid.aptivate.org'
SERVER_EMAIL = 'server@internewshid.aptivate.org'

TIME_ZONE = 'Asia/Dhaka'

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
]

SITE_ID = 1

USE_I18N = True

USE_L10N = False

USE_TZ = True

SHORT_DATETIME_FORMAT = 'd M Y H:i'
SHORT_DATE_FORMAT = 'd M Y'

MEDIA_ROOT = path.join(BASE_DIR, 'uploads')

MEDIA_URL = '/uploads/'

STATIC_ROOT = path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    path.join(BASE_DIR, 'media'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_assets.finders.AssetsFinder'
)

LOCALE_DIR = path.join(BASE_DIR, '..', 'locale')
if path.isdir(LOCALE_DIR):
    LOCALE_PATHS = (LOCALE_DIR,)

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'bootstrap3',
    'constance',
    'rest_framework',
    'django_tables2',
    'djangojs',
    'django_assets',
    'floppyforms',
    'widget_tweaks'
)

LOCAL_APPS = (
    'hid',
    'dashboard',
    'users',
    'chn_spreadsheet',
    'tabbed_page',
)

DATA_LAYER_APPS = (
    'taxonomies',
    'data_layer',
    'rest_api',
    'transport',
)

INSTALLED_APPS = DATA_LAYER_APPS + LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

SECURE = False
if SECURE:
    INSTALLED_APPS += ("djangosecure",)

    # set this to 60 seconds and then to 518400 when you can prove it works
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_FRAME_DENY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = True

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

AUTH_USER_MODEL = "users.User"
EMAIL_BOT_ADDRESS = 'blackhole@aptivate.org'
LOGIN_REDIRECT_URL = "dashboard"
SITE_NAME = 'Internews Humanitarian Information Dashboard'

BOOTSTRAP3 = {
    'jquery_url': STATIC_URL + '/js/jquery.min.js',
    'javascript_url': STATIC_URL + '/bootstrap/js/bootstrap.min.js',

}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

# We use a custom back-end to avoid a hard character limit on
# the utf8mb4 encoding/collation whereby the constance model
# must be overriden. We set the max_length to 190 instead of 255.
# See https://github.com/jazzband/django-constance/issues/121
CONSTANCE_BACKEND = 'data_layer.models.CustomConstanceBackend'

CONSTANCE_CONFIG = {
    'CONTEXT_LOCATION': ("Cox's Bazaar, Bangladesh",
                         'Location of dashboard deployment'),
    'DEFAULT_TABBED_PAGE_NAME': ('main',
                                 'Name of default tabbed page'),
    'DEFAULT_TAB_NAME': ('all',
                         'Name of default tab within page'),
    'ITEM_TYPE_CATEGORY': (
        json.dumps(
            {'all': 'bangladesh-refugee-crisis-sectors'}
        ),
        'Single taxonomy to use to categorise all types of item'),
    'GLOBAL_DATA_SOURCE': ('kobo',
                           'Sheet profile to use when loading data from the main menu'),
}

DJANGO_TABLES2_PAGE_RANGE = 6

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}


def update_recursive(dest, source):
    for k, v in source.items():
        if dest.get(k, None) and isinstance(v, collections.Mapping):
            update_recursive(dest[k], source[k])
        else:
            dest[k] = deepcopy(source[k])


# try:
#     import local_settings
# except ImportError:
#     print("Can't import the `local_settings` symlink!")
#     import sys
#     sys.exit(1)
# else:
#     import re
#     for attr in dir(local_settings):
#         match = re.search('^EXTRA_(\w+)', attr)  # noqa
#         if match:
#             name = match.group(1)
#             value = getattr(local_settings, attr)
#             try:
#                 original = globals()[name]
#                 if isinstance(original, collections.Mapping):
#                     update_recursive(original, value)
#                 else:
#                     original += value
#             except KeyError:
#                 globals()[name] = value
#         elif re.search('^[A-Z]', attr):
#             globals()[attr] = getattr(local_settings, attr)

from os import environ
from private_settings import DB_PASSWORD

DEBUG = True
ASSETS_DEBUG = DEBUG
ASSETS_AUTO_BUILD = DEBUG
DJANGOJS_DEBUG = DEBUG

# `MYSQL_DATABASE` and `MYSQL_ROOT_PASSWORD` are used for the CI
# https://hub.docker.com/_/mysql/
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': environ.get('MYSQL_DATABASE', 'internewshid'),
        'USER': environ.get('APTIVATE_CLI_MYSQL_USER', 'internewshid'),
        'HOST': environ.get('APTIVATE_CLI_MYSQL_HOST', 'localhost'),
        'PASSWORD': environ.get('MYSQL_ROOT_PASSWORD', DB_PASSWORD),
        'OPTIONS': {
          'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
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

INTERNAL_IPS = (
  '127.0.0.1',
)

LANGUAGE_CODE = 'en'


ALLOWED_HOSTS = [
    '*',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CSRF_FAILURE_VIEW = 'hid.views.csrf.csrf_failure'

if DEBUG:
    INSTALLED_APPS += (
        'django_extensions',
        'debug_toolbar',
        'template_timings_panel',
    )

    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    ]
