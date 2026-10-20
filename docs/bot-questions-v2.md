# Bot - Questions (V2)

| | |
|---|---|
| ID n8n | `39jFHOalFexDqKDq` |
| Actif | non |
| Déclencheur | Telegram Trigger "Message Telegram" (updates `message`), webhookId `4191105f-7fbb-4ac0-bb7d-e20f0548b2d9` |
| Export | `workflows/bot-questions-v2.json` |

## Rôle
Bot Telegram question-réponse minimal (3 intentions : prochain RDV, téléphone du client, adresse) pour les techniciens de la liste blanche `bot_users`. Haiku classe seulement l'intention et la date ; le code lit le planning du technicien via "Interfast - Lecture", choisit le prochain RDV, copie les données (jamais réécrites par le modèle), répond et journalise dans le Google Sheet. Remplacé par "Bot - Assistant".

## Services appelés
- Telegram — trigger + sendMessage, credential "Telegram account" (`thfKrKcwKcCWoR9V`)
- Anthropic — HTTP Request POST https://api.anthropic.com/v1/messages (node "Comprendre la question"), credential "Anthropic account 2" (`UtZzlYk97MvjuDan`), timeout 20 s
- Interfast — uniquement via le sous-workflow "Interfast - Lecture" (ops `events_jour`, `rdv_jour`, `client`)
- Google Sheets — append "Journal Bot ClimatPro" (doc `1AYGI1KRBJrVBRiE9VIcfq6i6-0Tcz0HF9Mjan12wJmg`, gid 282010760), credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Data Tables n8n lues : `bot_users` (`MAaqIFX2KBiCvHFa`)

## Modèle IA
Anthropic `claude-haiku-5-5` dans le node HTTP "Comprendre la question" : classification d'intention (`prochain_rdv` / `telephone` / `adresse` / `autre`) + date éventuelle, JSON de 100 tokens max.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes Execute Workflow "Lire interventions du jour", "Lire RDV du jour", "Lire client"

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Obsolète : remplacé par "Bot - Assistant" (`fb86kJwEmjNC5Vcd`, actif) ; même credential Telegram, donc ne peut pas être réactivé en parallèle (un seul webhook par bot).
- Pas de quota ni de limitation de débit (mentionné "reste à faire" dans la sticky note).
- "Comprendre la question" en `onError: continueRegularOutput` : en cas d'erreur API, l'intention retombe sur `autre` sans message explicite.
- "Lire client" est appelé même quand `clientId` est vide (appel inutile au sous-workflow).
- Limite connue (sticky note) : les RDV encore au nom de Julien ne remontent pas pour Axel (filtre API par technicien), sans le remappage présent dans Brief 18h.
- Sticky note obsolète (le journal Google Sheet listé "à faire" existe déjà).
- Journal Google Sheet contient questions et réponses (téléphones de clients).
