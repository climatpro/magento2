# Bot - Brief 18h (V1, Lw8Dv81qmxIMwXVI)

| | |
|---|---|
| ID n8n | `Lw8Dv81qmxIMwXVI` |
| Actif | non |
| Déclencheur | Schedule Trigger "Tous les jours 18h" (daysInterval 1, 18:00, misfirePolicy skip) + Manual Trigger "Test manuel" |
| Export | `workflows/bot-brief-18h--Lw8Dv81qmxIMwXVI.json` |

## Rôle
Version V1 (pilote Laurent, 07/10/2026) du brief du soir : lit les événements Interfast de J+1 (jusqu'au lundi si vendredi), filtre les interventions non terminées, enrichit chacune (fiche intervention, fiche client avec téléphones, devis via `secondReference` DCxxxx ou devis signés du client, lignes matériel du devis) et envoie un ou plusieurs messages HTML Telegram à un chat_id fixe. Sans IA. Remplacée par le workflow du même nom `ZivtrXedkHo5phMD`.

## Services appelés
- Interfast — uniquement via le sous-workflow générique `MOZo7wkYxjOghKVZ` (entrées `path` + `query`) : GET /v1/events, /v1/intervention/{id}, /v1/client/{id}, /v1/billing/quotations (recherche par name ou clients), /v1/billing/quotations/{id}
- Telegram — sendMessage HTML, credential "Telegram account" (`thfKrKcwKcCWoR9V`)
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
- Interfast - Lecture V1 (`MOZo7wkYxjOghKVZ`, interface `path`/`query`, inactif ; distinct de "Interfast - Lecture" `Qgn9xL6dGSAcq4Zv` à interface `op`/`params`) via nodes Execute Workflow "Interfast - events J+1", "Interfast - detail intervention", "Interfast - fiche client", "Interfast - recherche devis", "Interfast - detail devis"

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow obsolète : doublon de "Bot - Brief 18h" (`ZivtrXedkHo5phMD`, actif) ; à archiver pour éviter une double activation.
- `CHAT_ID = '1857340429'` (Telegram de Laurent) codé en dur dans "Composition du brief" au lieu de la table `bot_users`.
- Sous-workflow `MOZo7wkYxjOghKVZ` (Interfast - Lecture V1, inactif) référencé par ID sans nom en cache ; deux workflows portent le nom "Interfast - Lecture" avec des interfaces différentes (`path`/`query` vs `op`/`params`).
- Fusions par index (`base[i]` / `res[i]`) après des Execute Workflow en `onError: continueRegularOutput` : un item manquant décale toutes les fiches.
- Une seule page d'événements (`count: 100`) sans pagination.
- Regex devis `\b(DC\s*\d{3,})\b` sur `secondReference` ; décodage de l'horaire par le dernier chiffre des minutes (1/2/3/4), convention implicite partagée avec les autres workflows.
- Pas de timezone dans les settings (le code force Europe/Paris) ; pas de journalisation.
