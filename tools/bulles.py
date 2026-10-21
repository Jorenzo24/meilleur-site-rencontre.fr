#!/usr/bin/env python3
"""Transforme les exemples des guides en maquettes d'appli de rencontre.

- Premier message : fenetre de conversation. Bon exemple : l'autre est en
  train d'ecrire. A eviter : "Vu", sans reponse.
- Bio : fiche de profil. Bon exemple : un message arrive. A eviter : rien.

    python3 tools/bulles.py --appliquer
"""
import argparse
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MOTS_SALUT = r"(?:Bonsoir|Bonjour|Salut|Hello|Coucou)"


def prenom(texte):
    m = re.match(MOTS_SALUT + r"\s+([A-ZÉÈ][a-zéèëïîç]+)", texte)
    return m.group(1) if m else None


def chat(m):
    sorte, contenu = m.group(1), m.group(2).strip()
    texte = re.sub(r'</?p>', '', contenu).strip()
    nom = prenom(re.sub(r'<[^>]+>', '', texte))
    titre = nom or 'Nouveau match'
    initiale = (nom or '♥')[0]
    if sorte == 'bon':
        suite = ('<p class="ch-ecrit" aria-label="%s est en train d\'écrire"><span></span><span></span><span></span></p>'
                 % (nom or 'Votre match'))
        statut = '<span class="ch-ligne">en ligne</span>'
        legende = 'Exemple de premier message qui obtient une réponse'
    else:
        suite = '<p class="ch-vu">Vu</p>'
        statut = ''
        legende = 'Exemple de premier message à éviter, resté sans réponse'
    return ('<figure class="ch ch--%s">\n'
            '          <figcaption class="visually-hidden">%s</figcaption>\n'
            '          <div class="ch-tete"><span class="ch-av" aria-hidden="true">%s</span><span class="ch-nom">%s%s</span></div>\n'
            '          <div class="ch-fil">\n'
            '            <p class="ch-bulle">%s</p>\n'
            '            %s\n'
            '          </div>\n'
            '        </figure>') % (sorte, legende, initiale, titre, statut, texte, suite)


def fiche(m):
    sorte, contenu = m.group(1), m.group(2).strip()
    texte = re.sub(r'</?p>', '', contenu).strip()
    if sorte == 'bon':
        pied = '<p class="pf-notif"><span aria-hidden="true">♥</span> Nouveau message</p>'
        legende = 'Exemple de bio qui donne envie d\'écrire'
    else:
        pied = '<p class="pf-rien">Aucun message pour l\'instant</p>'
        legende = 'Exemple de bio à éviter'
    return ('<figure class="pf pf--%s">\n'
            '          <figcaption class="visually-hidden">%s</figcaption>\n'
            '          <div class="pf-tete"><span class="pf-photo" aria-hidden="true"></span><span class="pf-id">Femme, 32 ans<small>Relation sérieuse</small></span></div>\n'
            '          <p class="pf-t">À propos de moi</p>\n'
            '          <p class="pf-bio">%s</p>\n'
            '          %s\n'
            '        </figure>') % (sorte, legende, texte, pied)


MOTIF = r'<figure class="gd-ex gd-ex--(bon|mauvais)">\s*<figcaption>.*?</figcaption>\s*<blockquote>(.*?)</blockquote>\s*</figure>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--appliquer', action='store_true')
    a = ap.parse_args()
    for dossier, fn in (('guide/premier-message', chat), ('guide/profil-attractif', fiche)):
        p = RACINE / dossier / 'index.html'
        t = p.read_text(encoding='utf-8')
        t2, n = re.subn(MOTIF, fn, t, flags=re.S)
        print('%s : %d exemples' % (dossier, n))
        if a.appliquer and n:
            p.write_text(t2, encoding='utf-8')


if __name__ == '__main__':
    main()
