# Archives factures - Notes Interfast + Pilotage

| | |
|---|---|
| ID n8n | `rUH5kAAMybl4Z9mk` |
| Actif | non |
| Déclencheur | 3 Manual Triggers indépendants : "Lancer" (écriture des notes), "Reformater les notes" (réécriture v2), "Calculer pilotage" (statistiques) |
| Export | `workflows/archives-factures-notes-interfast-pilotage.json` |

## Rôle
Branche 1 : pour chaque client de "Correspondance_Interfast" validé (`decision_laurent = OK`, ou statut `sur` sans décision), construit une note "Historique ClimatPro avant Interfast" (liste des factures avec lien Drive, matériel connu, sans montant) et la POSTe dans la fiche client Interfast, puis marque `note_interfast` dans le Sheet. Branche 2 : retrouve les notes déjà posées et les réécrit (PUT) au nouveau format (texte ou HTML test). Branche 3 : calcule des statistiques (CA, paniers médians, types, saisonnalité, prix par unité/kW) à partir de l'index.

## Services appelés
- Interfast — direct via HTTP Request, credential "Interfast API" (`GgJ5wsyGIUSWY0cN`) :
  - POST /v1/client/{id}/activities/notes (ÉCRITURE de notes client)
  - GET /v1/client/{id}/activities?page=0&size=50 (lecture du fil)
  - PUT /v1/client/{id}/activities/notes/{noteId} (RÉÉCRITURE de note)
- Google Sheets (doc `1qk6RULDlOTXvfAnrbqCh6MAnFK2Kp1-f6v07DUheIXg`) : lecture "Correspondance_Interfast" et "Feuille 1", update "Correspondance_Interfast" (clé `cle`, colonne `note_interfast`) — credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Seul workflow de la série qui ÉCRIT dans Interfast (notes client) : la protection contre les doublons repose uniquement sur la colonne `note_interfast` du Sheet ; si l'update Sheet échoue après le POST, la note sera reposée à la relance.
- HTTP en `neverError` + test du `statusCode` dans le code : les erreurs sont notées "ERREUR xxx" dans le Sheet mais pas remontées.
- "Lire fil Interfast" ne lit que page 0 / size 50 : pour un client avec beaucoup d'activités, la note à reformater n'est pas retrouvée (silencieusement ignorée).
- "Choisir note" et "Resultat 2" alignent les items par index (`src[i]`) : tout item HTTP manquant décale les résultats.
- Listes `MODE_HTML = ['NAVIGAIR']` et `EXCLURE = ['FREDERIC M FRANCE - LE CANNET']` codées en dur (clés de test).
- `LOT = 2000` en dur ; batching 1 req / 400 ms.
- Node "Bilan" produit un résumé qui n'est envoyé nulle part (sortie morte).
- Liens Drive dans les notes : privés, dépendent du partage du dossier Archives.
- Branche "Stats" manipule le CA historique (donnée sensible) ; résultat uniquement visible dans l'exécution.
- Description n8n tronquée/incomplète ("…par lots. Marque la colonne note_interfast.") ; ID Sheet en dur dans 7 nodes.
