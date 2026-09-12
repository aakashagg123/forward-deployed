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
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Typewriter: the real headline is already in the DOM (SEO/no-JS safe),
  // this just clears and retypes it once JS is confirmed running.
  var typed = document.getElementById('fdTyped');
  if (typed && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var full = typed.dataset.text || typed.textContent;
    var cursor = typed.querySelector('.fd-cursor');
    typed.textContent = '';
    if (cursor) typed.appendChild(cursor);
    var i = 0;
    (function type() {
      if (i <= full.length) {
        typed.textContent = full.slice(0, i);
        if (cursor) typed.appendChild(cursor);
        i++;
        setTimeout(type, 28);
      }
    })();
  }

  document.querySelectorAll('.fd-btn').forEach(function (btn) {
    btn.addEventListener('mousemove', function (e) {
      var r = btn.getBoundingClientRect();
      var x = (e.clientX - r.left - r.width / 2) * 0.15;
      var y = (e.clientY - r.top - r.height / 2) * 0.3;
      btn.style.transform = 'translate(' + x + 'px,' + y + 'px)';
    });
    btn.addEventListener('mouseleave', function () { btn.style.transform = 'translate(0,0)'; });
  });
})();
