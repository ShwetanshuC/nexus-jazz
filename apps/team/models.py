from django.db import models
from django.utils.text import slugify


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=120)
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="members"
    )
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    image_focal_y = models.FloatField(default=0.5)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    linkedin_url = models.URLField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return self.name

    @property
    def gallery_photos(self):
        """Every picture of this player, portrait first.

        The band page opens a lightbox on click, so a member with no extra
        photos still needs at least one image: fall back to the portrait.
        """
        return list(self.photos.filter(is_active=True))


class MemberPhoto(models.Model):
    """Additional pictures of one player — the set the band page opens.

    Kept separate from TeamMember.photo (the card portrait) so a member can
    have any number of shots without changing which one fronts the grid.
    """

    member = models.ForeignKey(
        TeamMember, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="team/")
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Member Photo"
        verbose_name_plural = "Member Photos"

    def __str__(self):
        return f"{self.member.name} — photo {self.sort_order}"
