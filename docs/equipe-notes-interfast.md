# Equipe - Notes Interfast

| | |
|---|---|
| ID n8n | `aG1bAfDj6ErD5IOQ` |
| Actif | oui |
| Déclencheur | cron « toutes les 5 minutes » (Schedule Trigger) |
| Export | `workflows/equipe-notes-interfast.json` |

## Rôle
Toutes les 5 min, après 3 min de calme, envoie à Claude Haiku le lot (≤ 60) des messages non traités du fil équipe avec le planning Interfast du jour. Les infos client détectées deviennent des notes « à valider » envoyées en privé à Laurent (boutons Telegram) avant écriture dans Interfast ; les demandes de matériel deviennent des tâches Todoist « À commander » dédoublonnées.

## Services appelés
- Interfast — direct via HTTP Request, credential « Interfast API » (`GgJ5wsyGIUSWY0cN`) : GET /v1/crm/search (recherche client par mot le plus long du nom), POST /v1/client/{id}/activities/notes (branche directe, inactive car TOUT_VALIDER = true)
- Interfast — via le sous-workflow « Interfast - Lecture » (op `events_jour`) pour le planning du jour
- Anthropic — HTTP Request POST https://api.anthropic.com/v1/messages, credential « Anthropic account 2 » (`UtZzlYk97MvjuDan`)
- Telegram — messages privés à Laurent (chat `1857340429`) avec clavier inline `nv:<id>:ok|no` ; credential « Bot Telegram - groupe climatpro » (`gQjbmvis03Oi1VtD`)
- Todoist — HTTP Request GET /api/v1/tasks/filter (`@commande`, limit 200) et POST /api/v1/tasks (projet `6hh423vw4vGgHFPw`, section `6hjM3Rw4RPRw474w`, labels commande/memo) ; credential « Todoist account » (`feB4B4HQds0e2tFC`)
- Data Tables n8n : equipe_messages `JtuuDgi9yHe84lHj` (lecture `traite = false` ; mise à jour traite/essais/client_nom/note_interfast/client_id) ; notes à valider `yUbZrUGS9DHJX3ss` (insertion statut `a_valider`, mise à jour `tg_message_id`)

## Modèle IA
Anthropic `claude-haiku-5-5` (en dur dans le jsonBody du node « Analyser (Haiku) », max_tokens 8000, timeout 120 s) : extrait du lot les notes client (rattachement nommé/planning/aucun, résumé) et les commandes de matériel, en JSON.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via node « Lire planning du jour » (Execute Workflow, `op = events_jour`, `params = { date, jours: 1 }`)

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Modèle `claude-haiku-5-5` (valide) et en-tête `anthropic-version: 2023-06-01` écrits en dur dans une expression : à maintenir à la main lors d'un changement de modèle.
- « Analyser (Haiku) » en `onError: continueRegularOutput` : une erreur API est traitée comme réponse illisible ; au 2e échec le lot est marqué traité avec `client_nom = (lot illisible)` et remonte à Laurent en une seule note.
- Branche directe vers Interfast (« Note autorisee ? » → consigner) : code mort tant que `TOUT_VALIDER = true` ; ce node n'a pas de `onError` et « Messages consignes » apparie les items par index (fragile).
- Constante `TOUT_VALIDER` et chat_id de Laurent (`1857340429`) en dur dans le code.
- Recherche client Interfast sur un seul mot (le plus long du nom, 5 résultats) puis filtrage par préfixe : homonymes et noms composés mal gérés.
- Alertes Telegram en `onError: continue` : si l'envoi échoue, `tg_message_id = 0` et la validation par réponse devient impossible.
- « Lire planning du jour » en `onError: continue` : sans planning, Haiku rattache moins bien.
- Dédoublonnage Todoist heuristique (≥ 60 % de mots communs) : faux positifs possibles (« Colson noirs » vs « Colson blancs »).
- Lot limité à 60 messages et attente de 3 min de calme : un groupe très actif retarde indéfiniment le traitement.
- Prompt système long stocké dans une expression `JSON.stringify` : difficile à relire/modifier.
