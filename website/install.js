// Tabs + copy buttons. No framework — vanilla, defer-loaded.

(function () {
  // ── tab groups ────────────────────────────────────────────────────────
  document.querySelectorAll('.tabs').forEach(function (tabBar) {
    var scope = tabBar.parentElement;
    var tabs = tabBar.querySelectorAll('.tab');
    function activate(name) {
      tabs.forEach(function (t) {
        t.setAttribute('aria-selected', t.dataset.tab === name ? 'true' : 'false');
      });
      scope.querySelectorAll('[data-panel]').forEach(function (panel) {
        panel.hidden = panel.dataset.panel !== name;
      });
    }
    tabs.forEach(function (t) {
      t.addEventListener('click', function () { activate(t.dataset.tab); });
    });
  });

  // ── copy buttons ──────────────────────────────────────────────────────
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.closest('pre');
      var code = pre && pre.querySelector('code');
      if (!code) return;
      var text = code.innerText;
      var done = function () {
        var prev = btn.textContent;
        btn.textContent = 'copied';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = prev;
          btn.classList.remove('copied');
        }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {
          fallbackCopy(text); done();
        });
      } else {
        fallbackCopy(text); done();
      }
    });
  });

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
  }
})();
