from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.staticfiles.storage import ManifestFilesMixin


class StaticManifestStorage(ManifestFilesMixin, S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    # Filenames are content-hashed by ManifestFilesMixin, so a change in
    # content always produces a new URL - safe to cache "forever".
    object_parameters = {
        'CacheControl': 'public, max-age=31536000, immutable',
    }


class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    # file_overwrite=False means every upload gets a unique filename, so
    # (like the hashed static files above) these URLs are effectively
    # immutable and safe to cache for a long time.
    object_parameters = {
        'CacheControl': 'public, max-age=31536000, immutable',
    }
