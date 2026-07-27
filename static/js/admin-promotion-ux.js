(function () {
  'use strict';

  function isPromotionPage() {
    return /\/promotions\/promotion\/(add\/|\d+\/change\/)/.test(window.location.pathname);
  }

  // ── Utilities ─────────────────────────────────────────────────────────────────

  function findFieldsetByTitle(title) {
    var t = title.trim().toLowerCase();
    return Array.from(document.querySelectorAll('fieldset.module')).find(function (fs) {
      var h2 = fs.querySelector('h2');
      return h2 && h2.textContent.trim().toLowerCase() === t;
    }) || null;
  }

  function findFormRowForField(fieldName) {
    var el = document.querySelector("[name='" + fieldName + "']");
    if (!el) return null;
    return el.closest('.form-row') || el.parentNode;
  }

  function getSlug() {
    var slugInput = document.querySelector("input[name='slug']");
    return slugInput ? (slugInput.value || '').trim() : '';
  }

  function triggerFocalRefresh() {
    document.querySelectorAll('[data-focal-picker-refresh]').forEach(function (el) {
      if (el._focalRefresh) el._focalRefresh();
    });
  }

  function hasActiveCustomPage() {
    var inlineGroup = document.getElementById('page-group');
    if (!inlineGroup) return false;
    var rows = Array.from(inlineGroup.querySelectorAll('.inline-related:not(.empty-form)'));
    return rows.some(function (row) {
      var del = row.querySelector('input[name$="-DELETE"]');
      return !del || !del.checked;
    });
  }

  // ── 1. Template rules ─────────────────────────────────────────────────────────

  var TEMPLATE_DESCRIPTIONS = {
    hero:         'Full-width banner with a large image and bold headline — the most prominent layout on the promotions page.',
    spotlight:    'Image on one side, headline and text on the other — great for a focused, editorial feel.',
    card:         'A standard card in the promotion grid — compact and clean.',
    ribbon:       'A slim accent strip with a title and CTA button, but no image.',
    image_banner: 'Full image displayed edge-to-edge with no text overlay — ideal for supplied banner graphics.',
  };

  var ribbonNote = null;
  var templateDescEl = null;

  function applyTemplateRules(template) {
    var imageFieldset = findFieldsetByTitle('Image');

    if (template === 'ribbon') {
      if (imageFieldset) imageFieldset.style.display = 'none';
      if (!ribbonNote) {
        ribbonNote = document.createElement('div');
        ribbonNote.id = 'mt-ribbon-note';
        ribbonNote.style.cssText = [
          'margin:0 0 12px',
          'padding:9px 14px',
          'background:#1a1714',
          'border:1px solid #3b342f',
          'border-left:3px solid #3730a3',
          'border-radius:0 2px 2px 0',
          'font-size:12px',
          'color:#c8b8a8',
          'line-height:1.5',
        ].join(';');
        ribbonNote.innerHTML =
          '<strong style="color:#d4d0ff;">Ribbon banners don\'t use an image.</strong> ' +
          'The title and CTA button are shown on a solid colour background. ' +
          'Switch to Hero, Spotlight, or Card to add an image.';
      }
      var bannerStyleFieldset = findFieldsetByTitle('Banner Style');
      var insertAfter = bannerStyleFieldset || imageFieldset;
      if (insertAfter && !insertAfter.parentNode.contains(ribbonNote)) {
        insertAfter.parentNode.insertBefore(ribbonNote, insertAfter.nextSibling);
      }
    } else {
      if (imageFieldset) imageFieldset.style.display = '';
      if (ribbonNote && ribbonNote.parentNode) ribbonNote.parentNode.removeChild(ribbonNote);
    }

    var bgColorRow = findFormRowForField('bg_color');
    var noCropRow  = findFormRowForField('image_no_crop');
    var isImgBanner = (template === 'image_banner');
    if (bgColorRow) bgColorRow.style.display  = isImgBanner ? 'none' : '';
    if (noCropRow)  noCropRow.style.display   = isImgBanner ? 'none' : '';

    var templateSelect = document.querySelector("select[name='template']");
    if (templateSelect) {
      if (!templateDescEl) {
        templateDescEl = document.createElement('p');
        templateDescEl.id = 'mt-template-desc';
        templateDescEl.style.cssText = [
          'margin:8px 0 0',
          'padding:7px 12px',
          'background:#1a1714',
          'border-left:3px solid #6b5e57',
          'border-radius:0 2px 2px 0',
          'font-size:12px',
          'color:#c8b8a8',
          'line-height:1.5',
        ].join(';');
        var tRow = templateSelect.closest('.form-row') || templateSelect.parentNode;
        if (tRow && tRow.parentNode) tRow.parentNode.insertBefore(templateDescEl, tRow.nextSibling);
      }
      var desc = TEMPLATE_DESCRIPTIONS[template] || '';
      templateDescEl.textContent = desc;
      templateDescEl.style.display = desc ? '' : 'none';
    }

    triggerFocalRefresh();
  }

  function bindTemplateSelect() {
    var templateSelect = document.querySelector("select[name='template']");
    if (!templateSelect) return;
    applyTemplateRules(templateSelect.value);
    templateSelect.addEventListener('change', function () {
      applyTemplateRules(this.value);
    });
  }

  // ── 2. image_no_crop sync ──────────────────────────────────────────────────────

  function bindNoCropCheckbox() {
    var cb = document.querySelector("input[name='image_no_crop']");
    if (!cb) return;
    cb.addEventListener('change', triggerFocalRefresh);
  }

  // ── 3. CTA ↔ Custom Landing Page mutual exclusivity ───────────────────────────

  var ctaNote = null;

  function applyCtaMutualExclusivity() {
    var active = hasActiveCustomPage();
    var ctaUrlRow    = findFormRowForField('cta_url');
    var ctaNewTabRow = findFormRowForField('cta_opens_in_new_tab');
    var ctaHelper    = document.getElementById('mt-cta-url-helper');

    if (active) {
      if (ctaUrlRow)    ctaUrlRow.style.display    = 'none';
      if (ctaNewTabRow) ctaNewTabRow.style.display = 'none';
      if (ctaHelper)    ctaHelper.style.display    = 'none';

      var ctaFieldset = findFieldsetByTitle('Call-to-Action Button');
      if (ctaFieldset) {
        if (!ctaNote) {
          ctaNote = document.createElement('div');
          ctaNote.id = 'mt-cta-page-note';
          ctaNote.style.cssText = [
            'margin:0 0 10px',
            'padding:10px 14px',
            'background:#0d1a0d',
            'border:1px solid #1e3e1e',
            'border-left:3px solid #2d7d2d',
            'border-radius:0 2px 2px 0',
            'font-size:12px',
            'color:#a8d4a8',
            'line-height:1.6',
          ].join(';');
        }
        var slug = getSlug();
        var pageUrl = slug ? '/promotions/' + slug + '/' : '/promotions/&lt;slug&gt;/';
        ctaNote.innerHTML =
          '<strong style="color:#c8f0c8;">Custom Landing Page active</strong> — ' +
          'the CTA button automatically links to ' +
          '<code style="background:#081408;padding:1px 5px;border-radius:2px;font-size:11px;color:#a8d4a8;">' +
          pageUrl + '</code>. ' +
          'URL and "open in new tab" settings are managed inside the custom page editor.';

        if (!ctaFieldset.contains(ctaNote)) {
          var ctaTextRow = findFormRowForField('cta_text');
          if (ctaTextRow && ctaTextRow.parentNode) {
            ctaTextRow.parentNode.insertBefore(ctaNote, ctaTextRow.nextSibling);
          } else {
            ctaFieldset.insertBefore(ctaNote, ctaFieldset.firstChild);
          }
        }
      }
    } else {
      if (ctaUrlRow)    ctaUrlRow.style.display    = '';
      if (ctaNewTabRow) ctaNewTabRow.style.display = '';
      if (ctaHelper)    ctaHelper.style.display    = '';
      if (ctaNote && ctaNote.parentNode) ctaNote.parentNode.removeChild(ctaNote);
    }
  }

  function bindDeleteCheckboxListeners(inlineGroup) {
    inlineGroup.querySelectorAll('input[name$="-DELETE"]').forEach(function (cb) {
      if (cb._mtBound) return;
      cb._mtBound = true;
      cb.addEventListener('change', applyCtaMutualExclusivity);
    });
  }

  function setupCustomPageSync() {
    var inlineGroup = document.getElementById('page-group');
    if (!inlineGroup) return;

    applyCtaMutualExclusivity();

    var observer = new MutationObserver(function () {
      applyCtaMutualExclusivity();
      bindDeleteCheckboxListeners(inlineGroup);
    });
    observer.observe(inlineGroup, { childList: true, subtree: true });

    bindDeleteCheckboxListeners(inlineGroup);
  }

  // ── 4. Slug URL preview ───────────────────────────────────────────────────────

  function setupSlugPreview() {
    var slugInput = document.querySelector("input[name='slug']");
    if (!slugInput) return;

    var preview = document.createElement('p');
    preview.id = 'mt-slug-preview';
    preview.style.cssText = [
      'margin:6px 0 0',
      'font-size:12px',
      'color:#6b5e57',
      'font-family:monospace',
    ].join(';');

    function update() {
      var slug = slugInput.value.trim();
      preview.textContent = slug ? '/promotions/' + slug + '/' : '';
      preview.style.display = slug ? '' : 'none';
      if (ctaNote && ctaNote.parentNode) applyCtaMutualExclusivity();
    }

    slugInput.addEventListener('input', update);
    update();

    var row = slugInput.closest('.form-row') || slugInput.parentNode;
    if (row && row.parentNode) row.parentNode.insertBefore(preview, row.nextSibling);
  }

  // ── 5. CTA text quick-fill ────────────────────────────────────────────────────

  function buildCtaTextHelper() {
    var ctaTextInput = document.querySelector("input[name='cta_text']");
    if (!ctaTextInput) return;

    var presets = ['Shop Now', 'Learn More', 'View Catalog', 'See Deals', 'Contact Us', 'Book Now'];

    var chips = document.createElement('div');
    chips.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;';

    presets.forEach(function (text) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = text;
      btn.style.cssText = [
        'padding:3px 10px',
        'border:1px solid #3b342f',
        'border-radius:3px',
        'background:#1e1a17',
        'color:#c8b8a8',
        'font-size:11px',
        'font-family:inherit',
        'cursor:pointer',
        'line-height:1.6',
        'transition:border-color 0.15s,color 0.15s,background 0.15s',
      ].join(';');
      btn.addEventListener('mouseenter', function () {
        btn.style.borderColor = '#3730a3';
        btn.style.background = '#0e0d2a';
        btn.style.color = '#c7d2fe';
      });
      btn.addEventListener('mouseleave', function () {
        btn.style.borderColor = '#3b342f';
        btn.style.background = '#1e1a17';
        btn.style.color = '#c8b8a8';
      });
      btn.addEventListener('click', function () {
        ctaTextInput.value = text;
        ctaTextInput.dispatchEvent(new Event('input', { bubbles: true }));
        ctaTextInput.focus();
      });
      chips.appendChild(btn);
    });

    var row = ctaTextInput.closest('.form-row') || ctaTextInput.parentNode;
    if (row && row.parentNode) row.parentNode.insertBefore(chips, row.nextSibling);
  }

  // ── 6. CTA URL quick-fill ─────────────────────────────────────────────────────

  function buildCtaUrlHelper() {
    var ctaUrlInput = document.querySelector("input[name='cta_url']");
    if (!ctaUrlInput) return;

    var presets = [
      { label: 'All Catalog',      value: '/catalog/' },
      { label: 'New Items',        value: '/catalog/new/' },
      { label: 'Pre-Owned Items',  value: '/catalog/preowned/' },
      { label: 'Promotions Page',  value: '/promotions/' },
      { label: 'Services',         value: '/services/' },
      { label: 'Contact',          value: '/contact/' },
    ];

    var wrap = document.createElement('div');
    wrap.id = 'mt-cta-url-helper';
    wrap.style.cssText = 'margin-top:10px;';

    var header = document.createElement('p');
    header.style.cssText = 'margin:0 0 7px;font-size:11px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:#8c7d74;';
    header.textContent = 'Quick-fill a local page';
    wrap.appendChild(header);

    var chips = document.createElement('div');
    chips.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;';
    wrap.appendChild(chips);

    presets.forEach(function (preset) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = preset.label;
      btn.style.cssText = [
        'padding:4px 12px',
        'border:1px solid #3b342f',
        'border-radius:3px',
        'background:#1e1a17',
        'color:#c8b8a8',
        'font-size:12px',
        'font-family:inherit',
        'cursor:pointer',
        'line-height:1.6',
        'transition:border-color 0.15s,color 0.15s,background 0.15s',
      ].join(';');
      btn.addEventListener('mouseenter', function () {
        btn.style.borderColor = '#3730a3';
        btn.style.background = '#0e0d2a';
        btn.style.color = '#c7d2fe';
      });
      btn.addEventListener('mouseleave', function () {
        btn.style.borderColor = '#3b342f';
        btn.style.background = '#1e1a17';
        btn.style.color = '#c8b8a8';
      });
      btn.addEventListener('click', function () {
        ctaUrlInput.value = preset.value;
        ctaUrlInput.dispatchEvent(new Event('change', { bubbles: true }));
        ctaUrlInput.focus();
      });
      chips.appendChild(btn);
    });

    var note = document.createElement('p');
    note.style.cssText = 'margin:8px 0 0;font-size:11px;color:#6b5e57;';
    note.textContent = 'For an external website, type the full URL directly in the field above (e.g. https://example.com).';
    wrap.appendChild(note);

    var row = ctaUrlInput.closest('.form-row') || ctaUrlInput.parentNode;
    if (row && row.parentNode) row.parentNode.insertBefore(wrap, row.nextSibling);
  }

  // ── Init ──────────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function () {
    if (!isPromotionPage()) return;
    bindTemplateSelect();
    bindNoCropCheckbox();
    setupSlugPreview();
    buildCtaTextHelper();
    buildCtaUrlHelper();
    setupCustomPageSync();
  });

})();
