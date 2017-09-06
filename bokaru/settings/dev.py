from bokaru.settings.common import *

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
# whitenoise.storage.CompressedManifestStaticFilesStorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "..", "www", "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "..", "www", "uploads")
MEDIA_URL = '/uploads/'
