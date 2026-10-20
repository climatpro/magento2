# Equipe - Archiviste

| | |
|---|---|
| ID n8n | `Sfax1FXhgLXoeyLN` |
| Actif | oui |
| Déclencheur | Telegram trigger (node "Message du groupe", updates `message` + `callback_query`, bot @Team_ClimatPro_bot, credential "Bot Telegram - groupe climatpro") |
| Export | `workflows/equipe-archiviste.json` |

## Rôle
Bot muet du groupe Telegram « ClimatPro Equipe » : enregistre chaque message du groupe (auteur résolu via la table des utilisateurs, texte, type, position, contact…) dans la table `equipe_messages` et range les photos dans Drive > Tableau de bord ClimatPro > fil-equipe-photos.
Les `callback_query` et les messages privés sont délégués au workflow "Equipe - Validation notes" ; le bot ne répond jamais lui-même.

## Services appelés
- Telegram (trigger ; node "Telecharger photo" : récupération du fichier, forcé en `image/jpeg`) — credential "Bot Telegram - groupe climatpro" (`gQjbmvis03Oi1VtD`)
- Google Drive (node "Ranger photo (Drive)" : upload dans le dossier `1B7lTbisc88kRcVsQ5QX8LdZ0BeWhX2NE`) — credential "Google Drive account 2" (`54fd9ApHaDydoOJv`)
- Data Tables n8n : table des utilisateurs (`MAaqIFX2KBiCvHFa`, nom non visible, colonnes `telegram_id`/`nom`) — lecture ; `equipe_messages` (`JtuuDgi9yHe84lHj`) — insertion

## Modèle IA
Aucun.

## Sous-workflows appelés
- Equipe - Validation notes (`7NeZSKB3GXm3tXOB`) via node "Valider une note" (Execute Workflow, `waitForSubWorkflow: false`, transmet l'update Telegram complet)

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Un bot Telegram n'a qu'un seul webhook : ce workflow est le point d'entrée unique du bot et doit rester actif pour que "Equipe - Validation notes" reçoive ses callbacks.
- Appel du sous-workflow sans attente (`waitForSubWorkflow: false`) : ses erreurs sont invisibles ici.
- Identifiant du dossier Drive en dur ; nom de fichier toujours en `.jpg` même pour un document image PNG/WebP ; `mimeType` forcé en `image/jpeg`.
- "Telecharger photo" et "Ranger photo (Drive)" en `continueRegularOutput` : si l'upload échoue, le message est quand même enregistré avec un `photo_drive_id` vide ou erroné (l'expression `$json.file_id ? '' : ($json.id || '')` dépend de la forme de l'item d'erreur).
- Traite uniquement le premier item (`$('Message du groupe').first()`) : adapté à un trigger (1 update par exécution), mais fragile si rejoué en lot.
- Pas de déduplication sur `tg_message_id` : une relivraison Telegram crée un doublon dans `equipe_messages`.
- Vocaux, vidéos, documents non-image : seul le type est noté, le contenu n'est pas archivé ; texte tronqué à 4 000 caractères.
- Le nom de la table des utilisateurs (`MAaqIFX2KBiCvHFa`) n'apparaît nulle part dans le workflow ; un inconnu est enregistré sous son prénom Telegram.
