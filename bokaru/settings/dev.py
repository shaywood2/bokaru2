import dj_database_url

from bokaru.settings.common import *

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "..", "www", "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "..", "www", "uploads")
MEDIA_URL = '/uploads/'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# Update database configuration with $DATABASE_URL
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# Local cache server
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Bokaru <admin@dev.bokaru.com>'
SERVER_EMAIL = 'server@dev.bokaru.com'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'il3dg4!5!r1sw%&i+%h7(&f4yu(6gog6pfjx()b8c%quwk5se5'

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
