from django.contrib import admin
from .models import BlogCategory, BlogTag, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author", "is_published", "published_at", "reading_time"]
    list_filter = ["is_published", "category", "tags"]
    search_fields = ["title", "body", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    filter_horizontal = ["tags"]
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "category", "tags")}),
        ("Content", {"fields": ("featured_image", "image_focal_y", "excerpt", "body")}),
        ("Publishing", {"fields": ("is_published", "published_at")}),
        ("SEO", {"fields": ("meta_description", "meta_keywords"), "classes": ("collapse",)}),
    )
    readonly_fields = ["reading_time"]
