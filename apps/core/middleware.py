from __future__ import annotations
import logging
import time
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.functional import SimpleLazyObject

logger = logging.getLogger("nexus_jazz.security")

VISIT_EXCLUDE_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/favicon",
    "/robots.txt",
    "/sitemap.xml",
    "/healthz",
)

THROTTLED_PATHS: dict[str, tuple[int, int]] = {
    "/inquiries/contact/": (5, 60),
    "/inquiries/quote/": (3, 60),
    "/events/subscribe/": (5, 60),
}


def _get_client_ip(request) -> str:
    import os
    trusted = os.environ.get("TRUSTED_PROXY", "")
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff and trusted:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


class PublicVisitCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == "GET" and "text/html" in response.get("Content-Type", ""):
            path = request.path_info
            if not any(path.startswith(p) for p in VISIT_EXCLUDE_PREFIXES):
                try:
                    from django.db.models import F
                    from apps.core.models import SiteVisitCounter
                    from django.db import OperationalError, ProgrammingError
                    try:
                        SiteVisitCounter.objects.update_or_create(
                            pk=1,
                            defaults={},
                        )
                        SiteVisitCounter.objects.filter(pk=1).update(
                            total_visits=F("total_visits") + 1
                        )
                    except (OperationalError, ProgrammingError):
                        pass
                except Exception:
                    pass
        return response


class PublicFormThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST":
            path = request.path_info
            if path in THROTTLED_PATHS:
                max_req, window = THROTTLED_PATHS[path]
                ip = _get_client_ip(request)
                cache_key = f"throttle:{ip}:{path}"
                data = cache.get(cache_key)
                if data is None:
                    cache.set(cache_key, {"count": 1, "start": time.time()}, window)
                else:
                    now = time.time()
                    if now - data["start"] > window:
                        cache.set(cache_key, {"count": 1, "start": now}, window)
                    else:
                        data["count"] += 1
                        if data["count"] > max_req:
                            retry_after = int(window - (now - data["start"]))
                            response = HttpResponse(
                                "Too many requests. Please try again later.",
                                status=429,
                            )
                            response["Retry-After"] = str(retry_after)
                            return response
                        cache.set(cache_key, data, window)
        return self.get_response(request)


class AdminLoginThrottleMiddleware:
    MAX_ATTEMPTS = 10
    WARN_AFTER = 3
    LOCKOUT_SECONDS = 900

    def __init__(self, get_response):
        self.get_response = get_response
        self._connected = False

    def _connect_signals(self):
        if not self._connected:
            from django.contrib.auth.signals import user_login_failed, user_logged_in
            user_login_failed.connect(self._on_failed)
            user_logged_in.connect(self._on_success)
            self._connected = True

    def _cache_key(self, request) -> str:
        ip = _get_client_ip(request)
        session_key = request.session.session_key or ""
        return f"admin_login_attempts:{ip}:{session_key}"

    def _on_failed(self, sender, credentials, request, **kwargs):
        if request is None:
            return
        key = self._cache_key(request)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, self.LOCKOUT_SECONDS)
        logger.warning("Admin login failed attempt #%d from %s", attempts, _get_client_ip(request))

    def _on_success(self, sender, request, user, **kwargs):
        if request is None:
            return
        key = self._cache_key(request)
        cache.delete(key)

    def __call__(self, request):
        self._connect_signals()
        if request.path_info.startswith("/admin/login/") and request.method == "POST":
            key = self._cache_key(request)
            attempts = cache.get(key, 0)
            if attempts >= self.MAX_ATTEMPTS:
                from django.contrib import messages
                remaining = self.LOCKOUT_SECONDS
                return HttpResponse(
                    f"Too many failed login attempts. Try again in {remaining // 60} minutes.",
                    status=429,
                )
            if attempts >= self.WARN_AFTER:
                from django.contrib import messages
                remaining = self.MAX_ATTEMPTS - attempts
                try:
                    messages.warning(
                        request,
                        f"Warning: {attempts} failed login attempts. "
                        f"{remaining} attempt(s) remaining before lockout.",
                    )
                except Exception:
                    pass
        return self.get_response(request)
