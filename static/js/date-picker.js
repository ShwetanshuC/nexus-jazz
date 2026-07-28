/* ============================================================
   DATE-PICKER.JS — replaces the browser's native date-input popup (OS
   chrome, can't be restyled) with a custom dropdown that matches the
   site's theme. Progressive enhancement: the real <input type="date">
   stays in the DOM and is what actually submits with the form — this
   just hides it visually and drives its value from a styled trigger +
   calendar panel. With JS off, the native date input and its native
   picker still work exactly as before.
   ============================================================ */
(function () {
  'use strict';

  var inputs = document.querySelectorAll('input[type="date"].form-control');
  if (!inputs.length) return;

  var MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];
  var WEEKDAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
  var CALENDAR_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" ' +
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ' +
    'aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/></svg>';

  inputs.forEach(setup);

  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function toISO(y, m, d) { return y + '-' + pad(m + 1) + '-' + pad(d); }
  function formatDisplay(y, m, d) { return MONTH_NAMES[m].slice(0, 3) + ' ' + d + ', ' + y; }

  function setup(nativeInput) {
    var wrap = document.createElement('div');
    wrap.className = 'date-picker';

    var trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'date-picker__trigger form-control';
    trigger.setAttribute('aria-haspopup', 'dialog');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.innerHTML = '<span class="date-picker__value">Select a date</span>' +
      '<span class="date-picker__icon">' + CALENDAR_ICON + '</span>';

    var panel = document.createElement('div');
    panel.className = 'date-picker__panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Choose a date');
    panel.hidden = true;

    nativeInput.parentNode.insertBefore(wrap, nativeInput);
    wrap.appendChild(nativeInput);
    wrap.appendChild(trigger);
    wrap.appendChild(panel);
    nativeInput.classList.add('date-picker__native');
    nativeInput.setAttribute('tabindex', '-1');
    nativeInput.setAttribute('aria-hidden', 'true');

    var today = new Date();
    var view = { y: today.getFullYear(), m: today.getMonth() };
    var selected = null; // {y, m, d} or null

    function readNativeValue() {
      var v = nativeInput.value; // Django DateField posts/reads YYYY-MM-DD
      var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || '');
      var valueEl = trigger.querySelector('.date-picker__value');
      if (m) {
        selected = { y: +m[1], m: +m[2] - 1, d: +m[3] };
        view = { y: selected.y, m: selected.m };
        valueEl.textContent = formatDisplay(selected.y, selected.m, selected.d);
        trigger.classList.add('has-value');
      } else {
        selected = null;
        valueEl.textContent = 'Select a date';
        trigger.classList.remove('has-value');
      }
    }
    readNativeValue();

    function renderPanel() {
      var y = view.y, m = view.m;
      var firstDow = new Date(y, m, 1).getDay();
      var daysInMonth = new Date(y, m + 1, 0).getDate();
      var daysInPrevMonth = new Date(y, m, 0).getDate();

      var cells = [];
      for (var i = 0; i < firstDow; i++) {
        cells.push({ day: daysInPrevMonth - firstDow + i + 1, muted: true });
      }
      for (var d = 1; d <= daysInMonth; d++) cells.push({ day: d, muted: false });
      var trailing = 1;
      while (cells.length < 42) cells.push({ day: trailing++, muted: true });

      var html = '<div class="date-picker__head">' +
        '<button type="button" class="date-picker__nav" data-nav="-1" aria-label="Previous month">&#8249;</button>' +
        '<span class="date-picker__month">' + MONTH_NAMES[m] + ' ' + y + '</span>' +
        '<button type="button" class="date-picker__nav" data-nav="1" aria-label="Next month">&#8250;</button>' +
        '</div><div class="date-picker__grid">';
      WEEKDAYS.forEach(function (wd) { html += '<span class="date-picker__dow">' + wd + '</span>'; });
      cells.forEach(function (cell) {
        var isToday = !cell.muted && y === today.getFullYear() && m === today.getMonth() && cell.day === today.getDate();
        var isSelected = !cell.muted && selected && selected.y === y && selected.m === m && selected.d === cell.day;
        var cls = 'date-picker__day';
        if (cell.muted) cls += ' is-muted';
        if (isToday) cls += ' is-today';
        if (isSelected) cls += ' is-selected';
        html += '<button type="button" class="' + cls + '"' +
          (cell.muted ? ' tabindex="-1"' : ' data-day="' + cell.day + '"') + '>' + cell.day + '</button>';
      });
      html += '</div>';
      panel.innerHTML = html;
    }

    function open() {
      renderPanel();
      panel.hidden = false;
      trigger.setAttribute('aria-expanded', 'true');
      document.addEventListener('click', onDocClick, true);
      document.addEventListener('keydown', onKeydown);
    }
    function close() {
      panel.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      document.removeEventListener('click', onDocClick, true);
      document.removeEventListener('keydown', onKeydown);
    }
    function onDocClick(e) { if (!wrap.contains(e.target)) close(); }
    function onKeydown(e) { if (e.key === 'Escape') { close(); trigger.focus(); } }

    trigger.addEventListener('click', function () {
      if (panel.hidden) open(); else close();
    });

    panel.addEventListener('click', function (e) {
      var navBtn = e.target.closest('[data-nav]');
      if (navBtn) {
        var dir = parseInt(navBtn.getAttribute('data-nav'), 10);
        view.m += dir;
        if (view.m < 0) { view.m = 11; view.y--; }
        if (view.m > 11) { view.m = 0; view.y++; }
        renderPanel();
        return;
      }
      var dayBtn = e.target.closest('.date-picker__day:not(.is-muted)');
      if (dayBtn) {
        var day = parseInt(dayBtn.getAttribute('data-day'), 10);
        selected = { y: view.y, m: view.m, d: day };
        nativeInput.value = toISO(view.y, view.m, day);
        nativeInput.dispatchEvent(new Event('change', { bubbles: true }));
        trigger.querySelector('.date-picker__value').textContent = formatDisplay(view.y, view.m, day);
        trigger.classList.add('has-value');
        close();
        trigger.focus();
      }
    });
  }
})();
