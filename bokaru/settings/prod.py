from bokaru.settings.common import *

# Secret key
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

INSTALLED_APPS += ('storages',)

# Set up S3 bucket as storage
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = 'bokaru-files'
AWS_S3_CUSTOM_DOMAIN = 's3.ca-central-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
S3_USE_SIGV4 = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'bokaru/static'),
]
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

DEFAULT_FILE_STORAGE = 'bokaru.storage_backends.MediaStorage'

# Set up ElastiCache
CACHES['default']['BACKEND'] = 'django_elasticache.memcached.ElastiCache'
CACHES['default']['LOCATION'] = os.environ['CACHE_URL']
