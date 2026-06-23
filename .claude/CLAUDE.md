# meilleur-site-rencontre.fr — Contexte projet

## Hébergement
- Serveur : VPS Hetzner avec cPanel
- Username cPanel : `meilleursiterenc`
- Deploy path : `/home/meilleursiterenc/public_html/`
- **Le dépôt Git est cloné directement dans `public_html`.** Publier = `git push` puis cliquer **"Update from Remote"** dans cPanel → Git Version Control. NE PAS utiliser "Deploy HEAD Commit" (le `.cpanel.yml` est volontairement réduit à un no-op `/bin/true`, car copier public_html dans lui-même créait des dossiers imbriqués).

## Stack technique
- HTML5 / CSS3 / JavaScript vanilla
- Aucun framework, aucun bundler
- Fichiers statiques uniquement

## Conventions de développement
- **Mobile-first** : écrire les styles pour mobile en premier, puis `min-width` media queries
- **Images** : format WebP privilégié, jamais de hotlink (toutes les images dans `/assets/`)
- **Icônes** : SVG inline de préférence
- **Alt text** : obligatoire sur toutes les balises `<img>`

## Règles SEO
- Chaque page doit avoir : `<title>` unique, `<meta name="description">`, balises Open Graph complètes
- Schema.org JSON-LD à ajouter selon le type de page
- `sitemap.xml` à mettre à jour à chaque nouvelle page
- `robots.txt` : ne jamais bloquer les crawlers sans raison

## Règles Git
- `main` = branche de production
- Workflow réel : commit + `git push origin main` directement (pas de PR), puis "Update from Remote" dans cPanel pour publier
- Messages de commit en français, impératif présent (ex: "Ajoute la page comparatif")
- Terminer les messages de commit par : `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

## Règle éditoriale d'or
- **Ne JAMAIS inventer de données** (prix, chiffres de test, dates, statistiques, anecdotes vécues). On reformule et on met en forme le contenu factuel existant ; la vraie matière vécue est fournie par l'éditeur.
- Pas de tiret cadratin (em-dash) dans le contenu : virgules, deux-points, parenthèses.
- Testeurs anonymes (intégrité des profils de test) mais **rédacteurs identifiés et signés** (E-E-A-T).

## État d'avancement (dernière mise à jour : 23 juin 2026)

Refonte en cours : passer d'un site "froid / affiliation générique" à un **site éditorial propre et personnalisé**. Page étalon = `avis-meetic`.

**Fait :**
- Arborescence multi-pages + hubs `/avis/`, `/comparatifs/`, `/guides/` ; nav rebranchée (plus de one-page).
- SEO technique : robots `index,follow` explicite, canonicals, sitemap complet, schema Organization unifié via `@id` (`#organization`).
- E-E-A-T auteurs : 5 rédacteurs réels (Lucie, Marie, Patrice, Jeanne, Bastien), photos dans `/assets/auteurs/`, pages `/auteurs/<slug>/` (schema Person), hub `/auteurs/`, signatures + bloc auteur + Person comme `author` du schema Review. Section anonymat de `qui-sommes-nous` réécrite.
- **Les 8 avis** ont le gabarit éditorial complet : fond teinté + panneau blanc + sidebar sticky (logos), scorecard de notation qualitative, fiche d'identité (Meetic), tarifs en cartes (Meetic), bloc "fait pour vous ?", encadré "parti pris", verdict en voix 1re personne.
- Composants CSS réutilisables dans `css/style.css` (chercher les blocs commentés : scorecard, id-card, edito-note, price-grid, fit-grid, author-box, review-shell/sidebar). Cache-busting CSS via `?v=AAAAMMJJ-N` sur le `<link>` (bumper à chaque modif du CSS).

**À faire (prochaine session) :**
1. **Les 4 guides** = priorité, ils ont **0 image** (point le plus "froid"). Gabarit à inventer (sommaire illustré, encadrés conseils, schémas SVG ; pas de scorecard/tarifs).
2. Appliquer le gabarit éditorial aux **3 comparatifs**.
3. Optionnel : enrichir l'accueil, et affiner les pages auteur (ajouter `sameAs` LinkedIn, années d'expérience réelles si fournies).
4. Quand l'éditeur fournit du **vécu réel** (captures anonymisées, vrais prix, anecdotes), l'injecter dans les avis pour passer de "bien fichu" à "incontournable".
