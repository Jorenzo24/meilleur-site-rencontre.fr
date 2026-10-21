# Fiches du lexique : format des sources

Une fiche = un fichier `<slug>.json`. La page est construite par
`python3 tools/fiche_lexique.py <slug> --appliquer` (dans `lexique/` si la
fiche est en ligne, dans `_planning/lexique/` sinon).

| Champ | Contenu |
|---|---|
| `slug` | identifiant d'URL, minuscules et tirets |
| `mot` | le terme tel qu'affiché (« Red flag ») |
| `genre` | `n. m.` ou `n. f.` (ou `loc.` pour une locution) |
| `etymologie` | origine en HTML court, `<i>` pour le mot étranger ; peut être vide |
| `resume` | 3 à 6 mots pour les vignettes (« Signal d'alerte en amour ») |
| `definition_courte` | une phrase de dictionnaire pour le glossaire |
| `title` | balise title, 50 à 65 caractères, sans année |
| `description` | méta-description, 130 à 155 caractères |
| `h1` | titre avec la partie forte en `<em>` après les deux-points |
| `lede` | chapeau de 2 à 3 phrases, une scène concrète |
| `definition` | paragraphe de définition complète (2 à 3 phrases), HTML |
| `sections` | 3 ou 4 parties `{id, titre, html}` ; HTML : `<p>`, `<h3>`, `<ul class="prose-list">`, `<strong>`, liens |
| `conversation` | facultatif : `{nom, legende, messages:[{de:"recu"|"envoye", texte}], apres:<id de section>, commentaire:<p>…</p>}` |
| `parti_pris` | une opinion de la rédaction en 2 phrases, sans prétendre à des tests |
| `lies` | 2 à 4 slugs de fiches liées (n'apparaissent que si elles sont en ligne) |
| `lire_aussi` | 2 URL parmi les guides, comparatifs et `/avis/` |
| `auteur` | `lucie`, `marie`, `patrice`, `jeanne` ou `bastien` |
| `publie_le`, `modifie_le` | dates ISO |
