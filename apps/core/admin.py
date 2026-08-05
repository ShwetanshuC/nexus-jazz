import csv

from django.contrib import admin, messages
from django.urls import reverse, path
from django.utils.html import format_html
from django.http import HttpResponse
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
            path("inbox/archive/", self.admin_view(self.inbox_archive_view), name="inbox_archive"),
            path("inbox/archive/export.csv", self.admin_view(self.inbox_archive_csv), name="inbox_archive_csv"),
        ]
        return urls + super().get_urls()

    # -- Inbox helpers -----------------------------------------------------
    # Booking and contact inquiries share every field except a couple
    # (BaseInquiry, apps/inquiries/models.py) — everything below interleaves
    # both querysets into one list instead of making staff check two
    # separate places. "Archive" reuses the existing is_read flag (same
    # pattern as Miller Piano's inbox: unread = inbox, read = archive) rather
    # than adding a second field — one state to keep in sync, not two.
    def _inbox_item(self, obj, kind):
        if kind == "contact":
            kind_label, detail = "Contact", obj.subject or ""
            change_url = reverse("admin:inquiries_contactinquiry_change", args=[obj.pk])
        else:
            kind_label, detail = "Booking", obj.venue or obj.get_event_type_display()
            change_url = reverse("admin:inquiries_bookinginquiry_change", args=[obj.pk])
        return {
            "kind": kind, "kind_label": kind_label, "obj": obj,
            "name": obj.name, "email": obj.email, "submitted_at": obj.submitted_at,
            "is_read": obj.is_read, "detail": detail, "change_url": change_url,
        }

    def _inbox_items(self, *, is_read):
        from apps.inquiries.models import ContactInquiry, BookingInquiry
        items = [self._inbox_item(o, "contact") for o in ContactInquiry.objects.filter(is_read=is_read)]
        items += [self._inbox_item(o, "booking") for o in BookingInquiry.objects.filter(is_read=is_read)]
        items.sort(key=lambda i: i["submitted_at"], reverse=True)
        return items

    def _delete_selected_inbox_items(self, selected_items):
        from apps.inquiries.models import ContactInquiry, BookingInquiry
        deleted_count = 0
        for token in selected_items:
            kind, _, raw_id = (token or "").partition(":")
            try:
                obj_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            model = ContactInquiry if kind == "contact" else BookingInquiry if kind == "booking" else None
            if model is None:
                continue
            deleted, _ = model.objects.filter(pk=obj_id).delete()
            deleted_count += deleted
        return deleted_count

    def _inbox_item_by_kind(self, kind, pk):
        from apps.inquiries.models import ContactInquiry, BookingInquiry
        model = ContactInquiry if kind == "contact" else BookingInquiry
        return get_object_or_404(model, pk=pk)

    # -- Inbox views ---------------------------------------------------------
    def inbox_view(self, request):
        from apps.inquiries.models import ContactInquiry, BookingInquiry

        if request.method == "POST":
            action = (request.POST.get("action") or "").strip().lower()
            kind = (request.POST.get("kind") or "").strip().lower()
            pk = request.POST.get("pk")
            selected_items = request.POST.getlist("selected_items")

            if action == "archive_all":
                n = ContactInquiry.objects.filter(is_read=False).update(is_read=True)
                n += BookingInquiry.objects.filter(is_read=False).update(is_read=True)
                messages.success(request, f"Archived {n} message(s).") if n else messages.info(request, "Inbox is already clear.")
            elif action == "delete_all":
                n, _ = ContactInquiry.objects.filter(is_read=False).delete()
                n2, _ = BookingInquiry.objects.filter(is_read=False).delete()
                total = n + n2
                messages.success(request, f"Deleted {total} unread message(s).") if total else messages.info(request, "No unread messages to delete.")
            elif action == "delete_selected":
                if selected_items:
                    total = self._delete_selected_inbox_items(selected_items)
                    messages.success(request, f"Deleted {total} selected message(s).") if total else messages.info(request, "No selected messages were found.")
                else:
                    messages.info(request, "Select at least one message to delete.")
            elif action == "archive" and pk:
                obj = self._inbox_item_by_kind(kind, pk)
                obj.is_read = True
                obj.save(update_fields=["is_read"])
                messages.success(request, "Message archived.")
            elif action == "delete" and pk:
                self._inbox_item_by_kind(kind, pk).delete()
                messages.success(request, "Message deleted.")
            return redirect("admin:inbox")

        items = self._inbox_items(is_read=False)
        context = {
            **self.each_context(request),
            "title": "Inbox",
            "items": items,
            "unread_count": len(items),
        }
        return render(request, "admin/inbox.html", context)

    def inbox_archive_view(self, request):
        if request.method == "POST":
            action = (request.POST.get("action") or "").strip().lower()
            selected_items = request.POST.getlist("selected_items")
            if action == "delete_selected":
                if selected_items:
                    total = self._delete_selected_inbox_items(selected_items)
                    messages.success(request, f"Deleted {total} selected archived message(s).") if total else messages.info(request, "No selected archived messages were found.")
                else:
                    messages.info(request, "Select at least one archived message to delete.")
            return redirect("admin:inbox_archive")

        items = self._inbox_items(is_read=True)
        context = {
            **self.each_context(request),
            "title": "Inbox Archive",
            "items": items,
            "archived_count": len(items),
        }
        return render(request, "admin/inbox_archive.html", context)

    def inbox_archive_csv(self, request):
        items = self._inbox_items(is_read=True)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="nexus-jazz-inbox-archive.csv"'
        writer = csv.writer(response)
        writer.writerow(["Type", "Received", "Name", "Email", "Detail", "Message"])
        for item in items:
            obj = item["obj"]
            writer.writerow([
                item["kind_label"],
                item["submitted_at"].strftime("%Y-%m-%d %H:%M"),
                item["name"],
                item["email"],
                item["detail"],
                (obj.message or "").strip(),
            ])
        return response


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
        ("Contact", {"fields": ("phone_display", "phone_tel", "email", "address", "hours")}),
        ("Calendar", {"fields": ("calendar_url",)}),
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
