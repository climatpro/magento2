# Outil - Clients sans entretien

| | |
|---|---|
| ID n8n | `NvBI84JhjfoUH5FZ` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `villes`, `mois_min`, `client_id`, `rayon_km`) |
| Export | `workflows/outil-clients-sans-entretien.json` |

## Rôle
Outil du bot : liste les clients dont ClimatPro a posé la clim et qui n'ont pas eu d'entretien depuis X mois (défaut 12), hors contrat. Filtre par villes ou par rayon (défaut 3 km) autour d'un client, 25 premiers résultats. Ne calcule rien : lit une table pré-calculée chaque nuit par un autre workflow.

## Services appelés
- Data Table n8n lue : `wdM1D4E3ZOAmhvoy` (nom déduit de la description : `clients_sans_entretien`, colonnes client_id, nom, ville, adresse, lat, lon, mois, install_le, install_objet, dernier_entretien, maj)
- Data Table n8n lue : `xrWuLpFXi8qQWU86` (nom non visible ; géolocalisation des clients : client_id, lat, lon, nom), node « Centre »

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « clients_sans_entretien »

## Points fragiles
- Les deux Data Tables sont référencées par id sans `cachedResultName` : impossible de connaître leur nom exact depuis l'export.
- Dépend d'un workflow nocturne (non identifié ici) qui alimente la table ; si ce workflow s'arrête, l'outil renvoie des données périmées sans le dire (seule la colonne `maj` la plus récente est gardée).
- `returnAll: true` sur toute la table à chaque appel : coût croissant avec le nombre de clients.
- Node « Centre » en `onError: continueRegularOutput` : un client_id inconnu ou sans coordonnées désactive silencieusement le filtre par rayon.
- Limite fixe de 25 lignes affichées, rayon et mois par défaut en dur (3 km, 12 mois).
