from django.core.management.base import BaseCommand
from apps.core.s3_backup import restore_db


class Command(BaseCommand):
    help = "Download db.sqlite3 from S3 before migrate runs"

    def handle(self, *args, **options):
        if restore_db():
            self.stdout.write("DB restored from S3.")
        else:
            self.stdout.write("No S3 backup found — starting with a fresh DB.")
