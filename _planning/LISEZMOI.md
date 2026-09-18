# File d'attente de publication

Les pages placées ici sont terminées mais pas encore en ligne : elles ne sont
liées nulle part, absentes du sitemap, et l'accès web à `/_planning/` est
interdit par le `.htaccess`.

## Comment ça marche

1. Une page prête est déposée dans `_planning/<type>/<slug>/index.html`.
2. Son entrée est ajoutée à `planning.json` avec sa date de publication.
3. Chaque matin, GitHub Actions exécute `tools/publier.py`. Ce qui est arrivé
   à échéance est déplacé à la racine, ajouté au hub et au sitemap, puis commité.
4. Le serveur récupère le commit via sa tâche cron `git pull`.

## Règles à respecter

- **Ne jamais faire pointer une page en attente vers une autre page en attente** :
  le lien serait mort entre les deux dates de publication. On ne lie que vers
  des pages déjà en ligne.
- **Par lots de 5 à 8 pages maximum.** Sur ce domaine, Google n'explore pas les
  publications massives, elles finissent en « Détectée, actuellement non indexée ».
- Changer une date : modifier `publier_le`, rien d'autre.
- Retirer un contenu de la file : passer son `statut` à `suspendu`.

## Vérifier avant que ça parte

    python3 tools/publier.py                      # simulation, n'écrit rien
    python3 tools/publier.py --date 2026-09-22    # simule un jour précis
