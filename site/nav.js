/* Way back on the therapies page (22.11.2026), shared by / and /en/.
   1. In-page jumps (text, catalogue; not the top menu, the language switch or the chips) are real history entries:
      the position left is stored in the entry, the browser's Back returns to it, and a small button does the same.
   2. Marko's own midicontrol page opens in a panel inside this page (✕ Back to therapies, Esc, open in a new tab).
   Every other outside link is target=_blank (added in the HTML by tools/add_newtab.py). */
(function () {
  var en = document.documentElement.lang === 'en';
  var T = en ? { back: '← Back to where you were', close: '✕ Back to therapies', closeLabel: 'Back to therapies: closes this panel', tab: 'Open in a new tab ↗', title: 'MIDI control' }
             : { back: '← Natrag gdje si bio', close: '✕ Natrag na terapije', closeLabel: 'Natrag na terapije: zatvara ovaj prozor', tab: 'Otvori u novoj kartici ↗', title: 'MIDI upravljanje' };
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  var btn = document.createElement('button');
  btn.id = 'tp-back'; btn.type = 'button'; btn.hidden = true; btn.textContent = T.back;
  document.body.appendChild(btn);
  var from = null, land = 0, viaHist = false;
  // never over the picture grid or the donation bowl: the button hides while either is on screen (Back on the keyboard still works)
  if ('IntersectionObserver' in window) {
    var seen = new Set(), io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) seen.add(e.target); else seen.delete(e.target); }); btn.classList.toggle('away', seen.size > 0); });
    document.querySelectorAll('.igwrap,.mantra-bowl').forEach(function (e) { io.observe(e); });
  }
  function hide() { btn.hidden = true; from = null; }
  var idle = 0, settled = false;
  function show(y, h) { viaHist = h; from = y; btn.hidden = false; settled = false; clearTimeout(idle); idle = setTimeout(settle, 1000); }
  function settle() { land = window.scrollY; settled = true; }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    if (a.closest('.topnav,.langsw,.chips')) return;
    var y = window.scrollY;
    history.replaceState({ tpY: y }, '', location.href);   // the entry we leave remembers where we were
    show(y, a.hash !== location.hash);                                               // the default jump adds the next entry
  }, true);
  btn.addEventListener('click', function () {
    var y = from, h = viaHist; hide();
    if (h) history.back(); else window.scrollTo({ top: y, behavior: 'instant' });   // Back lands on the entry that stored y (popstate below)
  });
  window.addEventListener('popstate', function (e) {
    if (panelPop) { panelPop = false; return; }                                    // closing the panel: stay where we are
    if (panel && !panel.hidden && !(e.state && e.state.tpPanel)) { closePanel(true); return; }
    if (e.state && typeof e.state.tpY === 'number') { var y = e.state.tpY; setTimeout(function () { window.scrollTo({ top: y, behavior: 'instant' }); }, 30); hide(); }   // Back to an entry we stored (fragment jumps fire popstate too, with no state: ignored)
  });
  window.addEventListener('scroll', function () {
    if (btn.hidden) return;
    if (!settled) { clearTimeout(idle); idle = setTimeout(settle, 500); return; }   // still travelling to the target
    if (Math.abs(window.scrollY - land) > innerHeight * 1.5) hide();                // he scrolled far on his own
  }, { passive: true });
  /* the panel for his own page */
  var panel = null, opener = null, panelPop = false;
  function closePanel(fromPop) {
    if (!panel || panel.hidden) return;
    panel.hidden = true; panel.querySelector('iframe').src = 'about:blank'; document.documentElement.style.overflow = '';
    if (!fromPop && history.state && history.state.tpPanel) { panelPop = true; history.back(); }
    if (opener) opener.focus();
  }
  function openPanel(url, from) {
    if (!panel) {
      panel = document.createElement('div'); panel.id = 'tp-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true'); panel.setAttribute('aria-label', T.title);
      panel.innerHTML = '<div class="bar"><button type="button" class="x"></button><a target="_blank" rel="noopener"></a></div><iframe allow="midi; autoplay; fullscreen" loading="lazy" referrerpolicy="strict-origin-when-cross-origin"></iframe>';
      panel.querySelector('iframe').addEventListener('load', function () { if (!panel.hidden) panel.querySelector('.x').focus(); });   // Esc works until he clicks inside the other page
      panel.querySelector('iframe').title = T.title; panel.querySelector('.x').textContent = T.close; panel.querySelector('.x').title = T.closeLabel; panel.querySelector('.x').setAttribute('aria-label', T.closeLabel); panel.querySelector('a').textContent = T.tab;
      panel.querySelector('.x').addEventListener('click', function () { closePanel(); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel && !panel.hidden) closePanel(); });
      document.body.appendChild(panel);
    }
    opener = from; panel.querySelector('a').href = url; panel.querySelector('iframe').src = url; panel.hidden = false;
    document.documentElement.style.overflow = 'hidden'; panel.querySelector('.x').focus();
    history.pushState({ tpPanel: 1, tpY: window.scrollY }, '', location.href);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="https://midicontrol.markobosko.org"]');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault(); openPanel(a.href, a);
  });
})();
