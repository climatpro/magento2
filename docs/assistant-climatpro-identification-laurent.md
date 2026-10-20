# Assistant ClimatPro — Identification Laurent

| | |
|---|---|
| ID n8n | `UdHjR65FGA29FGQ4` |
| Actif | non |
| Déclencheur | Telegram Trigger (updates `message`), webhookId `4b2a6809-b899-422c-b34f-5117e4a76b40` |
| Export | `workflows/assistant-climatpro-identification-laurent.json` |

## Rôle
Squelette inachevé : un seul node Telegram Trigger, aucune connexion, aucun traitement. Servait vraisemblablement à récupérer l'identifiant Telegram (chat_id) de Laurent lors de la mise en place du bot (07/10/2026).

## Services appelés
- Telegram (trigger uniquement) — credential "Telegram account" (`thfKrKcwKcCWoR9V`)
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow vide (1 node, `connections: {}`) : code mort, à archiver.
- Utilise la même credential Telegram que "Bot - Assistant" (actif) : s'il était activé, il entrerait en conflit pour le webhook du même bot Telegram (un seul webhook par bot).
- Pas de description n8n.
