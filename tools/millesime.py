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
        r'(notre comparatif )(\d{4})(</em></h1>|</h1>)',
    ],
    'avis/index.html': [
        r'(Avis sites de rencontre )(\d{4})( : nos tests)',
        r'("name": "Avis sites de rencontre )(\d{4})(")',
    ],
    'comparatifs/index.html': [
        r'(Comparatifs sites de rencontre )(\d{4})( : selon)',
    ],
    'guides/index.html': [
        r'(Guides rencontre en ligne )(\d{4})( :)',
        r'(rencontres en ligne en )(\d{4})( :)',
    ],
    'qui-sommes-nous/index.html': [
        r'(recommandons en )(\d{4})(,)',
    ],
    'notre-methode/index.html': [
        r'(recommandons en )(\d{4})(,)',
    ],
    # sur toutes les pages : copyright, et liens qui citent le titre d'un comparatif
    '**/*.html': [
        r'(&copy; )(\d{4})( meilleur-site-rencontre\.fr)',
        r'(sites? de rencontre (?:sérieux|gay|senior|seniors) )(\d{4})(</a>)',
    ],
}


# Pages "edition" : tout millesime de l'annee precedente passe a l'annee en
# cours, sauf les dates (precedees d'un mois), les dates ISO et les versions
# de cache. Les comparatifs sont des classements dates de l'annee en cours.
PAGES_EDITION = ['comparatif-*/index.html']
GABARITS = ['tools/gabarits/*.html']
MOIS = r'(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)'


def edition(texte, annee):
    ancienne = str(int(annee) - 1)
    # les dates ("23 juin 2026") sont mises de cote avant le remplacement
    protege = {}
    def garde(m):
        cle = '\x00%d\x00' % len(protege)
        protege[cle] = m.group(0)
        return cle
    texte = re.sub(r'\b\d{1,2}(?:er)? %s %s\b' % (MOIS, ancienne), garde, texte)
    texte = re.sub(r'(?<![\d=-])%s(?![\d-])' % ancienne, annee, texte)
    for cle, val in protege.items():
        texte = texte.replace(cle, val)
    return texte


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--appliquer', action='store_true')
    parser.add_argument('--annee', type=int)
    args = parser.parse_args()

    annee = str(args.annee or datetime.now(ZoneInfo('Europe/Paris')).year)
    modifies = 0
    for motif_fichiers, motifs in MOTIFS.items():
        for chemin in sorted(glob.glob(str(RACINE / motif_fichiers), recursive=True)):
            if '/node_modules/' in chemin:
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
    for chemin in sorted(glob.glob(str(RACINE / GABARITS[0]))):
        texte = Path(chemin).read_text(encoding='utf-8')
        nouveau = re.sub(r'(&copy; )(\d{4})( meilleur-site-rencontre\.fr)', lambda m: m.group(1) + annee + m.group(3), texte)
        if nouveau != texte:
            modifies += 1
            print('%s : copyright passe a %s' % (Path(chemin).relative_to(RACINE), annee))
            if args.appliquer:
                Path(chemin).write_text(nouveau, encoding='utf-8')
    for motif_fichiers in PAGES_EDITION:
        for chemin in sorted(glob.glob(str(RACINE / motif_fichiers))):
            texte = Path(chemin).read_text(encoding='utf-8')
            nouveau = edition(texte, annee)
            if nouveau != texte:
                modifies += 1
                print('%s : edition passee a %s' % (Path(chemin).relative_to(RACINE), annee))
                if args.appliquer:
                    Path(chemin).write_text(nouveau, encoding='utf-8')
    if not modifies:
        print('Millesime deja a jour (%s).' % annee)


if __name__ == '__main__':
    main()
