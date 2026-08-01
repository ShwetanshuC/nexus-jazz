# AWS Lightsail Deployment Guide — Nexus Jazz

How to take this site out of the shared portfolio preview container and give it its own
independent AWS Lightsail Container Service, wired to its real domain. Written specifically
for this repo's current state (checked 2026-07-31) — not a generic template. Mirrors the
proven pattern already running in production for `SouthernParkWebsite`
(`SouthernParkWebsite/AWS_DEPLOY_GUIDE.md`), adapted to this project's actual code.

---

## Persistence — the part that's non-negotiable

Lightsail Container Service wipes every container's filesystem on each redeploy. Without the
S3 wiring in Part 1, **every push to `main` would erase the entire database and every uploaded
photo** — Keenan's bio, the gallery, events, booking inquiries, all of it. This guide gives
Nexus Jazz the exact same persistence guarantee SouthernParkWebsite already runs in
production, made of three pieces that all have to be in place together (Part 1 adds all
three — this section just says why each one exists):

1. **Auto-save on every change** (Part 1.8's signal in `apps/core/apps.py`) — any save or
   delete on a content model (blog posts, gallery photos, events, team members, inquiries,
   settings, users) uploads the whole SQLite DB to S3 immediately after the transaction
   commits. No cron job, no manual step — it fires on every single admin Save click.
2. **Restore before anything else runs** (`restore_db` in the Dockerfile's `CMD`, Part 1.2 +
   1.8) — on every container boot, the DB is pulled back down from S3 *before* `migrate` runs,
   so a fresh container always starts from the last real state, not an empty one.
3. **Media survives the same way** (Part 1.9's `ResizingS3Storage`, Part 1.8's `sync_media`) —
   every uploaded photo is written straight to S3 (with a local mirror for fast nginx serving,
   not instead of S3), and `sync_media` re-populates that local mirror on every fresh boot.

The one failure mode to watch for: if the `S3_AWS_STORAGE_BUCKET_NAME` / `S3_ACCESS_KEY` /
`S3_SECRET_KEY` secrets (Part 4) are ever missing from a deployment, all three of the above
silently no-op rather than erroring — `apps/core/apps.py`'s `ready()` logs a warning
(`"No S3 bucket configured — DB/media won't persist across redeploys"`) but the container
still starts and still serves traffic normally. That warning only shows up in the Lightsail
container logs, not anywhere client-facing, so it's easy to miss. **After Part 5's first
deploy, check the container logs once for that exact warning string** — its absence is your
confirmation persistence is actually wired up, not just configured to look like it is.

---

## 0. Where this project stands right now

Today, Nexus Jazz is **not** independently deployed — it only exists as an unlisted preview,
cloned at boot into the `shwetanshuc-portfolio` container (`nexus_jazz/settings_preview.py`,
`.github/workflows/bump-preview.yml`). Going live means giving it its own Lightsail Container
Service, its own domain, and its own persistence — decoupled from the portfolio entirely.

Gap check against the proven SouthernParkWebsite pattern — what's already here vs. what
Part 1 below adds:

| Piece | Nexus Jazz today | Needed to go live |
|---|---|---|
| `gunicorn`, `dj-database-url`, `psycopg2-binary` | ✅ already in `requirements.txt` | — |
| `boto3`, `django-storages` (S3) | ❌ missing | Part 1.1 |
| `Dockerfile` | ❌ none | Part 1.2 |
| `AWS/nginx/Dockerfile` + `default.conf` | ❌ none | Part 1.3 |
| `AWS/deploymentconfig.json` + `publicendpoint.json` | ❌ none | Part 1.4 |
| `.github/workflows/deploy.yml` (real deploy, not the preview trigger) | ❌ none | Part 1.5 |
| S3-backed DB backup/restore + media sync commands | ❌ none | Part 1.6 |
| Media served unconditionally (not gated on `DEBUG`) | ❌ gated | Part 1.7 |
| `CSRF_TRUSTED_ORIGINS` | ❌ not set at all | Part 1.8 |
| S3 media storage class | ❌ local filesystem only (`ResizingFileSystemStorage`) | Part 1.9 |
| `DJANGO_DEBUG` default | ⚠️ **defaults to `true`** if the env var is ever unset | Part 3, flagged loud |

**Read all of Part 1 before touching AWS.** None of it is optional — Lightsail Container
Service has an *ephemeral filesystem*: every redeploy wipes `db.sqlite3` and any uploaded
photos unless they're backed by S3, same as it would for any project on this host.

---

## Part 1 — Code changes (do these first, commit, then move to AWS)

### 1.1 — `requirements.txt`

Add two lines (everything else you need is already there):

```
boto3
django-storages
```

### 1.2 — `Dockerfile` (project root)

```dockerfile
FROM python:3.10-slim

EXPOSE 8000/tcp
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

COPY . .

RUN DJANGO_SECRET_KEY=build-placeholder python3 manage.py collectstatic --noinput

CMD ["sh", "-c", "\
  python3 manage.py restore_db || true && \
  python3 manage.py migrate --noinput && \
  python3 manage.py create_superusers || true && \
  python3 manage.py sync_media || true && \
  trap 'echo \"[startup] SIGTERM received — backing up DB before shutdown\" && python3 manage.py backup_db && exit 0' TERM INT && \
  gunicorn nexus_jazz.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 300 --keep-alive 5 --log-level info & \
  wait $!"]
```

(`python:3.10-slim` and this exact build-deps list are what SouthernPark already runs
successfully with the same Pillow/argon2-cffi/psycopg2-binary combination this project uses —
don't substitute a different base image on a first deploy.)

### 1.3 — `AWS/nginx/Dockerfile`

```dockerfile
FROM nginx:1.19.0-alpine
RUN mkdir /tmp/nginx
COPY staticfiles/ ./static
COPY staticfiles/ ./staticfiles
COPY AWS/nginx/default.conf ./etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 1.4 — `AWS/nginx/default.conf`

```nginx
gzip on;
gzip_types text/plain text/css text/javascript application/javascript application/json image/svg+xml;
gzip_min_length 1024;
gzip_proxied any;
gzip_vary on;

server {
    client_max_body_size 50m;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 90s;
        proxy_connect_timeout 10s;
        proxy_send_timeout 90s;
    }

    # Admin uploads (gallery photos, etc.) get more room and stream straight
    # through instead of nginx buffering the whole file first.
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_request_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 10s;
        proxy_send_timeout 300s;
    }

    location /healthcheck {
        add_header Content-Type text/plain;
        return 200 'Up and running!';
    }

    location /static/ {
        alias /static/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
        try_files $uri $uri/ =404;
    }

    location /media/ {
        alias /media/;
        expires 1h;
        add_header Cache-Control "public, max-age=3600";
        access_log off;
        try_files $uri $uri/ @media_proxy;
    }

    location @media_proxy {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }
}
```

The nginx container's own `/media/` directory is always empty (nothing `COPY`s media into
the nginx image) — every media request falls through `try_files` to `@media_proxy`, which
reaches the Django container over `localhost:8000`. That works because Lightsail runs every
container in one deployment inside the same task/network namespace — `localhost` from nginx
really does reach the sibling Django container. This is exactly how SouthernPark serves media
today; nothing here is preview/local-only behavior.

### 1.5 — `AWS/deploymentconfig.json`

```json
{
  "django": {
    "image": ":djangoapp.django.latest",
    "ports": {"8000": "HTTP"}
  },
  "nginx": {
    "image": ":djangoapp.nginx.latest",
    "ports": {"80": "HTTP"}
  }
}
```

### 1.6 — `AWS/publicendpoint.json`

```json
{
  "containerName": "nginx",
  "containerPort": 80,
  "healthCheck": {
    "healthyThreshold": 2,
    "unhealthyThreshold": 10,
    "timeoutSeconds": 30,
    "intervalSeconds": 60,
    "path": "/healthcheck",
    "successCodes": "200-299"
  }
}
```

### 1.7 — `.github/workflows/deploy.yml`

Copy `SouthernParkWebsite/.github/workflows/deploy.yml` verbatim, then change exactly these
three things:
- `AWS_LIGHTSAIL_SERVICE_NAME: djangoapp` → pick a service name for this project (e.g.
  `nexus-jazz`) and use it consistently here and in Part 2.
- `docker build -t django:latest .` step — no change needed, it already builds whatever
  `Dockerfile` is at repo root.
- The `southernpark.wsgi` reference doesn't appear in that workflow (it's only in the
  Dockerfile you already wrote in 1.2) — nothing else to touch.

This workflow is what actually builds and pushes both images and triggers the Lightsail
deployment on every push to `main`. It is separate from (and should eventually replace, see
Part 5) the existing `.github/workflows/bump-preview.yml`, which only pings the portfolio repo
and has nothing to do with this independent deploy.

### 1.8 — S3-backed SQLite backup/restore + media sync

Nexus Jazz currently has no `apps/core/management/commands/` beyond `seed.py`. Add four new
commands, ported from the proven SouthernPark pattern (same idea, same file names, adapted to
this project's module paths):

**`apps/core/s3_backup.py`** (new file) — copy
`SouthernParkWebsite/sitecontent/s3_backup.py` verbatim; it has zero SouthernPark-specific
references, it's generic (reads `S3_ACCESS_KEY` / `S3_SECRET_KEY` / `S3_AWS_STORAGE_BUCKET_NAME`
from the environment and backs up/restores whatever `settings.DATABASES["default"]["NAME"]`
points at).

**`apps/core/management/commands/restore_db.py`**:
```python
from django.core.management.base import BaseCommand
from apps.core.s3_backup import restore_db


class Command(BaseCommand):
    help = "Download db.sqlite3 from S3 before migrate runs"

    def handle(self, *args, **options):
        if restore_db():
            self.stdout.write("DB restored from S3.")
        else:
            self.stdout.write("No S3 backup found — starting with a fresh DB.")
```

**`apps/core/management/commands/backup_db.py`**:
```python
from django.core.management.base import BaseCommand
from apps.core.s3_backup import backup_db


class Command(BaseCommand):
    help = "Upload db.sqlite3 to S3"

    def handle(self, *args, **options):
        backup_db()
        self.stdout.write("DB backed up to S3.")
```

**`apps/core/management/commands/create_superusers.py`** — this project's `User` model is
email-only (`AUTH_USER_MODEL = "accounts.User"`, `USERNAME_FIELD = "email"`), so don't copy
SouthernPark's `username=`-based version verbatim:
```python
from apps.accounts.models import User
from django.core.management.base import BaseCommand

SUPERUSERS = [
    {"email": "keenan@nexusjazz.com"},
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
```
(You already have a working `admin@nexusjazz.com` account baked into the committed
`db.sqlite3` from earlier in this project — once that DB is restored from S3 on first boot,
this command is a no-op for it. It only matters the very first deploy, before any backup
exists in S3, or if you ever need to recover from a lost bucket.)

**`apps/core/management/commands/sync_media.py`** — copy
`SouthernParkWebsite/sitecontent/management/commands/sync_media.py` verbatim (it's generic;
downloads everything under `settings.MEDIA_ROOT`'s prefix from S3 to local disk at boot so
nginx serves it without a round-trip).

**Wire the auto-backup-on-save signal** in `apps/core/apps.py`:
```python
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

        post_save.connect(backup_on_change)
        post_delete.connect(backup_on_change)
```

### 1.9 — Serve `/media/` unconditionally (not gated on `DEBUG`)

Today `nexus_jazz/urls.py` only serves media when `DEBUG=True` — fine for local dev, but in
production nginx's `@media_proxy` fallback needs *something* answering on the Django side too.
Add one unconditional route (SouthernPark does the same — its own `re_path` for media isn't
gated on `DEBUG` either):

```python
from django.urls import re_path
from django.views.static import serve as _serve_static

urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", _serve_static, {"document_root": settings.MEDIA_ROOT}),
]
```
Add this near the bottom of `nexus_jazz/urls.py`, after the existing `if settings.DEBUG:`
block (outside it, unconditional).

### 1.10 — `CSRF_TRUSTED_ORIGINS` (currently not set at all)

In `nexus_jazz/settings.py`, near `ALLOWED_HOSTS`:
```python
_csrf_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = (
    [o.strip() for o in _csrf_origins.split(",") if o.strip()]
    if _csrf_origins
    else ["https://*.amazonlightsail.com"]
)
```
You'll set the real value via the `DJANGO_CSRF_TRUSTED_ORIGINS` secret in Part 4 once the
domain is live — e.g. `https://nexusjazz.com,https://www.nexusjazz.com`. Without this, admin
logins and form POSTs will 403 the moment the site is reached through the real domain instead
of the raw `*.amazonlightsail.com` URL.

### 1.11 — S3 media storage class

`nexus_jazz/storage.py` already has the exact resizing logic needed
(`_process()` — EXIF fix, 3840px cap, progressive JPEG); it just needs an S3-backed sibling
class alongside the existing filesystem one. Add to the bottom of `nexus_jazz/storage.py`:

```python
def _make_resizing_s3():
    try:
        from storages.backends.s3boto3 import S3Boto3Storage
    except ImportError:
        return None

    class ResizingS3Storage(S3Boto3Storage):
        def _save(self, name, content):
            new_content, ext = _process(content)
            if ext and "." in name:
                name = name.rsplit(".", 1)[0] + ext
            saved_name = super()._save(name, new_content)
            # Mirror to local disk so nginx serves it instantly, no S3 round-trip.
            try:
                from pathlib import Path
                from django.conf import settings
                local_path = Path(settings.MEDIA_ROOT) / saved_name
                local_path.parent.mkdir(parents=True, exist_ok=True)
                new_content.seek(0)
                local_path.write_bytes(new_content.read())
            except Exception:
                pass
            return saved_name

    return ResizingS3Storage


try:
    ResizingS3Storage = _make_resizing_s3()
except Exception:
    ResizingS3Storage = None
```

Then in `nexus_jazz/settings.py`, add `"storages"` to `INSTALLED_APPS`, and switch the
`STORAGES["default"]` backend to it whenever an S3 bucket is configured:
```python
_s3_bucket = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
if _s3_bucket:
    AWS_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = _s3_bucket
    AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    STORAGES["default"] = {"BACKEND": "nexus_jazz.storage.ResizingS3Storage"}
```
Place this right after the existing `STORAGES = {...}` block.

### 1.12 — Commit

```bash
git add requirements.txt Dockerfile AWS/ .github/workflows/deploy.yml \
        apps/core/s3_backup.py apps/core/management/commands/ apps/core/apps.py \
        nexus_jazz/urls.py nexus_jazz/settings.py nexus_jazz/storage.py
git commit -m "Add independent AWS Lightsail deploy: S3 backup/media, Docker, nginx"
git push origin main
```
This push alone won't deploy anything yet — the new `deploy.yml` needs AWS credentials to
exist as GitHub secrets first (Part 4), and there's no Lightsail service for it to push to
until Part 2.

---

## Part 2 — AWS Lightsail setup

1. Go to **lightsail.aws.amazon.com** → **Containers** → **Create container service**.
2. Pick a region (e.g. `us-east-1`) and the **Nano** power tier ($7/mo) to start — bump up
   later if traffic warrants it.
3. Name it **exactly** what you put in `deploy.yml`'s `AWS_LIGHTSAIL_SERVICE_NAME` (e.g.
   `nexus-jazz`) — this has to match precisely, it's how the workflow finds the service.
4. Skip the "first deployment" prompt during creation — GitHub Actions will do the actual
   deploy in Part 5. Just create the empty service for now.
5. **IAM permissions** (skip if you already have a Lightsail-capable IAM user from another
   project — reuse it, don't create a second one): IAM → Users → your deploy user → Add
   permissions → Create inline policy →
   ```json
   {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"lightsail:*","Resource":"*"}]}
   ```
   Name it `LightsailFullAccess`, save. Note that user's Access Key ID / Secret Access Key —
   you'll need them in Part 4.
6. **S3 bucket for media/DB backups**: Lightsail → **Storage** → **Create bucket**. Any name,
   same region as the container service. Open the bucket → **Access keys** tab → create a new
   access key pair — this is different from the IAM user's keys above, keep them separate.

---

## Part 3 — Custom domain + SSL

1. Lightsail → your container service → **Custom domains** tab → **Create certificate**.
2. Enter both `nexusjazz.com` and `www.nexusjazz.com` on the same certificate.
3. Lightsail gives you one CNAME validation record per domain. Add both at your DNS
   provider (wherever `nexusjazz.com` is registered/hosted) exactly as shown — host and value,
   copy-paste, don't retype.
4. Wait for the certificate to move from "Pending validation" to "Valid" (usually minutes,
   can take longer depending on DNS propagation/TTL). Then **attach** it to the service from
   the same tab.
5. Point the domain itself at the service:
   - `www.nexusjazz.com` → CNAME → the service's default address, shown at the top of the
     container service page (`nexus-jazz.<random>.<region>.cs.amazonlightsail.com`).
   - Root/apex `nexusjazz.com` → most registrars don't allow a CNAME at the bare apex. Use
     whatever ALIAS/ANAME/"CNAME flattening" feature your DNS provider offers pointing at the
     same target, or use Route 53 with an ALIAS record if you move DNS there. If neither is
     available, set up apex→www forwarding at the registrar instead and only truly serve on
     `www`.
6. **Don't delete the raw `*.cs.amazonlightsail.com` URL access** — keep `*.amazonlightsail.com`
   in `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` (already the default from 1.10) so you always have
   a working fallback URL to debug against even if DNS is misbehaving.

---

## Part 4 — GitHub repository secrets

Repo → **Settings → Secrets and variables → Actions**, add:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | From the IAM user in Part 2.5 |
| `AWS_SECRET_ACCESS_KEY` | From the IAM user in Part 2.5 |
| `AWS_REGION` | Must match the Lightsail service's region |
| `DJANGO_SECRET_KEY` | `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` — generate a fresh one, don't reuse the dev one from `.env` |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | From the storage bucket in Part 2.6 |
| `S3_AWS_STORAGE_BUCKET_NAME` | The bucket's name |

Then update `deploy.yml`'s container `environment` block (the same spot SouthernPark's
workflow sets `DJANGO_DEBUG: "0"`) to also inject:
```python
"DJANGO_DEBUG": "0",
"DJANGO_ALLOWED_HOSTS": "nexusjazz.com,www.nexusjazz.com,*.amazonlightsail.com",
"DJANGO_CSRF_TRUSTED_ORIGINS": "https://nexusjazz.com,https://www.nexusjazz.com,https://*.amazonlightsail.com",
```
**This `DJANGO_DEBUG: "0"` line is not optional.** `nexus_jazz/settings.py` defaults `DEBUG`
to `true` if the env var is ever missing — the opposite of the safe default SouthernPark
uses. If this line gets dropped from a future edit to `deploy.yml`, the live site silently
starts running in debug mode (stack traces, `SECRET_KEY` behavior changes, no HSTS/secure
cookies) with no visible warning. Treat it as load-bearing, not a nice-to-have.

---

## Part 5 — First deploy

```bash
git push origin main
```
GitHub Actions builds the two images and deploys to Lightsail automatically. Watch progress
at `github.com/<you>/nexus-jazz/actions`.

**Smoke test once it's live** (raw Lightsail URL first, then the real domain once DNS/cert
are ready):
- `/healthz/` and `/healthcheck` both return 200
- Home page loads with images (confirms `sync_media` pulled from S3, or that the very first
  upload round-trips through the admin and actually appears)
- `/admin/` login works with the seeded `admin@nexusjazz.com` account
- Submit the contact form once, confirm no CSRF 403 (this is the `CSRF_TRUSTED_ORIGINS` check
  from 1.10/Part 4 — if it fails here, that's almost always why)
- 404 page renders correctly for a bad URL
- `robots.txt` and the `X-Robots-Tag` header on `/admin/` are both still in place (added in an
  earlier session — nothing here should touch them, just confirm the deploy didn't regress it)

---

## After go-live: retiring the preview

Once the real domain is live and the client has it, `.github/workflows/bump-preview.yml`
(which pings the portfolio repo to redeploy the unlisted preview) and
`nexus_jazz/settings_preview.py` become optional — decide with the client whether they still
want that unlisted preview URL kept around for staging future changes before they hit
production, or whether to delete both and route all changes straight through the new
`deploy.yml`. Neither file conflicts with the new setup either way; nothing here requires
removing them.

---

## Notes

- First deploy has no S3 backup yet, so `restore_db` is a no-op and the container starts with
  whatever's baked into the image at `git push` time (the current committed `db.sqlite3`,
  including the earlier session's real seeded content). The very first admin save triggers the
  first backup automatically — no manual step needed.
- Estimated cost: ~$7/mo Nano container service + a few cents/mo for the S3 bucket at this
  site's traffic/storage size.
- To move off SQLite entirely later: `DATABASE_URL` is already wired via `dj-database-url` in
  `settings.py` — add a Lightsail managed PostgreSQL database and set that one env var, no
  other code changes needed. Not necessary for launch; SQLite+S3-backup is the same pattern
  already proven in production for SouthernPark.
