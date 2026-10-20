# Equipe - Validation notes

| | |
|---|---|
| ID n8n | `7NeZSKB3GXm3tXOB` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrée `update` = objet update Telegram) |
| Export | `workflows/equipe-validation-notes.json` |

## Rôle
Traite la décision de Laurent sur une note « à valider » : clic sur ✅/🗑 (callback `nv:<id>:ok|no`) ou réponse privée à la note avec un nom ou un id client Interfast. Écrit la note sur la fiche client Interfast, met à jour le statut (`envoyee`, `ignoree`, motif) et édite/répond au message Telegram.

## Services appelés
- Interfast — direct via HTTP Request, credential « Interfast API » (`GgJ5wsyGIUSWY0cN`) : GET /v1/crm/search (nom saisi, 8 résultats), POST /v1/client/{id}/activities/notes
- Telegram — answerCallbackQuery, editMessageText (retire les boutons), sendMessage en réponse ; credential « Bot Telegram - groupe climatpro » (`gQjbmvis03Oi1VtD`)
- Data Tables n8n : bot_users `MAaqIFX2KBiCvHFa` (lecture : admins actifs) ; notes à valider `yUbZrUGS9DHJX3ss` (lecture par id ou tg_message_id ; mise à jour statut/client_id/client_nom/motif)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Equipe - Archiviste](equipe-archiviste.md) — node « Valider une note »

## Points fragiles
- Mode test résiduel : `MODE_TEST = false` et liste `AUTORISES = ['406157', '405318']` en dur dans « Decider » (code mort).
- Seuls les `telegram_id` de rôle `admin` dans bot_users sont écoutés : si la table est vide, tout est ignoré en silence.
- Retrouver la note par `tg_message_id` suppose qu'il soit unique ; si l'alerte Telegram avait échoué (`tg_message_id = 0`), la réponse ne peut pas être rattachée.
- Recherche client par le mot le plus long du nom saisi, puis filtrage par préfixe : homonymes mal gérés (réponse « plusieurs fiches »).
- Un id saisi à la main (`\d{3,10}`) est écrit directement sans vérification d'existence du client.
- POST Interfast en `onError: continue` ; la détection d'échec repose sur `error`/`statusCode` dans la sortie.
- « Mettre a jour la note » filtre sur `note_id || -1` : si la note est introuvable, update sans effet mais le flux continue et répond à Laurent.
- Texte édité limité à 3 200 caractères (troncature possible du message d'origine).
