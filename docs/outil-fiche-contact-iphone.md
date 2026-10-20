# Outil - Fiche contact iPhone

| | |
|---|---|
| ID n8n | `oabRTfuN2I91bsfK` |
| Actif | oui |
| Déclencheur | webhook POST `/webhook/fiche-contact-iphone-k7q2` (réponse = JSON du dernier node) |
| Export | `workflows/outil-fiche-contact-iphone.json` |

## Rôle
Reçoit une fiche client en POST (prenom, nom, societe, telephone, email, adresse, ville, code_postal, note), construit une vCard 3.0 et l'envoie en pièce jointe Telegram à Laurent (chat_id 1857340429) pour ajout direct aux Contacts iPhone.

## Services appelés
- Telegram Bot API — POST `https://api.telegram.org/bot<token>/sendDocument` (multipart, fichier .vcf) via HTTP Request sans credential n8n (token injecté dans l'URL)
- Data Table n8n `ZS80JIsncc2f3ZED` (lecture, 1 ligne, colonne `telegram_bot_token` ; nom non visible dans le node, c'est la table "secrets" du tableau de bord)

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Webhook public sans aucune authentification : seule l'obscurité du chemin (`-k7q2`) protège ; quiconque connaît l'URL peut envoyer des fichiers sur le Telegram de Laurent.
- `chat_id` Telegram (1857340429) en dur dans le code.
- Token du bot placé dans l'URL de la requête HTTP : il apparaît en clair dans les données d'exécution n8n.
- Lecture de la Data Table avec `limit 1` sans filtre : dépend de l'ordre des lignes.
- Description du workflow parle de `sendContact` (carte native) alors que le code envoie un fichier vCard via `sendDocument`.
- Aucun `onError` : une erreur Telegram renvoie une erreur HTTP à l'appelant.
- Téléphone normalisé uniquement pour les numéros français à 10 chiffres ; e-mail non échappé dans la vCard.
