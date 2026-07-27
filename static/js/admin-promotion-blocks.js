(function () {
  function injectRuntimeStyles() {
    if (document.getElementById('mp-promo-builder-runtime-style')) return;

    var style = document.createElement('style');
    style.id = 'mp-promo-builder-runtime-style';
    style.textContent = [
      '.inline-group.mp-promo-block-builder .inline-related { margin: 0 14px 12px !important; border: 1px solid var(--mt-border) !important; background: var(--mt-surface-alt) !important; }',
      '.inline-group.mp-promo-block-builder .inline-related h3 { display: flex !important; align-items: center !important; gap: 10px !important; padding: 9px 12px !important; font-family: var(--mt-font-brand) !important; font-size: 18px !important; line-height: 1.2 !important; letter-spacing: 0.01em !important; background: rgba(15, 13, 12, 0.82) !important; border-bottom: 1px solid var(--mt-border) !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-block-toolbar { margin: 10px 14px 9px !important; padding: 9px 11px !important; font-size: 13px !important; line-height: 1.45 !important; border: 1px dashed rgba(196, 68, 68, 0.5) !important; background: rgba(196, 68, 68, 0.1) !important; }',
      '.inline-group.mp-promo-block-builder .form-row { padding-top: 10px !important; padding-bottom: 10px !important; }',
      '.inline-group.mp-promo-block-builder .form-row > div > label, .inline-group.mp-promo-block-builder .form-row label { font-family: var(--mt-font-brand) !important; font-size: 18px !important; line-height: 1.2 !important; letter-spacing: 0.01em !important; color: var(--mt-ink) !important; }',
      '.inline-group.mp-promo-block-builder textarea, .inline-group.mp-promo-block-builder input[type="text"], .inline-group.mp-promo-block-builder input[type="url"], .inline-group.mp-promo-block-builder select { font-size: 16px !important; line-height: 1.45 !important; min-height: 44px !important; padding: 8px 12px !important; }',
      '.inline-group.mp-promo-block-builder textarea { min-height: 190px !important; }',
      '.inline-group.mp-promo-block-builder .form-row.field-sort_order { display: none !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-drag-handle { display: inline-flex !important; align-items: center !important; justify-content: center !important; width: 22px !important; height: 22px !important; margin-right: 2px !important; border-radius: 4px !important; border: 1px solid rgba(196, 68, 68, 0.65) !important; background: rgba(196, 68, 68, 0.18) !important; color: #c44444 !important; font-size: 14px !important; font-weight: 700 !important; line-height: 1 !important; cursor: grab !important; user-select: none !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-drag-handle:active { cursor: grabbing !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-inline-tools { margin-left: auto !important; display: inline-flex !important; align-items: center !important; gap: 10px !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-order { display: inline-flex !important; align-items: center !important; gap: 6px !important; padding: 4px 7px !important; border: 1px solid rgba(196, 68, 68, 0.45) !important; background: rgba(196, 68, 68, 0.12) !important; border-radius: 3px !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-order label { font-family: var(--mt-font-ui) !important; font-size: 11px !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; color: var(--mt-body) !important; margin: 0 !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-order input { width: 66px !important; min-height: 30px !important; font-size: 13px !important; font-weight: 700 !important; color: var(--mt-ink) !important; border: 1px solid rgba(196, 68, 68, 0.55) !important; background: rgba(20, 18, 16, 0.95) !important; padding: 4px 8px !important; }',
      '.inline-group.mp-promo-block-builder .delete { display: inline-flex !important; align-items: center !important; gap: 6px !important; padding: 4px 8px !important; border: 1px solid rgba(196, 68, 68, 0.45) !important; border-radius: 3px !important; background: rgba(196, 68, 68, 0.1) !important; color: #f0d4d4 !important; font-family: var(--mt-font-ui) !important; font-size: 12px !important; font-weight: 600 !important; }',
      '.inline-group.mp-promo-block-builder .delete input[type="checkbox"] { accent-color: var(--mt-red) !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-block-ghost { opacity: 0.38 !important; outline: 2px dashed var(--mt-red) !important; outline-offset: 3px !important; }',
      '.inline-group.mp-promo-block-builder .mp-promo-block-dragging { box-shadow: 0 14px 36px rgba(0, 0, 0, 0.45) !important; }'
    ].join('\n');

    document.head.appendChild(style);
  }

  function findPromotionInlineGroup() {
    return Array.from(document.querySelectorAll('.inline-group')).find(function (group) {
      var heading = group.querySelector('h2');
      if (!heading) return false;
      return /page\s*content\s*blocks?/i.test(heading.textContent || '');
    }) || null;
  }

  function getActiveInlines(group) {
    if (!group) return [];
    return Array.from(group.querySelectorAll('.inline-related')).filter(function (inline) {
      if (inline.classList.contains('empty-form')) return false;
      var del = inline.querySelector('input[name$="-DELETE"]');
      return !(del && del.checked);
    });
  }

  function addDragHandle(inline) {
    var h3 = inline.querySelector('h3');
    if (!h3 || h3.querySelector('.mp-promo-drag-handle')) return;

    var handle = document.createElement('span');
    handle.className = 'mp-promo-drag-handle';
    handle.title = 'Drag to reorder block';
    handle.setAttribute('aria-hidden', 'true');
    handle.textContent = '::';
    h3.insertAdjacentElement('afterbegin', handle);
  }

  function hideSortOrderRow(inline) {
    var row = inline.querySelector('.form-row.field-sort_order');
    if (!row) return;
    row.style.display = 'none';
  }

  function readOrder(inline) {
    var input = inline.querySelector('input[name$="-sort_order"]');
    if (!input) return Number.MAX_SAFE_INTEGER;
    var n = parseInt(input.value, 10);
    return Number.isFinite(n) ? n : Number.MAX_SAFE_INTEGER;
  }

  function positionInlineByOrder(group, inline, desiredOrder) {
    if (!group || !inline || !inline.parentElement) return;
    var parent = inline.parentElement;
    var others = getActiveInlines(group).filter(function (item) {
      return item !== inline;
    });

    var inserted = false;
    for (var i = 0; i < others.length; i++) {
      if (desiredOrder < readOrder(others[i])) {
        parent.insertBefore(inline, others[i]);
        inserted = true;
        break;
      }
    }

    if (!inserted) {
      var empty = parent.querySelector('.inline-related.empty-form');
      if (empty) {
        parent.insertBefore(inline, empty);
      } else {
        parent.appendChild(inline);
      }
    }
  }

  function ensureHeaderTools(group, inline) {
    var h3 = inline.querySelector('h3');
    if (!h3) return;

    var deleteWrap = h3.querySelector('.delete');
    var tools = h3.querySelector('.mp-promo-inline-tools');
    if (!tools) {
      tools = document.createElement('span');
      tools.className = 'mp-promo-inline-tools';
      h3.appendChild(tools);
    }

    var orderWrap = h3.querySelector('.mp-promo-order');
    if (!orderWrap) {
      orderWrap = document.createElement('span');
      orderWrap.className = 'mp-promo-order';

      var orderLabel = document.createElement('label');
      orderLabel.textContent = 'Order';

      var orderInput = document.createElement('input');
      orderInput.type = 'number';
      orderInput.className = 'mp-promo-order-input';
      orderInput.step = '10';
      orderInput.min = '0';

      orderWrap.appendChild(orderLabel);
      orderWrap.appendChild(orderInput);
      tools.appendChild(orderWrap);

      var commitOrderChange = function () {
        var hidden = inline.querySelector('input[name$="-sort_order"]');
        if (!hidden) return;
        var next = parseInt(orderInput.value, 10);
        if (!Number.isFinite(next)) return;

        hidden.value = String(next);
        positionInlineByOrder(group, inline, next);
        refreshOrderLabels(group);
      };

      orderInput.addEventListener('change', commitOrderChange);
      orderInput.addEventListener('blur', commitOrderChange);
      orderInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
          event.preventDefault();
          commitOrderChange();
        }
      });
    }

    var hiddenOrder = inline.querySelector('input[name$="-sort_order"]');
    var headerOrder = orderWrap.querySelector('.mp-promo-order-input');
    if (hiddenOrder && headerOrder && document.activeElement !== headerOrder) {
      headerOrder.value = hiddenOrder.value || '';
    }

    if (deleteWrap && deleteWrap.parentElement !== tools) {
      tools.appendChild(deleteWrap);
    }
  }

  function refreshOrderLabels(group) {
    var active = getActiveInlines(group);
    active.forEach(function (inline, index) {
      var orderInput = inline.querySelector('input[name$="-sort_order"]');
      if (orderInput) {
        orderInput.value = String((index + 1) * 10);
      }

      var headerOrderInput = inline.querySelector('.mp-promo-order-input');
      if (headerOrderInput && document.activeElement !== headerOrderInput) {
        headerOrderInput.value = orderInput ? orderInput.value : String((index + 1) * 10);
      }

      var label = inline.querySelector('h3 .inline_label');
      if (label) {
        label.textContent = 'Content Block #' + (index + 1);
      }
    });
  }

  function initBlockDnd() {
    var group = findPromotionInlineGroup();
    if (!group) return;

    group.classList.add('mp-promo-block-builder');

    var toolbar = group.querySelector('.mp-promo-block-toolbar');
    var heading = group.querySelector('h2');
    if (!toolbar && heading) {
      toolbar = document.createElement('div');
      toolbar.className = 'mp-promo-block-toolbar';
      toolbar.textContent = 'Content Builder: drag blocks using the dot handle to reorder. Order updates automatically.';
      heading.insertAdjacentElement('afterend', toolbar);
    }

    var allInlines = Array.from(group.querySelectorAll('.inline-related')).filter(function (inline) {
      return !inline.classList.contains('empty-form');
    });
    allInlines.forEach(function (inline) {
      addDragHandle(inline);
      hideSortOrderRow(inline);
      ensureHeaderTools(group, inline);
    });

    if (typeof Sortable !== 'undefined' && group.dataset.mpPromoSortable !== '1' && allInlines.length) {
      var container = allInlines[0].parentElement;
      if (container) {
        group.dataset.mpPromoSortable = '1';
        Sortable.create(container, {
          draggable: '.inline-related:not(.empty-form)',
          handle: '.mp-promo-drag-handle',
          animation: 170,
          ghostClass: 'mp-promo-block-ghost',
          dragClass: 'mp-promo-block-dragging',
          onEnd: function () {
            refreshOrderLabels(group);
          },
        });
      }
    }

    refreshOrderLabels(group);
  }

  function setRowState(inline, fieldName, visible) {
    var row = inline.querySelector('.form-row.field-' + fieldName);
    if (!row) return;

    row.style.display = visible ? '' : 'none';
    row.querySelectorAll('input, select, textarea, button').forEach(function (el) {
      if (el.type === 'hidden') return;
      el.disabled = !visible;
    });
  }

  function getFieldsetByHeading(inline, headingText) {
    var target = headingText.trim().toLowerCase();
    var fieldsets = inline.querySelectorAll('fieldset');
    for (var i = 0; i < fieldsets.length; i++) {
      var head = fieldsets[i].querySelector('h2');
      if (head && head.textContent.trim().toLowerCase().indexOf(target) === 0) {
        return fieldsets[i];
      }
    }
    return null;
  }

  function setFieldsetVisible(fieldset, visible) {
    if (!fieldset) return;
    fieldset.style.display = visible ? '' : 'none';

    if (visible) {
      fieldset.classList.remove('collapsed');
    }

    fieldset.querySelectorAll('input, select, textarea, button').forEach(function (el) {
      if (el.type === 'hidden') return;
      el.disabled = !visible;
    });
  }

  function applyBlockRules(inline) {
    var typeSelect = inline.querySelector('.form-row.field-block_type select');
    if (!typeSelect) return;

    var type = typeSelect.value;
    var isText = type === 'heading' || type === 'paragraph' || type === 'quote';
    var isImage = type === 'image';
    var isHeading = type === 'heading';
    var isStructural = type === 'divider' || type === 'spacer';

    var textFieldset = getFieldsetByHeading(inline, 'text');
    var imageFieldset = getFieldsetByHeading(inline, 'image');
    var styleFieldset = getFieldsetByHeading(inline, 'style');

    setFieldsetVisible(textFieldset, isText);
    setFieldsetVisible(imageFieldset, isImage);
    setFieldsetVisible(styleFieldset, isText || isStructural);

    setRowState(inline, 'text', isText);
    setRowState(inline, 'heading_level', isHeading);

    setRowState(inline, 'image', isImage);
    setRowState(inline, 'image_url', isImage);
    setRowState(inline, 'image_caption', isImage);
    setRowState(inline, 'image_max_width', isImage);

    setRowState(inline, 'font_family', isText);
    setRowState(inline, 'font_size', isText);
    setRowState(inline, 'text_color', isText);
    setRowState(inline, 'text_align', isText);

    setRowState(inline, 'margin_top', true);
    setRowState(inline, 'margin_bottom', true);
  }

  function findPromotionBlockInlines(root) {
    var scope = root && root.querySelectorAll ? root : document;
    var found = new Set();

    scope.querySelectorAll('select[name$="-block_type"]').forEach(function (select) {
      var inline = select.closest('.inline-related');
      if (inline && !inline.classList.contains('empty-form')) {
        found.add(inline);
      }
    });

    return Array.from(found);
  }

  function bindInline(inline) {
    if (!inline || inline.dataset.mpGuardrailsBound === '1' || inline.classList.contains('empty-form')) return;
    inline.dataset.mpGuardrailsBound = '1';

    hideSortOrderRow(inline);
    applyBlockRules(inline);

    var typeSelect = inline.querySelector('.form-row.field-block_type select');
    if (typeSelect) {
      typeSelect.addEventListener('change', function () {
        applyBlockRules(inline);
      });
    }
  }

  function init() {
    injectRuntimeStyles();
    initBlockDnd();
    findPromotionBlockInlines(document).forEach(bindInline);

    var form = document.querySelector('form');
    if (form && form.dataset.mpPromotionOrderBound !== '1') {
      form.dataset.mpPromotionOrderBound = '1';
      form.addEventListener('submit', function () {
        var group = findPromotionInlineGroup();
        if (group) {
          refreshOrderLabels(group);
        }
      });
    }

    if (!window.MutationObserver) return;

    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (!(node instanceof Element)) return;
          initBlockDnd();
          findPromotionBlockInlines(node).forEach(bindInline);
        });
      });
    });

    var inlineGroup = document.getElementById('content-main');
    if (inlineGroup) {
      observer.observe(inlineGroup, { childList: true, subtree: true });
    }

    document.addEventListener('click', function () {
      initBlockDnd();
      findPromotionBlockInlines(document).forEach(bindInline);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
