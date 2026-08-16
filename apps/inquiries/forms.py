import re

from django import forms

from .models import ContactInquiry, BookingInquiry

MAX_NAME_LENGTH = 80
MAX_EMAIL_LENGTH = 254
MAX_PHONE_LENGTH = 14  # e.g. "(704) 555-1234"
MAX_SUBJECT_LENGTH = 150
MAX_VENUE_LENGTH = 150
MAX_MESSAGE_LENGTH = 1200


def _validate_phone(value: str) -> str:
    """Strip formatting and require exactly 10 digits when a value is provided."""
    if not value:
        return value
    digits = re.sub(r"\D", "", value)
    if len(digits) != 10:
        raise forms.ValidationError("Please enter a valid 10-digit US phone number (e.g. (704) 555-1234).")
    return value


class HoneypotMixin:
    """Bot bait: a plain text field, visually hidden off-screen (not a
    type=hidden input — unsophisticated bots that skip hidden inputs still
    fill this one). A human never sees or fills it. Filling it does NOT
    fail form validation (a bot watching for a rejected submission would
    just adapt) — is_spam_submission() lets the view accept-and-discard
    instead, so the bot gets an identical "success" response either way."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["website"] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "aria-hidden": "true",
                "class": "hp-field",
            }),
            label="",
        )

    def is_spam_submission(self) -> bool:
        return bool((self.cleaned_data.get("website") or "").strip())


class ContactInquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name", "class": "form-control", "maxlength": MAX_NAME_LENGTH}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email", "class": "form-control", "maxlength": MAX_EMAIL_LENGTH}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone (optional)", "class": "form-control", "maxlength": MAX_PHONE_LENGTH}),
            "subject": forms.TextInput(attrs={"placeholder": "Subject", "class": "form-control", "maxlength": MAX_SUBJECT_LENGTH}),
            "message": forms.Textarea(attrs={"placeholder": "Your message", "class": "form-control", "rows": 5, "maxlength": MAX_MESSAGE_LENGTH}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].max_length = MAX_NAME_LENGTH
        self.fields["email"].max_length = MAX_EMAIL_LENGTH
        self.fields["phone"].max_length = MAX_PHONE_LENGTH
        self.fields["subject"].max_length = MAX_SUBJECT_LENGTH
        self.fields["message"].max_length = MAX_MESSAGE_LENGTH

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_phone(self):
        return _validate_phone(self.cleaned_data.get("phone", ""))

    def clean_message(self):
        msg = self.cleaned_data.get("message", "").strip()
        if not msg:
            raise forms.ValidationError("Message is required.")
        return msg


class BookingInquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = BookingInquiry
        fields = ["name", "email", "phone", "event_date", "event_type", "venue", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name", "class": "form-control", "maxlength": MAX_NAME_LENGTH}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email", "class": "form-control", "maxlength": MAX_EMAIL_LENGTH}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone (optional)", "class": "form-control", "maxlength": MAX_PHONE_LENGTH}),
            "event_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "event_type": forms.Select(attrs={"class": "form-control"}),
            "venue": forms.TextInput(attrs={"placeholder": "Venue name and city", "class": "form-control", "maxlength": MAX_VENUE_LENGTH}),
            "message": forms.Textarea(attrs={"placeholder": "Tell us about your event — audience, set length, sound provided…", "class": "form-control", "rows": 5, "maxlength": MAX_MESSAGE_LENGTH}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].max_length = MAX_NAME_LENGTH
        self.fields["email"].max_length = MAX_EMAIL_LENGTH
        self.fields["phone"].max_length = MAX_PHONE_LENGTH
        self.fields["venue"].max_length = MAX_VENUE_LENGTH
        self.fields["message"].max_length = MAX_MESSAGE_LENGTH

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_phone(self):
        return _validate_phone(self.cleaned_data.get("phone", ""))

    def clean_message(self):
        msg = self.cleaned_data.get("message", "").strip()
        if not msg:
            raise forms.ValidationError("Message is required.")
        return msg
