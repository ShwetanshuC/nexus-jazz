from django.urls import path
from . import views

urlpatterns = [
    path("contact/", views.contact, name="contact"),
    path("booking/", views.booking, name="booking"),
    path("thank-you/", views.thank_you, name="inquiry_thank_you"),
]
