from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import redirect, render, get_object_or_404
from .models import SiteSettings, HeroSlide, FAQ, SiteVisitCounter

# ---------------------------------------------------------------------------
# Custom AdminSite
# ---------------------------------------------------------------------------
class MasterAdminSite(admin.AdminSite):
    site_header = "Site Manager"
    site_title = "Site Manager"
    index_title = "Dashboard"
    # site_url is left at AdminSite's own default ("/"): each_context()
    # already substitutes request.META["SCRIPT_NAME"] whenever site_url is
    # still "/", which is what correctly resolves Django's built-in "View
    # site" link under a subpath mount (e.g. the preview deploy's
    # /preview/<slug>/ via FORCE_SCRIPT_NAME) — no override needed here.

    def each_context(self, request):
        context = super().each_context(request)
        try:
            counter = SiteVisitCounter.objects.first()
            context["site_visit_count"] = counter.total_visits if counter else 0
        except Exception:
            context["site_visit_count"] = 0
        return context

    def get_urls(self):
        urls = [
            path("inbox/", self.admin_view(self.inbox_view), name="inbox"),
            path("inbox/<str:kind>/<int:pk>/toggle-read/", self.admin_view(self.inbox_toggle_read), name="inbox_toggle_read"),
        ]
        return urls + super().get_urls()

    def inbox_view(self, request):
        # Booking and contact inquiries share every field except a couple
        # (BaseInquiry, apps/inquiries/models.py) — this just interleaves
        # both querysets into one list instead of making staff check two
        # separate places (the dashboard "Inbox" card used to link straight
        # to BookingInquiry only, so ContactInquiry submissions were only
        # ever visible via a direct URL — the unread COUNT on the dashboard
        # already combined both, so it looked like inquiries were "missing"
        # whenever a contact-form one came in).
        from apps.inquiries.models import ContactInquiry, BookingInquiry

        items = []
        for obj in ContactInquiry.objects.all():
            items.append({
                "kind": "contact", "kind_label": "Contact", "obj": obj,
                "name": obj.name, "email": obj.email, "submitted_at": obj.submitted_at,
                "is_read": obj.is_read, "detail": obj.subject or "",
                "change_url": reverse("admin:inquiries_contactinquiry_change", args=[obj.pk]),
            })
        for obj in BookingInquiry.objects.all():
            items.append({
                "kind": "booking", "kind_label": "Booking", "obj": obj,
                "name": obj.name, "email": obj.email, "submitted_at": obj.submitted_at,
                "is_read": obj.is_read, "detail": obj.venue or obj.get_event_type_display(),
                "change_url": reverse("admin:inquiries_bookinginquiry_change", args=[obj.pk]),
            })
        items.sort(key=lambda i: i["submitted_at"], reverse=True)

        context = {
            **self.each_context(request),
            "title": "Inbox",
            "items": items,
        }
        return render(request, "admin/inbox.html", context)

    def inbox_toggle_read(self, request, kind, pk):
        from apps.inquiries.models import ContactInquiry, BookingInquiry
        model = ContactInquiry if kind == "contact" else BookingInquiry
        obj = get_object_or_404(model, pk=pk)
        obj.is_read = not obj.is_read
        obj.save(update_fields=["is_read"])
        return redirect("admin:inbox")


# Replace default admin site
admin.site.__class__ = MasterAdminSite
admin.site.site_header = "Site Manager"
admin.site.site_title = "Site Manager"
admin.site.index_title = "Dashboard"


# ---------------------------------------------------------------------------
# SiteSettings admin — singleton redirect
# ---------------------------------------------------------------------------
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("site_name", "tagline")}),
        ("Contact", {"fields": ("phone_display", "phone_tel", "email", "address", "hours", "map_embed_url")}),
        ("Calendar", {"fields": ("calendar_url", "calendar_embed_code")}),
        ("Social Media", {"fields": ("facebook_url", "instagram_url", "youtube_url", "twitter_url", "linkedin_url")}),
        ("Site Alert", {"fields": ("alert_enabled", "alert_message", "alert_color")}),
    )

    def changelist_view(self, request, extra_context=None):
        obj, created = SiteSettings.objects.get_or_create(pk=1)
        return redirect(
            reverse("admin:core_sitesettings_change", args=[obj.pk])
        )


# ---------------------------------------------------------------------------
# HeroSlide
# ---------------------------------------------------------------------------
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["sort_order", "title", "is_active", "image_preview"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["title"]
    ordering = ["sort_order"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;object-fit:cover;border-radius:4px">',
                obj.image.url,
            )
        return "-"
    image_preview.short_description = "Preview"


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["sort_order", "question", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["question"]
    ordering = ["sort_order"]


# ---------------------------------------------------------------------------
# SiteVisitCounter — read-only
# ---------------------------------------------------------------------------
@admin.register(SiteVisitCounter)
class SiteVisitCounterAdmin(admin.ModelAdmin):
    list_display = ["total_visits", "updated_at"]
    readonly_fields = ["total_visits", "updated_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
