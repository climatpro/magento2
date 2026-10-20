# Plaud vers Interfast CRM

| | |
|---|---|
| ID n8n | `jbzd2fq9MTIGLJK5` |
| Actif | oui |
| Déclencheur | cron "toutes les 15 minutes" (Schedule Trigger) |
| Export | `workflows/plaud-vers-interfast-crm.json` |

## Rôle
Toutes les 15 min : liste les enregistrements Plaud des 2 derniers jours (≥ 4 s, à partir du 07/10/2026), assemble le transcript, le fait classer par Claude (client, prospect, fournisseur, interne, perso, bruit) avec rédaction d'une note CRM ; si un client Interfast unique est identifié, consigne la note (appel ou note) sur sa fiche et crée une tâche Todoist en cas d'engagement ; sinon crée une tâche Todoist "A rattacher". Chaque fichier traité est mémorisé dans la Data Table plaud_traites. Écriture Interfast et Todoist.

## Services appelés
- Plaud MCP — `https://mcp.plaud.ai/mcp`, outils `list_files` et `get_file` (nodes MCP Client, credential `mcpOAuth2Api` "Unnamed credential" `KxcxKLAx6oNuafZS`)
- Anthropic — node `Claude Sonnet` (lmChatAnthropic, credential "Anthropic account" `GfYoRA9p0AV4WXlD`)
- Interfast direct (credential "Interfast API" `GgJ5wsyGIUSWY0cN`) : GET `https://app.inter-fast.fr/v1/crm/search` (page 0, size 5, archived false, name) ; POST `https://app.inter-fast.fr/v1/client/{id}/activities/notes` (écriture de la note)
- Todoist (node Todoist, credential "Todoist account" `feB4B4HQds0e2tFC`) : création de tâches dans le projet `6hh423vJrW7RvQQg` (Laurent ClimatPro)
- Data Table n8n `plaud_traites` (`5iiREQs0cwhwUqhB`) : lecture (`rowNotExists` sur `file_id`) et écriture (insert `file_id`, `nom`, `categorie`, `resultat`, `traite_le`)

## Modèle IA
Anthropic `claude-sonnet-5-5` (node `Claude Sonnet`, `@n8n/n8n-nodes-langchain.lmChatAnthropic`, maxTokensToSample 8000) branché sur la chaîne LLM `Classer` avec le parser structuré `Schema JSON` : classification de l'enregistrement et rédaction de la note CRM, du titre et de la tâche.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Description du workflow annonce "Claude Haiku" mais le modèle configuré est `claude-sonnet-5-5` (identifiant valide) ; la description est tronquée ("plaud_tra").
- Credential Plaud nommée "Unnamed credential" (OAuth2 à renouveler, aucun `onError` sur les nodes MCP).
- Aucun `onError` sur Interfast, Todoist et Plaud : une erreur interrompt toute la boucle ; si l'échec survient entre `Interfast - consigner la note` et `Marquer comme traite`, la note sera consignée une seconde fois au cycle suivant (doublon CRM).
- Fenêtre `list_files` de 2 jours + abandon après 48 h sans transcription (`Marquer sans transcription`) : un enregistrement transcrit tardivement est définitivement ignoré.
- `DATE_MIN = '2026-10-07'` et seuil de durée 4 000 ms en dur.
- Recherche client Interfast limitée à `size 5` : au-delà de 5 homonymes, aucune correspondance possible ; rapprochement exigeant un candidat unique (sinon tâche Todoist à rattacher manuellement).
- Parser de sortie basé sur un exemple JSON (pas de schéma strict) ; transcript tronqué à 60 000 caractères ; la découverte des fichiers repose sur des ids commençant par `of_` dans une réponse MCP parsée "à la louche".
- Le prompt système contient des noms réels (gérant, techniciens) et les IDs de projet Todoist sont en dur.
