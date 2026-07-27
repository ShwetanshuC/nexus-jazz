from django.db import models


class BaseInquiry(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class ContactInquiry(BaseInquiry):
    subject = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ["-submitted_at"]


class BookingInquiry(BaseInquiry):
    EVENT_TYPES = [
        ("club", "Club / venue"),
        ("private", "Private event"),
        ("wedding", "Wedding"),
        ("corporate", "Corporate event"),
        ("festival", "Festival"),
        ("other", "Other"),
    ]

    event_date = models.DateField(
        null=True, blank=True, help_text="Requested performance date"
    )
    event_type = models.CharField(
        max_length=20, choices=EVENT_TYPES, default="private"
    )
    venue = models.CharField(
        max_length=255, blank=True, help_text="Venue name and city"
    )

    class Meta:
        verbose_name = "Booking Inquiry"
        verbose_name_plural = "Booking Inquiries"
        ordering = ["-submitted_at"]
