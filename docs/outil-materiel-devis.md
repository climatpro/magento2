# Outil - Materiel devis

| | |
|---|---|
| ID n8n | `RkGCPcG8e1gI0knk` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrées `client_id`, `ref_devis`) |
| Export | `workflows/outil-materiel-devis.json` |

## Rôle
Outil du bot Telegram : renvoie le matériel (sections, lignes, quantités, options) des devis signés d'un client, ou d'un devis désigné par sa référence, sans aucun prix. Lecture seule.

## Services appelés
- Interfast (devis par référence, devis signés d'un client, détail d'un devis) — uniquement via le sous-workflow "Interfast - Lecture" (ops `devis_par_ref`, `devis_client_signes`, `devis`)
- Data Tables : aucune

## Modèle IA
Aucun

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes `Chercher devis` et `Lire devis`

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « materiel_devis »

## Points fragiles
- Détection d'une référence de devis par regex `^[A-Z]{1,3}[0-9]{2,6}$` : toute référence d'un autre format est traitée comme un `client_id`.
- Limité aux 3 devis signés les plus récents et à 40 lignes par devis (le reste est tronqué sans avertissement).
- `onError: continueRegularOutput` sur les deux appels Interfast : une erreur devient silencieusement "Aucun devis signe trouve.".
- Si `client_id` est vide, l'appel part quand même avec `clientId: 'aucun'`.
- Dépend du format de réponse `{ ok, data.items }` du sous-workflow Interfast - Lecture.
