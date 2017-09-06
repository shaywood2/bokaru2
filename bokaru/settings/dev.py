from bokaru.settings.common import *

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
# whitenoise.storage.CompressedManifestStaticFilesStorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
