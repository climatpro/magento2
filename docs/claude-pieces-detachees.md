# Claude - Pieces detachees

| | |
|---|---|
| ID n8n | `EQvQIgDjOe2gq98m` |
| Actif | non |
| Déclencheur | webhook POST /webhook/pieces-detachees (node "Webhook Claude", sans authentification n8n ; clé vérifiée à la main dans le code via l'en-tête `x-cle`) |
| Export | `workflows/claude-pieces-detachees.json` |

## Rôle
Passerelle pour Claude (MCP n8n) vers les outils de disponibilité de pièces détachées Toshiba et Hitachi, en rôle admin.
Reçoit `marque` + `reference` (ou `modele` + `mots_cles`), aiguille vers le bon sous-workflow et renvoie son résultat tel quel. Lecture seule.

## Services appelés
- Aucun service externe direct : tout passe par les deux sous-workflows (qui interrogent eux-mêmes les sites fournisseurs).
- Data Tables n8n : aucune.

## Modèle IA
Aucun.

## Sous-workflows appelés
- Outil - Dispo Toshiba (`4PjuGOfWCDdkuoPq`) via node "Outil Toshiba" (Execute Workflow, attend le résultat, `role: admin`)
- Outil - Dispo Hitachi (`p7VfJ2HTKTctJBsv`) via node "Outil Hitachi" (Execute Workflow, attend le résultat, `role: admin`)

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Secret en dur : la clé d'accès (`x-cle`) est comparée en clair dans le code du node "Entree" (remplacée par `<SECRET-RETIRE>` dans l'export). La description indique que c'est la même clé que "Outil - Sonepar" : un secret partagé entre plusieurs workflows.
- Webhook sans authentification n8n (`headerAuth` non utilisé) : la protection repose uniquement sur ce code maison.
- Workflow inactif (`active: false`) : l'URL de production ne répond pas tant qu'il n'est pas publié.
- Les erreurs (clé invalide, marque inconnue) sont renvoyées en HTTP 200 avec `resultat: "Erreur : …"` ; l'appelant doit inspecter le contenu.
- `responseMode: lastNode` : seul le premier item du dernier node est renvoyé ; si un sous-workflow renvoie plusieurs lignes, les suivantes sont perdues.
- Le rôle `admin` est forcé quel que soit l'appelant : toute personne disposant de la clé obtient le niveau admin des outils de dispo.
- Aucun timeout ni `onError` sur les nodes Execute Workflow : une panne du site fournisseur fait échouer l'appel.
