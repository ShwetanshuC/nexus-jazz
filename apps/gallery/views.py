from django.shortcuts import render
from .models import GalleryPhoto, GalleryVideo, AudioEmbed


def gallery(request):
    photos = GalleryPhoto.objects.filter(is_active=True)
    videos = GalleryVideo.objects.filter(is_active=True)
    audio = AudioEmbed.objects.filter(is_active=True)
    context = {"photos": photos, "videos": videos, "audio_embeds": audio}
    return render(request, "gallery/gallery.html", context)
