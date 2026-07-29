# CLAUDE.md — Nexus Jazz

Client Django site, bootstrapped from master-template on 2026-07-12. Root pipeline rules
(`../CLAUDE.md`), skills, and prompt codes apply; this file only holds project facts.

## Brand

- Theme archetype: **T2 inverted — "night gallery"** (near-black ground, ivory type, brass
  accent; Blue Note/Reid Miles typography discipline, Zwirner-quiet chrome).
- Tokens live in `static/css/theme.css` brand block — the ONLY place brand values exist.
- Voice: earthy, bluesy, progressive, unhurried, confident. "Original music from Charlotte —
  jazz taken at its widest reach."
- Signature detail: oversized Bodoni Moda didone titles as exhibition wall-text (letter-spaced
  small-caps kickers, hairline rules, duotone photography).
- Hero (**current**, single-image announcer + pearl/switch 2026-07-25): `.hero-stage`,
  the "announcer's introduction" from the Claude Design home concept (project
  `99bb8987-878d-49db-bfa9-c4411ab2507e`, `Nexus Jazz - Home.dc.html`). ONE full-bleed portrait
  (`.hero-stage__feature > .hero-stage__img`) fills the whole section — the formal band lineup,
  gallery title "The full lineup" = `nexfor1.jpg`, passed as `hero_feature` from the home view
  (else first active `GalleryPhoto`, else the `HeroSlide` photo). `object-position: center 24%`
  sits the landscape crop on the band's faces. Height = `calc(100svh - var(--nav-h))`, see below.
  It plays as theatre: the stage holds BLACK while the announcer names the act one line at a time,
  each lit by a white follow-spot that CUTS in (light-switch snap) — "Welcome to the viewing of"
  → "Keenan Harmon" → "and the Nexus Jazz Group", on which the
  WHOLE HERO RISES IN ONE MOVE on that last beat — picture, group line, subtitle, CTAs, nav and
  replay all share the same `calc(var(--beat) * 0.85)` fade with NO delay, while the spots wash out.
  **Phase 3 is the end of the sequence; nothing fades in after it** (user, 2026-07-26 — the old
  phase 4 that brought chrome in a beat late is gone). The finished hero carries
  NO circles. Announced lines are
  centred (`width: fit-content` + auto-margins); the whole type block is v-centred (`top:50%`,
  `translateY(-50%)`). On ≤820px it's the same single image + centred type (a phone viewport is
  portrait, so the tall image crops kindly); ≤480px hides Replay. This REPLACED the checkerboard
  mosaic (2026-07-24, tiles + `--mosaic` grid — the user asked to go back to one central image),
  the light-switch flip, the old `.hero-full` hero, and the Cliburn wordmark loader (all deleted).
  - **Follow-spots = BLACK-STAGE LINES ONLY** (user: "circles during the animation, removed from the
    post-animated screen"). TWO spots now (`.hero-stage__spot--1/2`), luminous white radial glows
    (fade to transparent before the box edge — see superseded #3), `mix-blend-mode:screen`. Default
    opacity 0 (finished hero = none); switched ON only for phases 1–2 (the ONE *additive* layer —
    see invariant note; safe because spot-absence IS the finished look). They CUT in (per-phase
    `transition:none`); at **phase 3** the "on" rules simply drop away, so they wash out
    (`calc(var(--beat) * 0.35)`, beat-relative so it holds at any BPM) UNDER the picture's slower
    fade-up (0.85 beat) — verified: at the first frame where the picture is ≥95% opaque both spot
    opacities read 0. **The old spot--3 (lit the group line at phase 3) was deleted 2026-07-26**: it
    sat at full strength over the fully-revealed picture for a whole beat, which is the "circle in
    the final frame" the user screenshotted. Fading it later would NOT have fixed that — the last
    line is lit by the picture itself. Don't reintroduce a phase-3 spot. hero-intro.js measures each
    of the two lines' centres and parks its spot via `--spotN-left/top` (CSS `top` fallbacks
    41/50% cover no-JS).
  - **Tempo = 38 BPM, one phase per beat** (client's chosen tempo, locked 2026-07-27).
    `window.HERO_BPM_DEFAULT = 38` in home.html's inline script; beat = `60000/bpm` = 1.579s,
    phases fire at 1×/2×/3× the beat (verified: 1.58 / 3.16 / 4.72s). The same script writes
    `--beat` (seconds) on `:root`, and the hero's CSS fade durations are `calc(var(--beat) * …)` —
    so BPM re-times cues AND fades together, one dial. `:root { --beat: 1.579s }` in nexus.css is
    the no-JS fallback — **change both together**. `?bpm=NN` still overrides for a one-off check;
    the dev `?tempo` slider panel was deleted once 38 was chosen. NOTE: the slider used to write
    `localStorage.heroBpm`, which still wins over the default in any browser that used it — clear
    it (or hit `?bpm=38`) if a machine seems to play at the old tempo.
  - **Removed 2026-07-26 — the white pearl + flick light-switch** (`.hero-stage__lightswitch`,
    `__pearl`, `__switch`, `__knob`, `@keyframes pearl-roll`): a white bead rolled off the name onto
    an ivory toggle that flicked as the picture revealed. User asked for it gone; markup, CSS and the
    phase rules are all deleted. Do not reintroduce — the reveal is carried by the type + picture
    alone now.
  - **Whole band's faces must show** (user). The full-bleed crop is `object-position: center 11%`
    (fixed in CSS, decoupled from the model focal) — low enough that all four STANDING members clear
    the top (28% cut their foreheads; 15% still buried seated Keenan behind the subtitle) and seated
    Keenan's face lands framed just BELOW the CTAs. `object-position` Y is the single lever if the
    photo or copy changes; the type stays v-centred (`top:50%`).
  - **Hero stops short of the fold on purpose** (user, 2026-07-27): `height: calc(100svh -
    var(--hero-peek))`. Two `:root` variables at the TOP of nexus.css own the fold and are the
    only things to touch: `--hero-peek: 5rem` (how far short of the fold the hero stops — the
    81px black strip, identical at every viewport) and `--about-crest: 1.5rem` (how far the wall
    title rises INTO that strip — ~25px of letter-tops showing, the scroll cue). The about
    section's `padding-top` is DERIVED as `calc(var(--hero-peek) - var(--about-crest))` — never
    hardcode it, or the crest and the strip drift apart. Raising the crest shows more title
    without changing the black; raising the peek shrinks the hero. Traps, both of which cost real time: (1)
    `.hero-stage + .section-x` matches NOTHING — the hero's next sibling is the
    `.hero-stage__replay` button, so style `.about` directly; (2) the peeking `<h2>` carries
    **no `.reveal`** on purpose — a reveal holds it at opacity 0 until the observer fires, and
    reduced-motion screenshots hide that (there `.reveal` is opacity 1), so verify the fold with
    motion ON.
  - **The whole page is black during the intro** (user, 2026-07-27): `.about` is held at
    `opacity: 0` for phases 0–2 and fades in on the SAME beat as picture/nav/CTAs
    (`calc(var(--beat) * 0.85)`, no delay) — one reveal, no second event. `body` also takes the
    hero's deeper black (`--color-secondary`) for those phases, transitioning back at phase 3:
    without it the strip below the hero showed as a faint seam (`--color-bg` #0E0D0B against the
    stage's #0A0908) across an otherwise perfectly black screen. Both rules are subtractive, so
    no-JS / reduced-motion / repeat visits still get the composed page (verified).
  - **Superseded height notes** (kept for the reasoning): the hero used to be
    `calc(100svh - var(--nav-h))` because the sticky nav was in-flow; it now runs full-bleed
    UNDER a transparent nav via `margin-top: calc(-1 * var(--nav-h))`, with only `--hero-peek`
    subtracted. There is no scroll-cue chevron — the peeking title is the cue.
  - **Focal note**: the HERO no longer uses the model focal (its crop is the fixed CSS
    `object-position` above, since the portrait's model focal 0.28 is tuned for the gallery's SQUARE
    crop, not this landscape). The fallback `HeroSlide` img still passes it as a % via
    `{% widthratio image_focal_y 1 100 %}%` — note `image_focal_y` is a 0–1 FloatField, so a bare
    `{{ image_focal_y }}%` would emit e.g. `0.28%` ≈ top (use widthratio anywhere it's rendered as %).
  - **How it's driven**: a `data-phase` (0–3) attribute on `:root`, set synchronously by an inline
    script in `home.html` BEFORE the hero paints (no flash), advanced by that same script's own
    `setTimeout`s (a failed external JS load can't strand the page). Reveal rules (picture/type/
    chrome) are *subtractive* from the finished state; the spots are the one additive intro-only
    layer. No `data-phase` at all (no-JS, reduced-motion, repeat visits via
    sessionStorage `heroIntroSeen`) = the finished hero with nothing hidden and no circles. NOTE:
    a live intro ENDS on `data-phase="3"` (the attribute is set, not removed), so **phase 3 must
    equal the finished look** — it does (no phase-3 hide rules anywhere; spots not in any "on" list).
    That invariant is the reason chrome can't be held back a beat: any rule that hides something at
    phase 3 would stick forever.
  - **Superseded — do NOT reintroduce** (rejected on taste, in order): (1) floating CSS glow
    circles on the old static headline — "unmotivated decoration"; (2) brass-tinted glows
    (`color-mix(var(--color-primary))`) — read "yellow"; the light SOURCE stays pure white, brass is
    for type/CTAs only (the intro pearl was brass briefly, then changed to white per user); (3) flat solid-white discs — read as dull grey shapes AND
    `mix-blend-mode:screen` clipped them into visible SQUARES at the box edge (radial-fade-to-
    transparent is why the current spots don't clip); (4) the checkerboard mosaic of gallery tiles
    (2026-07-24) — user reverted to one central image; (5) a Paper Shaders WebGL metaballs glow —
    full-bleed greyed the photo, small contained mount rendered blank. Vendored lib still in
    `static/vendor/paper-shaders/` (unused).
  - **Gotcha (historical)**: `var(--space-20)` isn't a real token (scale jumps 16→24); an
    invalid `var()` inside a shorthand invalidates the whole declaration. Verify spacing tokens
    exist in theme.css before use.
- Fonts: **Bodoni Moda** (display — didone, mid-century print pairing) + **Jost** (body/UI —
  Futura/Blue Note nod). Cormorant Garamond was dropped 2026-07-12: it duplicated the display
  font used across Shwetanshu's own portfolio site (title logo + CTAs).
- **Display font = Fraunces, site-wide** (2026-07-24). `--font-heading` in theme.css is now
  `'Fraunces', Georgia, ...` — a warm, soft old-style serif with real soul (characterful ball
  terminals, expressive italic), chosen because Bodoni Moda's cold fashion-didone feel fought
  the "earthy, bluesy, unhurried" jazz vibe. Started hero-only, then rolled out to the whole
  site per user request; Bodoni Moda removed from the `@import` (nothing references it). The
  hero type also dropped its white-glow text-shadow halos (they read as a soft gradient bloom);
  crisp type + a dark drop-shadow for legibility over the photo is the current treatment.

## Facts

| | |
|---|---|
| Django package | `nexus_jazz` |
| Apps kept | accounts, core, blog (news), gallery, events, team, inquiries |
| Public pages | home · band/ (The Band) · media/ (Music & Media) · blog/ (Blog) · events/ (+ booking form) · inquiries/contact/ |
| Deploy target | TBD (contract: SSL + handover; decide at launch) |
| Domain | TBD |

- 2026-07-23: imported the "Nexus Jazz - Home.dc.html" Claude Design concept (project
  `99bb8987-878d-49db-bfa9-c4411ab2507e`) and merged its stage-lighting idea into the
  existing hero — not a wholesale swap. Added a second and third follow-spot
  (`.hero-full__pool--1/--3`) that glide in from off-frame corners and settle to an
  ambient hold (not fully fade like the old single beam), plus `.hero-full__wash` (house
  lights swelling once every line has landed) and `.hero-full__grain` (film grain, scoped
  to the hero only — not sitewide, to keep the rest of the "night gallery" chrome clean).
  The hero photo's cut-on keyframe now blooms saturation in with the brightness, not just
  a dimmer. All new elements respect `prefers-reduced-motion` and `body.no-intro` timing
  like the existing beam. Verified via a hand-rolled Playwright script (4.7s wait, no
  reduced-motion) since `shot.py`'s standard capture forces reduced-motion by design.
  **Follow-up same day**: user flagged the pools/beam as reading "yellow" — they had
  `color-mix(... var(--color-primary) ...)` baked into the gradient stops. Recolored every
  hero light element to pure white (`rgba(255,255,255,…)`, no brass mixed into the light
  source itself) to match the Claude Design mockup's own `wl()` function exactly — brass
  stays reserved for type/buttons only. This is the current, locked hero treatment.
- 2026-07-23: explored using `../Personal Portfolio/static/vendor/paper-shaders/` (a
  vendored, no-build-step WebGL shader lib — dot-orbit/metaballs/pulsing-border) to add
  "alive" motion elsewhere on the site, per user request. Copied the lib + metaballs
  shader into `static/vendor/paper-shaders/` here (kept, reusable). Two integration
  attempts failed and were reverted: (1) full-bleed metaballs behind the hero photo —
  screen-blending a shader across a whole dark photo just lifts the blacks to grey at any
  visible opacity, structurally incompatible with the "deep black, one full-bleed photo"
  hero design; (2) a small contained glow behind the primary booking-CTA button — the
  shader rendered fully transparent (verified via `gl.readPixels`, zero alpha across the
  entire canvas even with an opaque `u_colorBack`) when mounted into a small square host,
  despite matching the portfolio's own working uniform set; root cause not found in the
  time available (portfolio's only working reference uses a canvas-mask trick on a
  differently-shaped host, not a bare small box). Left unintegrated rather than ship
  something invisible or unreliable — the vendored files are available if someone wants
  to debug the small-host case properly later.
- 2026-07-23: real band roster from the group's own info sheet (was previously
  instrument-only placeholders) — Rich Graham (sax/flute/clarinet, new portrait photo),
  Casey Mink (violin), Leo Gayosso (bass), Evan Corey (drums), Denise Harding (piano &
  keys, no photo yet). Trombone has no name/bio/photo in anything supplied — stays "To be
  announced". `seed.py` updated to match for fresh installs; existing DB rows were
  updated in place (not re-created) to avoid duplicating chairs.
- 2026-07-23: `media/seed/press-group.jpg` had a press-kit caption bar baked into the
  bottom of the frame (pre-existing, predates this session) that leaked into the square
  gallery-grid crop — cropped it out at the source; re-seed is now clean.
- 2026-07-23: `Members/` (loose reference folder: info-sheet PDF + ensemble/candid
  photos) dissolved — bios merged into `TeamMember` rows above, photos into `media/team/`
  (Rich's portrait) and `apps.gallery.GalleryPhoto` (5 new ensemble/candid shots, plus
  `media/seed/` sources for fresh installs). Folder removed once every file had a home.

- **About / info hub section (`#sound`, home)** — rebuilt 2026-07-26 from the old centred
  "01 The Sound" wall-text block. `.about` in nexus.css: left copy column + a floating portrait
  right (`.about__media` → `.about__frame` → img). Rules that came from user direction:
  **no italics anywhere** (the brass emphasis on "always progressive." is COLOUR only — the old
  `<em>` italic read dated against the hero's roman type), copy left-aligned, and the numbered
  kicker deleted (Live/Listen renumbered 01/02 as a result — home page numbering must stay
  contiguous). The `<h2>` carries `id="about-title"` for the section's `aria-labelledby`.
  Content (2026-07-27, second/third pass): the client's own supplied bio, verbatim, split
  across two `.about__lede` paragraphs at the sentence break (words unchanged — one dense block
  read as clutter); then two actions, Meet the band + Music & Media. **Both the Latest news link
  and the dotted fact line were removed** at the user's request, the latter after the four-row
  `dl` fact table before it ("a weird graphic chart") — three deletions in a row, so don't
  re-add facts/links to this section without being asked. Air comes from
  `padding-block: calc(var(--section-y) * 1.35)`, a 0.82fr photo column, an 8vw column gap and
  a 40ch measure. Three normalizations of the pasted copy (PDF artifacts,
  flagged to the user): `R &B`→`R&B`, `backgrounds-from`→`backgrounds — from`, stray `..`→`.`.
  - **Hierarchy rules (user, 2026-07-27 — the title "didn't seem much like a title" and the body
    was "a bunch of large text" in "a very drab font")**: the `<h2>` is a WALL TITLE on its own
    full-width grid row (`grid-column: 1 / -1`) above both columns at
    `clamp(2rem, 1.45rem + 2.3vw, 3.35rem)`, weight 500 (matching the hero's "Keenan Harmon";
    600 read heavier than anything else on the site). The row-gap alone carries the separation —
    the hairline that was under it was removed 2026-07-27, don't reinstate it. Do NOT put it back inside the
    copy column; sitting beside the body is what made it read as just another paragraph. The
    BODY is set in the SERIF (`--font-heading`, Fraunces) at ~1.02–1.18rem/1.72 — Jost 300 at
    paragraph length read thin and lifeless on the dark ground. The sans stays for labels,
    buttons, captions and all chrome, so the two roles are visually separated.
  - **Photo**: `static/img/band-lineup.jpg` (1200px progressive JPEG made from
    `media/seed/band-lineup.png`) — a STATIC asset, not CMS-driven, because it's a fixed design
    element. It's a bright warm room shot, so it's pulled toward the night-gallery ground:
    `filter: saturate(.86) brightness(.9)` + a black foot gradient (`.about__frame::after`) that
    sits the wooden floor into the section, warming back up on hover.
  - **"Alive" layer** (user asked the section to feel alive): an 11s `about-float` drift
    (transform-only), the hover warm-up, and the drift PAUSING on hover so the photo settles
    under the pointer. All off under `prefers-reduced-motion`.
    **The drift MUST stay on `.about__frame`, never on `.about__media`**: the figure carries
    `.reveal`, whose entrance is a `transform`, and a CSS animation on the same property always
    wins the cascade — put the float on the figure and its scroll reveal silently dies. That bug
    is invisible to reduced-motion screenshots (which kill the animation and let the reveal
    work), so verify it by reading the figure's computed transform with motion ENABLED: 24px
    before `.visible`, `none` after, with `.about__frame` oscillating.
  - **The offset brass hairline** (`.about__media::before`) sits UP-RIGHT behind the frame —
    down-right crossed the caption. It's `content: none` below 900px: with the layout stacked
    there's nothing for it to add depth against and it read as a stray box.
  - Gotcha: the dev server caches templates (markup edits need a restart to show); CSS is live.

- **News = poster cards** (2026-07-27). One component, `templates/blog/_post_card.html`,
  included by BOTH the home "News" section (section 01, three latest posts + All news button —
  `featured_posts` in `apps/core/views.py`) and the news index, so the two can never drift.
  CSS lives under "NEWS POSTER CARDS" in nexus.css. Cover on top, then date / title / 3-line
  clamped teaser / "Read the story". **Posts without a featured image get a designed TYPE PLATE**
  (record-sleeve: brass-washed gradient, label, title, brass rule) — not a grey placeholder,
  because no post has art yet. On plate cards the body `<h3>` is visually hidden (`.post-card--plate
  .post-card__title`) so the title isn't printed twice — keep the element for heading semantics.
  Post detail gained a serif `.article__standfirst` (the excerpt) so the story opens on the promise
  the card made. Home numbering is now 01 News · 02 Live · 03 Listen.
- **"News" renamed to "Blog" site-wide** (2026-07-29, user-directed). Nav, footer, home section
  heading ("From the Blog"), the index page (kicker/H1 now "Blog"/"The Blog", page title,
  meta description), post-detail's "All posts" link, the post-card's no-category fallback tag,
  and the admin dashboard card all say Blog now, not News. The public URL moved from `/news/` to
  `/blog/` (`nexus_jazz/urls.py`) to match — no redirect was added since the site isn't launched
  yet (no real domain, no external links to break). The `apps.blog` app, its models
  (`BlogPost`/`BlogCategory`/`BlogTag`), the `blog_index`/`blog_detail`/etc. URL names, and the
  `news-retro`/`.news-retro__*` CSS class names were already named for the app, not the page, so
  none of that needed touching — only user-facing copy and the URL prefix changed. A `BlogCategory`
  named "News" still exists as sample taxonomy DATA (a post can be filed under a "News" category
  on the Blog) — that's content, not site chrome, and was left alone.
- **The Band = five players + a per-player modal** (2026-07-27, user-directed). The page shows
  exactly the five the client named — Rich Graham, Casey Mink, Leo Gayosso, Evan Corey,
  Denise Harding — with bios pasted **verbatim from the client; do not rewrite or extend them**.
  Keenan Harmon's and the "Trombone / To be announced" chairs were set `is_active=False` (rows
  kept, not deleted) — the user said "there are only 5, not 7" and supplied five bios; flag before
  re-adding Keenan as bandleader.
  - New model `team.MemberPhoto` (FK member, image, caption, sort_order, is_active) + a
    `MemberPhotoInline` on TeamMemberAdmin. `TeamMember.photo` is still the single card portrait;
    MemberPhoto rows are the set the modal opens. Seeded from files already on disk: Rich 3
    (portrait + clarinet + flute), Casey/Leo/Evan 1 press shot each, Denise 0 — everything else the
    client sends goes in via the admin inline.
  - **Layout = roster CARDS, picture left / bio right** (user, 2026-07-27, modelled on a reference
    they supplied). `.roster` → `.player-row` (`minmax(0,20rem) 1fr` ≥780px). Nothing is clickable
    and there is no modal: the card grid + click-to-open dialog it replaced is gone, along with
    `.player-panel`/`:target` (that was solving a no-JS problem this layout doesn't have — every
    bio is now plain visible copy).
  - **Multi-photo members get a crossfade carousel** (`.shots`, arrows + dots), adapted from the
    Miller Piano hero's `data-carousel-*` API — but MANUAL, no autoplay, since it sits beside copy
    people are reading. Only Rich has more than one picture today. **Progressive enhancement is in
    the CSS**: slides sit in normal flow and arrows/dots are `display:none` until JS adds
    `.is-live` to the root, so with JS off nothing is hidden behind a control that does nothing.
    Controls are site-styled: brass-hairline circular arrows on a blurred ground, brass pill dots
    on a foot scrim (`.shots.is-live::after`) so they read over bright photos.
  - **`.shots` MUST keep `aspect-ratio: 4/5` + `object-fit: cover`.** The first version let the
    press JPEGs (2048px) size themselves: full-bleed images with the bio stranded underneath, and
    the page looked broken (user, 2026-07-27). The frame is what makes the card a card.
  - Roster copy: "seven-piece" was swept out of home, gallery, booking and events templates AND
    `seed.py` (which used to create all seven chairs — a fresh seed would silently undo the
    five-player roster). MemberPhoto captions are intentionally EMPTY: any caption would be text
    the client didn't supply.
- **No grayscale anywhere** (user, 2026-07-27): the duotone-at-rest / colour-on-hover treatment
  was removed from `.duo`, `.gallery-item` and `base.css`'s `.brand-logo`. Photos render full
  colour everywhere; the only image effects left are the hover scale and the about photo's dimming.
  Don't reintroduce `filter: grayscale()`.
- **Nav ground on scroll** (2026-07-27): the nav is transparent over the hero, then `scripts.js`
  adds `.is-grounded` once `scrollY` passes the hero (or 8px on pages without one) and `.nav::before`
  fades in a **lifted** smoked-glass band (`--color-surface-2`, blurred). Two things make it
  seamless: the layer extends 2rem BELOW the bar and is `mask-image`d to transparent, so there is no
  border line and page text dissolves as it scrolls under. A darker band was tried first and is
  invisible — the page is already near-black. **Never set `position` on `.nav` in nexus.css**:
  base.css makes it `sticky`, and overriding to `relative` silently un-sticks the whole bar.

- **Static files were being served STALE — fixed with `static_v`** (2026-07-27). Django's dev
  static server sends only `Last-Modified` (no ETag, no Cache-Control), so browsers fall back to
  heuristic caching and can hold an old `nexus.css` for hours while templates keep updating
  server-side. Symptom: a page with new markup and none of its styles — it reads as "you broke
  the design", and it cost a full round trip. `apps/core/templatetags/assets.py` provides
  `{% load assets %}{% static_v 'css/nexus.css' %}`, which appends the file's mtime as `?v=`;
  base.html and home.html use it for all CSS/JS. **Use `static_v`, not `static`, for any new
  stylesheet or script.** When a design change "doesn't show", check the served URL has a `?v=`
  matching the file's mtime before assuming the CSS is wrong.

## Content Model Notes

- `gallery.AudioEmbed` — Spotify/SoundCloud auto-embed via `embed_url` property; raw
  `embed_code` fallback for Bandcamp.
- `inquiries.BookingInquiry` — event_date / event_type / venue; replaces the shop inquiry
  models. URLs: `/inquiries/booking/`, `/inquiries/contact/`.
- 2026-07-13: real 2025 media-kit content applied — bio copy, contact (keenan@nexusjazz.com,
  (803) 487-3696), hero + gallery + 5 band-chair photos cropped from press-kit photos in
  `media/seed/press-*.jpg`. Member names besides Keenan Harmon (Trumpet) were not in the kit —
  Saxophone/Violin/Bass/Drums have real photos but "To be announced" names; Trombone/Piano &
  Keys have neither yet. Upcoming Event dates are still SAMPLE placeholders — no real tour
  dates were supplied. Replace via admin as more info arrives.
- Local Python: system 3.9 venv at `.venv/` (Homebrew 3.14 ensurepip is broken on this Mac).

## Design Scores (visual-qa appends here)

| Date | Page | Code | H | T | S | C | M | Cr | Avg | Worst defect |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-12 | home | @D5 M3 C2 S3 | 8.5 | 9 | 8.5 | 8.5 | 9 | 8.5 | 8.7 | hero kicker sits on photo — legible on scrim, watch with future hero images |
| 2026-07-12 | band | @D5 M3 C2 S3 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | placeholder chairs until press kit lands (intentional) |
| 2026-07-12 | media | @D5 M3 C2 S3 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | pending plates until audio/video URLs arrive |
| 2026-07-12 | events | @D5 M3 C2 S3 | 8.5 | 9 | 8.5 | 8.5 | 8.5 | 8.5 | 8.6 | — |
| 2026-07-12 | booking | @D5 M3 C2 S3 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | date input renders native mm/dd/yyyy chrome |
| 2026-07-12 | news | @D5 M3 C2 S3 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 | only 2 sample posts; fills with real news |
| 2026-07-13 | home (hero rebuild) | @D5 M3 C2 S3 | 9 | 8 | 8 | 9 | 8 | 8 | 8.33 | hero content snug against fold on tablet/desktop — legible, not spacious |
| 2026-07-23 | home (light-forming merge) | @D5 M3 C2 S3 | 9 | 8.5 | 8.5 | 9 | 8.5 | 8.5 | 8.67 | mobile title still runs close to the trumpet bell (pre-existing framing, not from this edit) |
| 2026-07-23 | band (real roster) | @D5 M3 C2 S3 | 9 | 8.5 | 8.5 | 8.5 | 8.5 | 9 | 8.67 | Trombone + Denise's photo still placeholder — no source material supplied for either |
| 2026-07-23 | gallery (new photos) | @D5 M3 C2 S3 | 8.5 | 8.5 | 8.5 | 8.5 | 8 | 9 | 8.5 | motion verified via code read (hover-to-color, reveal stagger), not screenshot — static capture can't show it |
| 2026-07-23 | home (announcer hero rebuild) | @D5 M3 C2 S3 | 9 | 9 | 8 | 9 | 9 | 9 | 8.83 | announcer copy overlaps Keenan's face/trumpet at full colour — legible via glow shadows, thematically intentional, slightly busy |
| 2026-07-26 | home (about / info hub) | @D5 M3 C2 S3 | 9 | 8.5 | 8.5 | 9 | 8.5 | 8.5 | 8.67 | the lineup photo's warm wood wall still reads brighter than the night-gallery ground — dimmed + foot-gradient rather than true duotone |
| 2026-07-27 | home (about — wall title + serif body) | @D5 M3 C2 S3 | 9 | 9 | 9 | 9 | 8.5 | 8.5 | 8.83 | serif body copy is a deliberate break from the site's Jost body — reads editorial here, but it's the only page setting paragraphs in Fraunces |
| 2026-07-27 | home + news (poster cards) | @D5 M3 C2 S3 | 9 | 9 | 8.5 | 8.5 | 8.5 | 8.5 | 8.67 | no post has a real cover yet — every card shows the type plate, so the grid reads more uniform than it will with art |
| 2026-07-27 | band (five players + modal) | @D5 M3 C2 S3 | 9 | 8.5 | 8.5 | 9 | 8.5 | 9 | 8.75 | Denise has no photo (initial plate) and four players have a single press shot — the modal is built for sets |
| 2026-07-27 | band (roster cards + carousel) | @D5 M3 C2 S3 | 9 | 9 | 9 | 9 | 8.5 | 9 | 8.92 | four of five players have a single photo, so only Rich's card shows the carousel — the pattern is built for sets that don't exist yet |

QA note: screenshot with reduced-motion emulation (see visual-qa `shot.py`) — the intro
overlay and `.reveal` animations race normal full-page captures. Intro verified separately
mid-animation.
