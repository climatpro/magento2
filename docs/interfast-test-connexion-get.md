# Interfast — Test connexion GET

| | |
|---|---|
| ID n8n | `sNz4QD6CaaipqSyT` |
| Actif | non |
| Déclencheur | manuel (bouton « Execute workflow ») |
| Export | `workflows/interfast-test-connexion-get.json` |

## Rôle
Workflow de test manuel : un seul appel GET /v1/events?page=1&count=1 pour vérifier que le credential « Interfast API » fonctionne. Aucun traitement.

## Services appelés
- Interfast — direct via HTTP Request GET /v1/events (page 1, 1 résultat), credential « Interfast API » (`GgJ5wsyGIUSWY0cN`)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow de test sans description, inactif, jamais publié : candidat à l'archivage.
- Réponse brute Interfast non filtrée (prix d'achat, données perso visibles dans l'exécution).
- `callerPolicy: workflowsFromSameOwner` dans les settings, sans trigger de sous-workflow (sans effet).
