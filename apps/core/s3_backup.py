import os
import shutil
import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)

S3_KEY = "backups/db.sqlite3"


def _client():
    """Always create a fresh client — no singleton caching that can get stuck None."""
    access_key = os.environ.get("S3_ACCESS_KEY")
    secret_key = os.environ.get("S3_SECRET_KEY")
    if not access_key or not secret_key:
        print("[s3_backup] ERROR: S3_ACCESS_KEY or S3_SECRET_KEY not set — backup disabled.")
        return None
    try:
        return boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
    except Exception as e:
        print(f"[s3_backup] ERROR: Failed to init S3 client: {e}")
        return None


def _bucket():
    b = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
    if not b:
        print("[s3_backup] ERROR: S3_AWS_STORAGE_BUCKET_NAME not set — backup disabled.")
    return b


def _db_path():
    return str(settings.DATABASES["default"]["NAME"])


def backup_db():
    """Upload SQLite DB to S3 synchronously. Called after every admin save via on_commit."""
    bucket = _bucket()
    client = _client()
    if not bucket or not client:
        return
    db_path = _db_path()
    if not os.path.exists(db_path):
        print(f"[s3_backup] ERROR: DB file not found at {db_path}")
        return
    size_kb = os.path.getsize(db_path) // 1024
    try:
        client.upload_file(db_path, bucket, S3_KEY)
        print(f"[s3_backup] BACKUP OK — uploaded {db_path} ({size_kb} KB) to s3://{bucket}/{S3_KEY}")
        logger.info(f"[s3_backup] Backup succeeded ({size_kb} KB).")
    except Exception as e:
        print(f"[s3_backup] ERROR: Backup failed: {e}")
        logger.error(f"[s3_backup] Backup failed: {e}")


def restore_db():
    """Download SQLite DB from S3. Returns True if restored."""
    bucket = _bucket()
    client = _client()
    if not bucket or not client:
        return False

    db_path = _db_path()
    temp_path = db_path + ".tmp"

    try:
        print(f"[s3_backup] Attempting restore from s3://{bucket}/{S3_KEY} → {db_path}")
        client.download_file(bucket, S3_KEY, temp_path)
        size_kb = os.path.getsize(temp_path) // 1024 if os.path.exists(temp_path) else 0
        if size_kb > 0:
            shutil.move(temp_path, db_path)
            print(f"[s3_backup] RESTORE OK — {size_kb} KB written to {db_path}")
            logger.info(f"[s3_backup] Restore succeeded ({size_kb} KB).")
            return True
        else:
            print("[s3_backup] ERROR: Downloaded file is empty — discarding.")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "404":
            print(f"[s3_backup] No backup found at s3://{bucket}/{S3_KEY} — starting with fresh DB.")
        else:
            print(f"[s3_backup] ERROR: S3 download failed (code={code}): {e}")
            logger.error(f"[s3_backup] Download failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False
    except Exception as e:
        print(f"[s3_backup] ERROR: Unexpected restore error: {e}")
        logger.error(f"[s3_backup] Restore error: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False
