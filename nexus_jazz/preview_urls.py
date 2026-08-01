"""
URLconf for the unlisted preview deploy (see settings_preview.py).

Historically this added its own unconditional /media/ serving route on top
of the base urlconf, because settings.py only served media via Django when
DEBUG=True. nexus_jazz/urls.py now serves media unconditionally whenever
DEBUG is False too (added for the real Lightsail production deploy, which
also needs it — see AWS_DEPLOY_GUIDE.md), so the base urlpatterns already
cover what this module used to add by hand. Kept as a thin re-export, not
deleted outright, so settings_preview.py's ROOT_URLCONF doesn't need to
change.
"""
from .urls import handler404, handler500, urlpatterns  # noqa: F401
