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
    is_featured = models.BooleanField(
        default=False,
        help_text="Shown in the home page's \"See Us in Action\" section. Check as many as you like.",
    )

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
    is_featured = models.BooleanField(
        default=False,
        help_text="Shown in the home page's \"See Us in Action\" section — the first one checked (by sort order) wins, since that section shows one video.",
    )

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Gallery Video"
        verbose_name_plural = "Gallery Videos"

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        url = self.video_url or ""
        if "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0]
        if "youtube.com/watch" in url:
            from urllib.parse import urlparse, parse_qs
            return parse_qs(urlparse(url).query).get("v", [None])[0]
        if "youtube.com/embed/" in url:
            return url.split("youtube.com/embed/")[-1].split("?")[0]
        return None

    @property
    def watch_url(self):
        """Where the card links out to — plain YouTube/Vimeo watch page.

        Some videos restrict embedding to an approved domain list (a
        Content ID / rights-holder setting, invisible from the oEmbed
        "allow embedding" flag) and throw YouTube's opaque error 153 in
        an iframe. Linking out instead of embedding sidesteps that.
        """
        video_id = self.youtube_id
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return self.video_url

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        video_id = self.youtube_id
        if video_id:
            return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        return ""


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
