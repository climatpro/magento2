# Archives factures - Extraction index

| | |
|---|---|
| ID n8n | `FmosA6XoUHWvgDA5` |
| Actif | non |
| Déclencheur | cron Schedule Trigger "Toutes les 30 min" (interval 30 minutes, timezone Europe/Paris) |
| Export | `workflows/archives-factures-extraction-index.json` |

## Rôle
Indexe les factures PDF d'avant Interfast (FA/AV, numéros < 14146) copiées du NAS dans Drive > Archives-Factures-ClimatPro : liste dossiers et PDF via l'API Drive, dédoublonne par numéro, saute les déjà indexées, puis pour chaque facture d'un lot (900) télécharge le PDF, le fait lire par Claude Haiku et écrit une ligne (date, client, ville, intervention, matériel, montants) dans "Feuille 1" du Sheet Index-Factures-ClimatPro.

## Services appelés
- Google Drive API (GET https://www.googleapis.com/drive/v3/files, requêtes `q` sur dossiers puis PDF, pagination pageToken max 50 pages × 1000) — HTTP Request avec credential prédéfinie "Google Drive account 2" (`54fd9ApHaDydoOJv`)
- Google Drive (node natif, download fichier binaire) — même credential
- Anthropic (node `@n8n/n8n-nodes-langchain.anthropic`, resource document / analyze, PDF binaire) — credential "Anthropic account" (`GfYoRA9p0AV4WXlD`)
- Google Sheets (doc `1qk6RULDlOTXvfAnrbqCh6MAnFK2Kp1-f6v07DUheIXg`) : lecture puis append "Feuille 1" — credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Data Tables n8n : aucune

## Modèle IA
Anthropic `claude-haiku-4-5-20251001` dans le node "Extraire (Haiku)" : lit le PDF de facture et renvoie un JSON structuré (type_doc, dates, client, ville, CP, type_intervention, marque, modèle, puissance, montants HT/TTC, description), max 800 tokens.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Fenêtre Drive figée en dur dans "Parametres" (`createdTime` entre 2026-10-16T18:00 et 2026-10-17T09:00) : ne verra jamais des fichiers copiés plus tard.
- Si réactivé : cron toutes les 30 min avec lot = 900 et appels Haiku séquentiels → exécutions qui se chevauchent, doublons possibles dans l'index (la déduplication `dejaFaits` n'est lue qu'au départ).
- ID du dossier racine Drive (`18foeaN7yoGBfRc9USHJcp1ULzHUBIlgK`), seuil `PREMIER_INTERFAST = 14146` et ID du Sheet en dur dans le code.
- Regex de détection du numéro `^\s*(FA|AV)[\s\-_]*(\d{2,6})` et filtre Drive `name contains 'FA' or 'AV'` : fichiers nommés autrement ignorés ; choix du "meilleur" doublon par longueur de nom / absence de "PAYEE".
- "Telecharger PDF" et "Extraire (Haiku)" en `onError: continueRegularOutput` : une facture en échec produit une ligne `statut = erreur_lecture` qui bloque ensuite sa reprise (le numéro est considéré déjà fait).
- Modèle `claude-haiku-4-5-20251001` (génération précédente, les autres workflows utilisent `claude-haiku-5-5`) et credential Anthropic distincte ("Anthropic account" vs "Anthropic account 2").
- `saveDataSuccessExecution: none` : aucune trace des exécutions réussies pour audit.
- Code "Preparer lot" dupliqué quasi à l'identique dans "Archives factures - Liste à traiter".
