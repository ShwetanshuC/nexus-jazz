from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="events_index"),
    path("subscribe/", views.subscribe, name="events_subscribe"),
    path("<slug:slug>/", views.detail, name="event_detail"),
]
