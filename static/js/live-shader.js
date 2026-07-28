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

  /* Rebuilt AGAIN 2026-07-28 (fourth reference pass, user: "make the blobs
     more defined and circular like [the reference]"): the smooth monotonic
     ramp above (each stop only a small step lighter than the last) was
     never going to produce the reference's crisp nested-ring look, no
     matter how noise frequency/softness were tuned — LOW CONTRAST BETWEEN
     NEIGHBOURING BANDS is what made adjacent rings blend into 2-3 visually
     flat blobs instead of reading as concentric contours. The reference's
     own palette proves this: it alternates light/dark constantly (pink →
     purple → red → orange → cream → white, back down again), never
     drifting smoothly for more than one step. Rebuilt as a ZIGZAG through
     the same warm brand hues — every stop bounces between a deep and a
     bright tone — so each ring boundary is a real contrast edge, not a
     gradient. Still ends at the same amber peak (still under the event
     list's cream text), so the legibility cap holds. */
  var base = [
    tokenRgb('--color-bg', '#0E0D0B'),   // near-black ground
    [0.420, 0.110, 0.122],               // crimson (jump up)
    [0.102, 0.043, 0.055],               // deep aubergine (back down)
    [0.560, 0.310, 0.145],               // brass-orange (up, dialed back from 0.745 — too much of the
                                          // frame read bright/loud rather than moody with the old value)
    [0.196, 0.051, 0.075],               // deep wine (down)
    [0.560, 0.451, 0.235],               // brass, dialed back from the full token colour for the same reason
    [0.282, 0.063, 0.090],               // deep wine-crimson (down)
    [0.851, 0.651, 0.235],               // amber peak (up) — unchanged, still the legibility cap
  ];
  var stepsPerColor = 1;
  var palette = buildPalette(base, stepsPerColor).map(function (c) { return [c[0], c[1], c[2], 1]; });
  var paletteCount = palette.length; // (base.length - 1) * stepsPerColor + 1
  while (palette.length < 10) palette.push(palette[palette.length - 1]);

  var uniforms = {
    u_colors: palette,
    u_colorsCount: paletteCount,
    /* noiseScale 6.5 → 10 (2026-07-28, fourth pass, alongside the zigzag
       palette rewrite above): smaller/denser hills than the third pass
       used, matching the reference's fairly dense field of blobs rather
       than a few huge ones. Softness stays low (0.05) — the reference's
       ring boundaries are razor-edges, not soft blends. */
    u_softness: 0.05,
    u_noiseScale: 10,
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

  try {
    /* eslint-disable no-new */
    /* This 5th arg is ShaderMount's OWN playback speed — it drives u_time,
       separate from (and multiplicative with) the fragment shader's own
       u_speed uniform above. At the old value (0.08) the two multiplied
       out to a drift so slow it read as completely static within any
       normal viewing window (2026-07-27, user report) — not a rendering
       bug, just an over-cautious speed picked with nothing to compare it
       against. 1.5 here, combined with u_speed 0.65 and the fragment's
       internal *0.2 damping, drifts through a full slow cycle in ~25-30s —
       visibly alive but "unhurried," matching the brand voice. */
    new ShaderMount(host, simplexNoiseFragmentShader, uniforms, undefined, 1.5);
  } catch (e) {
    console.error(e);
    return;
  }

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
