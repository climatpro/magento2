# Prix achat fournisseurs - Extraction factures (HAC, Econology)

| | |
|---|---|
| ID n8n | `eIm19cWQyQ7RRshF` |
| Actif | oui |
| Déclencheur | cron "tous les jours 3h" (Schedule Trigger, node « Chaque nuit 3h ») |
| Export | `workflows/prix-achat-fournisseurs-extraction-factures-hac-econology.json` |

## Rôle
Chaque nuit, liste sur Google Drive les factures PDF des fournisseurs HAC (Hitachi) et Econology, écarte celles déjà traitées (colonne `file_id` du Sheet), puis traite un lot de 40 : téléchargement du PDF, extraction des lignes article par Claude Haiku, ajout des prix unitaires nets HT dans le Sheet « PRIX ACHAT ClimatPro ».
Résultat : une ligne par article (référence, désignation, catégorie, quantité, prix net HT, remise) + lignes de statut pour les PDF non exploitables (`erreur_lecture`, `pas_facture_fournisseur`, `avoir`, `aucune_ligne`).

## Services appelés
- Google Drive API — HTTP Request `GET https://www.googleapis.com/drive/v3/files` (recherche fullText « Hitachi Cooling » / nom « Econology », tous les Drives, pagination par `pageToken`), credential « Google Drive account 2 » (`54fd9ApHaDydoOJv`) ; node Google Drive « Telecharger PDF » (download) même credential.
- Google Sheets — document `1jemEEyKe-L3xdL4TuDmkPTG8cqbWRWvXLAy36iIBehU`, feuille gid `2035616917` : lecture complète (« Lire prix ») puis append (« Ecrire prix », autoMap, USER_ENTERED), credential « Google Sheets account » (`fKAETwT6ij09juV8`).
- Anthropic — node « Extraire lignes (Haiku) » (document → analyze), credential « Anthropic account » (`GfYoRA9p0AV4WXlD`).
- Data Tables n8n : aucune.

## Modèle IA
Anthropic `claude-haiku-4-5-20251001`, node « Extraire lignes (Haiku) » (`@n8n/n8n-nodes-langchain.anthropic`, maxTokens 4000) : lit le PDF et renvoie un JSON (fournisseur, type_doc, numéro, date, lignes article avec prix net HT).

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- « Telecharger PDF » et « Extraire lignes (Haiku) » sont en `onError: continueRegularOutput` : un échec de téléchargement ou d'appel IA produit quand même une ligne `erreur_lecture` avec le `file_id`, donc le fichier est considéré comme traité et ne sera **jamais retenté**.
- `maxTokens: 4000` : une facture longue peut donner un JSON tronqué → `erreur_lecture` définitive (même effet).
- Pagination Drive limitée à 20 pages × 1000 fichiers ; filtre `modifiedTime > 2024-01-01` et liste d'exclusions par nom (`Notice`, `SET FREE`, `brochure`, `Attestation`, `Rapport`) en dur dans la requête — un nouveau type de document HAC non facture passera à l'IA.
- `fullText contains 'Hitachi Cooling'` repose sur l'indexation Drive (OCR) : résultats non déterministes.
- Détection des frais par regex (`transport|frais de port|port |livraison|eco.?contribution|deee|^f\.f`) et liste `REF_FRAIS` en dur : une ligne article contenant « port » dans la désignation est écartée.
- Repli fournisseur par regex sur le nom de fichier (`/econology/i` sinon « HAC ») si l'IA répond « autre ».
- Aucune déduplication par numéro de facture : un même PDF présent sous deux `file_id` (copie) est extrait deux fois.
- « Lire prix » relit toute la feuille à chaque exécution (croissance linéaire) ; IDs du Sheet et de la feuille en dur.
- Lot de 40 / nuit sans alerte : aucun message (Telegram ou autre) en cas d'erreur ou de backlog ; `restants_avant_lot` n'est pas exploité.
- Code mort : test `d.est_facture_hac === false` (ancienne clé de prompt).
- Pas de node d'alerte, `settings` sans `errorWorkflow`.
