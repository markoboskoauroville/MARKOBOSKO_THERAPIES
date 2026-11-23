// DJ Mantra playlista: skladba se učita tek na dodir, jedna po jedna; uz svaku je i poveznica na YouTube (22.11.2026).
// Jedan modul za svaku stranicu (23.11.2026): svaki .pl ima svoj okvir (.video) i svoje gumbe (.pl-b), pa ih na stranici može biti više
// (markobosko.org/showreel koristi isti modul, nepromijenjen). data-t = naslov, događaj pl:play javlja koji je gumb pokrenut.
(() => {
  document.querySelectorAll('.pl').forEach(pl => {
    const box = pl.querySelector('.video'); if (!box) return;
    const btns = [...pl.querySelectorAll('.pl-b')];
    btns.forEach(b => b.onclick = () => {
      btns.forEach(x => x.setAttribute('aria-pressed', x === b));
      box.hidden = false;
      // data-v = YouTube id; data-vm = Vimeo id (23.11.2026, Marko's old Kanal Ri works live on Vimeo)
      const src = b.dataset.vm ? 'https://player.vimeo.com/video/' + b.dataset.vm + '?autoplay=1&dnt=1'
                               : 'https://www.youtube-nocookie.com/embed/' + b.dataset.v + '?autoplay=1&rel=0';
      // data-t = the title when the button holds more text (cards with show/year/duration, markobosko.org/showreel)
      box.innerHTML = '<iframe src="' + src + '" title="' + (b.dataset.t || b.textContent.trim()).replace(/"/g, '') +
        '" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
      box.scrollIntoView({block: 'nearest', behavior: 'smooth'});
      pl.dispatchEvent(new CustomEvent('pl:play', {detail: b}));   // a page may show "now playing" (showreel); nothing listens on therapies
    });
  });
})();
