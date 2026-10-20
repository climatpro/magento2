# Climapro - Ranger mémo (pro ou perso)

| | |
|---|---|
| ID n8n | `WioaHhSBgYJ2EbmU` |
| Actif | oui |
| Déclencheur | webhook POST /webhook/climapro-ranger (node "POST /climapro-ranger", authentification par en-tête `X-Key`, credential "Climapro X-Key" partagée avec "Climapro - Mémos vocaux"), réponse texte via node "Repondre a l'iPhone" |
| Export | `workflows/climapro-ranger-memo-pro-ou-perso.json` |

## Rôle
Réponse au menu iPhone « Pro ou perso ? » : prend le dernier mémo Todoist porteur du label `pro-ou-perso` et, selon `choix` (equipe / pro ou laurent / perso), retire le label, ajuste le titre (préfixe « À commander : » si label `commande`) et le déplace vers Perso, Équipe ClimatPro (ou sa section Commandes matériel) ou Laurent ClimatPro.
Renvoie un message de confirmation à l'iPhone.

## Services appelés
- Todoist API (GET /api/v1/tasks?label=pro-ou-perso ; POST /api/v1/tasks/{id} pour labels+titre ; POST /api/v1/tasks/{id}/move) — HTTP Request, credential "Todoist account" (`feB4B4HQds0e2tFC`)
- Data Tables n8n : aucune.

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Identifiants de projets/sections Todoist en dur (`6hh423vGr88f287j`, `6hh423vw4vGgHFPw`, `6hjM3Rw4RPRw474w`, `6hh4246PVq2H9Fp8`), dupliqués avec "Climapro - Mémos vocaux".
- Choisit « le dernier mémo » par `added_at` : si deux mémos attendent une réponse, la réponse peut être appliquée au mauvais ; aucun identifiant de mémo n'est transmis par l'iPhone.
- `onError: continueRegularOutput` sur la lecture Todoist : si l'API est indisponible, la réponse est « Aucun mémo en attente » (faux négatif).
- Deux écritures séquentielles sans transaction : si "Deplacer le memo" échoue après "Mettre a jour le memo", le label `pro-ou-perso` est déjà retiré et le mémo reste dans Perso sans marqueur.
- "Mettre a jour le memo" et "Deplacer le memo" sans `onError` : une erreur Todoist renvoie une réponse d'erreur brute à l'iPhone.
- Interprétation du `choix` par regex (`equipe`, `laurent|pro`, sinon perso) : toute valeur inattendue range en Perso sans avertir.
