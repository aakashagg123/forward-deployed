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

  var feedback = document.getElementById('fdFeedback');
  if (feedback) {
    var faces = feedback.querySelectorAll('.fd-face');
    var thanks = document.getElementById('fdFeedbackThanks');
    faces.forEach(function (f) {
      f.addEventListener('click', function () {
        faces.forEach(function (x) { x.classList.remove('picked'); });
        f.classList.add('picked');
        if (thanks) thanks.hidden = false;
      });
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

  var ghRoot = document.getElementById('fdGh');
  if (ghRoot) {
    var ghUser = ghRoot.dataset.username;
    var ghStatus = document.getElementById('fdGhStatus');
    var ghSync = document.getElementById('fdGhSync');
    var ghImgDark = document.getElementById('fdGhImgDark');
    var ghImgLight = document.getElementById('fdGhImgLight');
    var ghLoading = false;

    // An <img>, not a fetch() — avoids the CORS failure mode a cross-origin
    // JSON API read would hit (and did: an earlier version of this widget
    // used github-contributions-api.jogruber.de via fetch, which a browser
    // blocks client-side when that API doesn't grant this origin access).
    // ghchart.rshah.org is a long-standing public SVG-badge service built
    // exactly for hotlinking, so no CORS question applies to displaying it.
    var ghLoad = function () {
      if (ghLoading) return;
      ghLoading = true;
      if (ghSync) ghSync.classList.add('syncing');
      ghStatus.textContent = 'Syncing…';

      var cacheBust = Date.now();
      var base = 'https://ghchart.rshah.org/';
      var darkUrl = base + 'F4F4F2/' + encodeURIComponent(ghUser) + '?t=' + cacheBust;
      var lightUrl = base + '000000/' + encodeURIComponent(ghUser) + '?t=' + cacheBust;

      var pending = 2;
      var failed = false;
      var settle = function (ok) {
        if (!ok) failed = true;
        pending -= 1;
        if (pending > 0) return;
        ghLoading = false;
        if (ghSync) ghSync.classList.remove('syncing');
        if (failed) {
          ghStatus.textContent = 'Could not load GitHub activity right now — try the sync button, or see the profile above.';
        } else {
          var now = new Date();
          ghStatus.textContent = 'Synced ' + now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
      };

      ghImgDark.onload = function () { settle(true); };
      ghImgDark.onerror = function () { settle(false); };
      ghImgLight.onload = function () { settle(true); };
      ghImgLight.onerror = function () { settle(false); };
      ghImgDark.src = darkUrl;
      ghImgLight.src = lightUrl;
    };

    if (ghSync) ghSync.addEventListener('click', ghLoad);
    ghLoad();
  }

})();
