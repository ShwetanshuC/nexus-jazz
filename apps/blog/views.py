from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogTag


def index(request):
    posts = BlogPost.objects.filter(is_published=True).select_related("author", "category")

    category_slug = request.GET.get("category", "")
    tag_slug = request.GET.get("tag", "")

    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "posts": page_obj,
        "categories": BlogCategory.objects.filter(is_active=True),
        "current_category": category_slug,
        "current_tag": tag_slug,
    }
    return render(request, "blog/list.html", context)


def detail(request, slug):
    if request.user.is_staff:
        post = get_object_or_404(BlogPost, slug=slug)
    else:
        post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    context = {"post": post}
    return render(request, "blog/detail.html", context)


def by_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(category=category, is_published=True)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "category": category,
        "page_obj": page_obj,
        "posts": page_obj,
    }
    return render(request, "blog/list.html", context)


def by_tag(request, slug):
    tag = get_object_or_404(BlogTag, slug=slug)
    posts = BlogPost.objects.filter(tags=tag, is_published=True)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "tag": tag,
        "page_obj": page_obj,
        "posts": page_obj,
    }
    return render(request, "blog/list.html", context)
