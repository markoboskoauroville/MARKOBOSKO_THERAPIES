// DJ Mantra playlista: skladba se učita tek na dodir, jedna po jedna; uz svaku je i poveznica na YouTube (22.11.2026).
// Jedan modul za svaku stranicu (23.11.2026): svaki .pl ima svoj okvir (.video) i svoje gumbe (.pl-b), pa ih na stranici može biti više
// (markobosko.org/showreel koristi isti modul, nepromijenjen). data-t = naslov, događaj pl:play javlja koji je gumb pokrenut.
// Samo jedan video svira (23.11.2026, Marko): kad krene bilo koji YouTube ili Vimeo video na stranici, svi ostali se pauziraju.
(() => {
  // ---- one video at a time: every YouTube / Vimeo iframe on the page, via their postMessage APIs ----
  const YT = /youtube(-nocookie)?\.com\/embed\//, VM = /player\.vimeo\.com\/video\//;
  const kind = f => YT.test(f.src) ? 'yt' : VM.test(f.src) ? 'vm' : '';
  const send = (f, msg) => { try { f.contentWindow && f.contentWindow.postMessage(JSON.stringify(msg), '*'); } catch (e) {} };
  function withApi(src) {   // YouTube answers postMessage only with enablejsapi=1 (and the page origin)
    if (!YT.test(src) || /[?&]enablejsapi=1/.test(src)) return src;
    return src + (src.includes('?') ? '&' : '?') + 'enablejsapi=1&origin=' + encodeURIComponent(location.origin);
  }
  function hello(f) {       // ask the player to report its state
    const k = kind(f);
    if (k === 'yt') send(f, {event: 'listening', id: 'pl', channel: 'widget'});
    if (k === 'vm') send(f, {method: 'addEventListener', value: 'play'});
  }
  function watch(f) {
    if (!kind(f) || f.dataset.plOne) return;
    f.dataset.plOne = '1';
    const s = withApi(f.src); if (s !== f.src) f.src = s;
    f.addEventListener('load', () => { hello(f); setTimeout(() => hello(f), 800); });
  }
  function pauseOthers(src) {
    document.querySelectorAll('iframe').forEach(f => {
      if (f.contentWindow === src) return;
      const k = kind(f);
      if (k === 'yt') send(f, {event: 'command', func: 'pauseVideo', args: []});
      if (k === 'vm') send(f, {method: 'pause'});
    });
  }
  window.addEventListener('message', e => {
    if (!/youtube(-nocookie)?\.com$|vimeo\.com$/.test(new URL(e.origin).hostname)) return;
    let d = e.data; try { if (typeof d === 'string') d = JSON.parse(d); } catch (x) { return; }
    if (!d) return;
    const ytPlaying = (d.event === 'onStateChange' && d.info === 1) || (d.event === 'infoDelivery' && d.info && d.info.playerState === 1);
    if (ytPlaying || d.event === 'play') pauseOthers(e.source);
  });
  document.querySelectorAll('iframe').forEach(watch);

  // ---- the player: tap a .pl-b, it plays in its own .video box ----
  document.querySelectorAll('.pl').forEach(pl => {
    const box = pl.querySelector('.video'); if (!box) return;
    const btns = [...pl.querySelectorAll('.pl-b')];
    btns.forEach(b => b.onclick = () => {
      btns.forEach(x => x.setAttribute('aria-pressed', x === b));
      box.hidden = false;
      // data-v = YouTube id; data-vm = Vimeo id (23.11.2026, Marko's old Kanal Ri works live on Vimeo)
      const src = b.dataset.vm ? 'https://player.vimeo.com/video/' + b.dataset.vm + '?autoplay=1&dnt=1'
                               : withApi('https://www.youtube-nocookie.com/embed/' + b.dataset.v + '?autoplay=1&rel=0');
      // data-t = the title when the button holds more text (cards with show/year/duration, markobosko.org/showreel)
      box.innerHTML = '<iframe src="' + src + '" title="' + (b.dataset.t || b.textContent.trim()).replace(/"/g, '') +
        '" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
      const f = box.querySelector('iframe'); watch(f);
      pauseOthers(f.contentWindow);   // a tap starts this one: the rest stop at once
      box.scrollIntoView({block: 'nearest', behavior: 'smooth'});
      pl.dispatchEvent(new CustomEvent('pl:play', {detail: b}));   // a page may show "now playing" (showreel); nothing listens on therapies
    });
  });
})();
