#!/usr/bin/env python3
"""Met en file de publication un lot de nouvelles fiches du lexique.

Copie les sources validees dans tools/donnees/fiches/, fixe leur date de
publication (lots du mardi), construit leur page dans _planning/lexique/ et
les inscrit dans _planning/planning.json. Le workflow quotidien les publie
ensuite a echeance (tools/publier.py).

    python3 tools/planifier_lexique.py DOSSIER_SOURCES            # simulation
    python3 tools/planifier_lexique.py DOSSIER_SOURCES --appliquer
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / 'tools'))
import fiche_lexique  # noqa: E402

# Ordre de publication : les termes les plus recherches d'abord, 6 par mardi
LOTS = [
    ('2026-10-27', ['red-flag', 'match', 'crush', 'date', 'swipe', 'friendzone']),
    ('2026-11-03', ['green-flag', 'gaslighting', 'talking-stage', 'ick', 'bio', 'like']),
    ('2026-11-10', ['deal-breaker', 'exclusivite', 'love-language', 'attachement-anxieux', 'rebound', 'unmatch']),
    ('2026-11-17', ['negging', 'kittenfishing', 'slow-fade', 'opener', 'icebreaker', 'vu']),
    ('2026-11-24', ['soft-launch', 'hard-launch', 'pocketing', 'dating-fatigue', 'blind-date', 'cuffing-season']),
    ('2026-12-01', ['polyamour', 'relation-libre', 'friends-with-benefits', 'monkey-branching', 'roaching', 'phubbing']),
    ('2026-12-08', ['jalousie-retroactive', 'fizzling', 'hesitationship', 'slow-dating', 'boost', 'algorithme-de-matching']),
    ('2026-12-15', ['quiet-quitting-amoureux', 'textlationship', 'wokefishing']),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dossier')
    ap.add_argument('--appliquer', action='store_true')
    a = ap.parse_args()
    src = Path(a.dossier)
    planning_p = RACINE / '_planning' / 'planning.json'
    planning = json.loads(planning_p.read_text(encoding='utf-8'))
    deja = {e['slug'] for e in planning}
    n = 0
    for date, slugs in LOTS:
        for slug in slugs:
            f = src / (slug + '.json')
            if not f.exists():
                print('MANQUANT  %s' % slug)
                continue
            if slug in deja:
                print('deja en file  %s' % slug)
                continue
            d = json.loads(f.read_text(encoding='utf-8'))
            d['publie_le'] = d['modifie_le'] = date
            print('%s  %s' % (date, slug))
            n += 1
            if not a.appliquer:
                continue
            (RACINE / 'tools' / 'donnees' / 'fiches' / f.name).write_text(
                json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            fiche_lexique.construire(slug, True, dossier='_planning/lexique')
            planning.append({
                'slug': slug, 'type': 'lexique', 'titre': d['mot'], 'resume': d['resume'],
                'definition': d['definition_courte'], 'genre': d['genre'],
                'etymologie': d.get('etymologie', ''), 'publier_le': date, 'statut': 'planifie'})
    if a.appliquer:
        planning_p.write_text(json.dumps(planning, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('%d fiche(s) %s.' % (n, 'mises en file' if a.appliquer else 'a mettre en file (simulation)'))


if __name__ == '__main__':
    main()
