#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publie les contenus arrives a echeance.

La file d'attente vit dans _planning/ : les pages y sont completes et pretes,
mais ni liees, ni referencees dans le sitemap, et le .htaccess en interdit
l'acces public. Ce script deplace vers la racine du site ce dont la date est
atteinte, puis met a jour le hub et le sitemap.

  python3 tools/publier.py              -> simulation, n'ecrit rien
  python3 tools/publier.py --appliquer  -> publie pour de bon
  python3 tools/publier.py --date 2026-10-14 --appliquer  -> force une date
"""
import argparse, datetime, json, pathlib, re, shutil, sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
PLANNING = RACINE / '_planning' / 'planning.json'
SITE = 'https://meilleur-site-rencontre.fr'
FLECHE = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
          '<path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.5" '
          'stroke-linecap="round" stroke-linejoin="round"/></svg>')

HUBS = {
    'lexique': {
        'page': RACINE / 'lexique' / 'index.html',
        'lien': 'Lire la définition',
        'priorite': '0.6',
        'frequence': 'monthly',
    },
}


def carte(entree, cfg):
    return ('\n          <a href="/%s/%s/" class="related-card">\n'
            '            <h3>%s</h3>\n'
            '            <p>%s</p>\n'
            '            <span class="related-link">%s\n'
            '              %s\n'
            '            </span>\n'
            '          </a>\n' % (entree['type'], entree['slug'], entree['titre'],
                                  entree['resume'], cfg['lien'], FLECHE))


def ajouter_au_hub(entree, cfg, appliquer):
    page = cfg['page']
    html = page.read_text(encoding='utf-8')
    if '/%s/%s/' % (entree['type'], entree['slug']) in html:
        return 'deja dans le hub'
    repere = '          <!-- fiches:fin -->'
    if repere not in html:
        raise SystemExit('repere manquant dans %s' % page)
    html = html.replace(repere, carte(entree, cfg).rstrip('\n') + '\n' + repere, 1)

    # le DefinedTermSet du hub doit lister la nouvelle fiche
    def maj_schema(m):
        data = json.loads(m.group(1))
        if data.get('@type') == 'DefinedTermSet':
            data.setdefault('hasDefinedTerm', []).append(
                {"@type": "DefinedTerm", "name": entree['titre'],
                 "url": "%s/%s/%s/" % (SITE, entree['type'], entree['slug'])})
            corps = json.dumps(data, ensure_ascii=False, indent=2).replace('\n', '\n  ')
            return '<script type="application/ld+json">\n  %s\n  </script>' % corps
        return m.group(0)

    html = re.sub(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                  maj_schema, html, flags=re.S)
    if appliquer:
        page.write_text(html, encoding='utf-8')
    return 'carte ajoutee au hub'


def ajouter_au_sitemap(entree, cfg, date_iso, appliquer):
    p = RACINE / 'sitemap.xml'
    xml = p.read_text(encoding='utf-8')
    loc = '%s/%s/%s/' % (SITE, entree['type'], entree['slug'])
    if loc in xml:
        return 'deja dans le sitemap'
    bloc = ('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
            '    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>\n'
            % (loc, date_iso, cfg['frequence'], cfg['priorite']))
    xml = xml.replace('</urlset>', bloc + '</urlset>')
    # le hub a change aujourd'hui
    xml = re.sub(r'(<loc>%s/%s/</loc>\s*<lastmod>)[0-9-]+' % (re.escape(SITE), entree['type']),
                 r'\g<1>' + date_iso, xml)
    if appliquer:
        p.write_text(xml, encoding='utf-8')
    return 'url ajoutee au sitemap'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--appliquer', action='store_true', help="ecrire les modifications")
    ap.add_argument('--date', help="forcer la date du jour (AAAA-MM-JJ)")
    args = ap.parse_args()

    aujourdhui = args.date or datetime.date.today().isoformat()
    planning = json.loads(PLANNING.read_text(encoding='utf-8'))

    dues = [e for e in planning
            if e.get('statut') == 'planifie' and e['publier_le'] <= aujourdhui]
    if not dues:
        prochaines = sorted(e['publier_le'] for e in planning if e.get('statut') == 'planifie')
        print('Rien a publier le %s.' % aujourdhui,
              'Prochaine echeance : %s' % prochaines[0] if prochaines else 'File vide.')
        return

    for entree in dues:
        cfg = HUBS[entree['type']]
        source = RACINE / '_planning' / entree['type'] / entree['slug']
        cible = RACINE / entree['type'] / entree['slug']
        if not (source / 'index.html').exists():
            raise SystemExit('page introuvable : %s' % source)
        if cible.exists():
            raise SystemExit('la cible existe deja : %s' % cible)

        print('\n%s  ->  /%s/%s/' % (entree['publier_le'], entree['type'], entree['slug']))
        if args.appliquer:
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(cible))
        print('  page deplacee' + ('' if args.appliquer else ' (simulation)'))
        print('  ' + ajouter_au_hub(entree, cfg, args.appliquer))
        print('  ' + ajouter_au_sitemap(entree, cfg, aujourdhui, args.appliquer))
        entree['statut'] = 'publie'
        entree['publie_le'] = aujourdhui

    if args.appliquer:
        PLANNING.write_text(json.dumps(planning, ensure_ascii=False, indent=2) + '\n',
                            encoding='utf-8')
    print('\n%d contenu(s) %s.' % (len(dues), 'publie(s)' if args.appliquer else 'a publier (simulation)'))
    # liste des URLs, reprise par le workflow pour verifier la mise en ligne
    urls = ' '.join('/%s/%s/' % (e['type'], e['slug']) for e in dues)
    (RACINE / '_planning' / 'derniere-publication.txt').write_text(urls + '\n', encoding='utf-8') if args.appliquer else None


if __name__ == '__main__':
    main()
