from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from .models import SiteSettings, HeroSlide, FAQ, SiteVisitCounter

# ---------------------------------------------------------------------------
# Custom AdminSite
# ---------------------------------------------------------------------------
class MasterAdminSite(admin.AdminSite):
    site_header = "Site Manager"
    site_title = "Site Manager"
    index_title = "Dashboard"

    def each_context(self, request):
        context = super().each_context(request)
        try:
            counter = SiteVisitCounter.objects.first()
            context["site_visit_count"] = counter.total_visits if counter else 0
        except Exception:
            context["site_visit_count"] = 0
        return context


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
