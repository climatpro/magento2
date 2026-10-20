# Tri scans Brother

| | |
|---|---|
| ID n8n | `u0mZuNjuW4LW54vI` |
| Actif | non |
| Déclencheur | Google Drive Trigger « Trigger - Drive Watch » : fichier créé dans le dossier `1RiEj8rvkgx9GR-ULdvvnrwL1lMYvUO0d` (scans du copieur Brother), polling chaque minute |
| Export | `workflows/tri-scans-brother.json` |

## Rôle
Classe automatiquement les PDF scannés : téléchargement, hash de déduplication (Sheet `DEDUP_SCANS_BROTHER`), classification par Gemini (facture fournisseur vs autre + sous-type URSSAF/impôts/attestations/relevés/paie/RIB, date, émetteur, objet, montants, confiance).
Confiance < 0,85 → dossier « A-trier » ; facture → dossier mensuel `depenses <mois> <année>` du Drive partagé « DEPENSES FIMAREX » + ligne dans le Sheet de suivi factures ; autre → `depenses <mois>/administratif/<sous-type>`. Dans les deux cas, trace dans le Sheet de dédup.

## Services appelés
- Google Drive (credential « Google Drive account 2 » `54fd9ApHaDydoOJv`) : trigger, download, move (dossiers Doublons `1O9FObKt6aRNcXLUiOXEPrG3qSU3EDIMj`, A-trier `1vakJ22BlyeToQn-8RdykHanAOOtmCSWD`, dossiers mensuels), recherche/création de dossiers dans le Drive partagé `0AAse2-rbb-B9Uk9PVA` (« DEPENSES FIMAREX »), update (renommage).
- Google Sheets (credential « Google Sheets account 2 » `sI64hm3ZUMyRS8JL`) : `DEDUP_SCANS_BROTHER` (`1MCpIeHZpRLekJ22We9rG94JdJQIHcGzGLttA0c-ow60`) lecture + append ; Sheet de suivi factures Interfast `15wNATo6gpL-rDyTdPjaQemLx8GXgd_4TtFbJtfk-tVY` feuille « Sheet1 » appendOrUpdate (Libellé, Date facture, Montant TTC, Montant HT).
- Google Gemini API — HTTP Request `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` (PDF inline base64, `responseSchema` JSON, temperature 0), credential « Header Auth account » (`ZcL2hYc3F444ZEyn`).
- Data Tables n8n : aucune.

## Modèle IA
Google `gemini-2.5-flash`, node « Call Gemini » (HTTP Request) : classification et extraction des métadonnées du scan.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- **Déduplication cassée** : « Lookup Dedup » lit toute la feuille sans filtre et « IF - Is Duplicate? » teste seulement `Hash MD5 notEmpty` sur chaque ligne lue, sans jamais comparer au hash calculé → dès que la feuille contient une ligne, tout nouveau scan est traité comme doublon (et « Move to Doublons » s'exécute pour chaque ligne). Le « MD5 » est en réalité un cyrb53 (53 bits).
- « Rename Facture » / « Rename Autre » : opération `update` avec `options: {}` → aucun nouveau nom transmis, le fichier n'est pas renommé (`newFilename` calculé mais inutilisé).
- « List Autre Monthly » : `queryString` commence par `==` (double `=`) → requête Drive malformée.
- Nom de feuille « Sheet1 » pour le Sheet de suivi factures alors que la feuille réelle s'appelle « Feuille 1 » (cf. workflow Gmail v3) ; même incohérence possible sur `DEDUP_SCANS_BROTHER` (lecture par gid, append par nom « Sheet1 »).
- Les nodes « move » ciblent `driveId: My Drive` alors que les dossiers sont dans le Drive partagé `0AAse2-rbb-B9Uk9PVA`.
- « Parse Gemini Response » : `new Date(data.doc_date)` sur une chaîne libre (schéma sans format) → `throw` « Date invalide » qui bloque le fichier dans le dossier d'entrée ; aucune branche d'erreur, aucune alerte.
- `pdfBase64` conservé dans le `json` de chaque item (mémoire) ; IDs de dossiers, du Drive partagé et seuil 0,85 en dur.
- Doublon fonctionnel avec « Factures Gmail → Google Drive v3 » (même Sheet de suivi, arborescence différente : `depenses octobre 2026` vs `DEPENSES OCTOBRE 2026`, Drive « FIMAREX » vs dossier `1qiVL5cq9nCdEFGMCOIsZsiKJEQJdTQrD`).
- Inactif depuis sa dernière modification (2026-10-07) : vraisemblablement abandonné, à archiver ou corriger.
