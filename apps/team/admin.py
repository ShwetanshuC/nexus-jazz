from django.contrib import admin
from django.utils.html import format_html
from .models import Department, TeamMember, MemberPhoto


class MemberPhotoInline(admin.TabularInline):
    """Every picture of a player, edited on the player's own page.

    These are what the band page's lightbox opens; TeamMember.photo stays the
    single portrait that fronts the grid card.
    """

    model = MemberPhoto
    extra = 3
    fields = ["preview", "image", "caption", "sort_order", "is_active"]
    readonly_fields = ["preview"]
    ordering = ["sort_order", "id"]

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:64px;width:64px;object-fit:cover">',
                obj.image.url,
            )
        return "—"
    preview.short_description = "Preview"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["sort_order", "name"]
    list_editable = ["sort_order"]
    list_display_links = ["name"]
    ordering = ["sort_order", "name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["photo_thumbnail", "name", "role", "department", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["name"]
    list_filter = ["department", "is_active"]
    search_fields = ["name", "role", "bio"]
    ordering = ["sort_order", "name"]
    inlines = [MemberPhotoInline]

    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:50%">',
                obj.photo.url,
            )
        return format_html('<span style="color:#ccc">No photo</span>')
    photo_thumbnail.short_description = "Photo"
