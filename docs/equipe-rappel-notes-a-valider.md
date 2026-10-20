# Equipe - Rappel notes a valider

| | |
|---|---|
| ID n8n | `dsuziDLsOVsyISIk` |
| Actif | oui |
| Déclencheur | cron `0 18 * * *` (tous les jours 18h, fuseau de l'instance n8n) |
| Export | `workflows/equipe-rappel-notes-a-valider.json` |

## Rôle
Chaque soir, s'il reste des notes du fil équipe au statut `a_valider`, envoie à Laurent en privé sur Telegram la liste (15 max) des clients concernés pour qu'il les traite dans la conversation du bot.

## Services appelés
- Telegram — sendMessage (HTML) vers le chat privé `1857340429` ; credential « Bot Telegram - groupe climatpro » (`gQjbmvis03Oi1VtD`)
- Data Table n8n : notes à valider `yUbZrUGS9DHJX3ss` (lecture, filtre `statut = a_valider`)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- chat_id de Laurent en dur (`1857340429`).
- Heure du cron dépendante du fuseau configuré sur l'instance n8n (pas de fuseau explicite dans le node).
- Pas de `onError` sur le node Telegram.
- Liste tronquée à 15 lignes ; pas de lien direct vers chaque note.
