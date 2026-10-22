#!/usr/bin/env python3
"""Genere /auteurs/ et les pages des redacteurs.

Les publications de chaque auteur sont retrouvees automatiquement sur le
site (avis, comparatifs, guides, fiches du lexique en ligne) : rien a tenir
a jour a la main. publier.py relance ce script a chaque publication.

    python3 tools/pages_auteurs.py --appliquer
"""
import argparse
import glob
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = 'https://meilleur-site-rencontre.fr'
AUTEURS = json.loads((RACINE / 'tools' / 'donnees' / 'auteurs.json').read_text(encoding='utf-8'))
ORDRE = ['lucie', 'marie', 'patrice', 'jeanne', 'bastien']
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
COEUR = ('<svg class="btn-coeur-ico" width="15" height="14" viewBox="0 0 24 22" aria-hidden="true">'
         '<path d="M12 20.3s-8.8-5.3-8.8-11.4A4.9 4.9 0 0 1 12 6.1a4.9 4.9 0 0 1 8.8 2.8c0 6.1-8.8 11.4-8.8 11.4z"/></svg>')
FLECHE = ('<svg class="btn-coeur-fl" width="18" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true">'
          '<path d="M1 5h15M12 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def lire(p):
    return (RACINE / p).read_text(encoding='utf-8')


def net(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()


def auteur_de(t):
    m = re.search(r'Par <a href="/auteurs/(\w+)/"', t)
    return m.group(1) if m else None


def date_maj(t):
    m = re.search(r'"dateModified": "([0-9-]+)"', t)
    return m.group(1) if m else ''


def publications():
    pubs = {a: [] for a in ORDRE}
    avis = {a['slug']: a for a in json.loads(lire('tools/donnees/avis.json'))['avis']}
    for p in sorted(glob.glob(str(RACINE / 'avis-*/index.html'))):
        t = Path(p).read_text(encoding='utf-8')
        slug = Path(p).parent.name.replace('avis-', '')
        a = auteur_de(t)
        if a in pubs and slug in avis:
            d = avis[slug]
            pubs[a].append({'type': 'avis', 'url': '/avis-%s/' % slug, 'titre': 'Avis ' + d['nom'],
                            'sous': d['accroche'], 'note': d['note'], 'image': d['image'],
                            'il': d['image_l'], 'ih': d['image_h'], 'date': date_maj(t)})
    for dossier, typ in (('comparatif-*', 'comparatif'), ('guide/*', 'guide')):
        for p in sorted(glob.glob(str(RACINE / dossier / 'index.html'))):
            t = Path(p).read_text(encoding='utf-8')
            a = auteur_de(t)
            if a not in pubs:
                continue
            url = '/' + str(Path(p).parent.relative_to(RACINE)) + '/'
            img = re.search(r'<figure class="(?:gd|cp)-photo">\s*<img src="([^"]+)"', t)
            pubs[a].append({'type': typ, 'url': url, 'titre': net(re.search(r'<h1>(.*?)</h1>', t, re.S).group(1)),
                            'sous': net(re.search(r'name="description" content="([^"]*)"', t).group(1)),
                            'image': img.group(1) if img else '', 'date': date_maj(t)})
    for p in sorted(glob.glob(str(RACINE / 'tools/donnees/fiches/*.json'))):
        d = json.loads(Path(p).read_text(encoding='utf-8'))
        if not (RACINE / 'lexique' / d['slug'] / 'index.html').exists():
            continue
        if d['auteur'] in pubs:
            pubs[d['auteur']].append({'type': 'lexique', 'url': '/lexique/%s/' % d['slug'], 'titre': d['mot'],
                                      'sous': d['resume'], 'date': d.get('modifie_le', d['publie_le'])})
    return pubs


def btn(h, l):
    return '<a class="btn-coeur" href="%s">%s<span>%s</span>%s</a>' % (h, COEUR, l, FLECHE)


def bloc_publications(liste):
    parties = []
    avis = [p for p in liste if p['type'] == 'avis']
    if avis:
        items = '\n'.join('''            <li><a class="au-avis" href="{url}">
              <span class="au-avis-img"><img src="{image}" alt="" width="{il}" height="{ih}" loading="lazy"></span>
              <span class="au-avis-tete"><span class="au-avis-nom">{titre}</span><span class="au-avis-note">{note}<small>/5</small></span></span>
              <span class="au-avis-sous">{sous}</span>
            </a></li>'''.format(**p) for p in avis)
        parties.append('''        <section class="au-groupe">
          <h2 class="au-groupe-t"><span class="tt">Ses avis</span></h2>
          <ul class="au-avis-liste">
{i}
          </ul>
        </section>'''.format(i=items))
    articles = [p for p in liste if p['type'] in ('comparatif', 'guide')]
    if articles:
        items = '\n'.join('''            <li><a class="au-art" href="{url}">
              {img}<span><span class="au-art-k">{k}</span><span class="au-art-t">{titre}</span><span class="au-art-s">{sous}</span></span>
            </a></li>'''.format(url=p['url'], titre=p['titre'], sous=p['sous'],
                                k='Comparatif' if p['type'] == 'comparatif' else 'Guide',
                                img=('<span class="au-art-img"><img src="%s" alt="" width="960" height="480" loading="lazy"></span>' % p['image']) if p['image'] else '')
                          for p in articles)
        parties.append('''        <section class="au-groupe">
          <h2 class="au-groupe-t"><span class="tt">Ses comparatifs et guides</span></h2>
          <ul class="au-art-liste">
{i}
          </ul>
        </section>'''.format(i=items))
    lex = sorted([p for p in liste if p['type'] == 'lexique'], key=lambda p: p['titre'].lower())
    if lex:
        items = '\n'.join('            <li><a href="{url}"><dfn>{titre}</dfn><span>{sous}</span></a></li>'.format(**p) for p in lex)
        parties.append('''        <section class="au-groupe">
          <h2 class="au-groupe-t"><span class="tt">Ses définitions du lexique</span></h2>
          <ul class="au-lex">
{i}
          </ul>
        </section>'''.format(i=items))
    return '\n'.join(parties)


def page_auteur(slug, pubs, gabarit_tete, header, footer, v):
    a = AUTEURS[slug]
    url = '%s/auteurs/%s/' % (SITE, slug)
    tags = ''.join('<li>%s</li>' % t for t in a['tags'])
    bio = '\n'.join('          <p>%s</p>' % p for p in a['bio'])
    autres = '\n'.join('''          <li><a href="/auteurs/{s}/"><span class="qs-photo"><img src="/assets/auteurs/{s}.webp" alt="" width="320" height="320" loading="lazy"></span><span class="qs-nom">{n}</span><span class="qs-role">{r}</span></a></li>'''.format(
        s=s, n=AUTEURS[s]['nom'], r=AUTEURS[s]['role'].split('·')[-1].strip().capitalize()) for s in ORDRE if s != slug)
    ld = [
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Auteurs', 'item': SITE + '/auteurs/'},
            {'@type': 'ListItem', 'position': 3, 'name': a['nom'], 'item': url}]},
        {'@context': 'https://schema.org', '@type': 'ProfilePage', 'mainEntity': {
            '@type': 'Person', '@id': url + '#person', 'name': a['nom'], 'url': url,
            'image': '%s/assets/auteurs/%s.webp' % (SITE, slug), 'jobTitle': a['job'],
            'worksFor': {'@id': SITE + '/#organization'},
            'knowsAbout': ['Sites de rencontre', 'Rencontre en ligne', 'Applications de rencontre'] + a['tags'],
            'description': a['description']},
         'hasPart': [{'@type': 'CreativeWork', 'name': p['titre'], 'url': SITE + p['url']} for p in pubs]},
    ]
    schemas = '\n'.join('  <script type="application/ld+json">\n  %s\n  </script>' % json.dumps(o, ensure_ascii=False, indent=2).replace('\n', '\n  ') for o in ld)
    tete = gabarit_tete.format(title=html.escape(a['title']), description=html.escape(a['meta']), url=url,
                               og_title=html.escape('%s, %s' % (a['nom'], a['job'].lower())), type='profile', v=v, schemas=schemas)
    main = '''  <main id="main" class="av gd au">

    <section class="av-ouverture au-ouverture">
      <span class="av-motif av-motif--plume" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
          <ol>
            <li><a href="/">Accueil</a></li>
            <li><a href="/auteurs/">Auteurs</a></li>
            <li aria-current="page">{nom}</li>
          </ol>
        </nav>
        <div class="au-grille">
          <span class="au-portrait"><img src="/assets/auteurs/{slug}.webp" alt="Portrait de {nom}" width="320" height="320" fetchpriority="high"></span>
          <div>
            <p class="au-job">{job}</p>
            <h1>{nom}</h1>
            <p class="au-role">{role}</p>
            <ul class="au-tags">{tags}</ul>
{bio}
          </div>
        </div>
      </div>
    </section>

    <div class="au-pubs">
      <div class="container">
{publications}
      </div>
    </div>

    <section class="au-autres">
      <div class="container">
        <h2 class="av-h2"><span class="tt">Le reste de la rédaction</span></h2>
        <ul class="qs-grille au-autres-grille">
{autres}
        </ul>
        {btn}
      </div>
    </section>
  </main>'''.format(nom=a['nom'], slug=slug, job=a['job'], role=a['role'].split('·')[-1].strip().capitalize(), tags=tags, bio=bio,
                    publications=bloc_publications(pubs), autres=autres, btn=btn('/qui-sommes-nous/', 'Qui sommes-nous'))
    return tete + '<body>\n' + header + '\n' + main + '\n' + footer + '\n  <script src="/js/main.js?v=%s"></script>\n</body>\n</html>\n' % v


def page_hub(toutes, gabarit_tete, header, footer, v):
    cartes = []
    for s in ORDRE:
        a = AUTEURS[s]
        recentes = sorted(toutes[s], key=lambda p: p['date'], reverse=True)[:3]
        lis = ''.join('<li><a href="%s">%s</a></li>' % (p['url'], p['titre']) for p in recentes)
        cartes.append('''        <li class="au-carte">
          <a class="au-carte-lien" href="/auteurs/{s}/">
            <span class="qs-photo"><img src="/assets/auteurs/{s}.webp" alt="Portrait de {n}" width="320" height="320" loading="lazy"></span>
            <span class="qs-nom">{n}</span>
            <span class="qs-role">{r}</span>
            <span class="qs-bio">{b}</span>
          </a>
          <p class="au-carte-t">Derniers articles</p>
          <ul class="au-carte-pubs">{l}</ul>
        </li>'''.format(s=s, n=a['nom'], r=a['role'].split('·')[-1].strip().capitalize(), b=a['bio'][0], l=lis))
    url = SITE + '/auteurs/'
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': 'Auteurs', 'item': url}]},
          {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'La rédaction', 'url': url,
           'isPartOf': {'@id': SITE + '/#website'},
           'hasPart': [{'@type': 'Person', '@id': '%s/auteurs/%s/#person' % (SITE, s), 'name': AUTEURS[s]['nom'],
                        'url': '%s/auteurs/%s/' % (SITE, s)} for s in ORDRE]}]
    schemas = '\n'.join('  <script type="application/ld+json">\n  %s\n  </script>' % json.dumps(o, ensure_ascii=False, indent=2).replace('\n', '\n  ') for o in ld)
    tete = gabarit_tete.format(title='La rédaction : nos auteurs | MeilleurSiteRencontre.fr',
                               description="Les rédacteurs de MeilleurSiteRencontre.fr : qui ils sont, ce qu'ils regardent quand ils testent une plateforme, et tous leurs articles.",
                               url=url, og_title='La rédaction de MeilleurSiteRencontre.fr', type='website', v=v, schemas=schemas)
    main = '''  <main id="main" class="hb au">

    <section class="hb-ouverture">
      <span class="hb-motif hb-motif--loupe" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
          <ol>
            <li><a href="/">Accueil</a></li>
            <li aria-current="page">Auteurs</li>
          </ol>
        </nav>
        <header class="hb-open hb-open--bloc">
          <h1>La rédaction, <em>visage découvert</em></h1>
          <p>Chaque avis, comparatif, guide et définition est signé par l'un de nos rédacteurs. Voici qui ils sont, ce qu'ils regardent quand ils testent une plateforme, et ce qu'ils ont écrit.</p>
        </header>
      </div>
    </section>

    <section class="au-hub">
      <div class="container">
        <ul class="au-hub-grille">
{c}
        </ul>
      </div>
    </section>
  </main>'''.format(c='\n'.join(cartes))
    return tete + '<body>\n' + header + '\n' + main + '\n' + footer + '\n  <script src="/js/main.js?v=%s"></script>\n</body>\n</html>\n' % v


def generer(appliquer=False):
    ref = lire('qui-sommes-nous/index.html')
    header = re.search(r'(?s)  <a class="skip-link".*?</header>', ref).group(0)
    header = header.replace(' aria-current="page"', '')
    footer = re.search(r'(?s)  <footer class="site-footer">.*?</footer>', ref).group(0)
    v = re.search(r'style\.css\?v=([0-9-]+)', ref).group(1)
    fav = re.search(r'(?s)  <link rel="icon" type="image/svg\+xml".*?apple-touch-icon[^>]*>', ref).group(0)
    tete = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#e6336c">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="https://meilleur-site-rencontre.fr/assets/hero.jpg">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="{type}">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="MeilleurSiteRencontre.fr">
''' + fav.replace('{', '{{').replace('}', '}}') + '''
  <link rel="preload" href="/assets/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/css/style.css?v={v}">
  <link rel="stylesheet" href="/css/avis.css?v={v}">
  <link rel="stylesheet" href="/css/hub.css?v={v}">
  <link rel="stylesheet" href="/css/guide.css?v={v}">
  <link rel="stylesheet" href="/css/lexique.css?v={v}">
{schemas}
</head>
'''
    pubs = publications()
    pages = {RACINE / 'auteurs' / 'index.html': page_hub(pubs, tete, header, footer, v)}
    for s in ORDRE:
        pages[RACINE / 'auteurs' / s / 'index.html'] = page_auteur(s, pubs[s], tete, header, footer, v)
    for p, contenu in pages.items():
        if appliquer:
            p.write_text(contenu, encoding='utf-8')
    return {s: len(pubs[s]) for s in ORDRE}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--appliquer', action='store_true')
    a = ap.parse_args()
    print(generer(a.appliquer))
