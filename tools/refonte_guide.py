#!/usr/bin/env python3
"""Passe un guide sur le gabarit d'octobre 2026.

Reprend tout le contenu existant et le recompose comme un article :
ouverture sable avec photo en arche, corps a fonds alternes avec colonne
collante (redacteur et sommaire qui suit la lecture), exemples mis en
valeur, redacteur, FAQ, lectures liees en vignettes. Aucun texte nouveau
hors intitules.

    python3 tools/refonte_guide.py guide/faux-profils            # simulation
    python3 tools/refonte_guide.py --tous --appliquer
"""
import argparse
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AVIS = json.loads((RACINE / 'tools' / 'donnees' / 'avis.json').read_text(encoding='utf-8'))['avis']
PAGES = ['guide/profil-attractif', 'guide/premier-message', 'guide/faux-profils', 'guide/site-fiable']
IMAGES = {
    '/comparatif-relation-serieuse/': ('/assets/comparatifs/comparatif-relation-serieuse.webp', 960, 480),
    '/comparatif-seniors/': ('/assets/comparatifs/comparatif-seniors.webp', 960, 480),
    '/comparatif-gay/': ('/assets/comparatifs/comparatif-gay.webp', 760, 380),
}
for g in ['profil-attractif', 'premier-message', 'faux-profils', 'site-fiable']:
    IMAGES['/guide/%s/' % g] = ('/assets/guides/guide-%s.webp' % g, 960, 480)
for a in AVIS:
    IMAGES['/avis-%s/' % a['slug']] = (a['image'], a['image_l'], a['image_h'])
MOTIFS = ['telephone', 'cafe', 'loupe', 'lettre', 'avion', 'plume']

COEUR = ('<svg class="btn-coeur-ico" width="15" height="14" viewBox="0 0 24 22" aria-hidden="true">'
         '<path d="M12 20.3s-8.8-5.3-8.8-11.4A4.9 4.9 0 0 1 12 6.1a4.9 4.9 0 0 1 8.8 2.8c0 6.1-8.8 11.4-8.8 11.4z"/></svg>')
FLECHE = ('<svg class="btn-coeur-fl" width="18" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true">'
          '<path d="M1 5h15M12 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def btn(href, libelle):
    return '<a class="btn-coeur" href="%s">%s<span>%s</span>%s</a>' % (href, COEUR, libelle, FLECHE)


def un(motif, texte, defaut=None):
    m = re.search(motif, texte, re.S)
    if not m:
        if defaut is not None:
            return defaut
        raise SystemExit('Introuvable : %s' % motif[:80])
    return m.group(1)


def net(t):
    return re.sub(r'\s+', ' ', t).strip()


def exemples(prose):
    """Exemples de messages ou de bios : bon / mauvais, en citations marquees."""
    def cite(m):
        sorte = 'bon' if m.group(1) == 'good' else 'mauvais'
        libelle = 'Bon exemple' if sorte == 'bon' else 'À éviter'
        return ('<figure class="gd-ex gd-ex--%s">\n          <figcaption>%s</figcaption>\n          <blockquote>%s</blockquote>\n        </figure>'
                % (sorte, libelle, m.group(2).strip()))
    return re.sub(r'<blockquote class="example-quote example-quote--(good|bad)">(.*?)</blockquote>', cite, prose, flags=re.S)


def refait(dossier):
    chemin = RACINE / dossier / 'index.html'
    page = chemin.read_text(encoding='utf-8')
    main = page[page.index('<main'):page.index('</main>') + 7]

    fil = un(r'<li aria-current="page">(.*?)</li>', main)
    h1 = un(r'<h1>(.*?)</h1>', main)
    lede = net(un(r'<p class="lede">(.*?)</p>', main))
    aurl, anom = re.search(r'Par <a href="(/auteurs/\w+/)">([^<]+)</a>', main).groups()
    aslug = aurl.strip('/').split('/')[-1]
    maj = un(r'<span>Mise à jour le ([^<]+)</span>', main)
    fig = re.search(r'<figure class="edito-figure">\s*<img src="([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)"', main)
    toc = [(i, t) for i, t in re.findall(r'<li><a href="#([a-z-]+)">(.*?)</a></li>', un(r'<ol class="page-toc-list">(.*?)</ol>', main))]

    sections, encart = [], ''
    rang = 0
    for m in re.finditer(r'<section( id="([a-z-]+)")? class="review-section">\s*<div class="container review-prose">(.*?)</div>\s*</section>', main, re.S):
        ident, prose = m.group(2), m.group(3)
        if 'author-box' in prose:
            continue
        if not ident:
            # encart de fin (renvoi vers le lexique) : rattache a la derniere section
            encart = prose.strip()
            continue
        motif = MOTIFS[rang % len(MOTIFS)]
        rang += 1
        sections.append([ident, motif, exemples(prose).rstrip()])
    if encart and sections:
        sections[-1][2] += '\n        ' + encart
    corps = '\n\n'.join('''      <section id="{i}" class="av-sec">
        <span class="av-motif av-motif--{m}" aria-hidden="true"></span>
        <div class="av-prose">{p}
        </div>
      </section>'''.format(i=i, m=mo, p=p) for i, mo, p in sections)

    auteur = re.search(r'<p class="author-role">(.*?)</p>\s*<p class="author-bio">(.*?)</p>', main, re.S)
    faq_items = re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*(<p>.*?</p>)\s*</details>', main, re.S)
    titre_faq = un(r'<section id="faq" class="faq">.*?<h2>(.*?)</h2>', main)
    rel_titre = un(r'<section class="related-reviews">.*?<h2>(.*?)</h2>', main)
    cartes = []
    for href, t, d in re.findall(r'<a href="([^"]+)" class="related-card">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', main, re.S):
        img = IMAGES.get(href)
        visuel = ('<span class="av-autre-img"><img src="%s" alt="" width="%d" height="%d" loading="lazy"></span>' % img) if img else ''
        cartes.append('''          <a class="av-autre{c}" href="{h}">
            {v}<span class="av-autre-tete"><span class="av-autre-nom">{t}</span></span>
            <span class="av-autre-acc">{d}</span>
          </a>'''.format(c='' if img else ' av-autre--texte', h=href, v=visuel, t=net(t), d=net(d)))

    nouveau = '''<main id="main" class="av gd">

    <!-- Ouverture -->
    <section class="av-ouverture">
      <span class="av-motif av-motif--loupe" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
          <ol>
            <li><a href="/">Accueil</a></li>
            <li><a href="/guides/">Guides</a></li>
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
          </div>
          <figure class="gd-photo">
            <img src="{img}" alt="{alt}" width="{l}" height="{h}" fetchpriority="high">
          </figure>
        </div>
      </div>
    </section>

    <!-- Corps du guide, avec colonne collante -->
    <div class="av-corps">
      <aside class="av-cote" aria-label="Dans ce guide">
        <div class="av-cote-carte gd-cote">
          <p class="gd-cote-auteur"><img src="/assets/auteurs/{aslug}.webp" alt="" width="40" height="40"><span><a href="{aurl}">{anom}</a><small>mis à jour le {maj}</small></span></p>
          <p class="av-cote-t">Dans ce guide</p>
          <ol class="av-sommaire" data-sommaire>
{sommaire}
          </ol>
        </div>
      </aside>
      <article class="av-article">
{corps}
      </article>
    </div>

    <section class="av-auteur">
      <span class="av-motif av-motif--plume" aria-hidden="true"></span>
      <div class="container av-auteur-grille" data-reveal>
        <span class="av-auteur-img"><img src="/assets/auteurs/{aslug}.webp" alt="Portrait de {anom}" width="320" height="320" loading="lazy"></span>
        <div>
          <p class="av-auteur-k">Guide rédigé par</p>
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

    <!-- Lire aussi -->
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
        fil=fil, h1=h1, lede=lede, aslug=aslug, aurl=aurl, anom=anom, maj=maj,
        img=fig.group(1), alt=fig.group(2), l=fig.group(3), h=fig.group(4),
        sommaire='\n'.join('            <li><a href="#%s">%s</a></li>' % (i, t) for i, t in toc),
        corps=corps, role=net(auteur.group(1)), bio=net(auteur.group(2)),
        btn_auteur=btn(aurl, 'Tous les articles de %s' % anom),
        titre_faq=titre_faq, btn_contact=btn('/contact/', 'Contacter la rédaction'),
        faq='\n'.join('''          <details>
            <summary>{q}</summary>
            {a}
          </details>'''.format(q=q, a=net(a)) for q, a in faq_items),
        rel_titre=rel_titre, cartes='\n'.join(cartes), btn_tous=btn('/guides/', 'Tous nos guides'))

    sortie = page.replace(main, nouveau)
    if 'css/guide.css' not in sortie:
        v = re.search(r'style\.css\?v=([0-9-]+)', sortie).group(1)
        sortie = sortie.replace('<link rel="stylesheet" href="/css/style.css?v=%s">' % v,
                                '<link rel="preload" href="/assets/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin>\n'
                                '  <link rel="stylesheet" href="/css/style.css?v=%s">\n'
                                '  <link rel="stylesheet" href="/css/avis.css?v=%s">\n'
                                '  <link rel="stylesheet" href="/css/guide.css?v=%s">' % (v, v, v))
    return chemin, page, sortie


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dossiers', nargs='*')
    parser.add_argument('--tous', action='store_true')
    parser.add_argument('--appliquer', action='store_true')
    args = parser.parse_args()
    for d in (PAGES if args.tous else args.dossiers):
        if 'class="av gd"' in (RACINE / d / 'index.html').read_text(encoding='utf-8'):
            print('%s : deja au nouveau gabarit, ignore' % d)
            continue
        chemin, avant, apres = refait(d)
        print('%s : %d -> %d caracteres' % (d, len(avant), len(apres)))
        if args.appliquer:
            chemin.write_text(apres, encoding='utf-8')


if __name__ == '__main__':
    main()
