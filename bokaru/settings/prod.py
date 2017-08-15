from bokaru.settings.common import *

# Secret key
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Set up S3 bucket as storage
INSTALLED_APPS += ('storages',)
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = 'bokaru-files'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_HOST = 's3.ca-central-1.amazonaws.com'
S3_USE_SIGV4 = True
