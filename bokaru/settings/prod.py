from bokaru.settings.common import *

# Set up S3 bucket as storage
INSTALLED_APPS += ('storages',)
AWS_ACCESS_KEY_ID = 'AKIAJKZZF54QTZ2FEZ7A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bokaru-files'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_HOST = 's3.ca-central-1.amazonaws.com'
S3_USE_SIGV4 = True

# Set up the RDS database connection
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bokaru',
        'USER': 'bokaru',
        'PASSWORD': 'bokaru123',
        'HOST': 'bokaru.ccmerekzzbun.ca-central-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}
