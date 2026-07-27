"""Cache-busted static URLs.

Django's dev static server sends only Last-Modified — no ETag, no Cache-Control
— so browsers fall back to *heuristic* caching and can serve a stale CSS file
for hours while templates keep updating server-side. That looks exactly like
"the styles are broken": new markup, old stylesheet.

`{% static_v 'css/nexus.css' %}` appends the file's mtime as a query string, so
the URL changes the moment the file does. In production the manifest storage
already fingerprints names; the extra parameter is harmless there.
"""

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from pathlib import Path
import os

register = template.Library()


@register.simple_tag
def static_v(path):
    url = static(path)
    try:
        found = finders.find(path)
        if found:
            stamp = int(os.path.getmtime(Path(found)))
            sep = "&" if "?" in url else "?"
            return f"{url}{sep}v={stamp}"
    except Exception:
        pass
    return url
