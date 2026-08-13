from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve as _serve_static

from apps.core.views import robots_txt
from apps.core.sitemaps import StaticViewSitemap, BlogPostSitemap, EventSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogPostSitemap,
    "events": EventSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("apps.core.urls")),
    path("blog/", include("apps.blog.urls")),
    path("media/", include("apps.gallery.urls")),
    path("events/", include("apps.events.urls")),
    path("band/", include("apps.team.urls")),
    path("inquiries/", include("apps.inquiries.urls")),
    path("healthz/", lambda r: HttpResponse("ok")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production (Lightsail): nginx's /media/ location falls back to Django
    # (@media_proxy) whenever a file isn't already on the container's local
    # disk — this route is what answers that fallback. Placed after the
    # patterns above, same as the DEBUG-only `static()` helper is appended
    # above: apps.gallery.urls only matches the bare "/media/" page itself,
    # so any non-empty remainder (an actual file path) falls through to here.
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", _serve_static, {"document_root": settings.MEDIA_ROOT}),
    ]

handler404 = "apps.core.views.handler404"
handler500 = "apps.core.views.handler500"
