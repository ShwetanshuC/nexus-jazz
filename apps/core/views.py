from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    from .models import HeroSlide, FeaturedBrand, HomeSectionCard, FAQ
    context = {}
    try:
        context["hero_slides"] = list(HeroSlide.objects.filter(is_active=True).order_by("sort_order"))
    except Exception:
        context["hero_slides"] = []
    # Hero picture: one full-bleed portrait (the formal band lineup, gallery
    # title "The full lineup") that fades up on the last announced line.
    # Falls back to the first active photo, then to the HeroSlide image.
    try:
        from apps.gallery.models import GalleryPhoto
        gp = list(GalleryPhoto.objects.filter(is_active=True).order_by("sort_order"))
        feature = next((p for p in gp if p.title == "The full lineup"), None)
        if feature is None and gp:
            feature = gp[0]
        context["hero_feature"] = feature
        # About section's mobile-only photo swap (see home.html): needs a shot
        # that's already close to the card's narrow portrait aspect, so the
        # crop doesn't lose band members off the sides the way the wide
        # "full lineup" hero shot did (2026-07-28, user report — two of five
        # were cropped out entirely on a phone).
        context["about_mobile_photo"] = next(
            (p for p in gp if p.title == "Backstage, before the set"), feature
        )
    except Exception:
        context["hero_feature"] = None
        context["about_mobile_photo"] = None
    try:
        context["featured_brands"] = list(FeaturedBrand.objects.filter(is_active=True).order_by("sort_order"))
    except Exception:
        context["featured_brands"] = []
    try:
        context["section_cards"] = list(HomeSectionCard.objects.filter(is_active=True).order_by("sort_order"))
    except Exception:
        context["section_cards"] = []
    # Featured news: the six most recent published posts, shown as covers.
    try:
        from apps.blog.models import BlogPost
        context["featured_posts"] = list(
            BlogPost.objects.filter(is_published=True)
            .select_related("category")[:6]
        )
    except Exception:
        context["featured_posts"] = []
    try:
        from django.utils import timezone
        from apps.events.models import Event
        context["upcoming_events"] = list(
            Event.objects.filter(date__gte=timezone.now().date(), is_active=True).order_by("date")[:3]
        )
    except Exception:
        context["upcoming_events"] = []
    return render(request, "core/home.html", context)


def handler404(request, exception=None):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
