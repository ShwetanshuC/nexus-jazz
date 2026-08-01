from django.core.management.base import BaseCommand
from apps.core.s3_backup import backup_db


class Command(BaseCommand):
    help = "Upload db.sqlite3 to S3"

    def handle(self, *args, **options):
        backup_db()
        self.stdout.write("DB backed up to S3.")
