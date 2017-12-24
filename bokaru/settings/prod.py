import json

from django.core.exceptions import ImproperlyConfigured

from bokaru.settings.common import *

# Read env file
with open(BASE_DIR + '/configs/prod/env.json') as f:
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

INSTALLED_APPS += ('storages',)

# S3 bucket as storage
AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'bokaru-files'
AWS_S3_CUSTOM_DOMAIN = 's3.ca-central-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_MEDIA_LOCATION = 'media'
S3_USE_SIGV4 = True

STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_MEDIA_LOCATION)
DEFAULT_FILE_STORAGE = 'bokaru.storage_backends.MediaStorage'

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

# ElastiCache
CACHES = {
    'default': {
        'BACKEND': 'django_elasticache.memcached.ElastiCache',
        'LOCATION': get_env_var('CACHE_LOCATION')
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Mailgun backend
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = get_env_var('MAILGUN_KEY')
MAILGUN_SERVER_NAME = get_env_var('MAILGUN_SERVER')
DEFAULT_FROM_EMAIL = 'Bokaru <admin@bokaru.com>'
SERVER_EMAIL = 'admin@bokaru.com'

DEBUG = False

# Logging
# Will output to console
# TODO: set up proper logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Security
ALLOWED_HOSTS = ['bokaru.com', '.bokaru.com', 'localhost', '.amazonaws.com']
# TODO: set to 1 year (31536000)
# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-SECURE_PROXY_SSL_HEADER
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
