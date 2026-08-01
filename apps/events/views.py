from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Event


def index(request):
    # The schedule is a Google Calendar embed now (SiteSettings.calendar_url /
    # calendar_embed_code, via the site_settings context processor) — nothing
    # from the Event model to query here anymore.
    return render(request, "events/list.html")


def detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_active=True)
    return render(request, "events/detail.html", {"event": event})


@require_POST
def subscribe(request):
    email = request.POST.get("email", "").strip()
    if not email or "@" not in email:
        return JsonResponse({"success": False, "error": "Please enter a valid email address."}, status=400)
    # In a real project: save to a newsletter/subscriber model or send to a service.
    # Here we just acknowledge the submission.
    return JsonResponse({"success": True, "message": "Thank you! You have been subscribed to event notifications."})
