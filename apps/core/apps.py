from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Content apps whose saves should trigger an S3 backup. Excludes 'admin' (a
# LogEntry write on every page view) and 'sessions' (every login).
_BACKUP_APPS = frozenset(["core", "blog", "gallery", "events", "team", "inquiries", "accounts"])


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"

    def ready(self):
        import os
        from django.db.models.signals import post_save, post_delete
        from django.db import connection
        from apps.core.s3_backup import backup_db

        if not os.environ.get("S3_AWS_STORAGE_BUCKET_NAME") and not settings.DEBUG:
            logger.warning(
                "[core] No S3 bucket configured — DB/media won't persist across redeploys."
            )

        def backup_on_change(sender, **kwargs):
            if sender._meta.app_label in _BACKUP_APPS:
                try:
                    connection.on_commit(backup_db)
                except Exception as e:
                    logger.error(f"[core] Failed to schedule S3 backup: {e}")

        # weak=False: backup_on_change is a local closure with no other
        # strong reference. Django's default weak-reference connect() lets
        # the GC collect it right after ready() returns, silently
        # disconnecting the signal with no error — which is why the S3
        # backup never fired across 13 production deployments despite the
        # trigger code being correct (found 2026-08-14 while investigating
        # a data-loss incident: no backups/db.sqlite3 object had ever been
        # written to S3).
        post_save.connect(backup_on_change, weak=False)
        post_delete.connect(backup_on_change, weak=False)
