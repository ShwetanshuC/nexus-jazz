"""
Download all media files from S3 to local MEDIA_ROOT at container startup.
Nginx serves /media/ from local disk first — this makes uploaded images load
at the same speed as baked-in static files, with no S3/CloudFront round-trips.
Only downloads files that are missing or smaller than the S3 version.
"""
import os
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sync all S3 media files to local disk for fast nginx serving"

    def handle(self, *args, **options):
        bucket = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
        access_key = os.environ.get("S3_ACCESS_KEY")
        secret_key = os.environ.get("S3_SECRET_KEY")

        if not bucket or not access_key:
            print("[sync_media] No S3 credentials — skipping media sync.")
            return

        client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        media_root = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)

        paginator = client.get_paginator("list_objects_v2")
        total = 0
        skipped = 0

        try:
            for page in paginator.paginate(Bucket=bucket):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if key.startswith("backups/"):
                        continue
                    local_path = media_root / key
                    if local_path.exists() and local_path.stat().st_size >= obj["Size"]:
                        skipped += 1
                        continue
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    client.download_file(bucket, key, str(local_path))
                    total += 1
        except ClientError as e:
            print(f"[sync_media] ERROR: {e}")
            return

        print(f"[sync_media] Synced {total} file(s), skipped {skipped} already up to date.")
