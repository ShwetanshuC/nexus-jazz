(function () {
  "use strict";

  // Container dimensions [width, height] in px representing actual rendered size on the live site.
  // These are at the maximum desktop viewport (1440px) and typical mobile (390×844px, iPhone 14).
  // Desktop heights come directly from Tailwind classes in each template:
  //   heroslide       → min-h-[85vh] at 900px screen ≈ 765px
  //   servicepage     → min-h-[500px]
  //   aboutpage       → min-h-[560px]
  //   testimonials    → min-h-[520px]
  //   resources       → py-14 section with ~130px content ≈ 244px total
  //   listing detail  → h-[360px]
  //   promotion card  → h-72 (288px) at max-w-7xl (1280px)
  //   promotion hero  → min-h-[420px] full-width
  //   promotion spot  → min-h-[420px] at ~640px (half of 1280px grid)
  //   promo page hero → h-[380px] full-width (promotion_detail.html)
  //   mobile hero     → min-h-[65vh] at 844px ≈ 549px, 390px wide
  var CONFIGS = {
    heroslide:               { desktop: [1440, 765], mobile: [390, 549] },
    servicepagecontent:      { desktop: [1440, 500], mobile: null },
    aboutpagecontent:        { desktop: [1440, 560], mobile: null },
    testimonialspagecontent: { desktop: [1440, 520], mobile: null },
    resourcespagecontent:    { desktop: [1440, 244], mobile: null },
    listing:                 { desktop: [1440, 360], mobile: null },
    promotionpage:           { desktop: [1440, 380], mobile: null },
    // Promotion dims are template-dependent; see getPromotionDims().
    // Mobile widths use 375px (common phone CSS width) with the mobile
    // Tailwind breakpoint heights (h-60 = 240px, min-h-[300px], min-h-[420px]).
    promotion_card:          { desktop: [1280, 288], mobile: [375, 240] },
    promotion_hero:          { desktop: [1440, 420], mobile: [375, 420] },
    promotion_spotlight:     { desktop: [640,  420], mobile: [375, 300] },
  };

  var PREVIEW_MAX_W     = 440;
  var PREVIEW_MAX_IMG_H = 360;

  var COLOR_DESKTOP = "#8B1A1A";
  var COLOR_MOBILE  = "#1e3a6e";
  var GLOW_DESKTOP  = "rgba(139,26,26,0.55)";
  var GLOW_MOBILE   = "rgba(30,58,110,0.55)";

  // ── Config detection ────────────────────────────────────────────────────────
  function getPromotionDims(isMobile) {
    // Read the currently selected template from the form to return accurate dims.
    var templateSelect = document.querySelector("select[name='template']");
    var tpl = templateSelect ? templateSelect.value : "card";
    var key;
    if (tpl === "hero")         key = "promotion_hero";
    else if (tpl === "spotlight") key = "promotion_spotlight";
    else                          key = "promotion_card";
    var cfg = CONFIGS[key];
    return isMobile ? (cfg.mobile || cfg.desktop) : cfg.desktop;
  }

  // Returns true when the image should be shown full-size with no crop.
  // Applies when "Full image — no crop" is checked, or the template is image_banner.
  function getNoCropActive() {
    var cb = document.querySelector("input[name='image_no_crop']");
    if (cb && cb.checked) return true;
    var templateSelect = document.querySelector("select[name='template']");
    if (templateSelect && templateSelect.value === "image_banner") return true;
    return false;
  }

  function detectModelConfig(inputName) {
    var path = window.location.pathname.toLowerCase();
    var isMobile = inputName.indexOf("_mobile") !== -1;

    if (path.indexOf("heroslide") !== -1) {
      return isMobile ? CONFIGS.heroslide.mobile : CONFIGS.heroslide.desktop;
    }
    if (path.indexOf("servicepagecontent")      !== -1) return CONFIGS.servicepagecontent.desktop;
    if (path.indexOf("aboutpagecontent")         !== -1) return CONFIGS.aboutpagecontent.desktop;
    if (path.indexOf("testimonialspagecontent")  !== -1) return CONFIGS.testimonialspagecontent.desktop;
    if (path.indexOf("resourcespagecontent")     !== -1) return CONFIGS.resourcespagecontent.desktop;
    // promotionpage must be checked before promotion (it's a substring match)
    if (path.indexOf("promotionpage")            !== -1) return CONFIGS.promotionpage.desktop;
    if (path.indexOf("promotion")                !== -1) return getPromotionDims(isMobile);
    if (path.indexOf("listing")                  !== -1) return CONFIGS.listing.desktop;
    return CONFIGS.listing.desktop; // safe fallback
  }

  function getViewDims(inputName) {
    var isMobile = inputName.indexOf("_mobile") !== -1;
    var dims = detectModelConfig(inputName);
    return { dims: dims, isMobile: isMobile };
  }

  // ── File input selectors ─────────────────────────────────────────────────────
  var DESKTOP_FILE_SELECTORS = [
    "input[type='file'][name='hero_image']",
    "input[type='file'][name='image']",
    "input[type='file'][name='image_file']",
    "input[type='file'][name$='hero_image']",
    "input[type='file'][name$='-image']",
  ];
  var MOBILE_FILE_SELECTORS = [
    "input[type='file'][name='image_mobile']",
    "input[type='file'][name$='-image_mobile']",
  ];
  var URL_INPUT_SELECTORS = [
    "input[name='hero_image_url']",
    "input[name='image_url']",
    "input[name$='hero_image_url']",
    "input[name$='-hero_image_url']",
    "input[name$='-image_url']",
    "input[name$='_image_url']",
  ];

  function findFirst(container, selectors) {
    for (var i = 0; i < selectors.length; i++) {
      var el = container.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }

  // ── SVG icons ────────────────────────────────────────────────────────────────
  var ICON_DESKTOP = [
    '<svg width="13" height="10" viewBox="0 0 13 10" fill="none">',
    '<rect x="0.5" y="0.5" width="12" height="7.5" rx="1" stroke="currentColor" stroke-width="1.1"/>',
    '<path d="M4 9.5H9M6.5 8V9.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>',
    '</svg>',
  ].join("");
  var ICON_MOBILE = [
    '<svg width="7" height="12" viewBox="0 0 7 12" fill="none">',
    '<rect x="0.5" y="0.5" width="6" height="11" rx="1.5" stroke="currentColor" stroke-width="1.1"/>',
    '<circle cx="3.5" cy="9.5" r="0.75" fill="currentColor"/>',
    '</svg>',
  ].join("");

  // ── Init trigger ─────────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(
      "input[name='image_focal_y'], input[name$='-image_focal_y'], " +
      "input[name='image_focal_y_mobile'], input[name$='-image_focal_y_mobile'], " +
      "input[name='hero_image_focal_y'], input[name$='-hero_image_focal_y']"
    ).forEach(initPicker);

    // When the template dropdown changes, re-render all promotion pickers
    // so the crop overlay reflects the new template's real dimensions.
    var templateSelect = document.querySelector("select[name='template']");
    if (templateSelect) {
      templateSelect.addEventListener("change", function () {
        document.querySelectorAll("[data-focal-picker-refresh]").forEach(function (fn) {
          fn._focalRefresh && fn._focalRefresh();
        });
      });
    }
  });

  function initPicker(input) {
    if (input.dataset.focalInit) return;
    input.dataset.focalInit = "1";

    var form = input.closest("form") || document;
    var vd   = getViewDims(input.name);
    var dims = vd.dims;

    var barColor = vd.isMobile ? COLOR_MOBILE  : COLOR_DESKTOP;
    var barGlow  = vd.isMobile ? GLOW_MOBILE   : GLOW_DESKTOP;

    var fileSelectors = vd.isMobile ? MOBILE_FILE_SELECTORS : DESKTOP_FILE_SELECTORS;
    var imageFileInput = findFirst(form, fileSelectors);
    var imageUrlInput  = vd.isMobile ? null : findFirst(form, URL_INPUT_SELECTORS);

    // Mobile: also track the sibling focal_x input (horizontal position).
    var focalXInput = null;
    if (vd.isMobile) {
      focalXInput = form.querySelector("input[name='image_focal_x_mobile']") ||
                    form.querySelector("input[name$='-image_focal_x_mobile']");
    }

    // Desktop fallback sources for mobile pickers.
    var desktopFileInput = vd.isMobile ? findFirst(form, DESKTOP_FILE_SELECTORS) : null;
    var desktopUrlInput  = vd.isMobile ? findFirst(form, URL_INPUT_SELECTORS)    : null;

    // Live container dims — can update when template changes.
    var containerAspect = dims[0] / dims[1];
    var imgNaturalAspect = 0;
    // cropMode: "vertical" = top/bottom crop (NS drag), "horizontal" = left/right crop (EW drag)
    var cropMode = "vertical";

    // ── Build wrapper ────────────────────────────────────────────────────────
    var wrap = document.createElement("div");
    wrap.style.cssText = "margin-top:10px;";
    wrap.dataset.focalPickerRefresh = "1";

    // Expose a refresh callback for template-change / no-crop-checkbox redraws.
    wrap._focalRefresh = function () {
      dims = detectModelConfig(input.name);
      containerAspect = dims[0] / dims[1];
      infoLabel.textContent = dims[0] + "×" + dims[1] + "px";
      if (getNoCropActive()) {
        applyFocal(parseInt(input.value) || 50, focalXInput ? (parseInt(focalXInput.value) || 50) : 50);
        return;
      }
      if (imgNaturalAspect) {
        updateCropMode();
        updateCropLabel();
        applyFocal(parseInt(input.value) || 50, focalXInput ? (parseInt(focalXInput.value) || 50) : 50);
      }
    };

    // ── Header row ───────────────────────────────────────────────────────────
    var header = document.createElement("div");
    header.style.cssText = "display:flex;align-items:center;gap:8px;margin-bottom:7px;flex-wrap:wrap;";

    var deviceBadge = document.createElement("span");
    deviceBadge.style.cssText = [
      "display:inline-flex", "align-items:center", "gap:5px",
      "padding:4px 10px", "border-radius:3px",
      "font-size:11px", "font-weight:700", "letter-spacing:0.06em",
      "background:" + (vd.isMobile ? "#0e1a2e" : "#1c0808"),
      "border:1px solid " + (vd.isMobile ? "#1e3a6e" : "#5c1212"),
      "color:" + (vd.isMobile ? "#7ea8d8" : "#c44444"),
    ].join(";");
    deviceBadge.innerHTML = (vd.isMobile ? ICON_MOBILE : ICON_DESKTOP) +
      "<span>" + (vd.isMobile ? "Mobile" : "Desktop") + "</span>";

    var infoLabel = document.createElement("span");
    infoLabel.style.cssText = "font-size:10px;color:#6b5e57;font-family:monospace;";
    infoLabel.textContent = dims[0] + "×" + dims[1] + "px";

    var cropLabel = document.createElement("span");
    cropLabel.style.cssText = "font-size:10px;font-family:monospace;";

    function getCropFracs() {
      if (!imgNaturalAspect) return { vertical: null, horizontal: null };
      var vFrac = imgNaturalAspect < containerAspect ? imgNaturalAspect / containerAspect : 1.0;
      var hFrac = imgNaturalAspect > containerAspect ? containerAspect / imgNaturalAspect : 1.0;
      return { vertical: vFrac, horizontal: hFrac };
    }

    function updateCropMode() {
      if (!imgNaturalAspect) return;
      // Use whichever axis has real cropping; prefer horizontal for mobile portrait containers.
      var fracs = getCropFracs();
      if (fracs.horizontal < 1.0 && fracs.vertical >= 1.0) {
        cropMode = "horizontal";
      } else if (fracs.vertical < 1.0 && fracs.horizontal >= 1.0) {
        cropMode = "vertical";
      } else if (fracs.horizontal < fracs.vertical) {
        cropMode = "horizontal";
      } else {
        cropMode = "vertical";
      }
      previewBox.style.cursor = cropMode === "horizontal" ? "ew-resize" : "ns-resize";
    }

    function updateCropLabel() {
      var fracs = getCropFracs();
      var cf = cropMode === "horizontal" ? fracs.horizontal : fracs.vertical;
      if (cf === null) { cropLabel.textContent = ""; return; }
      var pct = Math.round(cf * 100);
      var axis = cropMode === "horizontal" ? "width" : "height";
      cropLabel.textContent = "— " + pct + "% of image " + axis + " visible";
      cropLabel.style.color = pct < 50 ? "#8B1A1A" : "#6b5e57";
    }

    header.appendChild(deviceBadge);
    header.appendChild(infoLabel);
    header.appendChild(cropLabel);
    wrap.appendChild(header);

    // ── Preview container ────────────────────────────────────────────────────
    var previewBox = document.createElement("div");
    previewBox.style.cssText = [
      "position:relative",
      "width:100%",
      "max-width:" + PREVIEW_MAX_W + "px",
      "min-height:80px",
      "background:#1a1714",
      "border:1px solid " + (vd.isMobile ? "#1e2a3e" : "#3a1818"),
      "border-radius:4px",
      "overflow:hidden",
      "cursor:ns-resize",
      "user-select:none", "-webkit-user-select:none",
    ].join(";");

    var previewImg = document.createElement("img");
    previewImg.style.cssText = "display:block;width:100%;height:auto;pointer-events:none;";

    // Dim/line overlays — reused for both vertical and horizontal crop modes.
    var dimA = document.createElement("div"); // top or left
    dimA.style.cssText = "position:absolute;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";
    var dimB = document.createElement("div"); // bottom or right
    dimB.style.cssText = "position:absolute;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";

    var lineA = document.createElement("div"); // top or left edge of crop rect
    lineA.style.cssText = [
      "position:absolute",
      "background:" + barColor,
      "box-shadow:0 0 6px " + barGlow,
      "pointer-events:none", "z-index:2",
    ].join(";");
    var lineB = document.createElement("div"); // bottom or right edge
    lineB.style.cssText = lineA.style.cssText;

    var handle = document.createElement("div");
    handle.style.cssText = [
      "position:absolute",
      "background:" + barColor, "border-radius:6px",
      "width:52px", "height:18px",
      "display:flex", "align-items:center", "justify-content:center",
      "z-index:3", "pointer-events:none",
    ].join(";");
    handle.innerHTML = '<svg width="16" height="10" viewBox="0 0 16 10" fill="none"><path d="M2 3.5h12M2 6.5h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

    var badge = document.createElement("div");
    badge.style.cssText = [
      "position:absolute", "right:8px", "top:8px",
      "background:" + barColor, "color:#fff",
      "font-size:10px", "font-weight:700", "letter-spacing:0.08em",
      "text-transform:uppercase", "padding:3px 8px", "border-radius:3px",
      "z-index:4", "pointer-events:none",
    ].join(";");

    var placeholder = document.createElement("div");
    placeholder.style.cssText = [
      "position:absolute", "inset:0",
      "display:flex", "align-items:center", "justify-content:center",
      "color:#5a4f49", "font-size:11px", "font-weight:600",
      "letter-spacing:0.06em", "text-transform:uppercase",
      "text-align:center", "padding:0 16px", "min-height:80px",
    ].join(";");
    placeholder.textContent = "Upload or paste an image URL above to see the preview";

    // No-crop overlay — shown instead of crop lines when full-image mode is active.
    var noCropOverlay = document.createElement("div");
    noCropOverlay.style.cssText = [
      "position:absolute", "inset:0",
      "display:none", "align-items:center", "justify-content:center",
      "background:rgba(0,40,0,0.22)",
      "border:2px solid #2a7a2a",
      "z-index:5", "pointer-events:none",
    ].join(";");
    noCropOverlay.innerHTML = [
      '<div style="',
        'background:#0f1f0f;border:1px solid #2a7a2a;',
        'color:#6bc96b;padding:7px 16px;border-radius:4px;',
        'font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;',
        'text-align:center;line-height:1.5;',
      '">',
        'Full image — no crop<br>',
        '<span style="font-weight:400;font-size:10px;opacity:0.75;letter-spacing:0.04em;">100% of the image is shown to visitors</span>',
      '</div>',
    ].join("");

    previewBox.appendChild(previewImg);
    previewBox.appendChild(placeholder);
    previewBox.appendChild(dimA);
    previewBox.appendChild(dimB);
    previewBox.appendChild(lineA);
    previewBox.appendChild(lineB);
    previewBox.appendChild(handle);
    previewBox.appendChild(badge);
    previewBox.appendChild(noCropOverlay);

    var hint = document.createElement("p");
    hint.style.cssText = "margin:6px 0 0;font-size:11px;color:#8c7d74;";
    hint.textContent = vd.isMobile
      ? "Drag left/right (landscape image) or up/down (portrait image) — the bright area is what visitors see on mobile."
      : "Drag up or down — the highlighted area between the lines is what visitors see on desktop.";

    wrap.appendChild(previewBox);
    wrap.appendChild(hint);

    var row = input.closest(".form-row") || input.parentNode;
    row.parentNode.insertBefore(wrap, row.nextSibling);

    // ── Focal application ─────────────────────────────────────────────────────
    function applyFocal(pctY, pctX) {
      pctY = Math.max(0, Math.min(100, pctY));
      pctX = Math.max(0, Math.min(100, pctX === undefined ? 50 : pctX));

      // No-crop mode: show green overlay, hide all crop indicators.
      if (getNoCropActive()) {
        dimA.style.cssText = "position:absolute;pointer-events:none;z-index:1;";
        dimB.style.cssText = "position:absolute;pointer-events:none;z-index:1;";
        lineA.style.display = "none";
        lineB.style.display = "none";
        handle.style.display = "none";
        badge.textContent = "";
        noCropOverlay.style.display = "flex";
        cropLabel.textContent = "— 100% of image visible";
        cropLabel.style.color = "#4ade80";
        hint.textContent = "Full image mode is active — no part of the image will be cropped. The focal point has no effect.";
        previewBox.style.cursor = "default";
        return;
      }

      // Normal crop mode — restore elements hidden by no-crop.
      noCropOverlay.style.display = "none";
      lineA.style.display = "";
      lineB.style.display = "";
      handle.style.display = "";
      hint.textContent = vd.isMobile
        ? "Drag left/right (landscape image) or up/down (portrait image) — the bright area is what visitors see on mobile."
        : "Drag up or down — the highlighted area between the lines is what visitors see on desktop.";

      var fracs = getCropFracs();
      var fullH = previewBox.clientHeight;
      var fullW = previewBox.clientWidth;
      if (!fullH || !fullW) return;

      if (cropMode === "vertical") {
        var cf = fracs.vertical;
        if (cf === null) return;
        var cropH   = Math.round(fullH * cf);
        var cropTop = Math.round((pctY / 100) * (fullH - cropH));
        var cropBot = cropTop + cropH;

        // Reset to vertical layout
        dimA.style.cssText = "position:absolute;left:0;right:0;top:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";
        dimB.style.cssText = "position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";
        lineA.style.cssText = ["position:absolute","left:0","right:0","height:2px","background:"+barColor,"box-shadow:0 0 6px "+barGlow,"pointer-events:none","z-index:2"].join(";");
        lineB.style.cssText = lineA.style.cssText;
        handle.style.cssText = ["position:absolute","left:50%","transform:translateX(-50%)","background:"+barColor,"border-radius:6px","width:52px","height:18px","display:flex","align-items:center","justify-content:center","z-index:3","pointer-events:none"].join(";");
        handle.innerHTML = '<svg width="16" height="10" viewBox="0 0 16 10" fill="none"><path d="M2 3.5h12M2 6.5h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

        dimA.style.height  = cropTop + "px";
        dimB.style.height  = (fullH - cropBot) + "px";
        lineA.style.top    = cropTop + "px";
        lineB.style.top    = (cropBot - 2) + "px";
        handle.style.top   = (cropTop + Math.round(cropH / 2) - 9) + "px";

        badge.textContent  = pctY < 15 ? "Top" : pctY < 35 ? "Upper" : pctY < 65 ? "Center" : pctY < 85 ? "Lower" : "Bottom";

      } else {
        // Horizontal crop mode
        var hf = fracs.horizontal;
        if (hf === null) return;
        var cropW    = Math.round(fullW * hf);
        var cropLeft = Math.round((pctX / 100) * (fullW - cropW));
        var cropRight = cropLeft + cropW;

        // Vertical lines, horizontal dim panels
        dimA.style.cssText = "position:absolute;left:0;top:0;bottom:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";
        dimB.style.cssText = "position:absolute;right:0;top:0;bottom:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";
        lineA.style.cssText = ["position:absolute","top:0","bottom:0","width:2px","background:"+barColor,"box-shadow:0 0 6px "+barGlow,"pointer-events:none","z-index:2"].join(";");
        lineB.style.cssText = lineA.style.cssText;
        handle.style.cssText = ["position:absolute","top:50%","transform:translateY(-50%)","background:"+barColor,"border-radius:6px","width:18px","height:52px","display:flex","align-items:center","justify-content:center","z-index:3","pointer-events:none"].join(";");
        handle.innerHTML = '<svg width="10" height="16" viewBox="0 0 10 16" fill="none"><path d="M3.5 2v12M6.5 2v12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

        dimA.style.width   = cropLeft + "px";
        dimB.style.width   = (fullW - cropRight) + "px";
        lineA.style.left   = cropLeft + "px";
        lineB.style.left   = (cropRight - 2) + "px";
        handle.style.left  = (cropLeft + Math.round(cropW / 2) - 9) + "px";

        badge.textContent  = pctX < 15 ? "Left" : pctX < 35 ? "Left-Ctr" : pctX < 65 ? "Center" : pctX < 85 ? "Right-Ctr" : "Right";
      }
    }

    function setFocal(pctY, pctX) {
      pctY = Math.round(Math.max(0, Math.min(100, pctY)));
      if (pctX !== undefined) pctX = Math.round(Math.max(0, Math.min(100, pctX)));
      input.value = pctY;
      if (focalXInput && pctX !== undefined) focalXInput.value = pctX;
      applyFocal(pctY, pctX !== undefined ? pctX : (focalXInput ? parseInt(focalXInput.value) || 50 : 50));
    }

    function pctFromEvent(e) {
      var rect = previewBox.getBoundingClientRect();
      var clientX = e.touches ? e.touches[0].clientX : e.clientX;
      var clientY = e.touches ? e.touches[0].clientY : e.clientY;
      var fracs = getCropFracs();

      if (cropMode === "horizontal") {
        var hf = fracs.horizontal;
        if (hf === null || hf >= 1) return { x: ((clientX - rect.left) / rect.width) * 100, y: 50 };
        var cropW = rect.width * hf;
        var denomX = rect.width - cropW;
        var x = denomX <= 0 ? 50 : ((clientX - rect.left - cropW / 2) / denomX) * 100;
        return { x: x, y: parseInt(input.value) || 50 };
      } else {
        var cf = fracs.vertical;
        if (cf === null || cf >= 1) return { y: ((clientY - rect.top) / rect.height) * 100, x: 50 };
        var cropH = rect.height * cf;
        var denomY = rect.height - cropH;
        var y = denomY <= 0 ? 50 : ((clientY - rect.top - cropH / 2) / denomY) * 100;
        return { y: y, x: focalXInput ? (parseInt(focalXInput.value) || 50) : 50 };
      }
    }

    // ── Drag ─────────────────────────────────────────────────────────────────
    var dragging = false;
    previewBox.addEventListener("mousedown", function (e) {
      dragging = true;
      var p = pctFromEvent(e);
      setFocal(p.y, p.x);
      e.preventDefault();
    });
    document.addEventListener("mousemove", function (e) {
      if (!dragging) return;
      var p = pctFromEvent(e);
      setFocal(p.y, p.x);
    });
    document.addEventListener("mouseup", function () { dragging = false; });
    previewBox.addEventListener("touchstart", function (e) {
      dragging = true;
      var p = pctFromEvent(e);
      setFocal(p.y, p.x);
      e.preventDefault();
    }, { passive: false });
    document.addEventListener("touchmove", function (e) {
      if (!dragging) return;
      var p = pctFromEvent(e);
      setFocal(p.y, p.x);
    }, { passive: true });
    document.addEventListener("touchend", function () { dragging = false; });

    // ── Image load ────────────────────────────────────────────────────────────
    previewImg.addEventListener("load", function () {
      var IW = previewImg.naturalWidth, IH = previewImg.naturalHeight;
      if (!IW || !IH) return;
      imgNaturalAspect = IW / IH;

      // Cap preview height so tall images don't overflow the admin form.
      var naturalH = PREVIEW_MAX_W / imgNaturalAspect;
      if (naturalH > PREVIEW_MAX_IMG_H) {
        previewImg.style.height = PREVIEW_MAX_IMG_H + "px";
        previewImg.style.objectFit = "contain";
        previewImg.style.objectPosition = "center top";
        previewImg.style.background = "#1a1714";
      } else {
        previewImg.style.height = "";
        previewImg.style.objectFit = "";
        previewImg.style.objectPosition = "";
      }

      updateCropMode();
      updateCropLabel();
      var initY = parseInt(input.value) || 50;
      var initX = focalXInput ? (parseInt(focalXInput.value) || 50) : 50;
      setTimeout(function () { applyFocal(initY, initX); }, 0);
    });

    previewImg.addEventListener("error", function () {
      previewImg.removeAttribute("src");
      previewImg.style.display = "none";
      placeholder.style.display = "flex";
      placeholder.textContent = "Image could not be loaded — try re-uploading.";
    });

    // ── Image source ──────────────────────────────────────────────────────────
    function showImage(src) {
      if (!src) {
        previewImg.removeAttribute("src");
        previewImg.style.display = "none";
        placeholder.style.display = "flex";
        dimA.style.width = "0"; dimA.style.height = "0";
        dimB.style.width = "0"; dimB.style.height = "0";
        lineA.style.left = "-4px"; lineA.style.top = "-4px";
        lineB.style.left = "-4px"; lineB.style.top = "-4px";
        handle.style.top = "-20px"; handle.style.left = "-20px";
        badge.textContent = "";
        return;
      }
      previewImg.src = src;
      previewImg.style.display = "block";
      placeholder.style.display = "none";
    }

    function getUrlFromFileInput(fi) {
      if (!fi) return null;
      if (fi.files && fi.files.length) return URL.createObjectURL(fi.files[0]);
      var c = fi.closest("p.file-upload") || fi.closest(".field-box") || fi.closest(".form-row");
      if (c) {
        var anchors = c.querySelectorAll("a[href]");
        for (var i = 0; i < anchors.length; i++) {
          var href = anchors[i].href;
          if (href && href !== window.location.href &&
              (/\/media\//.test(href) || /\.(jpe?g|png|gif|webp|svg|bmp)(\?[^"]*)?$/i.test(href))) {
            return href;
          }
        }
      }
      return null;
    }

    function getCurrentImageUrl() {
      var url = getUrlFromFileInput(imageFileInput);
      if (url) return url;
      if (imageUrlInput && imageUrlInput.value.trim()) return imageUrlInput.value.trim();
      // Mobile pickers: fall back to desktop image if no mobile-specific image is set.
      if (vd.isMobile) {
        var fallback = getUrlFromFileInput(desktopFileInput);
        if (fallback) return fallback;
        if (desktopUrlInput && desktopUrlInput.value.trim()) return desktopUrlInput.value.trim();
      }
      return null;
    }

    if (imageFileInput) {
      imageFileInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    }
    if (imageUrlInput) {
      imageUrlInput.addEventListener("input",  function () { showImage(getCurrentImageUrl()); });
      imageUrlInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    }
    if (vd.isMobile && desktopFileInput) {
      desktopFileInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    }
    if (vd.isMobile && desktopUrlInput) {
      desktopUrlInput.addEventListener("input",  function () { showImage(getCurrentImageUrl()); });
    }

    // ── Init ──────────────────────────────────────────────────────────────────
    showImage(getCurrentImageUrl());
  }

})();
