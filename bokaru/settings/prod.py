from bokaru.settings.common import *

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

# ElastiCache
CACHES = {
    'default': {
        'BACKEND': 'django_elasticache.memcached.ElastiCache',
        'LOCATION': get_env_var('CACHE_LOCATION')
    }
}

# Mailgun backend
ANYMAIL = {
    'MAILGUN_API_KEY': get_env_var('MAILGUN_KEY'),
    'MAILGUN_SENDER_DOMAIN': get_env_var('MAILGUN_SERVER'),
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'Bokaru <no-reply@mg.bokaru.com>'
SERVER_EMAIL = 'admin@bokaru.com'

DEBUG = False

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s BOKARU_PROD: %(levelname)s | %(module)s %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'SysLog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'address': ('logs.papertrailapp.com', 37452)
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
        },
        'bokaru': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
        },
        'event': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
        },
        'account': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
        },
        'money': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
        },
        'web': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
        },
        'chat': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
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
