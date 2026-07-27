import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import ContactInquiry, BookingInquiry


def export_as_csv(modeladmin, request, queryset):
    """Generic CSV export action."""
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={meta.verbose_name_plural}.csv"

    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_csv.short_description = "Export selected to CSV"


class BaseInquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "submitted_at", "is_read"]
    list_editable = ["is_read"]
    list_display_links = ["name"]
    list_filter = ["is_read"]
    search_fields = ["name", "email", "message"]
    actions = [export_as_csv]
    readonly_fields = ["submitted_at"]


@admin.register(ContactInquiry)
class ContactInquiryAdmin(BaseInquiryAdmin):
    list_display = ["name", "email", "subject", "submitted_at", "is_read"]


@admin.register(BookingInquiry)
class BookingInquiryAdmin(BaseInquiryAdmin):
    list_display = ["name", "email", "event_date", "event_type", "venue", "submitted_at", "is_read"]
    list_filter = ["is_read", "event_type", "event_date"]
