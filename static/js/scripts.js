/* Nexus Jazz — site JS. Vanilla, progressive enhancement; page works with JS off. */

/* ---------- Scroll reveal (M2) — pairs with .reveal in theme.css ---------- */
(() => {
  const els = document.querySelectorAll('.reveal');
  if (!els.length || !('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('visible'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
  els.forEach(el => io.observe(el));
})();

/* ---------- Nav ground on scroll ----------
   The nav is transparent over the hero photo (deference — the picture leads).
   Once the hero has passed, the links would sit on whatever the section is, so
   the nav fades in its own ground. That band is masked at the foot rather than
   ruled, so there's no hard edge; see .nav::before in nexus.css. */
(() => {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  const hero = document.querySelector('.hero-stage');
  // Off the home page there's no hero, so the ground comes in almost at once.
  const threshold = () => (hero ? hero.offsetHeight - nav.offsetHeight : 8);
  let ticking = false;
  const update = () => {
    nav.classList.toggle('is-grounded', window.scrollY > threshold());
    ticking = false;
  };
  const onScroll = () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  };
  update();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
})();

/* ---------- Player photo carousels (band page) ----------
   Adapted from the Miller Piano hero carousel (same data-carousel-* API):
   crossfade slides, prev/next arrows, dots. Manual only — no autoplay, since
   these sit next to bios people are reading. With JS off every slide is
   visible in flow, so no picture is ever hidden. */
(() => {
  document.querySelectorAll('[data-carousel]').forEach(root => {
    const slides = Array.from(root.querySelectorAll('[data-carousel-slide]'));
    const dots = Array.from(root.querySelectorAll('[data-carousel-dot]'));
    const prev = root.querySelector('[data-carousel-prev]');
    const next = root.querySelector('[data-carousel-next]');
    if (slides.length < 2) return;

    root.classList.add('is-live');   // CSS stacks the slides only once JS runs
    let index = 0;

    const setIndex = (i) => {
      index = (i + slides.length) % slides.length;
      slides.forEach((el, idx) => {
        el.classList.toggle('is-current', idx === index);
        el.setAttribute('aria-hidden', idx === index ? 'false' : 'true');
      });
      dots.forEach((dot, idx) => {
        dot.classList.toggle('is-current', idx === index);
        dot.setAttribute('aria-current', idx === index ? 'true' : 'false');
      });
    };

    if (prev) prev.addEventListener('click', () => setIndex(index - 1));
    if (next) next.addEventListener('click', () => setIndex(index + 1));
    dots.forEach(dot => dot.addEventListener('click', () => {
      setIndex(Number(dot.getAttribute('data-carousel-dot') || 0));
    }));
    // arrow keys when the carousel has focus inside it
    root.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') { setIndex(index - 1); }
      if (e.key === 'ArrowRight') { setIndex(index + 1); }
    });

    setIndex(0);
  });
})();

/* ---------- Gallery lightbox ---------- */
(() => {
  const dlg = document.querySelector('.gallery-modal');
  if (!dlg) return;
  const items = Array.from(document.querySelectorAll('.gallery-item'));
  if (!items.length) return;

  const img = dlg.querySelector('img');
  const prevBtn = dlg.querySelector('.modal-nav--prev');
  const nextBtn = dlg.querySelector('.modal-nav--next');
  let index = 0;

  const show = i => {
    index = (i + items.length) % items.length;
    const b = items[index];
    img.src = b.dataset.full;
    img.alt = b.getAttribute('aria-label') || '';
  };

  items.forEach((b, i) => b.addEventListener('click', () => {
    show(i);
    dlg.showModal();
  }));

  if (items.length > 1) {
    prevBtn.addEventListener('click', e => { e.stopPropagation(); show(index - 1); });
    nextBtn.addEventListener('click', e => { e.stopPropagation(); show(index + 1); });
    dlg.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft') show(index - 1);
      else if (e.key === 'ArrowRight') show(index + 1);
    });
  } else {
    prevBtn.hidden = true;
    nextBtn.hidden = true;
  }

  dlg.querySelector('.modal-close').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
})();
