from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryPhoto, GalleryVideo, AudioEmbed


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ["sort_order", "title_display", "photo_thumb", "is_active", "is_featured"]
    list_editable = ["sort_order", "is_active", "is_featured"]
    list_display_links = ["title_display"]
    ordering = ["sort_order"]

    def title_display(self, obj):
        return obj.title or f"Photo #{obj.pk}"
    title_display.short_description = "Title"

    def photo_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;object-fit:cover;border-radius:4px">',
                obj.image.url,
            )
        return "-"
    photo_thumb.short_description = "Preview"


@admin.register(GalleryVideo)
class GalleryVideoAdmin(admin.ModelAdmin):
    list_display = ["sort_order", "title", "video_url", "is_active", "is_featured"]
    list_editable = ["sort_order", "is_active", "is_featured"]
    list_display_links = ["title"]
    ordering = ["sort_order"]


@admin.register(AudioEmbed)
class AudioEmbedAdmin(admin.ModelAdmin):
    list_display = ["sort_order", "title", "audio_url", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["title"]
    ordering = ["sort_order"]
