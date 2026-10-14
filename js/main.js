document.addEventListener('DOMContentLoaded', function () {
  // Menu mobile : le bouton ouvre le panneau, Echap ou un lien le ferment
  var toggle = document.querySelector('.nav-toggle');
  var header = document.querySelector('.site-header');
  if (toggle && header) {
    var root = document.documentElement;
    var setHeight = function () { root.style.setProperty('--header-h', header.offsetHeight + 'px'); };
    var close = function () {
      root.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.querySelector('.nav-toggle-t').textContent = 'Menu';
    };
    toggle.addEventListener('click', function () {
      setHeight();
      var open = root.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.querySelector('.nav-toggle-t').textContent = open ? 'Fermer' : 'Menu';
    });
    setHeight();
    window.addEventListener('resize', setHeight);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    header.querySelectorAll('nav a').forEach(function (a) { a.addEventListener('click', close); });
    window.addEventListener('resize', function () { if (window.innerWidth >= 960) close(); });
  }

  // Apparition discrete au scroll. Le contenu reste visible si le script ne
  // tourne pas : on ne masque qu'apres avoir pose .reveal-on.
  // Filtres des hubs : boutons a etat, les entrees sans le filtre sont masquees
  var barre = document.querySelector('[data-filtres-barre]');
  if (barre) {
    var boutons = barre.querySelectorAll('[data-filtre]');
    var entrees = Array.prototype.slice.call(document.querySelectorAll('article[data-filtres]'));
    var resultat = document.querySelector('[data-filtres-resultat]');
    var appliquer = function (cle) {
      var n = 0;
      entrees.forEach(function (el) {
        var ok = cle === 'tous' || (' ' + el.getAttribute('data-filtres') + ' ').indexOf(' ' + cle + ' ') > -1;
        el.hidden = !ok;
        if (ok) { n++; el.classList.add('is-in'); }
        // un fond sur deux, compte sur les avis visibles seulement
        el.classList.toggle('is-alt', ok && n % 2 === 0);
      });
      if (entrees.length) entrees[0].parentNode.classList.add('js-alt');
      boutons.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-filtre') === cle ? 'true' : 'false'); });
      if (resultat) resultat.textContent = cle === 'tous' ? '' : n + (n > 1 ? ' avis correspondent' : ' avis correspond');
    };
    boutons.forEach(function (b) {
      b.addEventListener('click', function () { appliquer(b.getAttribute('data-filtre')); });
    });
    barre.hidden = false;
  }

  var items = document.querySelectorAll('[data-reveal]');
  if (!items.length || !('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px' });

  // Ce qui est deja a l'ecran au chargement n'est pas anime
  var vh = window.innerHeight;
  items.forEach(function (el) {
    if (el.getBoundingClientRect().top < vh) el.classList.add('is-in');
    else io.observe(el);
  });
  document.documentElement.classList.add('reveal-on');
});
