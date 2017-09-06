from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    def created_time(self, name):
        pass

    def accessed_time(self, name):
        pass

    def path(self, name):
        pass

    location = 'media'
    file_overwrite = False
