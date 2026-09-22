# meilleur-site-rencontre.fr : contexte projet

## Hébergement
- Serveur : VPS Hetzner avec cPanel
- Username cPanel : `meilleursiterenc`
- Deploy path : `/home/meilleursiterenc/public_html/`
- **Le dépôt Git est cloné directement dans `public_html`.**
- **Publication automatique** : une tâche cron cPanel synchronise le serveur toutes les 30 minutes par `git fetch` puis `git reset --hard origin/main`. Publier = `git push`, rien d'autre. Ne plus utiliser « Update from Remote » ni « Deploy HEAD Commit ».
- `reset --hard` plutôt que `pull` parce que `pull` a bloqué le déploiement deux fois sur des modifications locales du `.htaccess`. Conséquence : ne jamais éditer un fichier directement sur le serveur, il sera écrasé sous 30 minutes.
- Le site est derrière **Cloudflare**, cache de 4 heures : pour vérifier une mise en ligne, ajouter un paramètre unique à l'URL, sinon on lit une version périmée.
- Journal du cron : `/home/meilleursiterenc/cron-test.log`

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

## État d'avancement (dernière mise à jour : 18 septembre 2026)

Le site est complet sur le plan éditorial et technique. **Le frein n'est plus la qualité des pages, c'est l'indexation et l'autorité.**

**Constat Search Console au 18 septembre 2026 :**
- 9 pages indexées sur 37 connues, 17 en « Détectée, actuellement non indexée » (Google ne vient même pas les explorer)
- 2 clics et 39 impressions sur 3 mois, position moyenne 35
- Les impressions viennent presque uniquement de Meetic (« meetic avis », « avis meetic », « test meetic »)
- Domaine créé le 3 mars 2026, donc 6 mois d'ancienneté, sans netlinking significatif

Conséquence stratégique : peaufiner les pages existantes ne produit plus rien de mesurable. Les leviers sont l'indexation (maillage, demandes d'indexation), les liens entrants, et des contenus visant des requêtes réellement gagnables.

**Fait :**
- Arborescence multi-pages, hubs `/avis/`, `/comparatifs/`, `/guides/`, `/lexique/`
- SEO technique propre : robots, canonicals, sitemap à jour, schema Organization unifié
- E-E-A-T : 5 rédacteurs réels, pages auteur, **les 15 pages de contenu sont signées** (avis, guides, comparatifs, lexique)
- Les 8 avis ont le gabarit éditorial complet ; les 3 comparatifs et les 4 guides ont image à la une et signature
- Images : tout en WebP, aucun JPEG servi dans un `src`
- Maillage : les guides pointent vers les avis (19 liens contextuels) et vers le lexique
- Lexique du dating lancé le 18 septembre 2026 : hub + 6 fiches (ghosting, love bombing, catfishing, situationship, breadcrumbing, benching)
- Tournures répétées d'un avis à l'autre supprimées (les 8 verdicts ouvraient sur la même formule)

**À faire :**
1. **Nouveaux lots de fiches lexique**, 5 à 8 à la fois, jamais plus : sur un domaine que Google explore à reculons, une publication massive finit en « Détectée, non indexée ». Générateur réutilisable dans `/private/tmp/lexique_build/` (à re-créer au besoin, c'est un dossier temporaire).
2. **Mettre en place un système de planification des contenus** sur le modèle de red-dead-redemption-3.com (demande de l'éditeur, 18 septembre 2026).
3. **Cluster Meetic** quand l'éditeur fournit la matière : résiliation, gratuité, tarifs réels. La page tarifs n'a d'intérêt qu'avec de vrais montants relevés.
4. Encadré « parti pris » sur les 3 comparatifs, illustrations dans le corps des guides.
5. **Point à trancher** : le pied de page annonce « depuis 2018 » alors que le domaine date de mars 2026.
