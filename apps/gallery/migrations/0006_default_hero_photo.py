# Backfills is_hero to match the previous hardcoded "The full lineup" title
# match, so this migration doesn't visibly change the live homepage the
# moment it deploys — admins can then repoint it via the admin checkbox.
from django.db import migrations


def set_default_hero(apps, schema_editor):
    GalleryPhoto = apps.get_model("gallery", "GalleryPhoto")
    GalleryPhoto.objects.filter(title="The full lineup").update(is_hero=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0005_galleryphoto_is_hero'),
    ]

    operations = [
        migrations.RunPython(set_default_hero, noop),
    ]
