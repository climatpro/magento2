# 📧 Factures Gmail → Google Drive (ClimatPro) v3 - recup drive

| | |
|---|---|
| ID n8n | `MdI9Kjjo1itBbbXC` |
| Actif | oui |
| Déclencheur | Gmail Trigger (polling chaque minute, label INBOX, requête `in:inbox has:attachment filename:pdf -in:draft {to:scan@climatpro.fr deliveredto:scan@climatpro.fr (-in:sent -from:climatpro.fr)}`, pièces jointes téléchargées) |
| Export | `workflows/factures-gmail-google-drive-climatpro-v3-recup-drive.json` |

## Rôle
Pour chaque e-mail reçu avec PDF (adressé à `scan@climatpro.fr` ou venant de l'extérieur), chaque pièce jointe PDF est analysée par un LLM : facture ou avoir fournisseur ? émetteur, objet, montant TTC, date, numéro. Les documents émis par ClimatPro (FA1xxxx) sont rejetés.
Les factures sont renvoyées sur Drive dans `DEPENSES <MOIS> <ANNÉE>` (créé si absent, sous `1qiVL5cq9nCdEFGMCOIsZsiKJEQJdTQrD`) sous le nom `Fournisseur_Objet_Montant EUR.pdf`, une ligne est upsertée (clé `fournisseur|numéro`) dans le Sheet de suivi factures, puis l'e-mail est marqué lu.

## Services appelés
- Gmail — trigger (credential « Gmail account » `QkVJEJmojKI4yW63`) et HTTP Request `POST https://gmail.googleapis.com/gmail/v1/users/me/messages/{id}/modify` (retrait du label UNREAD), même credential.
- Anthropic API (brouillon courant) — HTTP Request `POST https://api.anthropic.com/v1/messages` (node « 🤖 Claude Haiku - Analyser la facture », PDF en `document` base64, timeout 120 s), credential « Anthropic account » (`GfYoRA9p0AV4WXlD`).
- Google Gemini API (version **publiée**) — HTTP Request `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` (node « 🤖 Gemini - Analyser la facture »), credential « Query Auth account » (`Kzyo5YdstGMrLjn6`, clé API en query string).
- Google Drive — HTTP Request `GET/POST https://www.googleapis.com/drive/v3/files` (recherche / création du dossier du mois, tous Drives) et node Google Drive upload, credential « Google Drive account 2 » (`54fd9ApHaDydoOJv`).
- Google Sheets — document `15wNATo6gpL-rDyTdPjaQemLx8GXgd_4TtFbJtfk-tVY` feuille « Feuille 1 » (gid 0), appendOrUpdate sur colonne « Clé » (Libellé, Date facture, Montant TTC, N° facture, Client, Email ID, Fournisseur, Lien Drive), credential « Google Sheets account » (`fKAETwT6ij09juV8`).
- Data Tables n8n : aucune.

## Modèle IA
- Brouillon (versionId `f56baab1…`) : Anthropic `claude-haiku-5-5` (body construit dans « 🔍 Extraire les PDFs », appel dans « 🤖 Claude Haiku - Analyser la facture ») : classification facture/avoir et extraction des champs.
- Version active publiée (activeVersionId `2d359378…`, `sameAsDraft: false`) : Google `gemini-2.5-flash` (node « 🤖 Gemini - Analyser la facture »), même prompt.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- **Brouillon ≠ version publiée** : le passage de Gemini à Claude Haiku (13/10/2026) n'est pas publié ; en production c'est encore Gemini 2.5 Flash avec clé API en **query string** (credential httpQueryAuth) qui tourne. À publier ou à annuler explicitement.
- Le brouillon utilise `claude-haiku-5-5` (identifiant valide, génération actuelle) ; c'est la publication qui manque, pas le modèle.
- Un e-mail dont aucune pièce jointe n'est reconnue comme facture (ou en erreur de parsing LLM) n'est jamais marqué lu ni tracé : aucune ligne « rejet » dans le Sheet, aucune alerte ; en cas d'échec d'upload le message n'est pas retraité (le trigger ne repasse pas sur les anciens messages).
- Si le LLM ne renvoie pas de date, `date_facture` = date du jour → classement dans le mauvais mois ; `montant_ttc` par défaut `0,00` et conservé dans le nom de fichier.
- Clé de dédup `fournisseur|numéro` dépend de la stabilité du nom court renvoyé par le LLM (« EDF » vs « EDF SA ») ; sans numéro, clé = id e-mail + nom de PJ (pas de dédup inter-mails).
- Recherche de dossier par `name = '{{ folderName }}'` non échappé, prend le premier résultat ; dossier parent `1qiVL5cq9nCdEFGMCOIsZsiKJEQJdTQrD` et ID du Sheet en dur ; upload sur `driveId: My Drive`.
- Pairing `$('📧 Gmail - Nouveaux emails').item` depuis « Marquer comme lu » après plusieurs Code nodes avec `pairedItem` recalculés : fragile en cas de plusieurs PDF par e-mail.
- PDF encodé en base64 dans une chaîne JSON (`claudeBodyString`) stockée dans `json` : lourd en mémoire pour les gros scans ; `max_tokens: 1024`.
- Colonnes « Montant HT » et « Statut » du Sheet jamais renseignées ; « Marquer comme lu » en `onError: continueRegularOutput`.
- Doublon fonctionnel partiel avec « Tri scans Brother » (même Sheet de suivi).
