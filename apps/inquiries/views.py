from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactInquiryForm, BookingInquiryForm


def contact(request):
    if request.method == "POST":
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent. We will be in touch soon.")
            return redirect("inquiry_thank_you")
    else:
        form = ContactInquiryForm()
    return render(request, "inquiries/contact.html", {"form": form})


def booking(request):
    from apps.core.models import FAQ

    if request.method == "POST":
        form = BookingInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your booking request has been received. We will be in touch soon.")
            return redirect("inquiry_thank_you")
    else:
        form = BookingInquiryForm()
    faqs = FAQ.objects.filter(is_active=True).order_by("sort_order")
    return render(request, "inquiries/booking.html", {"form": form, "faqs": faqs})


def thank_you(request):
    return render(request, "inquiries/thank_you.html")
