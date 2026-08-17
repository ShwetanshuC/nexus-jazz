from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    from .models import HeroSlide
    context = {}
    try:
        context["hero_slides"] = list(HeroSlide.objects.filter(is_active=True).order_by("sort_order"))
    except Exception:
        context["hero_slides"] = []
    # Hero picture: one full-bleed portrait that fades up on the last
    # announced line. Admin picks it via GalleryPhoto.is_hero (desktop) /
    # is_hero_mobile (phones) — falls back to the first active photo, then
    # to the HeroSlide image.
    try:
        from apps.gallery.models import GalleryPhoto
        gp = list(GalleryPhoto.objects.filter(is_active=True).order_by("sort_order"))
        feature = next((p for p in gp if p.is_hero), None)
        if feature is None and gp:
            feature = gp[0]
        context["hero_feature"] = feature
        context["hero_feature_mobile"] = next((p for p in gp if p.is_hero_mobile), None)
        # About section's mobile-only photo swap (see home.html): needs a shot
        # that's already close to the card's narrow portrait aspect, so the
        # crop doesn't lose band members off the sides the way the wide
        # "full lineup" hero shot did (2026-07-28, user report — two of five
        # were cropped out entirely on a phone).
        context["about_mobile_photo"] = next(
            (p for p in gp if p.title == "Backstage, before the set"), feature
        )
        # "See Us in Action" section: whichever gallery photos/video are
        # marked featured in the admin. None marked = section just shows
        # heading + button, no broken layout.
        context["featured_photos"] = list(
            GalleryPhoto.objects.filter(is_active=True, is_featured=True).order_by("sort_order")[:5]
        )
        from apps.gallery.models import GalleryVideo
        context["featured_video"] = (
            GalleryVideo.objects.filter(is_active=True, is_featured=True).order_by("sort_order").first()
        )
    except Exception:
        context["hero_feature"] = None
        context["hero_feature_mobile"] = None
        context["about_mobile_photo"] = None
        context["featured_photos"] = []
        context["featured_video"] = None
    # Featured blog posts: the six most recent published posts, shown as covers.
    try:
        from apps.blog.models import BlogPost
        context["featured_posts"] = list(
            BlogPost.objects.filter(is_published=True)
            .select_related("category")[:6]
        )
    except Exception:
        context["featured_posts"] = []
    return render(request, "core/home.html", context)


def robots_txt(request):
    # Keeps the admin (and its login page) out of search results and off
    # crawlers' radar — it's a private, password-protected content-management
    # area, not a public page. Search engines that already indexed a URL
    # from before this existed can still show it until they recrawl and see
    # the Disallow; the X-Robots-Tag header on every /admin/ response
    # (AdminNoindexMiddleware) additionally tells any bot NOT to index a page
    # it does fetch, which is the belt to this robots.txt suspenders.
    sitemap_url = f"{request.scheme}://{request.get_host()}/sitemap.xml"
    lines = ["User-agent: *", "Disallow: /admin/", "", f"Sitemap: {sitemap_url}"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def handler404(request, exception=None):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
