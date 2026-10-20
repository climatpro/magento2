# Outil - Memos

| | |
|---|---|
| ID n8n | `6jYK4PkJgDjs4Zf2` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrées `theme`, `client`, `role`, `nom`) |
| Export | `workflows/outil-memos.json` |

## Rôle
Outil du bot : liste les mémos vocaux Todoist non cochés (label `memo`), filtrés selon les droits fixés dans le code (admin = projets "Laurent ClimatPro" + "Equipe" ; technicien = "Equipe" + mémos de Laurent portant le label à son prénom), puis par thème et par client. Lecture seule, 40 mémos max.

## Services appelés
- Todoist REST v1 — GET `https://api.todoist.com/api/v1/tasks?label=memo&limit=200`, credential `todoistApi` "Todoist account" (`feB4B4HQds0e2tFC`)
- Data Tables : aucune

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « memos »

## Points fragiles
- IDs de projets Todoist en dur (`6hh423vJrW7RvQQg` Laurent ClimatPro, `6hh423vw4vGgHFPw` Equipe) ; dupliqués dans "Page - Tableau technicien".
- Limite de 200 tâches sans pagination (`next_cursor` ignoré).
- `onError: continueRegularOutput` sur Todoist : une erreur API devient "Aucun memo trouve.".
- Les droits reposent sur `role` et `nom` transmis par l'appelant (le bot) : aucune vérification locale de l'identité.
- Parsing de la description par regex ("Dicté le ...", "(iPhone ...)", "Client à proximité au moment du mémo : ...") : dépend du format écrit par un autre workflow ; l'auteur "Laurent" est reconnu par la présence de "klb" dans le nom de l'iPhone.
- Thème "entretien" déduit par mots-clés (`entretien|maintenance|contrat|revision|nettoyage`).
