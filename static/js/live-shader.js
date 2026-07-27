/* ============================================================
   LIVE-SHADER.JS — home page only ("On stage next" section).
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

  /* Stage-lighting-gel palette, darkest to brightest: the site's own near-
     black ground, a deep wine/curtain red, brass (the site's one accent),
     a brighter amber, and cream (the site's light text colour) as the hot
     highlight — same "dark-to-bright" shape as the reference preset. */
  var base = [
    tokenRgb('--color-bg', '#0E0D0B'),
    [0.42, 0.11, 0.16],                 // wine/curtain red
    tokenRgb('--color-primary', '#C29B52'),
    [0.91, 0.64, 0.24],                 // bright amber
    tokenRgb('--color-text', '#F2EFE6'),
  ];
  var stepsPerColor = 2;
  var palette = buildPalette(base, stepsPerColor).map(function (c) { return [c[0], c[1], c[2], 1]; });
  var paletteCount = palette.length; // (base.length - 1) * stepsPerColor + 1
  while (palette.length < 10) palette.push(palette[palette.length - 1]);

  var uniforms = {
    u_colors: palette,
    u_colorsCount: paletteCount,
    /* Slightly softened vs. the reference's hard edge: high-frequency hard
       edges read as visual noise once real text sits on top, even where
       character-level contrast technically passes WCAG. u_noiseScale of
       0.35 (previous pass) made single blobs bigger than the section
       itself; 0.85 keeps them a readable size — a handful of shapes
       visible at once, not one wall of one colour. */
    u_softness: 0.18,
    u_noiseScale: 0.85,
    u_speed: 0.5,
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
    new ShaderMount(host, simplexNoiseFragmentShader, uniforms, undefined, 0.08);
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
