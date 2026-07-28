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
        # News — six full-length posts (2026-07-28 rewrite) spanning every
        # BlogPost feature: category, tags, a featured image, excerpt, SEO
        # meta fields, and a real multi-paragraph body — so the sample
        # content shows the CMS at the depth a real client would use it,
        # not just a one-sentence placeholder per post.
        # ---------------------------------------------------------------
        from apps.blog.models import BlogPost, BlogCategory, BlogTag
        from apps.accounts.models import User
        cat_live, _ = BlogCategory.objects.get_or_create(name="Live", defaults={"slug": "live", "is_active": True})
        cat_studio, _ = BlogCategory.objects.get_or_create(name="Studio", defaults={"slug": "studio", "is_active": True})
        cat_news, _ = BlogCategory.objects.get_or_create(name="News", defaults={"slug": "news", "is_active": True})
        tag_names = ["Live Shows", "Studio", "New Music", "Charlotte", "Festivals", "Band News"]
        tags = {name: BlogTag.objects.get_or_create(name=name)[0] for name in tag_names}
        author = User.objects.filter(is_superuser=True).first()

        posts = [
            dict(
                title="On Stage at Blumenthal Arts",
                slug="on-stage-at-blumenthal-arts",
                category=cat_live,
                tag_list=["Live Shows", "Charlotte"],
                image="blumenthal-arts.jpg",
                days_ago=14,
                excerpt="The group brought its original book to the Stagedoor Theater — and will return for an album release concert.",
                meta_description="Nexus Jazz Group's night at Blumenthal Arts' Stagedoor Theater, and the album release concert it's setting up.",
                meta_keywords="Nexus Jazz Group, Blumenthal Arts, Stagedoor Theater, Charlotte jazz, live jazz, album release concert",
                body="""Formed in 2019 by Keenan Harmon for his original music, the Nexus Jazz Group has spent the years since building a book that refuses to sit still — sets that open in a slow blues and land somewhere between symphonic swell and second-line groove without ever announcing the turn. That range is easier to feel live than describe, which is part of why the band keeps coming back to rooms with real stages rather than just corners of a bar.

Blumenthal Arts' Stagedoor Theater has become one of those rooms. The group's most recent night there filled the house with the full original book — the tunes that have carried the band from Charlotte breweries and clubs up through two runs at Huntersville's Jazz Appreciation Festival — played with the kind of headroom a proper stage and a real sound system give a band that's used to smaller rooms. Rich Graham's tenor cut through clean on the up-tempo numbers; Casey Mink's violin carried the ballads somewhere the horn alone couldn't have gone.

What made the night different from a typical set was the crowd itself — a mix of longtime followers who'd caught the band at a brewery show and first-timers who came for the Stagedoor's reputation and stayed for the music. Both left asking the same question: when's the next one.

The answer arrived before the house lights came up. The band is returning to the Stagedoor Theater for a full album release concert, drawing the same original material into a recorded set for the first time. Details on the date and ticketing will land here and on the Events page as soon as they're locked — followed, not long after, by the record itself.""",
            ),
            dict(
                title="In the Studio",
                slug="in-the-studio",
                category=cat_studio,
                tag_list=["Studio", "New Music"],
                image="in-the-studio.jpg",
                days_ago=19,
                excerpt="Tracking is underway on the group's next recording — first listens are closer than they look.",
                meta_description="Inside the studio sessions for Nexus Jazz Group's next recording — how the band is tracking, and what's next.",
                meta_keywords="Nexus Jazz Group, recording session, new jazz album, Charlotte jazz band, studio tracking",
                body="""There's a particular quiet that settles over a studio session once the click track starts and everyone stops talking — the sound of a band that has played a tune two hundred times finding the two hundred and first version of it. That's where the Nexus Jazz Group has been most weekends this stretch: tracking the material that's carried the band's live shows for the past year, this time for keeps.

The approach has been simple and a little old-fashioned. Rather than build the record piece by piece, the group is cutting as close to a live take as the format allows — full band in the room, drums and bass locking in first, horns and violin layered in close to real time so the takes keep the push-and-pull that a click track alone can't fake. It's slower than programming a session from scratch, and it's exactly the point: the record needs to sound like the band sounds from the third row at the Stagedoor Theater, not like a version of the band assembled after the fact.

Denise Harding's piano and keys work has anchored more of this session than any single instrument — voicings that move the harmony under a solo without ever crowding it, which is a skill that reads as effortless live and turns out to be the hardest thing to get right on tape. Evan Corey's drums and Leo Gayosso's bass have been tracked together in the same room on purpose, chasing the same in-the-pocket feel that makes the live shows move.

There's no release date locked yet — a record built this way earns its timeline rather than keeping one — but audio will land on the Music & Media page the moment a mix is ready to share. Until then, the road remains the best place to hear where these tunes are headed.""",
            ),
            dict(
                title="Summer Series Kickoff",
                slug="summer-series-kickoff",
                category=cat_live,
                tag_list=["Live Shows", "Charlotte", "Festivals"],
                image="summer-series-kickoff.jpg",
                days_ago=4,
                excerpt="The Evening Muse summer run opens with the full band, first time on that stage since spring.",
                meta_description="Nexus Jazz Group opens its summer series at Evening Muse with the full band and a preview of new material.",
                meta_keywords="Nexus Jazz Group, Evening Muse, Charlotte live music, summer jazz series, jazz band Charlotte",
                body="""Summer shows have a different energy than the rest of the calendar — later light, looser crowds, a room that fills up slow and then all at once around the second set. The Nexus Jazz Group's summer series opener at Evening Muse leaned into all of it, the full band back on that stage for the first time since the spring run wrapped.

The set list mixed the familiar with the new: a handful of the road-tested originals that have anchored shows since Huntersville's Jazz Appreciation Festival, alongside a couple of tunes still working their way out of the current studio sessions and into a live room for the first time. Casey Mink's violin took the lead on one of those new pieces — a slower, more symphonic turn than the band's usual up-tempo openers — and the room went quiet in the way a room only goes quiet when it's actually listening.

Evening Muse's stage sits close to the crowd, and the band used that proximity all night, trading solos and glances more than they would on a bigger stage, the kind of small-room chemistry that first drew people to these shows years ago at breweries and clubs around Charlotte. Rich Graham switched between tenor, clarinet, and flute across the set — a reminder of just how wide this group's palette runs once it stretches out.

This is the first of several summer dates now on the calendar, with more to be announced as venues confirm. Check the Events page for the full run, and expect at least one more surprise from the new material before the season's out.""",
            ),
            dict(
                title="A Night at Middle C Jazz",
                slug="a-night-at-middle-c-jazz",
                category=cat_live,
                tag_list=["Live Shows", "Charlotte"],
                image="middle-c-jazz.jpg",
                days_ago=11,
                excerpt="Uptown Charlotte turned out for a late show that ran long in the best way — two encores, one new tune.",
                meta_description="A late, extended set from Nexus Jazz Group at Middle C Jazz in uptown Charlotte — two encores and a new tune's live debut.",
                meta_keywords="Nexus Jazz Group, Middle C Jazz, uptown Charlotte, live jazz show, Charlotte jazz venue",
                body="""Uptown Charlotte turned out for a late show at Middle C Jazz that ran well past its scheduled end — the kind of night where the room asks for one more and the band, for once, doesn't need much convincing.

Middle C Jazz books serious rooms and expects a serious set, and the Nexus Jazz Group met it with one of the tighter shows the band has played this year. The first set stuck close to the core book — the tunes that have carried the group from its earliest brewery dates through two Jazz Appreciation Festival runs in Huntersville — before the second set opened the door to looser arrangements and longer solos, Leo Gayosso and Evan Corey stretching the groove out under extended features from Rich Graham and Casey Mink.

By the time the last tune ended, the crowd wasn't ready to let the band leave the stage. Two encores followed — the second unplanned, built around a new tune that's been circulating in soundchecks but hadn't been played for an audience before that night. It landed. Whatever it becomes on the record currently taking shape in the studio, it now has a first live performance behind it, and a room full of people who'll say they were there for it.

Middle C Jazz has quickly become one of the rooms the band returns to whenever the calendar allows — the kind of venue that rewards a band willing to play a genuinely long set rather than watch the clock. Expect this one back on the schedule before the year's out.""",
            ),
            dict(
                title="New Recordings This Fall",
                slug="new-recordings-this-fall",
                category=cat_studio,
                tag_list=["Studio", "New Music"],
                image="new-recordings-this-fall.jpg",
                days_ago=24,
                excerpt="Rich Graham tracking woodwinds for the new record — clarinet, flute, and the tenor sax solo that closes side A.",
                meta_description="Behind the scenes as Rich Graham tracks woodwinds — clarinet, flute, and a closing tenor solo — for Nexus Jazz Group's new record.",
                meta_keywords="Rich Graham, Nexus Jazz Group, saxophone recording, woodwinds, new jazz record, studio session",
                body="""Rich Graham has spent more hours in the studio this stretch than anyone else in the Nexus Jazz Group, and it shows in the sessions currently taking shape into the band's next record. Where most of the tracking has leaned on the full band playing together in the room, the woodwind parts have been built in careful, deliberate layers — clarinet on one pass, flute on another, tenor saxophone brought in last once the rest of the arrangement has settled around it.

That order matters. A tenor solo recorded too early fights for space against parts that haven't been finalized yet; recorded last, against a fully locked rhythm section and horn arrangement, it has somewhere to land. The solo that's expected to close out side A of the record — a long, unhurried tenor feature built over a bassline Leo Gayosso and Evan Corey have been refining since spring — was tracked in a single afternoon after weeks of the arrangement developing around it in rehearsal and on the road.

The clarinet and flute work is quieter, in every sense — coloring rather than leading, the kind of part that a casual listener might not consciously register on a first pass through the record but would immediately miss if it were gone. That's by design. The band's sound has always drawn from a wider well than a standard horn-and-rhythm quartet, pulling in textures from the R&B, bluegrass, and symphonic backgrounds its members carry individually, and the woodwind layering is where that shows up most clearly on tape.

There's still work ahead — strings, keys, and final mix passes among them — but the fall target for a first single release is holding. More from the studio as the pieces come together, and the earliest listens will land on the Music & Media page before anywhere else.""",
            ),
            dict(
                title="Backstage Before the Set",
                slug="backstage-before-the-set",
                category=cat_news,
                tag_list=["Band News", "Live Shows"],
                image="backstage-before-the-set.jpg",
                days_ago=26,
                excerpt="Fifteen minutes before doors — tuning up, running the setlist, and the quiet before a room fills.",
                meta_description="What happens backstage in the fifteen minutes before Nexus Jazz Group takes the stage.",
                meta_keywords="Nexus Jazz Group, behind the scenes, live music preparation, Charlotte jazz band",
                body="""Fifteen minutes before doors, backstage looks nothing like the stage does an hour later. No lights, no crowd noise — just five musicians finding their own version of ready. Casey Mink runs scales low and quiet in a corner, more habit than warm-up at this point. Evan Corey taps out the night's trickier transition on a practice pad, working through the one spot in the set that still occasionally catches the band off guard. Leo Gayosso checks a cable twice. Denise Harding looks over the setlist one more time, even though she wrote half of it.

This is the part of a show that almost nobody outside the band ever sees, and it's also the part that decides more of the night than people might guess. A setlist gets built in advance, but it rarely survives contact with a room unchanged — a slower crowd early might mean pulling a ballad forward, a rowdy Friday might mean saving the up-tempo opener for later so there's still somewhere to build to. Those calls get made in exactly this window, in the fifteen minutes before doors, based on nothing more than a read of the room and years of doing this together.

Rich Graham has a pre-show ritual that hasn't changed in years: reeds tested one at a time, in order, until one feels right for the night — humidity, room temperature, and something less explainable all factoring in. It's a small thing. It's also the kind of small thing that separates a band that shows up and plays from a band that shows up and performs.

Then the house lights start to dim, the room noise shifts from murmur to something closer to anticipation, and none of that backstage quiet matters anymore — just the first tune, and however the night decides to go from there.""",
            ),
        ]
        for data in posts:
            post, created = BlogPost.objects.get_or_create(
                slug=data["slug"],
                defaults=dict(
                    title=data["title"],
                    author=author,
                    category=data["category"],
                    excerpt=data["excerpt"],
                    body=data["body"],
                    meta_description=data["meta_description"],
                    meta_keywords=data["meta_keywords"],
                    is_published=True,
                    published_at=timezone.now() - datetime.timedelta(days=data["days_ago"]),
                ),
            )
            attach(post, "featured_image", data["image"])
            post.tags.set([tags[name] for name in data["tag_list"]])
        self.stdout.write(self.style.SUCCESS("  6 news posts (sample)"))

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
