# meilleur-site-rencontre.fr — Contexte projet

## Hébergement
- Serveur : VPS Hetzner avec cPanel
- Username cPanel : `meilleursiterenc`
- Deploy path : `/home/meilleursiterenc/public_html/`
- Déploiement automatique via `.cpanel.yml` (Git Version Control dans cPanel)

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
- `main` = branche de production (déployée automatiquement sur cPanel)
- Nouvelles fonctionnalités sur branches `feature/nom-feature`
- Corrections sur branches `fix/nom-fix`
- **Jamais de push direct sur `main`** — passer par une PR
- Messages de commit en français, impératif présent (ex: "Ajoute la page comparatif")
