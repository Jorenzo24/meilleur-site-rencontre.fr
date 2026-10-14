#!/usr/bin/env python3
"""Passe une page avis sur le gabarit d'octobre 2026.

Reprend tout le contenu de l'avis existant (textes, listes, FAQ, signature)
et le recompose dans la nouvelle mise en page : ouverture sable, bloc
"L'essentiel", corps a fonds alternes avec sommaire collant, redacteur,
FAQ, autres avis. Aucun texte n'est ecrit ici, sauf les intitules de
sections et la note sur les tarifs.

    python3 tools/refonte_avis.py avis-meetic            # simulation
    python3 tools/refonte_avis.py avis-meetic --appliquer
    python3 tools/refonte_avis.py --tous --appliquer
"""
import argparse
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DONNEES = json.loads((RACINE / 'tools' / 'donnees' / 'avis.json').read_text(encoding='utf-8'))

COEUR = ('<svg class="btn-coeur-ico" width="15" height="14" viewBox="0 0 24 22" aria-hidden="true">'
         '<path d="M12 20.3s-8.8-5.3-8.8-11.4A4.9 4.9 0 0 1 12 6.1a4.9 4.9 0 0 1 8.8 2.8c0 6.1-8.8 11.4-8.8 11.4z"/></svg>')
FLECHE = ('<svg class="btn-coeur-fl" width="18" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true">'
          '<path d="M1 5h15M12 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

# Un motif au trait par grande section, dans l'ordre de la page
MOTIFS = {'presentation': 'telephone', 'public': 'cafe', 'fonctionnement': 'loupe',
          'tarifs': 'lettre', 'fiabilite': 'plume', 'verdict': 'avion'}

NOTE_TARIFS = ("Les montants ne sont pas affichés publiquement et varient selon les promotions en cours&nbsp;: "
               "le tarif exact apparaît dans votre espace abonnement avant tout paiement.")
NOTE_TARIFS_APP = ("Les montants varient selon les promotions en cours&nbsp;: le tarif exact apparaît dans "
                   "l'application, via l'App Store ou Google Play, avant toute souscription.")


def btn_coeur(href, libelle, extra=''):
    return '<a class="btn-coeur%s" href="%s">%s<span>%s</span>%s</a>' % (extra, href, COEUR, libelle, FLECHE)


def un(motif, texte, defaut=None, flags=re.S):
    m = re.search(motif, texte, flags)
    if not m:
        if defaut is not None:
            return defaut
        raise SystemExit('Introuvable : %s' % motif[:70])
    return m.group(1)


def nettoie(texte):
    return re.sub(r'\s+', ' ', texte).strip()


def items(bloc):
    return [nettoie(x) for x in re.findall(r'<li>(.*?)</li>', bloc, re.S)]


def transforme_prose(prose, slug):
    """Recompose les composants a l'interieur d'une section de l'avis."""
    # Fiche d'identite : definition list sans filets
    def fiche(m):
        paires = re.findall(r'<span class="id-item-label">(.*?)</span><span class="id-item-value">(.*?)</span>', m.group(0))
        titre = un(r'<p class="id-card-head">(.*?)</p>', m.group(0))
        lignes = '\n'.join('            <div><dt>%s</dt><dd>%s</dd></div>' % p for p in paires)
        return ('<div class="av-fiche">\n          <p class="av-fiche-t">%s</p>\n          <dl>\n%s\n          </dl>\n        </div>'
                % (titre, lignes))
    prose = re.sub(r'<div class="id-card">.*?</div>\s*</div>\s*</div>\s*</div>', fiche, prose, flags=re.S)

    # Pour vous / pas pour vous
    def fit(m):
        bloc = m.group(0)
        oui = re.search(r'fit-col--yes">\s*<h4>.*?</svg>\s*(.*?)\s*</h4>\s*<ul>(.*?)</ul>', bloc, re.S)
        non = re.search(r'fit-col--no">\s*<h4>.*?</svg>\s*(.*?)\s*</h4>\s*<ul>(.*?)</ul>', bloc, re.S)
        def col(c, classe):
            lis = '\n'.join('              <li>%s</li>' % x for x in items(c.group(2)))
            return ('          <div class="av-fit-col %s">\n            <h4>%s</h4>\n            <ul>\n%s\n            </ul>\n          </div>'
                    % (classe, nettoie(c.group(1)), lis))
        return '<div class="av-fit">\n%s\n%s\n        </div>' % (col(oui, 'av-fit-oui'), col(non, 'av-fit-non'))
    prose = re.sub(r'<div class="fit-grid">.*?</ul>\s*</div>\s*<div class="fit-col fit-col--no">.*?</ul>\s*</div>\s*</div>', fit, prose, flags=re.S)

    # Le parti pris de la redaction : citation en marge
    def parti(m):
        tag = nettoie(re.sub(r'<svg.*?</svg>', '', m.group(1), flags=re.S))
        return ('<aside class="av-parti">\n          <p class="av-parti-t">%s</p>\n          <blockquote>%s</blockquote>\n        </aside>'
                % (tag, m.group(2).strip()))
    prose = re.sub(r'<div class="edito-note">\s*<span class="edito-note-tag">(.*?)</span>\s*(<p>.*?</p>)\s*</div>', parti, prose, flags=re.S)

    # Encadre d'acces de fin : remplace par le bloc de conclusion (ajoute plus bas)
    prose = re.sub(r'\s*<aside class="cta-box">.*?</aside>', '', prose, flags=re.S)

    # Tarifs : plus de "verifies en avril" sans montant
    note = NOTE_TARIFS_APP if slug == 'spiice' else NOTE_TARIFS
    prose = re.sub(r'<p class="review-note">.*?</p>', '<p class="av-note">%s</p>' % note, prose, flags=re.S)
    prose = prose.replace(', qui descend typiquement sous les 20 euros par mois', '')
    prose = prose.replace('Le tarif mensuel le plus avantageux, qui descend typiquement sous les 20 euros par mois.', 'Le tarif mensuel le plus avantageux des trois.')
    prose = prose.replace('<span class="price-badge">Notre reco</span>', '<span class="price-badge">Notre conseil</span>')
    return prose


def autres_avis(slug):
    liste = DONNEES['avis']
    i = next(k for k, a in enumerate(liste) if a['slug'] == slug)
    voisins = [a for a in liste if a['slug'] != slug]
    # les trois suivants dans le classement, en bouclant
    ordre = liste[i + 1:] + liste[:i]
    choix = ordre[:3]
    cartes = []
    for a in choix:
        cartes.append('''          <a class="av-autre" href="/avis-{slug}/">
            <span class="av-autre-img"><img src="{image}" alt="" width="{il}" height="{ih}" loading="lazy"></span>
            <span class="av-autre-tete"><span class="av-autre-nom">{nom}</span><span class="av-autre-note">{note}<small>/5</small></span></span>
            <span class="av-autre-acc">{accroche}</span>
          </a>'''.format(slug=a['slug'], image=a['image'], il=a['image_l'], ih=a['image_h'],
                         nom=html.escape(a['nom']), note=a['note'], accroche=html.escape(a['accroche'])))
    return '\n'.join(cartes)


def refait(dossier):
    chemin = RACINE / dossier / 'index.html'
    page = chemin.read_text(encoding='utf-8')
    slug = dossier.replace('avis-', '')
    data = next(a for a in DONNEES['avis'] if a['slug'] == slug)
    main = page[page.index('<main'):page.index('</main>') + 7]

    h1 = un(r'<h1>(.*?)</h1>', main)
    lede = un(r'<p class="lede">(.*?)</p>', main)
    note = un(r'class="verdict-rating-num">(.*?)</span>', main)
    auteur_url, auteur_nom = re.search(r'Par <a href="(/auteurs/\w+/)">([^<]+)</a>', main).groups()
    auteur_slug = auteur_url.strip('/').split('/')[-1]
    maj = un(r'<span>Mise à jour le ([^<]+)</span>', main)
    img = re.search(r'<div class="review-hero-image">\s*<img src="([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)"', main)
    resume = un(r'<p class="verdict-summary">(.*?)</p>', main)
    pros = items(un(r'<div class="pros">.*?<ul>(.*?)</ul>', main))
    cons = items(un(r'<div class="cons">.*?<ul>(.*?)</ul>', main))
    go = un(r'href="(/go/[^"]+)"', main)
    acces = nettoie(un(r'<span class="verdict-cta-note">(.*?)</span>', main))
    criteres = re.findall(r'<span class="score-crit">(.*?)</span><span class="score-label">(.*?)</span>\s*</div>\s*<div class="score-track"><div class="score-fill" style="width:(\d+)%">', main)
    toc = re.findall(r'<li><a href="#([a-z-]+)">(.*?)</a></li>', un(r'<ol class="page-toc-list">(.*?)</ol>', main))

    sections = []
    for ident, titre in toc:
        if ident == 'faq':
            continue
        bloc = un(r'<section id="%s" class="review-section">\s*<div class="container review-prose">(.*?)</div>\s*</section>' % ident, main)
        bloc = transforme_prose(bloc, slug)
        motif = MOTIFS.get(ident)
        conclusion = ''
        if ident == 'verdict':
            conclusion = '''
        <div class="av-conclure">
          <p class="av-conclure-acc"><span>Accès</span>{acces}</p>
          <div class="av-actions">
            <a class="btn-site" href="{go}" rel="sponsored nofollow noopener" target="_blank">Voir le site {nom}</a>
            {comparatifs}
          </div>
        </div>'''.format(acces=acces, go=go, nom=html.escape(data['nom']),
                         comparatifs=btn_coeur('/avis/', 'Comparer avec nos autres avis'))
        sections.append('''      <section id="{id}" class="av-sec">
        {motif}<div class="av-prose">{bloc}{conclusion}
        </div>
      </section>'''.format(id=ident, bloc=bloc.rstrip(), conclusion=conclusion,
                           motif=('<span class="av-motif av-motif--%s" aria-hidden="true"></span>\n        ' % motif) if motif else ''))

    sommaire = '\n'.join('            <li><a href="#%s">%s</a></li>' % (i, t) for i, t in toc)

    barres = '\n'.join('''            <li style="--w:{w}%"><span class="av-crit">{c}</span><span class="av-crit-n">{l}</span><span class="av-crit-bar" aria-hidden="true"></span></li>'''
                       .format(w=w, c=c, l=l) for c, l, w in criteres)

    faq_items = re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*(<p>.*?</p>)\s*</details>', main, re.S)
    faq_items = [(q, a.replace('qui descendent typiquement sous les 20 euros mensuels en engagement long', 'au tarif mensuel plus avantageux'))
                 for q, a in faq_items]
    faq = '\n'.join('''            <details>
              <summary>{q}</summary>
              {a}
            </details>'''.format(q=q, a=nettoie(a)) for q, a in faq_items)
    titre_faq = un(r'<section id="faq" class="faq">.*?<h2>(.*?)</h2>', main)

    auteur = re.search(r'<p class="author-role">(.*?)</p>\s*<p class="author-bio">(.*?)</p>', main, re.S)
    fiche_auteur = '''      <section class="av-auteur">
        <span class="av-motif av-motif--plume" aria-hidden="true"></span>
        <div class="container av-auteur-grille" data-reveal>
          <span class="av-auteur-img"><img src="/assets/auteurs/{a}.webp" alt="Portrait de {n}" width="320" height="320" loading="lazy"></span>
          <div>
            <p class="av-auteur-k">Testé et rédigé par</p>
            <p class="av-auteur-nom">{n}</p>
            <p class="av-auteur-role">{role}</p>
            <p class="av-auteur-bio">{bio}</p>
            {lien}
          </div>
        </div>
      </section>'''.format(a=auteur_slug, n=auteur_nom, role=nettoie(auteur.group(1)), bio=nettoie(auteur.group(2)),
                           lien=btn_coeur(auteur_url, 'Tous les avis de %s' % auteur_nom))

    nouveau = '''<main id="main" class="av">

    <!-- Ouverture -->
    <section class="av-ouverture">
      <span class="av-motif av-motif--loupe" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
          <ol>
            <li><a href="/">Accueil</a></li>
            <li><a href="/avis/">Avis</a></li>
            <li aria-current="page">{nom}</li>
          </ol>
        </nav>
        <div class="av-ouverture-grille">
          <div class="av-ouverture-texte">
            <h1>{h1}</h1>
            <p class="av-lede">{lede}</p>
            <div class="av-signature">
              <img src="/assets/auteurs/{aslug}.webp" alt="" width="44" height="44">
              <p>Par <a href="{aurl}">{anom}</a>, mis à jour le {maj}<br><a href="/notre-methode/">Test mené sur quatre semaines</a></p>
            </div>
            <div class="av-ouverture-note">
              <p class="av-note-grande"><span>{note}</span>/5</p>
              <div class="av-actions">
                <a class="btn-site" href="{go}" rel="sponsored nofollow noopener" target="_blank">Voir le site</a>
                {btn_verdict}
              </div>
            </div>
            <p class="av-acces">{acces}</p>
          </div>
          <figure class="av-capture">
            <span class="av-capture-barre"><span>Capture d'écran</span><span>{nom}</span></span>
            <img src="{img}" alt="{img_alt}" width="{img_l}" height="{img_h}" fetchpriority="high">
          </figure>
        </div>
      </div>
    </section>

    <!-- L'essentiel -->
    <section class="av-essentiel" aria-labelledby="essentiel">
      <div class="container">
        <h2 id="essentiel" class="av-h2">L'essentiel</h2>
        <div class="av-essentiel-grille">
          <blockquote class="av-resume" data-reveal>
            <p>{resume}</p>
            <footer><img src="/assets/auteurs/{aslug}.webp" alt="" width="36" height="36" loading="lazy"><span><a href="{aurl}">{anom}</a>, après quatre semaines de test</span></footer>
          </blockquote>
          <div class="av-plusmoins" data-reveal>
            <div>
              <h3>Points forts</h3>
              <ul class="av-plus">
{pros}
              </ul>
            </div>
            <div>
              <h3>Points faibles</h3>
              <ul class="av-moins">
{cons}
              </ul>
            </div>
          </div>
        </div>
        <figure class="av-ressorti" data-reveal>
          <figcaption>Ce qui ressort de notre test</figcaption>
          <ul>
{barres}
          </ul>
          <p class="av-ressorti-note">Appréciations de la rédaction. La note sur 5 suit <a href="/notre-methode/">notre grille de notation</a>, commune à tous les sites.</p>
        </figure>
      </div>
    </section>

    <!-- Corps de l'avis, avec sommaire collant -->
    <div class="av-corps">
      <aside class="av-cote" aria-label="Dans cet avis">
        <div class="av-cote-carte">
          <p class="av-cote-nom">{nom} <span>{note}<small>/5</small></span></p>
          <p class="av-cote-acc">{acces}</p>
          <a class="btn-site" href="{go}" rel="sponsored nofollow noopener" target="_blank">Voir le site</a>
          <p class="av-cote-t">Dans cet avis</p>
          <ol class="av-sommaire" data-sommaire>
{sommaire}
          </ol>
        </div>
      </aside>
      <article class="av-article">
{sections}
      </article>
    </div>

{fiche_auteur}

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

    <!-- Autres avis -->
    <section class="av-autres">
      <div class="container">
        <h2 class="av-h2">Nos autres avis</h2>
        <div class="av-autres-grille" data-reveal>
{autres}
        </div>
        {btn_tous}
      </div>
    </section>
  </main>'''.format(
        nom=html.escape(data['nom']), h1=h1, lede=lede, aslug=auteur_slug, aurl=auteur_url, anom=auteur_nom,
        maj=maj, note=note, go=go, acces=acces,
        btn_verdict=btn_coeur('#verdict', 'Lire notre verdict'),
        img=img.group(1), img_alt=img.group(2), img_l=data['image_l'], img_h=data['image_h'],
        resume=nettoie(resume),
        pros='\n'.join('                <li>%s</li>' % x for x in pros),
        cons='\n'.join('                <li>%s</li>' % x for x in cons),
        barres=barres, sommaire=sommaire, sections='\n\n'.join(sections), fiche_auteur=fiche_auteur,
        titre_faq=titre_faq, btn_contact=btn_coeur('/contact/', 'Contacter la rédaction'), faq=faq,
        autres=autres_avis(slug), btn_tous=btn_coeur('/avis/', 'Voir tous nos avis'))

    sortie = page.replace(main, nouveau)

    # En-tete : feuille de style dediee et police des titres prechargee
    if 'css/avis.css' not in sortie:
        v = re.search(r'style\.css\?v=([0-9-]+)', sortie).group(1)
        sortie = sortie.replace('<link rel="stylesheet" href="/css/style.css?v=%s">' % v,
                                '<link rel="preload" href="/assets/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin>\n'
                                '  <link rel="stylesheet" href="/css/style.css?v=%s">\n'
                                '  <link rel="stylesheet" href="/css/avis.css?v=%s">' % (v, v))

    # Donnees structurees : plus de nombre d'avis invente, on garde l'avis de la redaction
    def sans_agregat(m):
        d = json.loads(m.group(1))
        if d.get('@type') == 'Product' and 'aggregateRating' in d:
            del d['aggregateRating']
            return '<script type="application/ld+json">\n  %s\n  </script>' % json.dumps(d, ensure_ascii=False, indent=2).replace('\n', '\n  ')
        return m.group(0)
    sortie = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', sans_agregat, sortie, flags=re.S)

    # FAQ structuree regeneree depuis la FAQ visible, pour qu'elles disent la meme chose
    def texte(s):
        return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': texte(q), 'acceptedAnswer': {'@type': 'Answer', 'text': texte(a)}}
        for q, a in faq_items]}
    def remplace_faq(m):
        if json.loads(m.group(1)).get('@type') == 'FAQPage':
            return '<script type="application/ld+json">\n  %s\n  </script>' % json.dumps(faq_ld, ensure_ascii=False, indent=2).replace('\n', '\n  ')
        return m.group(0)
    sortie = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', remplace_faq, sortie, flags=re.S)
    return chemin, page, sortie


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dossiers', nargs='*')
    parser.add_argument('--tous', action='store_true')
    parser.add_argument('--appliquer', action='store_true')
    args = parser.parse_args()
    dossiers = ['avis-' + a['slug'] for a in DONNEES['avis']] if args.tous else args.dossiers
    for d in dossiers:
        if 'class="av"' in (RACINE / d / 'index.html').read_text(encoding='utf-8'):
            print('%s : deja au nouveau gabarit, ignore' % d)
            continue
        chemin, avant, apres = refait(d)
        print('%s : %d -> %d caracteres' % (d, len(avant), len(apres)))
        if args.appliquer:
            chemin.write_text(apres, encoding='utf-8')


if __name__ == '__main__':
    main()
