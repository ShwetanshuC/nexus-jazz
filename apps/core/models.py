from django.db import models
from colorfield.fields import ColorField


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="My Business")
    tagline = models.CharField(max_length=300, blank=True)
    phone_display = models.CharField(max_length=50, blank=True)
    phone_tel = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    hours = models.TextField(blank=True)
    map_embed_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    alert_enabled = models.BooleanField(default=False)
    alert_message = models.CharField(max_length=160, blank=True)
    alert_color = ColorField(default="#C44444")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce singleton: only keep one row
        if not self.pk and SiteSettings.objects.exists():
            existing = SiteSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)


class HeroSlide(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="site/hero/")
    mobile_image = models.ImageField(upload_to="site/hero/mobile/", blank=True, null=True)
    image_focal_y = models.FloatField(default=0.5, help_text="0=top 1=bottom")
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"

    def __str__(self):
        return self.title


class FeaturedBrand(models.Model):
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to="site/brands/")
    logo_color = ColorField(default="#000000")
    website_url = models.URLField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Featured Brand"
        verbose_name_plural = "Featured Brands"

    def __str__(self):
        return self.name


class HomeSectionCard(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to="site/cards/", blank=True, null=True)
    link_url = models.CharField(max_length=255)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Home Section Card"
        verbose_name_plural = "Home Section Cards"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class SiteVisitCounter(models.Model):
    total_visits = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Visit Counter"
        verbose_name_plural = "Site Visit Counter"

    def __str__(self):
        return f"Total visits: {self.total_visits}"
