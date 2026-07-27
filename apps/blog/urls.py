from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="blog_index"),
    path("category/<slug:slug>/", views.by_category, name="blog_by_category"),
    path("tag/<slug:slug>/", views.by_tag, name="blog_by_tag"),
    path("<slug:slug>/", views.detail, name="blog_detail"),
]
