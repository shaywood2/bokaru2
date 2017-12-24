import os
import json

from django.core.exceptions import ImproperlyConfigured


# Build paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Read env file
with open(BASE_DIR + '/env.json') as f:
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


# Application definition
INSTALLED_APPS = [
    'web.apps.WebConfig',
    'money.apps.MoneyConfig',
    'account.apps.AccountConfig',
    'event.apps.EventConfig',
    'chat.apps.ChatConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'imagekit',
    'widget_tweaks',
    'formtools'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bokaru.urls'
APPEND_SLASH = True

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

WSGI_APPLICATION = 'bokaru.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/topics/auth/passwords/#module-django.contrib.auth.password_validation
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

# https://docs.djangoproject.com/en/1.10/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
PASSWORD_RESET_TIMEOUT_DAYS = 3
# Registration settings
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Toronto'
USE_I18N = True
USE_L10N = True
USE_TZ = True

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

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# ===========
# Secret keys
# ===========
# TokBox
TOKBOX_KEY = get_env_var('TOKBOX_KEY')
TOKBOX_SECRET = get_env_var('TOKBOX_SECRET')

# Stripe
STRIPE_KEY = get_env_var('STRIPE_KEY')

# Registration
REGISTRATION_SALT = get_env_var('REGISTRATION_SALT')

# Django
SECRET_KEY = get_env_var('DJANGO_SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
