#!/usr/bin/env python3
"""Passe une page comparatif sur le gabarit d'octobre 2026.

Reprend tout le contenu existant et le recompose : ouverture sable,
classement en entrees editoriales avec captures, tableau comparatif (vrai
tableau au desktop, fiches empilees sur mobile), sections a fonds alternes,
redacteur, FAQ, liens pour aller plus loin. Aucun texte nouveau hors
intitules.

    python3 tools/refonte_comparatif.py comparatif-seniors            # simulation
    python3 tools/refonte_comparatif.py --tous --appliquer
"""
import argparse
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AVIS = {a['nom']: a for a in json.loads((RACINE / 'tools' / 'donnees' / 'avis.json').read_text(encoding='utf-8'))['avis']}
PAGES = ['comparatif-relation-serieuse', 'comparatif-seniors', 'comparatif-gay']
PHOTOS = {
    '/comparatif-relation-serieuse/': ('/assets/comparatifs/comparatif-relation-serieuse.webp', 960, 480),
    '/comparatif-seniors/': ('/assets/comparatifs/comparatif-seniors.webp', 960, 480),
    '/comparatif-gay/': ('/assets/comparatifs/comparatif-gay.webp', 760, 380),
}
MOTIFS = ['loupe', 'cafe', 'lettre', 'plume', 'avion', 'telephone']

COEUR = ('<svg class="btn-coeur-ico" width="15" height="14" viewBox="0 0 24 22" aria-hidden="true">'
         '<path d="M12 20.3s-8.8-5.3-8.8-11.4A4.9 4.9 0 0 1 12 6.1a4.9 4.9 0 0 1 8.8 2.8c0 6.1-8.8 11.4-8.8 11.4z"/></svg>')
FLECHE = ('<svg class="btn-coeur-fl" width="18" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true">'
          '<path d="M1 5h15M12 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def btn(href, libelle, extra=''):
    return '<a class="btn-coeur%s" href="%s">%s<span>%s</span>%s</a>' % (extra, href, COEUR, libelle, FLECHE)


def un(motif, texte, defaut=None):
    m = re.search(motif, texte, re.S)
    if not m:
        if defaut is not None:
            return defaut
        raise SystemExit('Introuvable : %s' % motif[:80])
    return m.group(1)


def net(t):
    return re.sub(r'\s+', ' ', t).strip()


def texte(t):
    return html.unescape(net(re.sub(r'<[^>]+>', '', t)))


def capture(nom):
    a = AVIS.get(nom)
    if not a:
        return ''
    return ('<a class="cp-capture" href="/avis-{s}/" tabindex="-1" aria-hidden="true">'
            '<img src="{i}" alt="" width="{l}" height="{h}" loading="lazy"></a>').format(
        s=a['slug'], i=a['image'], l=a['image_l'], h=a['image_h'])


def classement(bloc):
    titre = un(r'<h2>(.*?)</h2>', bloc)
    intro = un(r'<header class="section-head">.*?<p>(.*?)</p>', bloc, '')
    note = un(r'<p class="rank-note">(.*?)</p>', bloc, '')
    entrees = []
    for li in re.findall(r'<li class="rank-card[^"]*">(.*?)</li>\s*(?=<li class="rank-card|</ol>)', bloc, re.S):
        pos = un(r'<span class="rank-pos">(\d+)</span>', li)
        label = net(un(r'<span class="rank-pos-label">(.*?)</span>', li))
        nom = net(un(r'<h3>(.*?)</h3>', li))
        tag = net(un(r'<p class="rank-tag">(.*?)</p>', li))
        note_s = un(r'<p class="rank-rating"[^>]*><strong>(.*?)</strong>', li)
        desc = net(un(r'<p class="rank-desc">(.*?)</p>', li))
        pros = re.findall(r'<li>(.*?)</li>', un(r'<ul class="rank-pros">(.*?)</ul>', li))
        avis_href, avis_txt = re.search(r'<a href="(/avis-[^"]+)" class="btn btn-link">(.*?)</a>', li).groups()
        go = un(r'href="(/go/[^"]+)"', li)
        kicker = label if 'n°' in label.lower() else 'N°%s · %s' % (pos, label)
        entrees.append('''        <article class="cp-rang" data-reveal>
          <div class="cp-rang-media">{capture}</div>
          <div class="cp-rang-corps">
            <p class="cp-rang-k">{kicker}</p>
            <header class="cp-rang-tete">
              <h3><a href="{avis}">{nom}</a></h3>
              <p class="cp-rang-note"><span>{note}</span>/5</p>
            </header>
            <p class="cp-rang-tag">{tag}</p>
            <p class="cp-rang-desc">{desc}</p>
            <ul class="av-plus">
{pros}
            </ul>
            <div class="av-actions">
              {lire}
              <a class="btn-site" href="{go}" rel="sponsored nofollow noopener" target="_blank">Voir le site</a>
            </div>
          </div>
        </article>'''.format(capture=capture(nom), kicker=kicker, avis=avis_href, nom=nom, note=note_s, tag=tag,
                             desc=desc, pros='\n'.join('              <li>%s</li>' % net(p) for p in pros),
                             lire=btn(avis_href, net(avis_txt)), go=go))
    return titre, intro, entrees, note


def tableau(bloc):
    titre = un(r'<h2>(.*?)</h2>', bloc)
    intro = un(r'<header class="section-head">.*?<p>(.*?)</p>', bloc, '')
    cartes = re.findall(r'<article class="compare-card">(.*?)</article>', bloc, re.S)
    colonnes = None
    lignes = []
    for c in cartes:
        nom = un(r'<img src="[^"]+" alt="([^"]+)"', c)
        note = un(r'aria-label="Note [^"]+">([0-9,]+)<span>', c)
        paires = re.findall(r'<div><dt>(.*?)</dt><dd>(.*?)</dd></div>', c)
        if colonnes is None:
            colonnes = [p[0] for p in paires]
        href = un(r'<a href="(/avis-[^"]+)" class="compare-card-cta">', c)
        cellules = ''.join('<td data-label="%s">%s</td>' % (html.escape(texte(k)), v) for k, v in paires)
        lignes.append('              <tr><th scope="row"><a href="%s">%s</a><span class="cp-tab-note">%s<small>/5</small></span></th>%s</tr>'
                      % (href, html.escape(nom), note, cellules))
    entetes = ''.join('<th scope="col">%s</th>' % k for k in colonnes)
    return titre, intro, '''          <div class="cp-tab-cadre">
            <table class="cp-tab">
              <thead><tr><th scope="col">Plateforme</th>{e}</tr></thead>
              <tbody>
{l}
              </tbody>
            </table>
          </div>'''.format(e=entetes, l='\n'.join(lignes))


def refait(dossier):
    chemin = RACINE / dossier / 'index.html'
    page = chemin.read_text(encoding='utf-8')
    main = page[page.index('<main'):page.index('</main>') + 7]

    fil = un(r'<li aria-current="page">(.*?)</li>', main)
    h1 = un(r'<h1>(.*?)</h1>', main)
    lede = un(r'<p class="lede">(.*?)</p>', main)
    meta = re.findall(r'<span>(.*?)</span>', un(r'<p class="compare-meta">(.*?)</p>', main))
    aurl, anom = re.search(r'Par <a href="(/auteurs/\w+/)">([^<]+)</a>', main).groups()
    aslug = aurl.strip('/').split('/')[-1]
    maj = un(r'<span>Mise à jour le ([^<]+)</span>', main)
    faits = [m for m in meta if not m.startswith('Par ') and not m.startswith('Mise à jour')]
    fig = re.search(r'<figure class="edito-figure">\s*<img src="([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)"', main)
    toc = re.findall(r'<li><a href="#([a-z-]+)">(.*?)</a></li>', un(r'<ol class="page-toc-list">(.*?)</ol>', main))

    corps = []
    rang_motif = 0
    for m in re.finditer(r'<section( id="([a-z-]+)")? class="(review-section|rank-section|comparatif)">(.*?)</section>', main, re.S):
        ident, classe, bloc = m.group(2), m.group(3), m.group(4)
        if 'author-box' in bloc:
            continue
        motif = MOTIFS[rang_motif % len(MOTIFS)]
        rang_motif += 1
        deco = '<span class="av-motif av-motif--%s" aria-hidden="true"></span>' % motif
        if classe == 'rank-section':
            titre, intro, entrees, note = classement(bloc)
            corps.append('''    <section id="{id}" class="cp-sec cp-sec--classement">
      {deco}
      <div class="container">
        <header class="cp-tete" data-reveal>
          <h2>{t}</h2>
          <p>{i}</p>
        </header>
        <div class="cp-rangs">
{e}
        </div>
        {n}
      </div>
    </section>'''.format(id=ident, deco=deco, t=titre, i=intro, e='\n'.join(entrees),
                         n=('<p class="cp-note">%s</p>' % note) if note else ''))
        elif classe == 'comparatif':
            titre, intro, tab = tableau(bloc)
            corps.append('''    <section id="{id}" class="cp-sec">
      <div class="container">
        <header class="cp-tete" data-reveal>
          <h2>{t}</h2>
          <p>{i}</p>
        </header>
{tab}
      </div>
    </section>'''.format(id=ident, t=titre, i=intro, tab=tab))
        else:
            prose = un(r'<div class="container review-prose">(.*?)</div>\s*$', bloc)
            corps.append('''    <section id="{id}" class="cp-sec">
      {deco}
      <div class="container">
        <div class="av-prose">{p}
        </div>
      </div>
    </section>'''.format(id=ident, deco=deco, p=prose.rstrip()))

    auteur = re.search(r'<p class="author-role">(.*?)</p>\s*<p class="author-bio">(.*?)</p>', main, re.S)
    faq_items = re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*(<p>.*?</p>)\s*</details>', main, re.S)
    titre_faq = un(r'<section id="faq" class="faq">.*?<h2>(.*?)</h2>', main)
    rel_titre = un(r'<section class="related-reviews">.*?<h2>(.*?)</h2>', main)
    rel = re.findall(r'<a href="([^"]+)" class="related-card">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', main, re.S)
    cartes = []
    for href, t, d in rel:
        img = ''
        slug = href.strip('/').replace('avis-', '')
        a = next((x for x in AVIS.values() if x['slug'] == slug), None)
        if a:
            img = '<img src="%s" alt="" width="%d" height="%d" loading="lazy">' % (a['image'], a['image_l'], a['image_h'])
        elif href in PHOTOS:
            img = '<img src="%s" alt="" width="%d" height="%d" loading="lazy">' % PHOTOS[href]
        cartes.append('''          <a class="av-autre" href="{h}">
            <span class="av-autre-img">{img}</span>
            <span class="av-autre-tete"><span class="av-autre-nom">{t}</span></span>
            <span class="av-autre-acc">{d}</span>
          </a>'''.format(h=href, img=img, t=net(t), d=net(d)))

    sommaire = '\n'.join('          <li><a href="#%s">%s</a></li>' % (i, t) for i, t in toc)
    faits_html = ' · '.join(faits)

    nouveau = '''<main id="main" class="av cp">

    <!-- Ouverture -->
    <section class="av-ouverture">
      <span class="av-motif av-motif--loupe" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
          <ol>
            <li><a href="/">Accueil</a></li>
            <li><a href="/comparatifs/">Comparatifs</a></li>
            <li aria-current="page">{fil}</li>
          </ol>
        </nav>
        <div class="av-ouverture-grille">
          <div class="av-ouverture-texte">
            <h1>{h1}</h1>
            <p class="av-lede">{lede}</p>
            <div class="av-signature">
              <img src="/assets/auteurs/{aslug}.webp" alt="" width="44" height="44">
              <p>Par <a href="{aurl}">{anom}</a>, mis à jour le {maj}</p>
            </div>
            <div class="av-actions">
              {btn_top}
            </div>
          </div>
          <figure class="cp-photo">
            <img src="{img}" alt="{alt}" width="{l}" height="{h}" fetchpriority="high">
          </figure>
        </div>
      </div>
    </section>

    <!-- Sommaire -->
    <nav class="cp-sommaire" aria-label="Dans ce comparatif">
      <div class="container">
        <p>Dans ce comparatif</p>
        <ol>
{sommaire}
        </ol>
      </div>
    </nav>

{corps}

    <section class="av-auteur">
      <span class="av-motif av-motif--plume" aria-hidden="true"></span>
      <div class="container av-auteur-grille" data-reveal>
        <span class="av-auteur-img"><img src="/assets/auteurs/{aslug}.webp" alt="Portrait de {anom}" width="320" height="320" loading="lazy"></span>
        <div>
          <p class="av-auteur-k">Comparatif rédigé par</p>
          <p class="av-auteur-nom">{anom}</p>
          <p class="av-auteur-role">{role}</p>
          <p class="av-auteur-bio">{bio}</p>
          {btn_auteur}
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="av-faq">
      <span class="av-motif av-motif--bulles" aria-hidden="true"></span>
      <div class="container av-faq-grille">
        <header data-reveal>
          <h2 class="av-h2">{titre_faq}</h2>
          <p class="av-texte">Une autre question, une erreur à signaler&nbsp;? La rédaction vous lit.</p>
          {btn_contact}
        </header>
        <div class="av-qa" data-reveal>
{faq}
        </div>
      </div>
    </section>

    <!-- Aller plus loin -->
    <section class="av-autres">
      <div class="container">
        <h2 class="av-h2">{rel_titre}</h2>
        <div class="av-autres-grille" data-reveal>
{cartes}
        </div>
        {btn_tous}
      </div>
    </section>
  </main>'''.format(
        fil=fil, h1=h1, lede=net(lede), aslug=aslug, aurl=aurl, anom=anom, maj=maj, faits=faits_html,
        btn_top=btn('#top', 'Voir le classement'), img=fig.group(1), alt=fig.group(2), l=fig.group(3), h=fig.group(4),
        sommaire=sommaire, corps='\n\n'.join(corps), role=net(auteur.group(1)), bio=net(auteur.group(2)),
        btn_auteur=btn(aurl, 'Tous les articles de %s' % anom),
        titre_faq=titre_faq, btn_contact=btn('/contact/', 'Contacter la rédaction'),
        faq='\n'.join('''          <details>
            <summary>{q}</summary>
            {a}
          </details>'''.format(q=q, a=net(a)) for q, a in faq_items),
        rel_titre=rel_titre, cartes='\n'.join(cartes), btn_tous=btn('/comparatifs/', 'Tous nos comparatifs'))

    sortie = page.replace(main, nouveau)
    if 'css/comparatif.css' not in sortie:
        v = re.search(r'style\.css\?v=([0-9-]+)', sortie).group(1)
        sortie = sortie.replace('<link rel="stylesheet" href="/css/style.css?v=%s">' % v,
                                '<link rel="preload" href="/assets/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin>\n'
                                '  <link rel="stylesheet" href="/css/style.css?v=%s">\n'
                                '  <link rel="stylesheet" href="/css/avis.css?v=%s">\n'
                                '  <link rel="stylesheet" href="/css/comparatif.css?v=%s">' % (v, v, v))
    return chemin, page, sortie


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dossiers', nargs='*')
    parser.add_argument('--tous', action='store_true')
    parser.add_argument('--appliquer', action='store_true')
    args = parser.parse_args()
    for d in (PAGES if args.tous else args.dossiers):
        if 'class="av cp"' in (RACINE / d / 'index.html').read_text(encoding='utf-8'):
            print('%s : deja au nouveau gabarit, ignore' % d)
            continue
        chemin, avant, apres = refait(d)
        print('%s : %d -> %d caracteres' % (d, len(avant), len(apres)))
        if args.appliquer:
            chemin.write_text(apres, encoding='utf-8')


if __name__ == '__main__':
    main()
