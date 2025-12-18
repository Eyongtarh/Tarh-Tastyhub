from storages.backends.s3boto3 import S3Boto3Storage

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'


class StaticStorage(S3Boto3Storage):
    location = STATICFILES_LOCATION
    default_acl = 'public-read'


class MediaStorage(S3Boto3Storage):
    location = MEDIAFILES_LOCATION
    file_overwrite = False
