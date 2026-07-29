from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path("admin/", admin.site.urls),
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

handler404 = "apps.core.views.handler404"
handler500 = "apps.core.views.handler500"
