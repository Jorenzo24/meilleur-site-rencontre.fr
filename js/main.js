document.addEventListener('DOMContentLoaded', function () {
  // Apparition discrete au scroll. Le contenu reste visible si le script ne
  // tourne pas : on ne masque qu'apres avoir pose .reveal-on.
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
