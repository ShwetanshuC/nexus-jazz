"""
Settings for hosting this project as an unlisted client demo, mounted at a
random, unpublished path (e.g. /preview/<secret-slug>/) inside the
shwetanshu-portfolio container — see that project's entrypoint.sh and
AWS/nginx/default.conf. Not linked from anywhere public; the actual slug
lives only as a deploy-time secret, never committed to source.

Reuses settings.py's own env-var-driven config (DJANGO_SECRET_KEY,
DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS all already read from the environment
there) — only adds what settings.py has no notion of: mounting under a
subpath.
"""
import os

from .settings import *  # noqa: F401,F403

# Set by entrypoint.sh to "/preview/<slug>" — no trailing slash, matching
# Django's own FORCE_SCRIPT_NAME convention.
FORCE_SCRIPT_NAME = os.environ["PREVIEW_SCRIPT_NAME"]
STATIC_URL = FORCE_SCRIPT_NAME + "/static/"
MEDIA_URL = FORCE_SCRIPT_NAME + "/media/"

ROOT_URLCONF = "nexus_jazz.preview_urls"

CSRF_TRUSTED_ORIGINS = ["https://" + h for h in ALLOWED_HOSTS]
