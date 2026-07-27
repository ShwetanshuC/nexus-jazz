from django import forms
from .models import ContactInquiry, BookingInquiry


class HoneypotMixin:
    """Mixin to add a honeypot field for spam protection."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["website"] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
            label="",
        )

    def clean_website(self):
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value


class ContactInquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email", "class": "form-control"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone (optional)", "class": "form-control"}),
            "subject": forms.TextInput(attrs={"placeholder": "Subject", "class": "form-control"}),
            "message": forms.Textarea(attrs={"placeholder": "Your message", "class": "form-control", "rows": 5}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

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
            "name": forms.TextInput(attrs={"placeholder": "Your name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email", "class": "form-control"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone (optional)", "class": "form-control"}),
            "event_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "event_type": forms.Select(attrs={"class": "form-control"}),
            "venue": forms.TextInput(attrs={"placeholder": "Venue name and city", "class": "form-control"}),
            "message": forms.Textarea(attrs={"placeholder": "Tell us about your event — audience, set length, sound provided…", "class": "form-control", "rows": 5}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_message(self):
        msg = self.cleaned_data.get("message", "").strip()
        if not msg:
            raise forms.ValidationError("Message is required.")
        return msg
