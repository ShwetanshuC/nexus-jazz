from django.db import models


class GalleryPhoto(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="gallery/photos/")
    image_focal_y = models.FloatField(default=0.5)
    mobile_image = models.ImageField(upload_to="gallery/mobile/", blank=True, null=True)
    mobile_focal_y = models.FloatField(default=0.5)
    caption = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Gallery Photo"
        verbose_name_plural = "Gallery Photos"

    def __str__(self):
        return self.title or f"Photo #{self.pk}"


class GalleryVideo(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField(help_text="YouTube or Vimeo URL")
    thumbnail = models.ImageField(upload_to="gallery/thumbnails/", blank=True, null=True)
    caption = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Gallery Video"
        verbose_name_plural = "Gallery Videos"

    def __str__(self):
        return self.title

    @property
    def embed_url(self):
        url = self.video_url
        if not url:
            return url
        # Handle youtu.be shortlinks
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        # Handle youtube.com/watch?v=
        if "youtube.com/watch" in url:
            return url.replace("watch?v=", "embed/").split("&")[0].replace(
                "www.youtube.com/embed/", "www.youtube-nocookie.com/embed/"
            )
        # Handle youtube.com/embed/ links (including pasted embed codes)
        if "youtube.com/embed/" in url and "youtube-nocookie.com" not in url:
            return url.replace("www.youtube.com/embed/", "www.youtube-nocookie.com/embed/")
        # Handle Vimeo
        if "vimeo.com/" in url:
            video_id = url.rstrip("/").split("/")[-1]
            return f"https://player.vimeo.com/video/{video_id}"
        return url


class AudioEmbed(models.Model):
    title = models.CharField(max_length=200)
    audio_url = models.URLField(
        blank=True,
        help_text="Spotify or SoundCloud link — the player is generated automatically",
    )
    embed_code = models.TextField(
        blank=True,
        help_text="Bandcamp (or other) embed iframe — used when a plain link is not enough",
    )
    caption = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Audio Embed"
        verbose_name_plural = "Audio Embeds"

    def __str__(self):
        return self.title

    @property
    def embed_url(self):
        url = self.audio_url
        if not url:
            return url
        # Spotify: open.spotify.com/<kind>/<id> → open.spotify.com/embed/<kind>/<id>
        if "open.spotify.com/" in url and "/embed/" not in url:
            return url.replace("open.spotify.com/", "open.spotify.com/embed/").split("?")[0]
        # SoundCloud: wrap in the standard player
        if "soundcloud.com/" in url and "w.soundcloud.com" not in url:
            from urllib.parse import quote
            return f"https://w.soundcloud.com/player/?url={quote(url, safe='')}&color=%23b08a3e&inverse=true"
        return url
