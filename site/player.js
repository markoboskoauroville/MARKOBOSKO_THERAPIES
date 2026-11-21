(() => {
  // Gumbi za trgovine: jedan modul, svako mjesto s data-stores dobije iste gumbe.
  const STORES = [['Google Play', 'https://play.google.com/store/apps/details?id=com.hemisync.hemisyncflow'], ['App Store (iPhone)', 'https://apps.apple.com/us/app/hemi-sync-flow/id1398928728']];
  document.querySelectorAll('[data-stores]').forEach(el => { STORES.forEach(([n, u]) => { const a = document.createElement('a'); a.className = 'btn'; a.href = u; a.rel = 'noopener'; a.textContent = n; el.append(a, ' '); }); });
  // Preporučeni albumi: audio/albums.json + naslovnice u audio/albums/
  const grid = document.getElementById('albums'); if (!grid) return;
  fetch('audio/albums.json', {cache: 'no-cache'}).then(r => r.ok ? r.json() : Promise.reject()).then(d => {
    const a = (Array.isArray(d) ? d : d.albums || []).filter(x => x && (x.album || x.title)); if (!a.length) return;
    grid.innerHTML = '';
    a.forEach(x => {
      const c = document.createElement('div'); c.className = 'album';
      const cover = x.cover || x.image || x.thumb; const img = document.createElement('img'); img.loading = 'lazy'; img.alt = 'Naslovnica albuma ' + (x.album || x.title);
      if (cover) img.src = 'audio/' + (cover.includes('/') ? cover.replace(/^\/?audio\//, '') : 'albums/' + cover); else img.hidden = true;
      const b = document.createElement('b'); b.textContent = x.album || x.title;
      const s = document.createElement('small'); s.textContent = x.artist || '';
      const w = document.createElement('p'); w.textContent = x.why_hr || x.zasto || x.why || '';
      c.append(img, b, s, w);
      if (x.in_player || x.inPlayer || x.sample) { const m = document.createElement('span'); m.className = 'mark'; m.textContent = 'u playeru'; c.append(m); }
      grid.append(c);
    });
  }).catch(() => {});
})();
// Jedan zajednički player za cijelu stranicu: popis uzoraka (audio/samples.json) i način "terapija (demo)" na cijelom zaslonu
// koriste ISTI audio element i isti red skladbi. Slika u terapiji: MilkDrop (butterchurn, isti kao u Mantra Room) ili spore boje čakri.
(() => {
  const $ = id => document.getElementById(id);
  const box = $('player');
  const P = window.Therapy = {tracks: [], groups: [], i: -1, audio: new Audio(), listeners: []};
  P.audio.preload = 'none'; P.audio.muted = false; P.audio.volume = 1;
  // iPhone/Safari: sound as "playback", so the mute switch and an unconnected WebAudio context (MilkDrop) cannot silence the music
  try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}
  const tell = () => P.listeners.forEach(f => f());
  P.src = t => 'audio/' + t.file.replace(/^\/?audio\//, '');
  P.play = i => { if (!P.tracks.length) return; P.i = (i + P.tracks.length) % P.tracks.length; P.audio.src = P.src(P.tracks[P.i]); P.audio.play().catch(() => {}); tell(); };
  P.toggle = () => { if (P.i < 0) P.play(0); else if (P.audio.paused) P.audio.play().catch(() => {}); else P.audio.pause(); tell(); };
  P.audio.onended = () => P.play(P.i + 1);
  P.audio.onplay = P.audio.onpause = tell;
  P.audio.onerror = () => { const n = document.getElementById('tm-title'); const m = 'Zvuk se ne može učitati. Pokušaj ponovno ili odaberi drugu skladbu.'; if (n) n.textContent = m; };
  P.audio.volume = 1;
  if (!box) return;   // pages without #player (the admin catalogue) use only P: the one shared audio element

  const say = t => { box.innerHTML = '<p class="todo">' + t + '</p>'; };
  const tr = t => ({title: t.title || t.name || t.file, file: t.file || t.src || t.url, sub: t.artist || t.sub || '',
    label: (t.n ? String(t.n).padStart(2, '0') + '. ' : '') + (t.title || t.name || t.file) + ((t.artist || t.sub) ? ' · ' + (t.artist || t.sub) : '')});
  (async () => {
    let data;
    try { const r = await fetch('audio/samples.json', {cache: 'no-cache'}); if (!r.ok) throw 0; data = await r.json(); }
    catch (e) { say('Uzorci od jedne minute stižu uskoro.'); return; }
    let groups = [];
    const bucket = a => { const m = new Map(); a.forEach(t => { const c = t.category || t.group || 'Uzorci'; if (!m.has(c)) m.set(c, []); m.get(c).push(tr(t)); }); return [...m].map(([title, tracks]) => ({title, tracks})); };
    if (Array.isArray(data)) groups = bucket(data);
    else if (data.groups) groups = data.groups.map(g => ({title: g.title || g.name || g.id, tracks: (g.tracks || []).map(tr)}));
    else if (data.categories && !Array.isArray(data.categories)) groups = Object.entries(data.categories).map(([title, a]) => ({title, tracks: a.map(tr)}));
    else if (data.tracks) groups = bucket(data.tracks);
    else if (data.samples) groups = bucket(data.samples);
    groups = groups.filter(g => g.tracks.length && g.tracks.every(t => t.file));
    if (!groups.length) { say('Uzorci od jedne minute stižu uskoro.'); return; }
    P.groups = groups; P.tracks = groups.flatMap(g => g.tracks);
    const tabs = document.createElement('div'); tabs.className = 'tabs'; tabs.setAttribute('role', 'group'); tabs.setAttribute('aria-label', 'Vrsta glazbe');
    const list = document.createElement('div'); let gi = 0;
    function show(k) {
      gi = k; [...tabs.children].forEach((b, j) => b.setAttribute('aria-pressed', j === k)); list.innerHTML = '';
      groups[k].tracks.forEach(t => {
        const idx = P.tracks.indexOf(t), row = document.createElement('div'); row.className = 'trk';
        const b = document.createElement('button'); b.type = 'button'; b.dataset.idx = idx; b.setAttribute('aria-label', 'Slušaj: ' + t.title);
        const d = document.createElement('div'); d.className = 't'; d.innerHTML = '<b></b><small></small>';
        d.firstChild.textContent = t.label; d.lastChild.textContent = '';
        b.onclick = () => P.i === idx ? P.toggle() : P.play(idx);
        row.append(b, d); list.append(row);
      }); mark();
    }
    function mark() { list.querySelectorAll('button').forEach(b => { b.textContent = (+b.dataset.idx === P.i && !P.audio.paused) ? '❚❚' : '▶'; }); }
    P.listeners.push(mark);
    groups.forEach((g, k) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = g.title; b.onclick = () => show(k); tabs.append(b); });
    box.innerHTML = ''; box.append(tabs, list); show(0);
    const go = $('therapy-start'); if (go) { go.disabled = false; go.removeAttribute('aria-disabled'); }
  })();

  // ---------- terapija (demo): cijeli zaslon ----------
  const go = $('therapy-start'), tm = $('tm'); if (!go || !tm) return;
  const cv = $('tm-cv'), col = $('tm-col'), title = $('tm-title'), ui = $('tm-ui'), pp = $('tm-pp');
  // samo spori, nježni MilkDrop predlošci (isti popis kao u Mantra Room); zvuk se ne šalje u vizualizaciju, pa slika ne reagira na ritam
  const CALM = ['martin - castle in the air', 'cope + martin - mother-of-pearl', 'Aderrasi - Songflower (Moss Posy)', 'martin - frosty caves 2'];
  const COLORS = ['#6a1b1b', '#7a4a14', '#7a6a14', '#1f5a2e', '#14507a', '#2a2a7a', '#5a1f7a', '#8a7330'];   // spore, prigušene boje čakri i zlato
  let fsOn = false, mode = 'milk', viz = null, raf = 0, auto = 0, colI = 0, colT = 0, hideT = 0, ac = null, loading = null, open = false;
  const flat = new Uint8Array(1024).fill(128);
  const loadJs = src => new Promise((ok, no) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.append(s); });
  async function initMilk() {
    if (viz) return true;
    try {
      loading = loading || Promise.all([loadJs('vendor/butterchurn.min.js'), loadJs('vendor/butterchurnPresets.min.js')]); await loading;
      const BC = window.butterchurn.default || window.butterchurn, BP = (window.butterchurnPresets.default || window.butterchurnPresets).getPresets();
      const keys = CALM.filter(k => BP[k]); if (!keys.length) return false;
      ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      const w = Math.round(innerWidth * .7), h = Math.round(innerHeight * .7); cv.width = w; cv.height = h;
      viz = BC.createVisualizer(ac, cv, {width: w, height: h, pixelRatio: 1, textureRatio: 1});
      viz.keys = keys; viz.all = BP; viz.ix = 0; P.viz = viz; viz.loadPreset(BP[keys[0]], 0); return true;
    } catch (e) { return false; }
  }
  function frame() {
    if (!open || mode !== 'milk' || !viz) return;
    viz.render({audioLevels: {timeByteArray: flat, timeByteArrayL: flat, timeByteArrayR: flat}}); raf = requestAnimationFrame(frame);
  }
  function setMode(m) {
    mode = m; cv.hidden = m !== 'milk'; col.hidden = m !== 'col';
    document.querySelectorAll('#tm-ui [data-mode]').forEach(b => b.setAttribute('aria-pressed', b.dataset.mode === m));
    clearInterval(auto); cancelAnimationFrame(raf);
    if (m === 'col') { col.style.transition = 'none'; col.style.backgroundColor = COLORS[colI]; void col.offsetWidth; col.style.transition = ''; auto = setInterval(() => { colI = (colI + 1) % COLORS.length; col.style.backgroundColor = COLORS[colI]; }, 12000); }
    else initMilk().then(ok => {
      if (!open || mode !== 'milk') return;
      if (!ok) { setMode('col'); return; }
      raf = requestAnimationFrame(frame);
      auto = setInterval(() => { viz.ix = (viz.ix + 1) % viz.keys.length; viz.loadPreset(viz.all[viz.keys[viz.ix]], 6); }, 40000);
    });
  }
  function names() { const t = P.tracks[P.i]; title.textContent = t ? t.label : 'Pritisni ▶ za početak'; pp.textContent = P.audio.paused ? '▶' : '❚❚'; pp.setAttribute('aria-label', P.audio.paused ? 'Pokreni' : 'Pauziraj'); }
  P.listeners.push(names);
  function wake() { ui.classList.remove('off'); clearTimeout(hideT); hideT = setTimeout(() => ui.classList.add('off'), 4000); }
  function openTm() {
    open = true; tm.hidden = false; document.body.style.overflow = 'hidden'; names(); wake();
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; setMode(reduce ? 'col' : mode);
    if (tm.requestFullscreen) tm.requestFullscreen().then(() => { fsOn = true; }).catch(() => {});
    if (P.i < 0) P.play(0);
  }
  function closeTm() {
    open = false; fsOn = false; tm.hidden = true; document.body.style.overflow = ''; clearInterval(auto); cancelAnimationFrame(raf); clearTimeout(hideT);
    P.audio.pause(); if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); go.focus();
  }
  go.onclick = openTm;
  $('tm-x').onclick = closeTm;
  $('tm-prev').onclick = () => { P.play(P.i - 1); wake(); };
  $('tm-next').onclick = () => { P.play(P.i + 1); wake(); };
  pp.onclick = () => { P.toggle(); wake(); };
  document.querySelectorAll('#tm-ui [data-mode]').forEach(b => b.onclick = () => { setMode(b.dataset.mode); wake(); });
  tm.addEventListener('pointerdown', wake); tm.addEventListener('mousemove', wake);
  document.addEventListener('keydown', e => { if (!open) return; if (e.key === 'Escape') closeTm(); else if (e.key === ' ') { e.preventDefault(); P.toggle(); wake(); } else if (e.key === 'ArrowRight') P.play(P.i + 1); else if (e.key === 'ArrowLeft') P.play(P.i - 1); });
  document.addEventListener('fullscreenchange', () => { if (open && fsOn && !document.fullscreenElement) closeTm(); });
})();
