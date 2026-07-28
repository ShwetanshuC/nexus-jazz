"""
Seed command — Nexus Jazz content.
Run with: python manage.py seed

Bio copy, contact info, and the press-* photos in media/seed/ come from the
group's 2025 media kit. Member names and bios (2026-07-23 update) come from
the band's own info sheet — Trombone has no name, bio, or photo in anything
supplied yet, so that chair stays "To be announced". Upcoming Event dates
remain SAMPLE placeholders (no future tour dates were provided) — replace
via the admin.
"""
import datetime
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

SEED_DIR = Path(__file__).resolve().parents[4] / "media" / "seed"


def attach(instance, field, filename):
    src = SEED_DIR / filename
    if src.exists() and not getattr(instance, field):
        with open(src, "rb") as fh:
            getattr(instance, field).save(filename, File(fh), save=True)


class Command(BaseCommand):
    help = "Seed the database with Nexus Jazz sample data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # ---------------------------------------------------------------
        # SiteSettings
        # ---------------------------------------------------------------
        from apps.core.models import SiteSettings
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = "Nexus Jazz Group"
        settings.tagline = "Sometimes earthy, sometimes bluesy, always progressive."
        settings.email = "keenan@nexusjazz.com"
        settings.phone_display = "(803) 487-3696"
        settings.phone_tel = "+18034873696"
        settings.address = "Charlotte, NC"
        settings.instagram_url = "https://www.instagram.com/nexusjazzgroup/"
        settings.save()
        self.stdout.write(self.style.SUCCESS("  SiteSettings"))

        # ---------------------------------------------------------------
        # Hero slide — the band against the mural wall
        # ---------------------------------------------------------------
        from apps.core.models import HeroSlide
        if not HeroSlide.objects.exists():
            slide = HeroSlide.objects.create(
                title="Nexus Jazz Group",
                subtitle="Five musicians, one book of original music — sometimes earthy, sometimes bluesy, always progressive.",
                cta_label="Hear the Band",
                cta_url="/media/",
                image_focal_y=0.18,
                sort_order=0,
            )
            attach(slide, "image", "hero-negspace.jpg")
        self.stdout.write(self.style.SUCCESS("  HeroSlide"))

        # ---------------------------------------------------------------
        # FAQs — booking questions
        # ---------------------------------------------------------------
        from apps.core.models import FAQ
        faqs = [
            ("What kind of events does the group play?",
             "Clubs and listening rooms, festivals, weddings, private and corporate events. "
             "The set is shaped to the room — from a trio up to the full five-piece band."),
            ("How far will the band travel?",
             "The group is based in Charlotte, NC and regularly performs across the Carolinas. "
             "Travel farther afield is happily considered — just ask in the booking form."),
            ("Do you provide your own sound?",
             "Yes — the band can be fully self-contained for small and mid-size rooms, "
             "or work with your production team at larger venues."),
        ]
        for i, (q, a) in enumerate(faqs):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "sort_order": i})
        self.stdout.write(self.style.SUCCESS("  FAQs"))

        # ---------------------------------------------------------------
        # The band — FIVE players. Bios are the client's own words, pasted
        # verbatim (user, 2026-07-27: "use exactly the text I provide for their
        # bios, nothing more"). Do not rewrite, tighten or extend them.
        # Keenan Harmon (bandleader) and the TBA trombone chair are NOT seeded:
        # the client said the group is five, not seven.
        # ---------------------------------------------------------------
        from apps.team.models import TeamMember, Department
        dept, _ = Department.objects.get_or_create(
            name="The Band", defaults={"slug": "the-band"}
        )
        members = [
            ("Rich Graham", "Saxophone · Flute · Clarinet",
             "Sax, flute, clarinet, and nearly any other woodwind are Rich Graham’s specialty. He "
             "studied clarinet at New England Conservatory and aside from actively performing in "
             "many musical theatre shows, he is a clarinetist with the Salisbury Symphony.",
             "press-rich-portrait.png"),
            ("Casey Mink", "Violin",
             "Violinist Casey Mink enjoys balancing his love for performing violin literature and "
             "repertoire, with pedagogy. He performs all styles and is an avid Suzuki teacher. Aside "
             "from having performed recitals in both Montreal and in the Baltic region, he also "
             "performs with the Roanoke Symphony, the South Carolina Philharmonic.",
             "press-violin.jpg"),
            ("Leo Gayosso", "Bass",
             "Bassist Leo Gayosso is like the rest of the band with Nexus, at home in nearly any "
             "environment. A sultry upright player and savvy electric player-frets or fretless. He is "
             "also quite the trained pianist. Leo also plays with the band Matthews and Company.",
             "press-bass.jpg"),
            ("Evan Corey", "Drums · Percussion",
             "Drummer and percussionist Evan Corey has done everything from percussion "
             "ensemble to polka band to perform with the Charlotte Symphony. A former student of "
             "Rick Dior, Evan has a dynamic touch, both remarkably light and rousingly symphonic "
             "when the moment calls for it.",
             "press-drums.jpg"),
            ("Denise Harding", "Piano & Keys",
             "The gifted and quiet Denise Harding. Former student of Eugene Barban and graduate "
             "of Berklee School of Music (Boston Campus), she has an incredible touch with a "
             "“singing sound” and a very natural improviser. At home to virtually any environment and "
             "nearly any set of keys: upright, grand, or electronic.",
             ""),
        ]
        for i, (name, role, bio, photo) in enumerate(members):
            member, _ = TeamMember.objects.get_or_create(
                name=name,
                defaults={"role": role, "bio": bio, "department": dept, "sort_order": i},
            )
            if photo:
                attach(member, "photo", photo)
        self.stdout.write(self.style.SUCCESS("  5 band members (photos where available)"))

        # ---------------------------------------------------------------
        # Events — sample Charlotte dates
        # ---------------------------------------------------------------
        from apps.events.models import Event, EventCategory
        cat_live, _ = EventCategory.objects.get_or_create(
            name="Live", defaults={"slug": "live"}
        )
        today = timezone.now().date()
        events = [
            ("An Evening with Nexus Jazz Group", 18, "19:30", "Middle C Jazz, Charlotte NC",
             "A full evening of original music — two sets in Charlotte's premier listening room. (Sample event.)", True),
            ("Nexus Jazz Group — Summer Series", 39, "20:00", "The Evening Muse, Charlotte NC",
             "The group returns to NoDa with new material from the upcoming record. (Sample event.)", False),
            ("Festival Set", 74, "17:00", "Uptown Charlotte — Festival Stage",
             "An outdoor festival set — the full five-piece band. (Sample event.)", False),
        ]
        for title, days, start, location, desc, featured in events:
            if not Event.objects.filter(title=title).exists():
                Event.objects.create(
                    title=title,
                    slug=slugify(title),
                    category=cat_live,
                    date=today + datetime.timedelta(days=days),
                    start_time=start,
                    location=location,
                    description=desc,
                    is_active=True,
                    is_featured=featured,
                )
        self.stdout.write(self.style.SUCCESS("  3 events (sample)"))

        # ---------------------------------------------------------------
        # News
        # ---------------------------------------------------------------
        from apps.blog.models import BlogPost, BlogCategory
        from apps.accounts.models import User
        cat_news, _ = BlogCategory.objects.get_or_create(
            name="News", defaults={"slug": "news", "is_active": True}
        )
        author = User.objects.filter(is_superuser=True).first()
        posts = [
            ("On Stage at Blumenthal Arts",
             "The group brought its original book to the Stagedoor Theater — and will return for an album release concert.",
             "Formed in 2019 by Keenan Harmon for his original music, the Nexus Jazz Group has "
             "performed throughout the Charlotte region in settings from breweries and clubs to "
             "Huntersville's Jazz Appreciation Festival to a full-length concert at Blumenthal "
             "Arts' Stagedoor Theater. The band returns to the Stagedoor Theater for an album "
             "release concert — drawing from the members' collectively diverse backgrounds, from "
             "R&B to rock to bluegrass to symphonic music, brought together as the Nexus Jazz Group."),
            ("In the Studio",
             "The group has been tracking new material — a first listen is coming soon.",
             "Sessions are underway for the group's next recording, set for release around the "
             "band's return to Blumenthal Arts' Stagedoor Theater. Audio will land on the Music "
             "& Media page the moment it's ready."),
        ]
        for title, excerpt, body in posts:
            if not BlogPost.objects.filter(title=title).exists():
                BlogPost.objects.create(
                    title=title,
                    slug=slugify(title),
                    author=author,
                    category=cat_news,
                    excerpt=excerpt,
                    body=body,
                    is_published=True,
                    published_at=timezone.now(),
                )
        self.stdout.write(self.style.SUCCESS("  2 news posts (sample)"))

        # ---------------------------------------------------------------
        # Gallery — the band's own photos
        # ---------------------------------------------------------------
        from apps.gallery.models import GalleryPhoto
        photos = [
            ("On stage at Blumenthal Arts", "press-ensemble.jpg", 0.35),
            ("The full band", "press-group.jpg", 0.3),
            ("Against the wall", "band-wall.jpg", 0.4),
            ("Justice for all", "band-justice.jpg", 0.5),
            ("The balcony", "band-balcony.jpg", 0.5),
            ("Golden hour", "band-street.jpg", 0.5),
            ("The full lineup", "band-lineup.png", 0.28),
            ("In black and white", "band-bw.png", 0.35),
            ("Backstage, before the set", "band-backstage.png", 0.3),
            ("Rich Graham on clarinet", "rich-clarinet.png", 0.4),
            ("Rich Graham on flute", "rich-flute.png", 0.35),
        ]
        for i, (title, filename, focal) in enumerate(photos):
            if not GalleryPhoto.objects.filter(title=title).exists():
                photo = GalleryPhoto.objects.create(
                    title=title, image_focal_y=focal, sort_order=i
                )
                attach(photo, "image", filename)
        self.stdout.write(self.style.SUCCESS(f"  {len(photos)} gallery photos"))

        from apps.gallery.models import GalleryVideo
        if not GalleryVideo.objects.filter(title="Latin Tune by Keenan Harmon (with Nexus Jazz)").exists():
            GalleryVideo.objects.create(
                title="Latin Tune by Keenan Harmon (with Nexus Jazz)",
                video_url="https://www.youtube.com/embed/Dp2g6cJ9Gto",
                sort_order=0,
            )
        self.stdout.write(self.style.SUCCESS("  1 gallery video"))

        self.stdout.write(self.style.SUCCESS("\nSeeded. Sample records are marked — replace via admin."))
