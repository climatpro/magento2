# Claude - SCAN vers MAIL pour PJ

| | |
|---|---|
| ID n8n | `qVSGol88bMMOGOKf` |
| Actif | non |
| Déclencheur | webhook POST /webhook/claude-envoi-fichier (node "Webhook", aucune authentification) |
| Export | `workflows/claude-scan-vers-mail-pour-pj.json` |

## Rôle
Permet à Claude d'envoyer un fichier Google Drive (un scan) en pièce jointe d'un mail Gmail : télécharge le fichier `fileId` depuis Drive puis, selon `mode`, envoie le mail directement (`send`) ou crée un brouillon Gmail (avec `threadId` optionnel).
Corps attendu : `fileId`, `mode`, `to`, `subject`, `body`, `threadId`.

## Services appelés
- Google Drive (node "Drive - Telecharger", téléchargement par id) — credential "Google Drive account 2" (`54fd9ApHaDydoOJv`)
- Gmail (node "Gmail - Envoyer" : envoi texte ; node "Gmail - Brouillon" : création de brouillon avec PJ `data`) — credential "Gmail account" (`QkVJEJmojKI4yW63`)
- Data Tables n8n : aucune.

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Webhook public sans aucune authentification : quiconque connaît l'URL peut faire envoyer un mail depuis la boîte Gmail de ClimatPro avec n'importe quel fichier Drive accessible au compte.
- Workflow inactif (`active: false`) : l'URL de production ne répond pas tant qu'il n'est pas publié.
- Node "Gmail - Envoyer" : la pièce jointe est déclarée avec un objet vide (`attachmentsBinary: [{}]`, aucune propriété binaire) ; en mode `send`, le mail part probablement sans la PJ. Le brouillon, lui, référence bien `data`.
- Aucune validation des champs du corps (`to`, `subject`, `fileId`) ni `onError` : un `fileId` inconnu fait échouer l'exécution avec une réponse d'erreur brute.
- Pas de description de workflow ; `binaryMode: separate` dans les settings (comportement binaire spécifique à vérifier à la migration).
- Le mode d'envoi est comparé en « loose » et insensible à la casse ; toute valeur autre que `send` crée un brouillon (pas de message d'erreur).
