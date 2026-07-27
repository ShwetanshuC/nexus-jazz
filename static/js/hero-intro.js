/* ============================================================
   HERO-INTRO.JS — home only. Progressive enhancement for the
   "announcer's introduction" hero (see .hero-stage in nexus.css).

   The phase machine itself lives in a synchronous inline script in
   home.html so it can never fail to load and strand the page. This
   file only ADDS polish:
     1. Measures each announced line's centre and parks its follow-spot
        exactly on it (CSS falls back to sensible % positions without it).
     2. Wires the "Replay intro" control.
   (A dev BPM slider lived here while the tempo was being chosen; it was
   removed 2026-07-27 once the client settled on 38 BPM. ?bpm=NN still works
   for one-off checks.)
   Everything here is optional — if it never runs, the hero still plays
   and still composes correctly.
   ============================================================ */
(function () {
  'use strict';

  var stage = document.getElementById('hero-stage');
  if (!stage) return;
  var root = document.documentElement;

  // Only the two black-stage lines get a spot; the last line is lit by the
  // picture coming up, so there is no third pool to park.
  var lines = ['.hero-stage__welcome', '.hero-stage__name']
    .map(function (s) { return stage.querySelector(s); });

  function measure() {
    var hb = stage.getBoundingClientRect();
    if (!hb.height || !hb.width) return;
    lines.forEach(function (el, i) {
      if (!el) return;
      var r = el.getBoundingClientRect();
      // Centre each spot on its line's midpoint (both axes) so the pools
      // land on the type wherever it sits.
      var top = ((r.top + r.height / 2 - hb.top) / hb.height) * 100;
      var left = ((r.left + r.width / 2 - hb.left) / hb.width) * 100;
      stage.style.setProperty('--spot' + (i + 1) + '-top', top.toFixed(2) + '%');
      stage.style.setProperty('--spot' + (i + 1) + '-left', left.toFixed(2) + '%');
    });
  }

  measure();
  // Fonts change the line metrics; re-measure once they settle, plus a few
  // passes to catch late layout shifts.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
  [120, 400, 900, 1500].forEach(function (t) { setTimeout(measure, t); });
  window.addEventListener('resize', measure);

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // One beat = one announced line; BPM is the single speed dial (set by the
  // inline script in home.html, which also writes --beat for the CSS fades).
  function bpm() { return window.HERO_BPM || window.HERO_BPM_DEFAULT || 38; }
  var timers = [];
  function play(rate) {
    timers.forEach(clearTimeout);
    timers = [];
    var beat = 60000 / rate;
    root.style.setProperty('--beat', (beat / 1000).toFixed(3) + 's');
    root.setAttribute('data-phase', '0');
    measure();
    [1, 2, 3].forEach(function (phase) {
      timers.push(setTimeout(function () {
        root.setAttribute('data-phase', String(phase));
      }, beat * phase));
    });
  }

  var replay = document.getElementById('hero-replay');
  if (replay && !reduce) {
    replay.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      play(bpm());
    });
  }

})();
