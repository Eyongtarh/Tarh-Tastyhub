"""
One-off backfill for dish/category images uploaded before
custom_storages.MediaStorage started setting a long-lived Cache-Control
header on new uploads. S3Boto3Storage's object_parameters only apply at
upload time, so anything already in the bucket was left with S3's
default (no Cache-Control header, which Lighthouse flags as TTL "None").
Re-run only if older uploads still show up with a missing cache header.
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Set a long-lived Cache-Control header on every object already "
        "in the media/ prefix of the S3 bucket, in place."
    )

    CACHE_CONTROL = "public, max-age=31536000, immutable"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List objects that would be updated without changing them.",
        )

    def handle(self, *args, **options):
        if not getattr(settings, "USE_AWS", False):
            raise CommandError("USE_AWS is off - nothing to backfill locally.")

        import boto3

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client("s3")
        paginator = s3.get_paginator("list_objects_v2")

        updated = 0
        skipped = 0
        for page in paginator.paginate(Bucket=bucket_name, Prefix="media/"):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                head = s3.head_object(Bucket=bucket_name, Key=key)
                if head.get("CacheControl") == self.CACHE_CONTROL:
                    skipped += 1
                    continue

                action = (
                    "Would update" if options["dry_run"] else "Updating"
                )
                self.stdout.write(f"{action}: {key}")
                if not options["dry_run"]:
                    content_type = head.get(
                        "ContentType", "binary/octet-stream"
                    )
                    s3.copy_object(
                        Bucket=bucket_name,
                        Key=key,
                        CopySource={"Bucket": bucket_name, "Key": key},
                        MetadataDirective="REPLACE",
                        CacheControl=self.CACHE_CONTROL,
                        ContentType=content_type,
                        ACL="public-read",
                    )
                updated += 1

        verb = "would be updated" if options["dry_run"] else "updated"
        self.stdout.write(self.style.SUCCESS(
            f"{updated} object(s) {verb}, {skipped} already had the header."
        ))
