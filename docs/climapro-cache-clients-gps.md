# Climapro - Cache clients GPS

| | |
|---|---|
| ID n8n | `xip9MMQ4aXhfpQ67` |
| Actif | oui |
| Déclencheur | cron quotidien 3h07 Europe/Paris (node "Chaque nuit 3h") |
| Export | `workflows/climapro-cache-clients-gps.json` |

## Rôle
Chaque nuit, relit toutes les fiches clients/prospects Interfast ayant une adresse (fournisseurs exclus), géocode via l'IGN celles qui sont nouvelles ou dont l'adresse/le nom a changé, et met à jour la table `clients_gps`.
Cette table sert à "Climapro - Mémos vocaux" pour proposer le client le plus proche du lieu d'un mémo.

## Services appelés
- Interfast (GET /v1/crm/search, 40 pages × 100, `archived=false`) — direct via HTTP Request, credential "Interfast API" (`GgJ5wsyGIUSWY0cN`)
- IGN Géoplateforme (GET https://data.geopf.fr/geocodage/search, gratuit, sans credential) — appelé depuis le code du node "Geocoder les nouveaux" (`this.helpers.httpRequest`, 4 requêtes en parallèle, 2 essais)
- Data Tables n8n : `clients_gps` (`xrWuLpFXi8qQWU86`) — lecture (node "Cache actuel") et upsert sur `client_id` (node "Enregistrer")

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Pagination limitée en dur : 40 pages × 100 = 4 000 fiches maximum ; au-delà, les clients les plus récents ne sont jamais géocodés.
- `onError: continueRegularOutput` sur l'appel Interfast : une page en erreur est silencieusement ignorée (clients manquants sans alerte).
- Plafond de 1 500 géocodages par nuit (`slice(0, 1500)`) ; un échec IGN après 2 essais retourne `null` et la fiche est simplement sautée, sans journalisation.
- Les fiches sans résultat IGN sont stockées avec `lat: null`, donc re-géocodées chaque nuit (charge inutile, jamais résolue).
- Le géocodage se fait dans un node Code (pas de credential, pas de rate-limit configurable) ; dépend de la disponibilité et des quotas de data.geopf.fr.
- `executionTimeout: 900` s : une nuit avec beaucoup de nouveaux clients peut dépasser le délai et laisser la table partiellement mise à jour.
- La table n'est jamais purgée : les clients archivés/supprimés dans Interfast restent dans `clients_gps`.
- Le nom du node ("Chaque nuit 3h") ne correspond pas exactement à l'heure réelle (3h07).
