# Archives factures - Correspondance Interfast

| | |
|---|---|
| ID n8n | `8GN2GvWHNhjTrew5` |
| Actif | non |
| Déclencheur | manuel (node "Lancer", Manual Trigger) |
| Export | `workflows/archives-factures-correspondance-interfast.json` |

## Rôle
Rapproche les clients des anciennes factures (onglet "Feuille 1" du Sheet Index-Factures-ClimatPro) avec les fiches clients Interfast, par heuristique de noms + code postal/ville, et ajoute les groupes nouveaux dans l'onglet "Correspondance_Interfast" avec un statut `sur` / `a_verifier` / `absent` pour validation par Laurent. Lecture seule Interfast, aucune IA, relançable (ne réécrit jamais une clé déjà présente).

## Services appelés
- Interfast (GET /v1/crm/search, pages 0-31 non archivés + 0-11 archivés, size 100) — direct via HTTP Request, credential "Interfast API" (httpHeaderAuth `GgJ5wsyGIUSWY0cN`)
- Google Sheets (doc `1qk6RULDlOTXvfAnrbqCh6MAnFK2Kp1-f6v07DUheIXg`) : lecture "Feuille 1" (index factures), lecture puis append "Correspondance_Interfast" — credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Pagination Interfast figée dans le code : 32 pages × 100 clients actifs + 12 pages × 100 archivés (node "Pages Interfast"). Au-delà de 3 200 clients actifs, les derniers sont ignorés silencieusement.
- HTTP "Clients Interfast" en `onError: continueRegularOutput` : une page en erreur passe inaperçue (seul garde-fou : exception si moins de 500 clients au total).
- Rapprochement purement heuristique (tokens, Levenshtein 1, préfixes 5 lettres, mots "rares" < 8 occurrences, bonus CP/ville) : faux positifs possibles classés `sur` si même nom exact + même ville.
- ID du Google Sheet et noms d'onglets en dur dans 4 nodes ; append en `autoMapInputData` (dépend de l'ordre/nom des colonnes du Sheet).
- Regroupement des factures par `dossier_client` ; dossiers "ANCIENS CLIENTS"/"(racine)" regroupés par nom de client brut : variations d'orthographe créent des groupes distincts.
- Pas de déclencheur automatique : usage one-shot, dépend de l'exécution préalable de "Archives factures - Extraction index".
