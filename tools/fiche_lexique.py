#!/usr/bin/env python3
"""Construit une fiche du lexique a partir de sa source JSON.

Sources : tools/donnees/fiches/<slug>.json (format documente dans
tools/donnees/fiches/LISEZMOI.md). Sortie : lexique/<slug>/index.html pour une
fiche en ligne, _planning/lexique/<slug>/index.html pour une fiche en attente.

Les "termes lies" ne pointent que vers des fiches deja en ligne : a chaque
publication, publier.py reconstruit toutes les fiches en ligne pour que les
liens apparaissent au fil de l'eau, sans jamais pointer vers une page absente.

    python3 tools/fiche_lexique.py ghosting --appliquer      # une fiche
    python3 tools/fiche_lexique.py --en-ligne --appliquer    # toutes les fiches en ligne
"""
import argparse
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCES = RACINE / 'tools' / 'donnees' / 'fiches'
SITE = 'https://meilleur-site-rencontre.fr'

AUTEURS = {
    'lucie': ('Lucie', 'Rédactrice · web, modes de vie et relations',
              "Je regarde ce qui compte vraiment pour l'utilisateur : qualité des profils, ambiance, simplicité et clarté des abonnements."),
    'marie': ('Marie', 'Rédactrice · célibat et usages numériques',
              "Je compare les plateformes avec un regard concret et j'essaie de rendre les avis plus humains et moins froids."),
    'patrice': ('Patrice', 'Rédacteur · veille digitale et services en ligne',
                "Je m'intéresse à la fiabilité, à la lisibilité des offres et aux différences concrètes entre les services."),
    'jeanne': ('Jeanne', 'Rédactrice · société et rencontres en ligne',
               "J'attache de l'importance à la sécurité, à la sincérité des profils et à l'ambiance des communautés."),
    'bastien': ('Bastien', 'Rédacteur · analyse de plateformes et SEO',
                "Je décortique chaque plateforme avec une approche pratique : inscription, navigation, messagerie, modération, rapport qualité-prix."),
}

# Lectures complementaires possibles (toutes deja en ligne)
LECTURES = {
    '/guide/premier-message/': ('Premier message : exemples et accroches', "Des accroches qui ouvrent vraiment la conversation, selon le profil.", '/assets/guides/guide-premier-message.webp'),
    '/guide/premier-rendez-vous/': ('Le premier rendez-vous après une rencontre en ligne', "Quand se voir, où, et ce que deviennent ces rendez-vous, d'après les études.", '/assets/guides/guide-premier-rendez-vous.webp'),
    '/guide/profil-attractif/': ('Rédiger un profil qui attire', "Photos, bio, intentions : les leviers d'un profil qui donne envie d'écrire.", '/assets/guides/guide-profil-attractif.webp'),
    '/guide/faux-profils/': ('Reconnaître un faux profil', "Signaux d'alerte, arnaques sentimentales et vérifications simples.", '/assets/guides/guide-faux-profils.webp'),
    '/guide/site-fiable/': ('Choisir un site de rencontre fiable', "La check-list à dérouler avant de s'inscrire.", '/assets/guides/guide-site-fiable.webp'),
    '/avis/': ('Nos avis sur les sites de rencontre', "Chaque plateforme testée avec un vrai profil, notée et signée.", '/assets/ui-meetic.webp'),
    '/comparatif-relation-serieuse/': ('Les sites de rencontre sérieux', "Notre classement des plateformes pour une relation durable.", '/assets/comparatifs/comparatif-relation-serieuse.webp'),
    '/comparatif-seniors/': ('Les sites de rencontre seniors', "Les plateformes où les plus de 50 ans sont vraiment représentés.", '/assets/comparatifs/comparatif-seniors.webp'),
    '/comparatif-gay/': ('Les sites de rencontre gay', "Plateformes dédiées et sites généralistes qui accueillent vraiment.", '/assets/comparatifs/comparatif-gay.webp'),
}

COEUR = ('<svg class="btn-coeur-ico" width="15" height="14" viewBox="0 0 24 22" aria-hidden="true">'
         '<path d="M12 20.3s-8.8-5.3-8.8-11.4A4.9 4.9 0 0 1 12 6.1a4.9 4.9 0 0 1 8.8 2.8c0 6.1-8.8 11.4-8.8 11.4z"/></svg>')
FLECHE = ('<svg class="btn-coeur-fl" width="18" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true">'
          '<path d="M1 5h15M12 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
MOTIFS = ['telephone', 'lettre', 'cafe', 'avion', 'bulles', 'plume', 'loupe']


def texte(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()


def en_ligne(slug):
    return (RACINE / 'lexique' / slug / 'index.html').exists()


def source(slug):
    return json.loads((SOURCES / (slug + '.json')).read_text(encoding='utf-8'))


def conversation(c):
    bulles = []
    for m in c['messages']:
        classe = 'ch-bulle ch-bulle--recu' if m['de'] == 'recu' else 'ch-bulle'
        bulles.append('            <p class="%s">%s</p>' % (classe, m['texte']))
    nom = c.get('nom', 'Nouveau match')
    return ('''        <figure class="ch ch--recu">
          <figcaption class="visually-hidden">{leg}</figcaption>
          <div class="ch-tete"><span class="ch-av" aria-hidden="true">{ini}</span><span class="ch-nom">{nom}<span class="ch-ligne">en ligne</span></span></div>
          <div class="ch-fil">
{b}
          </div>
        </figure>'''.format(leg=html.escape(c.get('legende', 'Exemple de conversation')), ini=nom[0], nom=nom, b='\n'.join(bulles)))


def article(f):
    blocs = []
    for i, s in enumerate(f['sections']):
        corps = s['html'].strip()
        conv = f.get('conversation')
        if conv and conv.get('apres') == s['id']:
            corps += '\n' + conversation(conv) + ('\n        ' + conv['commentaire'] if conv.get('commentaire') else '')
        blocs.append('''      <section id="{id}" class="av-sec">
        <div class="av-prose">
        <h2><span class="tt">{t}</span></h2>
        {c}
        </div>
      </section>'''.format(id=s['id'], t=s['titre'], c=corps))
    if f.get('parti_pris'):
        blocs.append('''      <section class="av-sec">
        <div class="av-prose">
        <aside class="av-parti">
          <p class="av-parti-t">Le parti pris de la rédaction</p>
          <blockquote><p>{p}</p></blockquote>
        </aside>
        </div>
      </section>'''.format(p=f['parti_pris']))
    return '\n\n'.join(blocs)


def lies(f):
    items = []
    for slug in f.get('lies', []):
        if slug == f['slug'] or not en_ligne(slug) or not (SOURCES / (slug + '.json')).exists():
            continue
        s = source(slug)
        items.append('          <li><a href="/lexique/{s}/"><span class="lxf-lie-mot">{m}</span><span class="lxf-lie-res">{r}</span></a></li>'.format(
            s=slug, m=s['mot'], r=s['resume']))
    if not items:
        return ''
    return '''    <section class="lxf-lies" aria-labelledby="lies-titre">
      <div class="container">
        <h2 id="lies-titre" class="lxf-lies-t">Termes liés</h2>
        <ul>
{i}
        </ul>
      </div>
    </section>
'''.format(i='\n'.join(items[:4]))


def lectures(f):
    cartes = []
    for url in f.get('lire_aussi', [])[:3]:
        if url not in LECTURES:
            continue
        t, d, img = LECTURES[url]
        cartes.append('''          <a class="av-autre" href="{u}">
            <span class="av-autre-img"><img src="{img}" alt="" width="960" height="480" loading="lazy"></span>
            <span class="av-autre-tete"><span class="av-autre-nom">{t}</span></span>
            <span class="av-autre-acc">{d}</span>
          </a>'''.format(u=url, img=img, t=t, d=d))
    if not cartes:
        return ''
    return '''    <section class="av-autres">
      <div class="container">
        <h2 class="av-h2">Pour aller plus loin</h2>
        <div class="av-autres-grille" data-reveal>
{c}
        </div>
        <a class="btn-coeur" href="/lexique/">{coeur}<span>Tout le lexique</span>{fl}</a>
      </div>
    </section>
'''.format(c='\n'.join(cartes), coeur=COEUR, fl=FLECHE)


def ld(o):
    return '  <script type="application/ld+json">\n  %s\n  </script>' % json.dumps(o, ensure_ascii=False, indent=2).replace('\n', '\n  ')


def page(f, version):
    a_nom, a_role, a_bio = AUTEURS[f['auteur']]
    url = '%s/lexique/%s/' % (SITE, f['slug'])
    ety = (' <span class="lxf-ety">(%s)</span>' % f['etymologie']) if f.get('etymologie') else ''
    genre = f.get('genre', 'n. m.').replace(' ', '&nbsp;')
    deco = ''.join('<span class="gd-m gd-m--%s" style="--y:%d%%"></span>' % (m, y) for m, y in zip(MOTIFS, [8, 24, 40, 56, 72, 88]))
    schemas = '\n'.join([
        ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Lexique', 'item': SITE + '/lexique/'},
            {'@type': 'ListItem', 'position': 3, 'name': f['mot'], 'item': url}]}),
        ld({'@context': 'https://schema.org', '@type': 'DefinedTerm', 'name': f['mot'],
            'description': texte(f['definition']), 'url': url,
            'inDefinedTermSet': {'@type': 'DefinedTermSet', 'name': 'Lexique du dating', 'url': SITE + '/lexique/'}}),
        ld({'@context': 'https://schema.org', '@type': 'Article', 'headline': texte(f['h1']),
            'description': f['description'],
            'author': {'@type': 'Person', 'name': a_nom, 'url': '%s/auteurs/%s/' % (SITE, f['auteur'])},
            'publisher': {'@id': SITE + '/#organization'},
            'datePublished': f['publie_le'], 'dateModified': f.get('modifie_le', f['publie_le']),
            'mainEntityOfPage': url}),
    ])
    mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    a, m, j = f.get('modifie_le', f['publie_le']).split('-')
    date_txt = '%d %s %s' % (int(j), mois[int(m) - 1], a)
    gabarit = (RACINE / 'tools' / 'gabarits' / 'fiche_lexique.html').read_text(encoding='utf-8')
    return gabarit.format(
        title=html.escape(f['title']), description=html.escape(f['description']), url=url,
        og_description=html.escape(f.get('og_description', f['description'])), v=version,
        schemas=schemas, mot=f['mot'], h1=f['h1'], lede=f['lede'], auteur=f['auteur'], a_nom=a_nom,
        date=date_txt, genre=genre, ety=ety, definition=f['definition'], deco=deco,
        article=article(f), lies=lies(f), a_role=a_role, a_bio=a_bio, lectures=lectures(f),
        coeur=COEUR, fleche=FLECHE)


def version_courante():
    t = (RACINE / 'index.html').read_text(encoding='utf-8')
    return re.search(r'style\.css\?v=([0-9-]+)', t).group(1)


def construire(slug, appliquer, dossier=None):
    f = source(slug)
    cible = (dossier or ('lexique' if en_ligne(slug) else '_planning/lexique'))
    chemin = RACINE / cible / slug / 'index.html'
    contenu = page(f, version_courante())
    if appliquer:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(contenu, encoding='utf-8')
    return chemin, len(texte(re.sub(r'(?s)<head>.*?</head>|<header class="site-header">.*?</header>|<footer.*?</footer>', '', contenu)).split())


def reconstruire_en_ligne(appliquer=True):
    faits = []
    for p in sorted(SOURCES.glob('*.json')):
        if en_ligne(p.stem):
            construire(p.stem, appliquer)
            faits.append(p.stem)
    return faits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slugs', nargs='*')
    ap.add_argument('--en-ligne', action='store_true')
    ap.add_argument('--planning', action='store_true', help='toutes les fiches en attente')
    ap.add_argument('--appliquer', action='store_true')
    a = ap.parse_args()
    slugs = list(a.slugs)
    if a.en_ligne:
        slugs += [p.stem for p in sorted(SOURCES.glob('*.json')) if en_ligne(p.stem)]
    if a.planning:
        slugs += [p.stem for p in sorted(SOURCES.glob('*.json')) if not en_ligne(p.stem)]
    for s in slugs:
        chemin, mots = construire(s, a.appliquer)
        print('%-28s %4d mots  -> %s' % (s, mots, chemin.relative_to(RACINE)))


if __name__ == '__main__':
    main()
