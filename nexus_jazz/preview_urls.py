"""
URLconf for the unlisted preview deploy (see settings_preview.py). Same
routes as the real site, plus media file serving even though DEBUG=False —
settings.py only serves /media/ via Django when DEBUG=True (the assumption
being a real production deploy serves media through S3/whitenoise/nginx
instead), but this preview has none of that set up and does need its 52
real seeded photos to actually load for the client. Fine for a low-traffic,
single-client, unlisted demo; not something to do on the real production
site.
"""
import re

from django.urls import re_path
from django.views.static import serve as _serve_static

from . import settings as _base_settings
from .urls import handler404, handler500  # noqa: F401
from .urls import urlpatterns as _base_urlpatterns

# Deliberately not using django.conf.urls.static.static(): it silently
# no-ops whenever settings.DEBUG is False (which it is here), regardless
# of the prefix passed in — so it can't be used to serve media outside
# DEBUG at all. Calling django.views.static.serve directly bypasses that
# gate. The pattern is also built from the *base* (unprefixed) MEDIA_URL
# on purpose: incoming requests are matched against path_info, which is
# always unprefixed (nginx strips /preview/<slug> before forwarding —
# FORCE_SCRIPT_NAME only affects outgoing hrefs, not incoming routing).
_media_prefix = re.escape(_base_settings.MEDIA_URL.lstrip("/"))
urlpatterns = _base_urlpatterns + [
    re_path(rf"^{_media_prefix}(?P<path>.*)$", _serve_static, {"document_root": _base_settings.MEDIA_ROOT}),
]
