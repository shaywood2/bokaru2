import json

from django.core.exceptions import ImproperlyConfigured

from bokaru.settings.common import *

# Read env file
with open(BASE_DIR + '/configs/dev/env.json') as f:
    env = json.loads(f.read())


def get_env_var(setting):
    try:
        val = env[setting]
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        return val
    except KeyError:
        error_msg = "ImproperlyConfigured: Set {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


# TokBox settings
TOKBOX_KEY = get_env_var('TOKBOX_KEY')
TOKBOX_SECRET = get_env_var('TOKBOX_SECRET')

# Stripe settings
STRIPE_KEY = get_env_var('STRIPE_KEY')

REGISTRATION_SALT = get_env_var('REGISTRATION_SALT')

# Secret key
SECRET_KEY = get_env_var('DJANGO_SECRET_KEY')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "www", "uploads")
MEDIA_URL = '/uploads/'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': get_env_var('DATABASE_NAME'),
        'USER': get_env_var('DATABASE_USER'),
        'PASSWORD': get_env_var('DATABASE_PASSWORD'),
        'HOST': get_env_var('DATABASE_HOST'),
        'PORT': get_env_var('DATABASE_PORT'),
        'CONN_MAX_AGE': 500,
    }
}

# Local cache server
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': get_env_var('CACHE_LOCATION')
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Bokaru <admin@dev.bokaru.com>'
SERVER_EMAIL = 'server@dev.bokaru.com'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Logging
# Will output to console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'bokaru': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'event': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'account': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'money': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'web': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'chat': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Allow local hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
