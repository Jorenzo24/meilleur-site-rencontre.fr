#!/usr/bin/env python3
"""Regenere le glossaire /lexique/ a partir de tools/donnees/lexique.json.

Remplace ce qui se trouve entre les reperes de lexique/index.html :
  <!-- lexique:alphabet:debut --> ... <!-- lexique:alphabet:fin -->
  <!-- lexique:liste:debut -->    ... <!-- lexique:liste:fin -->
  <!-- lexique:jsonld:debut -->   ... <!-- lexique:jsonld:fin -->

    python3 tools/hub_lexique.py              # simulation
    python3 tools/hub_lexique.py --appliquer  # ecrit la page

Le script de publication (tools/publier.py) appelle ajouter() puis
regenerer() quand une nouvelle fiche sort de la file d'attente.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / 'tools' / 'donnees' / 'lexique.json'
PAGE = RACINE / 'lexique' / 'index.html'
SITE = 'https://meilleur-site-rencontre.fr'
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def cle(mot):
    """Cle de tri sans accents ni casse."""
    return unicodedata.normalize('NFD', mot).encode('ascii', 'ignore').decode().lower()


def lettre(mot):
    return cle(mot)[:1].upper()


def charger():
    return json.loads(DONNEES.read_text(encoding='utf-8'))


def ajouter(slug, mot, resume, definition='', genre='n. m.', etymologie='', appliquer=False):
    """Ajoute une fiche au fichier de donnees (sans doublon)."""
    d = charger()
    if any(m['slug'] == slug for m in d['mots']):
        return False
    d['mots'].append({'slug': slug, 'mot': mot, 'genre': genre, 'etymologie': etymologie,
                      'resume': resume, 'definition': definition or resume})
    d['mots'].sort(key=lambda m: cle(m['mot']))
    if appliquer:
        DONNEES.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return True


def alphabet(mots):
    presentes = {lettre(m['mot']) for m in mots}
    cases = []
    for l in ALPHABET:
        if l in presentes:
            cases.append('            <li><a href="#lettre-%s">%s</a></li>' % (l.lower(), l))
        else:
            cases.append('            <li><span aria-disabled="true" title="Bientôt">%s</span></li>' % l)
    return '\n'.join(cases)


def liste(mots):
    groupes = {}
    for m in mots:
        groupes.setdefault(lettre(m['mot']), []).append(m)
    blocs = []
    for l in ALPHABET:
        if l not in groupes:
            continue
        entrees = []
        for m in sorted(groupes[l], key=lambda x: cle(x['mot'])):
            ety = (' <span class="lx-ety">(%s)</span>' % m['etymologie']) if m.get('etymologie') else ''
            genre = m.get('genre', 'n. m.').replace(' ', '&nbsp;')
            entrees.append('''            <li class="lx-mot">
              <a href="/lexique/{slug}/">
                <span class="lx-tete"><dfn>{mot}</dfn> <span class="lx-genre">{genre}</span>{ety}</span>
                <span class="lx-def">{definition}</span>
                <span class="lx-lien">Lire la fiche</span>
              </a>
            </li>'''.format(slug=m['slug'], mot=m['mot'], genre=genre, ety=ety, definition=m['definition']))
        blocs.append('''        <section class="lx-lettre" id="lettre-{l}" aria-labelledby="titre-{l}">
          <h2 class="lx-initiale" id="titre-{l}">{L}</h2>
          <ul class="lx-mots">
{e}
          </ul>
        </section>'''.format(l=l.lower(), L=l, e='\n'.join(entrees)))
    return '\n'.join(blocs)


def jsonld(mots):
    data = {
        '@context': 'https://schema.org',
        '@type': 'DefinedTermSet',
        'name': 'Lexique du dating',
        'url': SITE + '/lexique/',
        'inLanguage': 'fr-FR',
        'hasDefinedTerm': [{
            '@type': 'DefinedTerm',
            'name': m['mot'],
            'description': re.sub(r'<[^>]+>', '', m['definition']).replace('&nbsp;', ' '),
            'url': '%s/lexique/%s/' % (SITE, m['slug']),
        } for m in mots],
    }
    return '  <script type="application/ld+json">\n  %s\n  </script>' % json.dumps(
        data, ensure_ascii=False, indent=2).replace('\n', '\n  ')


def remplacer(page, nom, contenu):
    motif = re.compile(r'(<!-- lexique:%s:debut -->).*?(\s*<!-- lexique:%s:fin -->)' % (nom, nom), re.S)
    if not motif.search(page):
        raise SystemExit('Repere lexique:%s introuvable dans lexique/index.html' % nom)
    return motif.sub(lambda m: m.group(1) + '\n' + contenu + m.group(2), page)


def regenerer(appliquer=False):
    mots = charger()['mots']
    page = PAGE.read_text(encoding='utf-8')
    nouvelle = remplacer(page, 'alphabet', alphabet(mots))
    nouvelle = remplacer(nouvelle, 'liste', liste(mots))
    nouvelle = remplacer(nouvelle, 'jsonld', jsonld(mots))
    if nouvelle != page and appliquer:
        PAGE.write_text(nouvelle, encoding='utf-8')
    return nouvelle != page, len(mots)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--appliquer', action='store_true')
    a = ap.parse_args()
    change, n = regenerer(a.appliquer)
    if not change:
        print('Glossaire deja a jour (%d mots).' % n)
    else:
        print('Glossaire %s (%d mots).' % ('regenere' if a.appliquer else 'a regenerer, relancer avec --appliquer', n))


if __name__ == '__main__':
    main()
