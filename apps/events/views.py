from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Event, EventCategory


def index(request):
    today = timezone.now().date()
    upcoming = Event.objects.filter(date__gte=today, is_active=True).order_by("date")
    featured = Event.objects.filter(is_featured=True, is_active=True).first()
    categories = EventCategory.objects.all()
    context = {
        "upcoming_events": upcoming,
        "featured_event": featured,
        "categories": categories,
    }
    return render(request, "events/list.html", context)


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
