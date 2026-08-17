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
    calendar_url = models.URLField(
        blank=True,
        help_text=(
            "Google Calendar's own “Public URL to this calendar” (Settings and "
            "sharing → Integrate calendar), or just the calendar ID "
            "(name@group.calendar.google.com) — either works."
        ),
    )
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

    @property
    def calendar_embed_src(self):
        """Normalizes whatever was pasted into calendar_url into a real Google
        Calendar embed src — the field accepts either the ready-made embed URL
        or a bare calendar ID, same "accept a few common paste formats"
        approach as gallery.AudioEmbed.embed_url."""
        url = (self.calendar_url or "").strip()
        if not url:
            return ""
        if "calendar.google.com/calendar/embed" in url:
            return url
        if "://" not in url and "@" in url:
            from urllib.parse import quote
            return f"https://calendar.google.com/calendar/embed?src={quote(url, safe='')}&ctz=America%2FNew_York"
        return url


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
