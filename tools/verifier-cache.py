#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuse un commit qui modifie la CSS ou le JS sans changer le parametre ?v=.

Sans ce bump, Cloudflare continue de servir l'ancien fichier pendant un mois
(max-age=2592000 impose par le .htaccess) et les visiteurs recoivent le nouveau
HTML avec l'ancienne CSS. C'est arrive le 24 septembre 2026.
"""
import re, subprocess, sys, pathlib

def versions_dans_html():
    v = set()
    for f in pathlib.Path('.').rglob('*.html'):
        if '.git' in str(f):
            continue
        t = f.read_text(encoding='utf-8')
        v |= set(re.findall(r'style\.css\?v=([0-9-]+)', t))
        v |= set(re.findall(r'main\.js\?v=([0-9-]+)', t))
    return v

def modifie(chemin, depuis):
    r = subprocess.run(['git', 'diff', '--name-only', depuis, 'HEAD', '--', chemin],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())

base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD~1'
actuelles = versions_dans_html()
if len(actuelles) > 1:
    print('ECHEC : plusieurs versions de cache coexistent dans le HTML : %s' % sorted(actuelles))
    sys.exit(1)

r = subprocess.run(['git', 'diff', '--name-only', base, 'HEAD'], capture_output=True, text=True)
touches = r.stdout.split()
assets = [f for f in touches if f.endswith(('css/style.css', 'js/main.js'))]
html_touche = any(f.endswith('.html') for f in touches)

if assets:
    r2 = subprocess.run(['git', 'diff', base, 'HEAD', '--', '*.html'], capture_output=True, text=True)
    if '?v=' not in r2.stdout:
        print('ECHEC : %s modifie mais le parametre ?v= n a pas ete change.' % ', '.join(assets))
        print('        Cloudflare servirait l ancien fichier pendant un mois.')
        sys.exit(1)

print('OK : version de cache coherente (%s)' % (sorted(actuelles)[0] if actuelles else 'aucune'))
