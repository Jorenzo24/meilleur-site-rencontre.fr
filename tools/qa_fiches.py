#!/usr/bin/env python3
"""Controle qualite des sources de fiches du lexique, avant mise en file.

Verifie, pour chaque JSON : champs obligatoires, longueurs (mots, title,
description), tirets cadratins, tics d'ecriture interdits, chiffres a
verifier, liens internes hors liste autorisee, liens vers des fiches pas
encore en ligne.

    python3 tools/qa_fiches.py chemin/vers/*.json
"""
import html
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CHAMPS = ['slug', 'mot', 'genre', 'resume', 'definition_courte', 'title', 'description', 'h1',
          'lede', 'definition', 'sections', 'parti_pris', 'lies', 'lire_aussi', 'auteur', 'publie_le']
LIENS_OK = {'/guide/premier-message/', '/guide/premier-rendez-vous/', '/guide/profil-attractif/', '/guide/faux-profils/', '/guide/site-fiable/',
            '/comparatif-relation-serieuse/', '/comparatif-seniors/', '/comparatif-gay/', '/avis/',
            '/avis-meetic/', '/avis-edarling/', '/avis-infinite-rencontre/', '/avis-spiice/', '/lexique/'}
TICS = [r"ce n'est pas [^.]{1,60}, c'est", r"il ne s'agit pas", r"n'est pas (?:un|une|le|la) [^.]{1,40}, mais",
        r'il est important de', r'en somme', r'en définitive', r'dans un monde où', r"à l'ère du",
        r'plongeons', r'\bnaviguer\b', r'\bcrucial', r'\bvéritable\b', r'lors de nos tests', r'notre panel',
        r'nous avons (?:testé|observé|constaté)', r'selon une étude', r'\bétude\b', r'\bsondage\b', r'\btu\b']


def texte(s):
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))


def corps(d):
    parties = [d['lede'], d['definition'], d.get('parti_pris', '')]
    parties += [s['html'] for s in d['sections']]
    c = d.get('conversation')
    if c:
        parties += [m['texte'] for m in c['messages']] + [c.get('commentaire', '')]
    return ' '.join(parties)


def controle(p):
    alertes = []
    try:
        d = json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception as e:
        return ['JSON INVALIDE : %s' % e], 0
    for c in CHAMPS:
        if c not in d or d[c] in (None, ''):
            if c != 'parti_pris':
                alertes.append('champ manquant : %s' % c)
    tout = corps(d)
    mots = len(texte(tout).split())
    if not 650 <= mots <= 1050:
        alertes.append('longueur : %d mots' % mots)
    if not 40 <= len(d.get('title', '')) <= 70:
        alertes.append('title %d car.' % len(d.get('title', '')))
    if not 115 <= len(d.get('description', '')) <= 165:
        alertes.append('description %d car.' % len(d.get('description', '')))
    if '<em>' not in d.get('h1', ''):
        alertes.append('h1 sans <em>')
    brut = json.dumps(d, ensure_ascii=False)
    if '—' in brut or '–' in brut:
        alertes.append('tiret cadratin ou demi-cadratin')
    plat = texte(tout + ' ' + d.get('title', '') + ' ' + d.get('description', ''))
    # le tutoiement est permis dans les messages cites et les conversations
    narratif = re.sub(r'«[^»]*»', ' ', texte(' '.join([d['lede'], d['definition'], d.get('parti_pris', '')] + [s['html'] for s in d['sections']])))
    for t in TICS:
        if t == r'\btu\b':
            for m in re.finditer(t, narratif, re.I):
                alertes.append('tutoiement hors citation : …%s…' % narratif[max(0, m.start() - 40):m.end() + 30].strip())
            continue
        for m in re.finditer(t, plat, re.I):
            alertes.append('tic « %s » : …%s…' % (t, plat[max(0, m.start() - 40):m.end() + 30].strip()))
    for m in re.finditer(r'\d[\d\s,.]*\s?(?:%|ans|heures|jours|semaines|mois|fois|\b)', plat):
        extrait = plat[max(0, m.start() - 30):m.end() + 20].replace('\n', ' ')
        if not re.search(r'3919|\b(?:19|20)\d\d\b|\b5 (?:langages|love)', extrait):
            alertes.append('chiffre à vérifier : …%s…' % extrait.strip())
    for href in re.findall(r'href="([^"]+)"', tout):
        if href.startswith('/lexique/') and href != '/lexique/':
            slug = href.strip('/').split('/')[-1]
            if not (RACINE / 'lexique' / slug / 'index.html').exists():
                alertes.append('lien vers une fiche pas en ligne : %s' % href)
        elif href not in LIENS_OK:
            alertes.append('lien hors liste : %s' % href)
    for u in d.get('lire_aussi', []):
        if u not in LIENS_OK:
            alertes.append('lire_aussi hors liste : %s' % u)
    return alertes, mots


def main():
    total = 0
    for p in sys.argv[1:]:
        alertes, mots = controle(p)
        total += 1
        etat = 'OK' if not alertes else '%d alerte(s)' % len(alertes)
        print('%-32s %4d mots  %s' % (Path(p).stem, mots, etat))
        for a in alertes:
            print('    - ' + a)
    print('%d fiche(s) controlee(s).' % total)


if __name__ == '__main__':
    main()
