from django.conf import settings
from storages.backends.s3 import S3Storage


class StaticStorage(S3Storage):
    location = settings.STATICFILES_LOCATION
    default_acl = "public-read"


class MediaStorage(S3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
