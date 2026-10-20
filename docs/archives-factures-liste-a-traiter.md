# Archives factures - Liste à traiter

| | |
|---|---|
| ID n8n | `TVISDTqWACLV6OIw` |
| Actif | non |
| Déclencheur | Schedule Trigger "Manuel (planning inactif)" avec cron `0 3 1 1 *` (1er janvier 3h, de fait lancé à la main) |
| Export | `workflows/archives-factures-liste-a-traiter.json` |

## Rôle
Établit la liste des factures d'archives (FA/AV < 14146 dans Drive > Archives-Factures-ClimatPro) qui restent à indexer : dédoublonnées par numéro, hors numéros Interfast, hors numéros déjà présents dans "Feuille 1", et l'écrit dans l'onglet "A_traiter" du Sheet Index-Factures-ClimatPro. Outil de contrôle, sans IA.

## Services appelés
- Google Drive API (GET https://www.googleapis.com/drive/v3/files, dossiers puis PDF, pagination max 50 pages × 1000) — HTTP Request avec credential prédéfinie "Google Drive account 2" (`54fd9ApHaDydoOJv`)
- Google Sheets (doc `1qk6RULDlOTXvfAnrbqCh6MAnFK2Kp1-f6v07DUheIXg`) : lecture "Feuille 1", append "A_traiter" — credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Déclencheur = cron `0 3 1 1 *` : si le workflow est activé par erreur, il tournera chaque 1er janvier à 3h.
- Append dans "A_traiter" sans vidage ni déduplication préalable : chaque exécution ré-ajoute toute la liste restante.
- Fenêtre Drive figée (`createdTime` 2026-10-16T18:00 → 2026-10-17T09:00), ID du dossier racine, seuil 14146 et ID Sheet en dur.
- Paramètre `lot` (99999) défini mais jamais utilisé par le code.
- Doublon fonctionnel de la partie "Inventaire" de "Archives factures - Extraction index" (même code, même regex `^(FA|AV)[\s\-_]*(\d{2,6})`).
