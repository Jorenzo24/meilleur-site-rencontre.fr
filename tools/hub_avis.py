#!/usr/bin/env python3
"""Regenere la liste du hub /avis/ a partir de tools/donnees/avis.json.

Remplace ce qui se trouve entre les reperes de avis/index.html :
  <!-- avis:filtres:debut --> ... <!-- avis:filtres:fin -->
  <!-- avis:liste:debut -->   ... <!-- avis:liste:fin -->
  <!-- avis:jsonld:debut -->  ... <!-- avis:jsonld:fin -->

    python3 tools/hub_avis.py              # simulation : dit ce qui changerait
    python3 tools/hub_avis.py --appliquer  # ecrit la page
"""
import argparse
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / 'tools' / 'donnees' / 'avis.json'
PAGE = RACINE / 'avis' / 'index.html'
SITE = 'https://meilleur-site-rencontre.fr'

COEUR = ('<svg class="btn-coeur-ico" width="15" height="14" viewBox="0 0 24 22" aria-hidden="true">'
         '<path d="M12 20.3s-8.8-5.3-8.8-11.4A4.9 4.9 0 0 1 12 6.1a4.9 4.9 0 0 1 8.8 2.8c0 6.1-8.8 11.4-8.8 11.4z"/></svg>')
FLECHE = ('<svg class="btn-coeur-fl" width="18" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true">'
          '<path d="M1 5h15M12 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def e(texte):
    return html.escape(texte, quote=True)


def filtres(donnees):
    avis = donnees['avis']
    lignes = ['          <button type="button" class="hb-filtre" data-filtre="tous" aria-pressed="true">'
              'Tous <span>%d</span></button>' % len(avis)]
    for cle, libelle in donnees['filtres'].items():
        n = sum(1 for a in avis if cle in a['filtres'])
        if n:
            lignes.append('          <button type="button" class="hb-filtre" data-filtre="%s" aria-pressed="false">'
                          '%s <span>%d</span></button>' % (cle, e(libelle), n))
    return '\n'.join(lignes)


def liste(donnees):
    blocs = []
    for rang, a in enumerate(donnees['avis'], 1):
        url = '/avis-%s/' % a['slug']
        tags = ''.join('<li>%s</li>' % e(donnees['filtres'][f]) for f in a['filtres'])
        blocs.append('''        <article class="hb-avis" id="avis-{slug}" data-filtres="{filtres}" data-reveal>
          <a class="hb-avis-shot" href="{url}" tabindex="-1" aria-hidden="true">
            <img src="{image}" alt="" width="{il}" height="{ih}" loading="{loading}">
          </a>
          <div class="hb-avis-corps">
            <header class="hb-avis-tete">
              <span class="hb-avis-rang">{rang:02d}</span>
              <div class="hb-avis-titre">
                <h2><a href="{url}">Avis {nom}</a></h2>
                <p>{accroche}</p>
              </div>
              <p class="hb-avis-note"><span>{note}</span>/5</p>
            </header>
            <ul class="hb-avis-tags">{tags}</ul>
            <blockquote class="hb-avis-verdict">
              <p>{verdict}</p>
              <footer>
                <img src="/assets/auteurs/{auteur}.webp" alt="" width="36" height="36" loading="lazy">
                <span><a href="/auteurs/{auteur}/">{auteur_nom}</a>, mis à jour le <time datetime="{maj_iso}">{maj}</time></span>
              </footer>
            </blockquote>
            <dl class="hb-avis-fit">
              <div><dt>Pour vous si</dt><dd>{pour}</dd></div>
              <div><dt>Moins pour vous si</dt><dd>{moins}</dd></div>
            </dl>
            <p class="hb-avis-acces">Accès&nbsp;: {acces}</p>
            <div class="hb-avis-actions">
              <a class="btn-coeur" href="{url}">{coeur}<span>Lire l'avis de {auteur_nom}</span>{fleche}</a>
              <a class="btn-site" href="{go}" rel="sponsored nofollow" target="_blank">Voir le site</a>
            </div>
          </div>
        </article>'''.format(
            slug=a['slug'], filtres=' '.join(a['filtres']), url=url, image=a['image'],
            il=a['image_l'], ih=a['image_h'], loading='eager' if rang == 1 else 'lazy',
            rang=rang, nom=e(a['nom']), accroche=e(a['accroche']), note=a['note'], tags=tags,
            verdict=e('« ' + a['verdict'] + ' »').replace('« ', '«&nbsp;').replace(' »', '&nbsp;»'),
            auteur=a['auteur'], auteur_nom=e(a['auteur_nom']), maj=a['maj'], maj_iso=a['maj_iso'],
            pour=e(a['pour']), moins=e(a['moins']), acces=e(a['acces']), go=a['go'],
            coeur=COEUR, fleche=FLECHE))
    return '\n'.join(blocs)


def jsonld(donnees):
    elements = [{
        '@type': 'ListItem',
        'position': i,
        'name': 'Avis ' + a['nom'],
        'url': SITE + '/avis-%s/' % a['slug'],
    } for i, a in enumerate(donnees['avis'], 1)]
    bloc = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Nos avis sur les sites de rencontre',
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'numberOfItems': len(elements),
        'itemListElement': elements,
    }
    texte = json.dumps(bloc, ensure_ascii=False, indent=2).replace('\n', '\n  ')
    return '  <script type="application/ld+json">\n  %s\n  </script>' % texte


def remplacer(page, nom, contenu):
    motif = re.compile(r'(<!-- avis:%s:debut -->).*?(\s*<!-- avis:%s:fin -->)' % (nom, nom), re.S)
    if not motif.search(page):
        raise SystemExit('Repere avis:%s introuvable dans avis/index.html' % nom)
    return motif.sub(lambda m: m.group(1) + '\n' + contenu + m.group(2), page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--appliquer', action='store_true')
    args = parser.parse_args()

    donnees = json.loads(DONNEES.read_text(encoding='utf-8'))
    page = PAGE.read_text(encoding='utf-8')
    nouvelle = remplacer(page, 'filtres', filtres(donnees))
    nouvelle = remplacer(nouvelle, 'liste', liste(donnees))
    nouvelle = remplacer(nouvelle, 'jsonld', jsonld(donnees))

    if nouvelle == page:
        print('Hub /avis/ deja a jour (%d avis).' % len(donnees['avis']))
    elif args.appliquer:
        PAGE.write_text(nouvelle, encoding='utf-8')
        print('Hub /avis/ regenere (%d avis).' % len(donnees['avis']))
    else:
        print('Le hub /avis/ changerait. Relancer avec --appliquer.')


if __name__ == '__main__':
    main()
