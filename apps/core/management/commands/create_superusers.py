from apps.accounts.models import User
from django.core.management.base import BaseCommand

# Only used the very first deploy, before any DB backup exists in S3 (or if
# the bucket is ever lost) — once db.sqlite3 restores from S3 on boot, this
# is a no-op for any account that already exists.
SUPERUSERS = [
    {"email": "admin@nexusjazz.com"},
]
PASSWORD = "change-me-immediately"  # rotate via the admin the moment you first log in


class Command(BaseCommand):
    help = "Create default superusers if they do not exist"

    def handle(self, *args, **options):
        for u in SUPERUSERS:
            if not User.objects.filter(email__iexact=u["email"]).exists():
                User.objects.create_superuser(email=u["email"], password=PASSWORD)
                self.stdout.write(f"Created superuser: {u['email']}")
            else:
                self.stdout.write(f"Superuser already exists: {u['email']}")
