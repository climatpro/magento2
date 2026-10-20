# Equipe - Fil (tableau)

| | |
|---|---|
| ID n8n | `2vzK7iVCvfsZLzhE` |
| Actif | oui |
| Déclencheur | 3 webhooks : GET /webhook/equipe-fil (lecture du fil), POST /webhook/equipe-envoyer (publication), GET /webhook/equipe-photo (photo Drive) |
| Export | `workflows/equipe-fil-tableau.json` |

## Rôle
Backend du « Fil équipe » du tableau de bord web : renvoie les 40 derniers messages du groupe Telegram (stockés en Data Table), publie un texte et/ou une photo dans le groupe au nom du membre authentifié par jeton signé HMAC (`fil.v1.<telegram_id>.<exp>`), et sert les photos Drive via un lien signé (`photo.v1.<id>`).

## Services appelés
- Telegram — sendMessage / sendPhoto dans le groupe équipe (chat_id lu dans la Data Table), credential « Bot Telegram - groupe climatpro » (`gQjbmvis03Oi1VtD`)
- Google Drive — téléchargement d'une photo par id (GET /equipe-photo) et dépôt des photos envoyées depuis le tableau dans le dossier `1B7lTbisc88kRcVsQ5QX8LdZ0BeWhX2NE`, credential « Google Drive account 2 » (`54fd9ApHaDydoOJv`)
- Data Tables n8n : secrets `ZS80JIsncc2f3ZED` (lecture, colonne `cookie_secret`) ; accès/membres `D0StwthqUQF0nV7Z` (lecture : telegram_id, nom, actif) ; equipe_messages `JtuuDgi9yHe84lHj` (lecture des 40 derniers, recherche du chat_id, insertion des envois)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- SHA-256/HMAC réimplémentés en JavaScript pur et dupliqués dans 3 nodes Code (Verifier fil / Verifier envoi / Verifier photo) : toute correction doit être faite 3 fois.
- Le secret de signature (`cookie_secret`) vit dans une Data Table, pas dans un credential n8n ; le fil répond 403 si la table est vide ou le secret < 32 caractères.
- CORS `Access-Control-Allow-Origin: *` sur les 3 webhooks ; seule la signature HMAC protège.
- Le chat_id du groupe est déduit de la dernière ligne `source = telegram` de la table : si aucune ligne n'existe, « Trouver le groupe » ne renvoie rien et l'envoi échoue sans réponse HTTP.
- Aucun `onError` sur les nodes Telegram et Google Drive : en cas d'échec, le webhook ne reçoit pas de réponse (timeout côté tableau).
- URL du webhook photo en dur dans le code (`https://n8n.climatpro.fr/webhook/equipe-photo`) et id du dossier Drive en dur.
- Photo acceptée en base64 jusqu'à 8 000 000 caractères dans le corps du POST : dépend de la limite de payload de l'instance n8n.
- Lecture limitée aux 40 dernières lignes (tri `id DESC`) ; le paramètre `apres` filtre seulement dans ces 40.
- Cache-Control 7 jours sur les photos servies ; une photo supprimée de Drive reste en cache navigateur.
