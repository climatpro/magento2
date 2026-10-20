# Outil - Memoire client

| | |
|---|---|
| ID n8n | `99B4KwoLPMWmJuNc` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrées `clientId`, `eventId`, `objet`, `actif`) |
| Export | `workflows/outil-memoire-client.json` |

## Rôle
Sous-workflow du brief 18h : assemble la mémoire d'un client avant une intervention (notes internes de la fiche, 40 dernières activités CRM dont appels Plaud, 6 dernières interventions terminées avec rapports et équipements, e-mails/SMS envoyés) puis la fait résumer par Claude en deux versions : `tech` (sans aucune donnée financière) et `admin` (pour Laurent). Lecture seule.

## Services appelés
- Interfast (fiche client, activités, historique d'événements, détail d'intervention) — uniquement via le sous-workflow "Interfast - Lecture" (ops `client`, `client_activites` taille 40, `client_events`, `intervention`)
- Anthropic — POST `https://api.anthropic.com/v1/messages` via HTTP Request, credential `anthropicApi` "Anthropic account 2" (`UtZzlYk97MvjuDan`), timeout 45 s
- Data Tables : aucune

## Modèle IA
Anthropic `claude-haiku-5-5` (node HTTP Request `Resumer (Haiku)`, max_tokens 4000) : produit un JSON `{tech, admin}` à partir du contexte assemblé.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes `Lire fiche`, `Lire activites`, `Lire historique`, `Lire rapports`

## Appelé par
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Mémoire client »

## Points fragiles
- Modèle `claude-haiku-5-5` : identifiant valide (les modèles actuels n'ont pas de suffixe de date).
- `onError: continueRegularOutput` sur tous les appels (Interfast et Anthropic) : une panne produit des résumés vides ou, pour Anthropic, `admin` = texte brut d'erreur, sans alerte.
- Filtre anti-argent `BAN` par regex (prix, tarif, ht, ttc, "galer"...) : peut supprimer des lignes légitimes du résumé tech (ex. "galerie").
- Extraction du JSON de réponse par `indexOf('{')` / `lastIndexOf('}')` : fragile si le modèle ajoute du texte.
- Troncatures silencieuses : contexte 24 000 caractères, chaque note 4 000, 15 e-mails max.
- Quand aucune intervention passée n'existe, un appel Interfast `intervention` part quand même avec `id: 'aucune'`.
- En-tête `anthropic-version: 2023-06-01` en dur.
