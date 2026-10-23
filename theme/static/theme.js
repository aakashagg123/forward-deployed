(function () {
  var root = document.documentElement;
  var KEY = 'fd-theme';
  var toggle = document.getElementById('fdThemeToggle');
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved === 'dark' || saved === 'light') root.setAttribute('data-theme', saved);

  function current() {
    var attr = root.getAttribute('data-theme');
    if (attr) return attr;
    return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
    });
  }

  var mobileToggle = document.getElementById('fdMobileToggle');
  var sidebar = document.getElementById('fdSidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (!sidebar.classList.contains('open')) return;
      if (sidebar.contains(e.target) || mobileToggle.contains(e.target)) return;
      sidebar.classList.remove('open');
    });
  }

  var switchEl = document.getElementById('fdSwitch');
  var switchBtn = document.getElementById('fdSwitchBtn');
  if (switchEl && switchBtn) {
    switchBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = switchEl.classList.toggle('open');
      switchBtn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) {
      if (!switchEl.contains(e.target)) {
        switchEl.classList.remove('open');
        switchBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  var outlineLinks = document.querySelectorAll('.fd-outline-link');
  if (outlineLinks.length) {
    var targets = Array.prototype.map.call(outlineLinks, function (l) {
      return document.getElementById(l.getAttribute('href').slice(1));
    });
    var onScroll = function () {
      var cur = -1;
      for (var i = 0; i < targets.length; i++) {
        if (targets[i] && targets[i].getBoundingClientRect().top < 140) cur = i;
      }
      outlineLinks.forEach(function (l, i) { l.classList.toggle('active', i === cur); });
    };
    // Coalesce to one layout read per frame — on iOS Safari an unthrottled
    // scroll listener runs a getBoundingClientRect() per outline target on
    // every tick, which forces a synchronous layout mid-scroll and is the
    // single biggest source of visible jank on long pages.
    var ticking = false;
    addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { onScroll(); ticking = false; });
    }, { passive: true });
    onScroll();
  }

  var pfGrid = document.getElementById('fdPfGrid');
  var pfFilters = document.querySelectorAll('.fd-pf-filter');
  if (pfGrid && pfFilters.length) {
    var pfCards = pfGrid.querySelectorAll('.fd-pf-card');
    pfFilters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        pfFilters.forEach(function (b) { b.classList.remove('on'); });
        btn.classList.add('on');
        var tag = btn.dataset.tag;
        pfCards.forEach(function (card) {
          var tags = (card.dataset.tags || '').split('|');
          card.hidden = tag !== 'All' && tags.indexOf(tag) === -1;
        });
      });
    });
  }

  var stackRoot = document.getElementById('fdStack');
  if (stackRoot) {
    var stackBtns = stackRoot.querySelectorAll('.fd-stack-toggle button');
    var stackCells = stackRoot.querySelectorAll('.fd-stack-cell');
    var stackCaption = document.getElementById('fdStackCaption');
    var stackCaptions = {
      pre: 'Pre-order to order journey — enabled through the customer portal and the Opportunity workflow on Salesforce.',
      post: 'Post-order to order-completion journey — enabled via ERP.'
    };
    var setStackPhase = function (phase) {
      stackBtns.forEach(function (b) { b.classList.toggle('on', b.dataset.phase === phase); });
      stackCells.forEach(function (c) {
        var active = c.dataset.phase === phase;
        c.classList.toggle('fd-stack-on', active);
        c.classList.toggle('fd-stack-dim', !active);
      });
      if (stackCaption) stackCaption.textContent = stackCaptions[phase];
    };
    stackBtns.forEach(function (b) { b.addEventListener('click', function () { setStackPhase(b.dataset.phase); }); });
    setStackPhase('pre');
  }

  // Phones: tap a book figure to open it near full size in a pannable overlay.
  document.addEventListener('click', function (e) {
    var img = e.target && e.target.closest && e.target.closest('.fd-plate-frame img');
    if (!img || !window.matchMedia('(max-width: 860px)').matches) return;
    var box = document.createElement('div');
    box.className = 'fd-lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', img.getAttribute('alt') || 'Figure');
    var bar = document.createElement('div');
    bar.className = 'fd-lightbox-bar';
    var hint = document.createElement('span');
    hint.textContent = 'Drag to pan. Pinch to zoom.';
    var close = document.createElement('button');
    close.type = 'button';
    close.className = 'fd-lightbox-close';
    close.textContent = 'Close';
    bar.appendChild(hint);
    bar.appendChild(close);
    var scroll = document.createElement('div');
    scroll.className = 'fd-lightbox-scroll';
    var big = document.createElement('img');
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    scroll.appendChild(big);
    box.appendChild(bar);
    box.appendChild(scroll);
    var prev = document.body.style.overflow;
    function shut() {
      document.body.style.overflow = prev;
      document.removeEventListener('keydown', onKey);
      box.remove();
    }
    function onKey(ev) { if (ev.key === 'Escape') shut(); }
    close.addEventListener('click', shut);
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    document.body.appendChild(box);
    close.focus();
  });
})();
