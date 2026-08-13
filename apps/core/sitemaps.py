from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import BlogPost
from apps.events.models import Event


class StaticViewSitemap(Sitemap):
    # Fixed pages with no per-object model — priority reflects how central
    # each is to the funnel (home/booking highest, contact/blog index lowest).
    priority_by_name = {
        "home": 1.0,
        "booking": 0.9,
        "team": 0.8,
        "gallery": 0.8,
        "events_index": 0.8,
        "blog_index": 0.6,
        "contact": 0.6,
    }
    changefreq_by_name = {
        "home": "weekly",
        "events_index": "weekly",
        "blog_index": "weekly",
        "team": "monthly",
        "gallery": "monthly",
        "booking": "monthly",
        "contact": "yearly",
    }

    def items(self):
        return list(self.priority_by_name.keys())

    def location(self, name):
        return reverse(name)

    def priority(self, name):
        return self.priority_by_name.get(name, 0.5)

    def changefreq(self, name):
        return self.changefreq_by_name.get(name, "monthly")


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True).order_by("-published_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("blog_detail", args=[obj.slug])


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Event.objects.filter(is_active=True).order_by("date")

    def location(self, obj):
        return reverse("event_detail", args=[obj.slug])
