// MilkDrop (butterchurn) na cijelom zaslonu, slika nastaje iz zvuka "Karipsko more" (21.11.2026).
(() => {
  const $ = id => document.getElementById(id);
  const go = $('milk-start'), box = $('mk'), cv = $('mk-cv'), au = $('mk-au'); if (!go || !box) return;
  const CALM = ['martin - castle in the air', 'Aderrasi - Songflower (Moss Posy)', 'cope + martin - mother-of-pearl', 'Geiss - Cauldron - painterly 2 (saturation remix)', 'martin - frosty caves 2'];
  let viz = null, ac = null, raf = 0, auto = 0, ix = 0, keys = [], BP = null, loaded = null;
  const loadJs = src => new Promise((ok, no) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.append(s); });
  function size() { const w = innerWidth, h = innerHeight; cv.width = w; cv.height = h; if (viz) viz.setRendererSize(w, h); }
  async function init() {
    loaded = loaded || Promise.all([loadJs('/vendor/butterchurn.min.js'), loadJs('/vendor/butterchurnPresets.min.js')]); await loaded;
    const BC = window.butterchurn.default || window.butterchurn; BP = (window.butterchurnPresets.default || window.butterchurnPresets).getPresets();
    keys = CALM.filter(k => BP[k]);
    ac = new (window.AudioContext || window.webkitAudioContext)();
    const src = ac.createMediaElementSource(au); src.connect(ac.destination);
    size(); viz = BC.createVisualizer(ac, cv, {width: cv.width, height: cv.height, pixelRatio: 1, textureRatio: 1});
    viz.connectAudio(src); viz.loadPreset(BP[keys[0]], 0);
  }
  function frame() { viz.render(); raf = requestAnimationFrame(frame); }
  async function open() {
    box.hidden = false; document.body.style.overflow = 'hidden';
    if (box.requestFullscreen) box.requestFullscreen().catch(() => {});
    if (!viz) await init(); else size();
    if (ac.state === 'suspended') await ac.resume();
    au.play().catch(() => {}); cancelAnimationFrame(raf); frame();
    clearInterval(auto); auto = setInterval(() => { ix = (ix + 1) % keys.length; viz.loadPreset(BP[keys[ix]], 8); }, 45000);
  }
  function close() {
    box.hidden = true; document.body.style.overflow = ''; au.pause(); cancelAnimationFrame(raf); clearInterval(auto);
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); go.focus();
  }
  go.onclick = open; $('mk-x').onclick = close;
  addEventListener('keydown', e => { if (e.key === 'Escape' && !box.hidden) close(); });
  addEventListener('resize', () => { if (!box.hidden) size(); });
  document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && !box.hidden) close(); });
})();
