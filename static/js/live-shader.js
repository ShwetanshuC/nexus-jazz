/* ============================================================
   LIVE-SHADER.JS — mounts behind any #live-shader-host element: the home
   page's "On stage next" section, and (2026-07-28) the /events/ (Live)
   index page's full date list, sharing the exact same look and behaviour.
   Safe to include on any page — it's a no-op if the page has no
   #live-shader-host.
   Mounts the vendored Paper Shaders engine with a hand-rolled simplex-noise
   fragment shader (static/vendor/paper-shaders/shaders/simplex-noise.js),
   matched to the real @paper-design/shaders-react `SimplexNoise` component
   the user referenced: bold posterized colour BANDS from raw noise (no fbm
   smoothing — that's what made the first pass read as smoky haze instead
   of contour blobs), not a two-colour fog blend.

   Colours are a warm stage-lighting-gel palette built from the site's own
   tokens (brass, a deeper wine/curtain red, cream) rather than the
   reference's red/pink/blue demo preset — vibrant like the reference, but
   the client's actual palette, not an arbitrary one.

   Falls back to the plain CSS background (no canvas) on WebGL failure or
   prefers-reduced-motion — the section already looks complete without it.
   ============================================================ */
import { ShaderMount } from '../vendor/paper-shaders/shader-mount.js';
import { simplexNoiseFragmentShader } from '../vendor/paper-shaders/shaders/simplex-noise.js';

(function () {
  'use strict';

  var host = document.getElementById('live-shader-host');
  if (!host) return;

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return;

  var gl = document.createElement('canvas').getContext('webgl2');
  if (!gl) return;

  function hexToRgb(hex, fallback) {
    var m = /^#([0-9a-f]{6})$/i.exec(hex || '');
    if (!m) return fallback;
    var h = m[1];
    return [
      parseInt(h.slice(0, 2), 16) / 255,
      parseInt(h.slice(2, 4), 16) / 255,
      parseInt(h.slice(4, 6), 16) / 255,
    ];
  }
  function tokenRgb(name, fallbackHex) {
    var v = '';
    try { v = getComputedStyle(document.documentElement).getPropertyValue(name).trim(); } catch (e) {}
    return hexToRgb(v, hexToRgb(fallbackHex, [1, 1, 1]));
  }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function lerpColor(a, b, t) {
    return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t), 1];
  }
  /* Mirrors the real component's stepsPerColor: N extra shades interpolated
     between each pair of listed base colours (not cyclic — the noise value
     is a linear 0..1 sweep, not a colour wheel). */
  function buildPalette(base, stepsPerColor) {
    var out = [];
    for (var i = 0; i < base.length - 1; i++) {
      for (var s = 0; s < stepsPerColor; s++) {
        out.push(lerpColor(base[i], base[i + 1], s / stepsPerColor));
      }
    }
    out.push(base[base.length - 1].concat(1).slice(0, 4));
    return out;
  }

  /* Rebuilt AGAIN 2026-07-28 (fifth pass, user: the zigzag palette below —
     alternating dark/bright every single stop, at high noise frequency —
     produced a dense field of small dark roundish holes peppered across a
     lighter ground. That's a textbook trypophobia trigger (clusters of
     small holes/bumps), which the user flagged directly by comparing
     against the reference: the reference has only a FEW large, well-
     separated dark accents on mostly-continuous lighter ground, not
     repeated small dark dots everywhere. Two changes fix this: (1) only
     ONE dark tone in the whole palette (the background itself) instead of
     three separate "deep" dips, so low noise values connect into large
     continuous dark channels instead of many isolated small holes; (2)
     noiseScale dropped hard (10 → 4.5, see below) for a few big islands
     instead of a dense field of small ones. Ring definition (the ORIGINAL
     ask) still comes from real contrast between neighbouring stops — that
     part of the fourth pass was right — it's the REPEATED dark dips and
     high frequency that caused the trigger pattern, not the contrast
     itself. */
  var base = [
    tokenRgb('--color-bg', '#0E0D0B'),   // near-black ground — the ONLY dark stop
    [0.420, 0.110, 0.122],               // crimson
    [0.612, 0.212, 0.125],               // crimson-orange
    [0.714, 0.353, 0.173],               // brass-brown
    tokenRgb('--color-primary', '#C29B52'), // brass
    [0.851, 0.651, 0.235],               // amber peak — unchanged, still the legibility cap
  ];
  var stepsPerColor = 1;
  var palette = buildPalette(base, stepsPerColor).map(function (c) { return [c[0], c[1], c[2], 1]; });
  var paletteCount = palette.length; // (base.length - 1) * stepsPerColor + 1
  while (palette.length < 10) palette.push(palette[palette.length - 1]);

  var uniforms = {
    u_colors: palette,
    u_colorsCount: paletteCount,
    /* noiseScale 10 → 4.5 (2026-07-28, fifth pass): the fourth pass's
       higher frequency made many small islands, which combined with that
       pass's alternating-dark palette produced the trypophobia-triggering
       cluster-of-holes look the user flagged. Lower frequency means fewer,
       bigger islands — still with clean ring definition inside each one
       (softness stays low, 0.05, for the same razor-edge boundaries), just
       not a dense repeated pattern of them. */
    u_softness: 0.05,
    u_noiseScale: 4.5,
    /* 0.65 → 0.39 → 0.234 (2026-07-27): overall morph speed down ~40%,
       then another ~40% on top (0.39 * 0.6) — this uniform scales `t`
       directly in the fragment shader, so it's a single-knob way to slow
       every z-time rate in there proportionally without re-tuning each
       one individually. */
    u_speed: 0.234,
    /* object-sizing uniforms the vertex shader requires (shader-sizing.js
       defaults) — u_scale must be 1, not 0, or the object box collapses.
       Distinct from u_noiseScale above (see simplex-noise.js). */
    u_fit: 2,
    u_scale: 1,
    u_rotation: 0,
    u_worldWidth: 0,
    u_worldHeight: 0,
    u_originX: 0.5,
    u_originY: 0.5,
    u_offsetX: 0,
    u_offsetY: 0,
  };

  var mount;
  try {
    /* This 5th arg is ShaderMount's OWN playback speed — it drives u_time,
       separate from (and multiplicative with) the fragment shader's own
       u_speed uniform above. At the old value (0.08) the two multiplied
       out to a drift so slow it read as completely static within any
       normal viewing window (2026-07-27, user report) — not a rendering
       bug, just an over-cautious speed picked with nothing to compare it
       against. 1.5 here, combined with u_speed 0.65 and the fragment's
       internal *0.2 damping, drifts through a full slow cycle in ~25-30s —
       visibly alive but "unhurried," matching the brand voice. */
    mount = new ShaderMount(host, simplexNoiseFragmentShader, uniforms, undefined, 1.5);
  } catch (e) {
    console.error(e);
    return;
  }

  /* 2026-07-28: the library's ResizeObserver sizes the WebGL canvas using
     the entry's `devicePixelContentBoxSize` when the browser reports one
     ("this.devicePixelsSupported = true" in shader-mount.js) — but that
     value came back WRONG in testing (reported ~2000×455 device px for a
     2000×743 CSS-px, 2dpr section, i.e. no dpr multiplier on width and a
     completely unrelated number for height — roughly 1/8 the pixels the
     canvas should have). Every resize re-triggers the same bad reading, so
     the blobs render soft/low-res permanently, not just on first paint.
     The library's OWN fallback path (plain `window.devicePixelRatio` ×
     the CSS size from `borderBoxSize`, which reported correctly) is
     reliable, so force it to always take that path by making
     devicePixelsSupported permanently read false — the resize handler
     is unmodified, it just never takes the buggy branch. */
  try {
    Object.defineProperty(mount, 'devicePixelsSupported', {
      get: function () { return false; },
      set: function () {},
    });
    mount.handleResize();
  } catch (e) {}

  /* At full strength the palette's brighter bands (amber/cream) read as a
     blown-out poster and the event rows lose contrast against them — same
     problem the hero solves with its own scrim. Darken uniformly here so
     the shader reads as moody jewel-tones behind the list, not a light
     background the text has to fight. Inserted right after the canvas
     (ShaderMount prepends the canvas as host's first child) so it sits
     above the shader but below the section's own content. */
  var scrim = document.createElement('div');
  scrim.className = 'live-shader__scrim';
  scrim.setAttribute('aria-hidden', 'true');
  host.insertBefore(scrim, host.children[1] || null);
})();
