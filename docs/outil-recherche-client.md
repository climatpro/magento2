# Outil - Recherche client

| | |
|---|---|
| ID n8n | `FHVtoHPBvB59ExMT` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrée `nom`) |
| Export | `workflows/outil-recherche-client.json` |

## Rôle
Outil du bot : recherche approximative de clients Interfast par nom et renvoie pour chacun (10 max) le `client_id`, l'adresse et les téléphones ; les fournisseurs sont exclus. Lecture seule.

## Services appelés
- Interfast (recherche CRM par nom) — uniquement via le sous-workflow "Interfast - Lecture" (op `client_recherche`)
- Data Tables : aucune

## Modèle IA
Aucun

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via node `Chercher client`

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « recherche_client »

## Points fragiles
- `onError: continueRegularOutput` : une erreur Interfast devient "Aucun client trouve pour ce nom.".
- Résultats tronqués à 10 sans indication du total.
- Aucun contrôle de rôle : tout appelant obtient les téléphones des clients.
- Seul le filtre `category !== 'supplier'` écarte les fournisseurs.
