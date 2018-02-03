from bokaru.settings.common import *

# Storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "www", "uploads")
MEDIA_URL = '/uploads/'

# Local cache server
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': get_env_var('CACHE_LOCATION')
    }
}

# Mailgun backend
ANYMAIL = {
    'MAILGUN_API_KEY': get_env_var('MAILGUN_KEY'),
    'MAILGUN_SENDER_DOMAIN': get_env_var('MAILGUN_SERVER'),
}
# EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Bokaru <no-reply@mg.bokaru.com>'
SERVER_EMAIL = 'admin@bokaru.com'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Logging
# Will output to console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s BOKARU_DEV: %(levelname)s | %(module)s %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
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
