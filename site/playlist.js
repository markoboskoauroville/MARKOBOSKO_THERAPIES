// DJ Mantra playlista: skladba se učita tek na dodir, jedna po jedna; uz svaku je i poveznica na YouTube (22.11.2026).
(() => {
  const box = document.getElementById('pl-box'); if (!box) return;
  const btns = [...document.querySelectorAll('.pl-b')];
  btns.forEach(b => b.onclick = () => {
    btns.forEach(x => x.setAttribute('aria-pressed', x === b));
    box.hidden = false;
    box.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + b.dataset.v + '?autoplay=1&rel=0" title="' + b.textContent.trim().replace(/"/g, '') +
      '" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    box.scrollIntoView({block: 'nearest', behavior: 'smooth'});
  });
})();
