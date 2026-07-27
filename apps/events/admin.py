from django.contrib import admin
from .models import EventCategory, Event


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "date", "start_time", "location", "is_featured", "is_active"]
    list_editable = ["is_featured", "is_active"]
    list_display_links = ["title"]
    list_filter = ["category", "date", "is_featured", "is_active"]
    date_hierarchy = "date"
    search_fields = ["title", "location", "description"]
    prepopulated_fields = {"slug": ("title",)}
