(function () {
  "use strict";

  // ── DOM references ────────────────────────────────────────────────
  var modal     = null;
  var cropImage = null;

  // ── State ─────────────────────────────────────────────────────────
  var activeInput = null;
  var activeFile  = null;
  var cropper     = null;
  var objectUrl   = null;

  // Suppress programmatic change events so applying a crop blob back
  // to the file input doesn't re-open the modal.
  var suppressNextChange = false;

  // Track whether the current click started on the backdrop so a
  // CropperJS drag that escapes the dialog doesn't accidentally close.
  var mousedownOnBackdrop = false;

  // ── Build modal (once) ────────────────────────────────────────────
  function ensureModal() {
    if (modal) return;

    modal = document.createElement("div");
    modal.className = "mp-cropper-modal";
    modal.hidden = true;
    modal.innerHTML = [
      '<div class="mp-cropper-dialog" role="dialog" aria-modal="true" aria-label="Crop image">',

      '  <div class="mp-cropper-header">',
      '    <span class="mp-cropper-title">Crop Image</span>',
      '  </div>',

      '  <div class="mp-cropper-ratios">',
      '    <span class="mp-cropper-tools-label">Ratio</span>',
      '    <button type="button" class="button" data-ratio="NaN">Free</button>',
      '    <button type="button" class="button" data-ratio="1.777777">16:9</button>',
      '    <button type="button" class="button" data-ratio="1.333333">4:3</button>',
      '    <button type="button" class="button" data-ratio="1">1:1</button>',
      '    <button type="button" class="button mp-cropper-scale-out" aria-label="Zoom out">−</button>',
      '    <button type="button" class="button mp-cropper-scale-in"  aria-label="Zoom in">+</button>',
      '  </div>',

      '  <div class="mp-cropper-body">',
      '    <img class="mp-cropper-image" alt="Crop canvas" crossorigin="anonymous" />',
      '  </div>',

      '  <div class="mp-cropper-actions">',
      '    <button type="button" class="button mp-cropper-cancel">Cancel</button>',
      '    <button type="button" class="button mp-cropper-original">Use original</button>',
      '    <button type="button" class="button button-primary mp-cropper-apply">Crop &amp; save</button>',
      '  </div>',

      '</div>'
    ].join("\n");

    document.body.appendChild(modal);

    cropImage = modal.querySelector(".mp-cropper-image");

    modal.querySelector(".mp-cropper-apply").addEventListener("click", applyCrop);
    modal.querySelector(".mp-cropper-original").addEventListener("click", closeModal);
    modal.querySelector(".mp-cropper-cancel").addEventListener("click", cancelSelection);

    modal.querySelector(".mp-cropper-scale-out").addEventListener("click", function () {
      if (cropper) cropper.zoom(-0.1);
    });
    modal.querySelector(".mp-cropper-scale-in").addEventListener("click", function () {
      if (cropper) cropper.zoom(0.1);
    });

    modal.querySelectorAll(".mp-cropper-ratios button[data-ratio]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (!cropper) return;
        var r = parseFloat(btn.getAttribute("data-ratio"));
        cropper.setAspectRatio(isNaN(r) ? NaN : r);
      });
    });

    // Only close on backdrop click if the mousedown also started on
    // the backdrop — not when a crop-handle drag escapes the dialog.
    modal.addEventListener("mousedown", function (e) {
      mousedownOnBackdrop = (e.target === modal);
    });
    modal.addEventListener("click", function (e) {
      if (mousedownOnBackdrop && e.target === modal) closeModal();
      mousedownOnBackdrop = false;
    });
  }

  // ── Apply crop to the file input ──────────────────────────────────
  function applyCrop() {
    if (!cropper || !activeInput || !activeFile) { closeModal(); return; }

    // No size limits — output at the full source-pixel resolution.
    var canvas = cropper.getCroppedCanvas({ imageSmoothingQuality: "high" });
    if (!canvas) { closeModal(); return; }

    var mime = (activeFile.type && activeFile.type.indexOf("image/") === 0)
      ? activeFile.type : "image/jpeg";

    canvas.toBlob(function (blob) {
      if (!blob) { closeModal(); return; }

      var dotIndex = activeFile.name.lastIndexOf(".");
      var baseName  = dotIndex > 0 ? activeFile.name.slice(0, dotIndex) : activeFile.name;
      var extension = dotIndex > 0 ? activeFile.name.slice(dotIndex) : ".jpg";
      var croppedFile = new File(
        [blob],
        baseName + "-crop" + extension,
        { type: mime, lastModified: Date.now() }
      );

      var dt = new DataTransfer();
      dt.items.add(croppedFile);
      suppressNextChange = true;
      activeInput.files = dt.files;
      activeInput.dispatchEvent(new Event("change", { bubbles: true }));
      closeModal();
    }, mime, 0.95);
  }

  // ── Modal lifecycle ───────────────────────────────────────────────
  function destroyCropper() {
    if (cropper) { cropper.destroy(); cropper = null; }
  }

  function clearObjectUrl() {
    if (objectUrl) { URL.revokeObjectURL(objectUrl); objectUrl = null; }
  }

  function closeModal() {
    destroyCropper();
    clearObjectUrl();
    modal.hidden = true;
    modal.style.display = "none";
    cropImage.removeAttribute("src");
    activeInput = null;
    activeFile  = null;
    mousedownOnBackdrop = false;
  }

  function cancelSelection() {
    if (activeInput) activeInput.value = "";
    closeModal();
  }

  // ── Open modal ────────────────────────────────────────────────────
  function openModalForImage(input, file) {
    ensureModal();
    destroyCropper();
    clearObjectUrl();

    activeInput = input;
    activeFile  = file;

    objectUrl = URL.createObjectURL(file);
    cropImage.src = objectUrl;
    modal.hidden = false;
    modal.style.display = "flex";

    cropImage.onload = function () {
      if (typeof Cropper === "undefined") return;
      cropper = new Cropper(cropImage, {
        viewMode: 1,
        dragMode: "move",
        aspectRatio: NaN,        // free crop by default
        autoCropArea: 1.0,       // show the full image selected on open
        background: false,
        responsive: true,
        restore: false,
        movable: true,
        zoomable: true,
        scalable: false,
        rotatable: false,
        checkCrossOrigin: false,
      });
    };
  }

  // ── "Crop existing image" button ──────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("p.file-upload").forEach(function (p) {
      var a     = p.querySelector("a");
      var input = p.querySelector("input[type='file']");
      if (!a || !input) return;

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "button mp-cropper-edit-existing";
      btn.textContent = "Crop existing image";
      btn.style.cssText = "margin-left:12px; padding:4px 10px; font-size:11px;";

      btn.addEventListener("click", function (e) {
        e.preventDefault();
        fetch(a.href, { mode: "cors", cache: "no-cache" })
          .then(function (res) { return res.blob(); })
          .then(function (blob) {
            var filename = a.textContent.trim() || (Date.now() + ".jpg");
            openModalForImage(input, new File([blob], filename, { type: blob.type || "image/jpeg" }));
          })
          .catch(function () {
            alert(
              "Could not load this image for cropping.\n" +
              "If storage is on S3/Cloud, ensure CORS allows GET requests from this domain."
            );
          });
      });

      a.parentNode.insertBefore(btn, a.nextSibling);
    });
  });

  // ── New file selected → open crop modal ──────────────────────────
  document.addEventListener("change", function (event) {
    var target = event.target;
    if (!(target instanceof HTMLInputElement) || target.type !== "file") return;
    if (suppressNextChange) { suppressNextChange = false; return; }
    if (!target.files || !target.files.length) return;
    var file = target.files[0];
    if (!file || !file.type || file.type.indexOf("image/") !== 0) return;
    openModalForImage(target, file);
  });

})();
