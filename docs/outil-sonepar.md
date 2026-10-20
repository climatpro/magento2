# Outil - Sonepar

| | |
|---|---|
| ID n8n | `nUxjWTbY2DyKPetM` |
| Actif | oui |
| Déclencheur | double : appel par sous-workflow (Execute Workflow Trigger, entrées `reference`, `role`) et webhook POST `/webhook/sonepar-prix` (en-tête `x-cle`, réponse = dernier node) |
| Export | `workflows/outil-sonepar.json` |

## Rôle
Outil du bot et de Claude : prix net ClimatPro, stock et délai d'une référence sur sonepar.fr, obtenus en pilotant un Chromium headless (browserless) qui se connecte avec le compte Sonepar personnel de Laurent. Réservé au rôle admin ; 8 produits max, correspondance exacte privilégiée.

## Services appelés
- browserless (VPS) — POST `http://browserless:3000/function?token=…` (script Puppeteer, timeout 90 s, `neverError`)
- sonepar.fr — login `login.sonepar.fr` puis recherche catalogue `/catalog/fr-fr/search/<ref>`, scraping du DOM (prix net, prix public, stock, livraison, retrait)
- Data Table n8n `sonepar_acces` (`lJhoGjf1oe1kfKJz`) lecture : `identifiant`, `mot_de_passe`
- Data Table n8n `hiparts_acces` (`VrTMPgLga7GykpX2`) lecture : `browserless_token`

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « prix_sonepar »

## Points fragiles
- Clé du webhook `x-cle` en dur dans le code du node `Entree` (retirée de l'export : `<SECRET-RETIRE>`) ; comparaison de chaîne non constante ; tout appel webhook muni de la clé obtient d'office le rôle admin.
- Identifiants Sonepar stockés en clair dans une Data Table et envoyés dans le corps de la requête browserless ; token browserless dans l'URL (visible dans les exécutions).
- Version publiée ≠ brouillon (`activeVersionId d57787d4…` vs `versionId fb9cb161…`) : le brouillon ajoute l'interception des requêtes (images, trackers) et le libellé "pas de stock" ; non publié.
- Scraping dépendant de sélecteurs et libellés du site (`#onetrust-reject-all-handler`, `#email`, `#next`, `data-testid`, classes `price-display-block_…`, textes "Réf.fab", "Comparer", "disponibles pour la livraison") : casse à la moindre refonte Sonepar.
- Connexion complète à chaque appel (pas de session réutilisée) : lent, et risque de blocage du compte en cas d'appels répétés.
- URL interne `http://browserless:3000` en dur ; aucun credential n8n (tout passe par les Data Tables).
- `alwaysOutputData` sur les lectures de tables : une table vide ne lève pas d'erreur, seulement un message.
