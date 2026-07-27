from django import template
from django.db.utils import OperationalError, ProgrammingError

register = template.Library()


@register.simple_tag
def site_stats():
    try:
        from apps.core.models import SiteVisitCounter
        from apps.inquiries.models import ContactInquiry, BookingInquiry
        from apps.blog.models import BlogPost
        from apps.events.models import Event
        from apps.gallery.models import GalleryPhoto

        unread = 0
        for Model in (ContactInquiry, BookingInquiry):
            try:
                unread += Model.objects.filter(is_read=False).count()
            except Exception:
                pass

        try:
            visitor_total = (
                SiteVisitCounter.objects
                .filter(pk=1)
                .values_list("total_visits", flat=True)
                .first() or 0
            )
        except (OperationalError, ProgrammingError):
            visitor_total = 0

        blog_count = BlogPost.objects.filter(is_published=True).count()
        event_count = Event.objects.count()
        photo_count = GalleryPhoto.objects.filter(is_active=True).count()

        return {
            "inquiries": unread,
            "inbox_unread": unread,
            "visitors": visitor_total,
            "blog_posts": blog_count,
            "events": event_count,
            "photos": photo_count,
        }
    except Exception:
        return {
            "inquiries": 0,
            "inbox_unread": 0,
            "visitors": 0,
            "blog_posts": 0,
            "events": 0,
            "photos": 0,
        }
