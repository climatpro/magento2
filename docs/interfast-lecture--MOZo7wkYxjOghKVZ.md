# Interfast - Lecture

| | |
|---|---|
| ID n8n | `MOZo7wkYxjOghKVZ` |
| Actif | non |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrées `path` string et `query` object) |
| Export | `workflows/interfast-lecture--MOZo7wkYxjOghKVZ.json` |

## Rôle
Première version du sous-workflow d'accès en lecture seule à Interfast : l'appelant fournit un chemin GET ; il est vérifié contre une liste blanche de regex, appelé avec le credential Interfast, puis les champs sensibles sont supprimés de la réponse. Sortie `{ ok, path, data }`.

## Services appelés
- Interfast — direct via HTTP Request, credential « Interfast API » (`GgJ5wsyGIUSWY0cN`) : GET sur /v1/events, /v1/events/to-plan, /v1/intervention/{id}, /v1/client/{id}, /v1/client/{id}/events, /v1/billing/quotations, /v1/billing/quotations/{uuid}

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Brief 18h](bot-brief-18h--Lw8Dv81qmxIMwXVI.md) (inactif) — node « Interfast - recherche devis »
- [Bot - Brief 18h](bot-brief-18h--Lw8Dv81qmxIMwXVI.md) (inactif) — node « Interfast - events J+1 »
- [Bot - Brief 18h](bot-brief-18h--Lw8Dv81qmxIMwXVI.md) (inactif) — node « Interfast - fiche client »
- [Bot - Brief 18h](bot-brief-18h--Lw8Dv81qmxIMwXVI.md) (inactif) — node « Interfast - detail intervention »
- [Bot - Brief 18h](bot-brief-18h--Lw8Dv81qmxIMwXVI.md) (inactif) — node « Interfast - detail devis »

## Points fragiles
- Doublon : même nom « Interfast - Lecture » que `Qgn9xL6dGSAcq4Zv` (créé 21 min plus tard, actif, plus complet) ; cette version est inactive et probablement obsolète — risque de confusion dans le sélecteur Execute Workflow.
- Chemin hors liste blanche → exception (pas de retour `ok:false`), ce qui fait échouer l'appelant.
- HTTP Request sans `neverError`/`fullResponse` : une erreur Interfast (4xx/5xx) lève une exception au lieu d'un retour structuré.
- Pas de normalisation horaire ni de dédoublonnage des techniciens (contrairement à la v2).
- Liste des champs bloqués différente de la v2 (`accountingNumber` bloqué ici, `birthDate`/`lastConnectionDate`/`onboarding` non).
