#!/usr/bin/env python3
"""Passe le millesime de l'accueil a l'annee en cours.

Tourne chaque matin dans le workflow de publication. Ne touche qu'a des
emplacements listes ci-dessous, ou l'annee designe l'edition du comparatif
(titre, H1, description, FAQ) et le copyright du pied de page.

Les annees qui sont des faits (date de mise a jour, annee d'un test, "Avis
Meetic 2026" qui signifie "teste en 2026") ne sont jamais modifiees ici :
les changer sans nouveau test serait faux.

    python3 tools/millesime.py                 # simulation
    python3 tools/millesime.py --appliquer     # ecrit les fichiers
    python3 tools/millesime.py --annee 2027    # simule une autre annee
"""
import argparse
import glob
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent

# Chaque motif capture (avant)(annee)(apres) ; seule l'annee est remplacee.
MOTIFS = {
    'index.html': [
        r'(Meilleur site de rencontre )(\d{4})( : notre comparatif)',
        r'(Comparatif )(\d{4})( des meilleurs sites de rencontre)',
        r'(Sites de rencontre recommandés )(\d{4})',
        r'(meilleur site de rencontre en )(\d{4})',
        r'(notre comparatif )(\d{4})(</h1>)',
    ],
    'avis/index.html': [
        r'(Avis sites de rencontre )(\d{4})( : nos tests)',
        r'("name": "Avis sites de rencontre )(\d{4})(")',
    ],
    'comparatifs/index.html': [
        r'(Comparatifs sites de rencontre )(\d{4})( : selon)',
    ],
    # copyright du pied de page, sur toutes les pages
    '**/*.html': [
        r'(&copy; )(\d{4})( meilleur-site-rencontre\.fr)',
    ],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--appliquer', action='store_true')
    parser.add_argument('--annee', type=int)
    args = parser.parse_args()

    annee = str(args.annee or datetime.now(ZoneInfo('Europe/Paris')).year)
    modifies = 0
    for motif_fichiers, motifs in MOTIFS.items():
        for chemin in sorted(glob.glob(str(RACINE / motif_fichiers), recursive=True)):
            if '/_planning/' in chemin or '/node_modules/' in chemin:
                continue
            texte = Path(chemin).read_text(encoding='utf-8')
            nouveau = texte
            for motif in motifs:
                nouveau = re.sub(motif, lambda m: m.group(1) + annee + (m.group(3) if m.lastindex >= 3 else ''), nouveau)
            if nouveau != texte:
                modifies += 1
                print('%s : millesime passe a %s' % (Path(chemin).relative_to(RACINE), annee))
                if args.appliquer:
                    Path(chemin).write_text(nouveau, encoding='utf-8')
    if not modifies:
        print('Millesime deja a jour (%s).' % annee)


if __name__ == '__main__':
    main()
