import datetime
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from colorfield.fields import ColorField


class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    color = ColorField(default="#4f46e5")

    class Meta:
        ordering = ["name"]
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        EventCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    image_focal_y = models.FloatField(default=0.5)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Leave blank for free"
    )
    ticket_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_featured:
            Event.objects.exclude(pk=self.pk).update(is_featured=False)
        super().save(*args, **kwargs)

    @property
    def is_free(self):
        return self.price is None or self.price == 0

    @property
    def is_past(self):
        return self.date < timezone.now().date()
