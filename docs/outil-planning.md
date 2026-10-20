# Outil - Planning

| | |
|---|---|
| ID n8n | `zA9fv7IqJnrBuRRy` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrées `date_debut`, `jours`, `categorie`, `technicien`, `user_id`, `role`) |
| Export | `workflows/outil-planning.json` |

## Rôle
Outil du bot : planning Interfast (interventions + RDV) sur 1 à 31 jours, filtré par catégorie (devis, installation, depannage, maintenance, tache, rdv) et par technicien ; un technicien ne voit que ses événements, admin/manager choisit. Sortie texte (60 lignes max) avec event_id et client_id. Lecture seule.

## Services appelés
- Interfast (événements du jour, RDV du jour) — uniquement via le sous-workflow "Interfast - Lecture" (ops `events_jour`, `rdv_jour`)
- Data Tables : aucune

## Modèle IA
Aucun

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes `Lire interventions` et `Lire RDV`

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « planning »

## Points fragiles
- IDs techniciens Interfast en dur et dupliqués dans deux nodes (`laurent 5066`, `christophe 5069`, `axel 9965 + 5198`).
- Catégorie déduite par regex sur `type` puis `title` (ex. "fuite" → dépannage) : classement approximatif.
- Date hors de la fenêtre −90 / +120 jours remplacée silencieusement par aujourd'hui.
- `onError: continueRegularOutput` sur les deux appels : une panne Interfast donne "Aucun evenement.".
- Les droits dépendent de `role` / `user_id` fournis par l'appelant ; sans `user_id` valide un technicien obtient `techIds: ['NaN']`.
- Sortie tronquée à 60 lignes.
