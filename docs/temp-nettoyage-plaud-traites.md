# TEMP - Nettoyage plaud_traites

| | |
|---|---|
| ID n8n | `q6UPtSoYET3qtUd3` |
| Actif | non |
| Déclencheur | Manual Trigger « Lancer » |
| Export | `workflows/temp-nettoyage-plaud-traites.json` |

## Rôle
Utilitaire jetable : supprime dans la Data Table `plaud_traites` les lignes dont `traite_le = '2026-10-07 23:19'` (nettoyage d'un test du pipeline Plaud).
Aucune autre action.

## Services appelés
- Data Tables n8n : `plaud_traites` (`5iiREQs0cwhwUqhB`) écriture (deleteRows).

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow temporaire (préfixe TEMP) créé le 2026-10-07, jamais modifié depuis : à supprimer.
- Suppression destructive sur une valeur de date en dur ; une relance accidentelle ne fait rien de plus mais le pattern (delete sans sauvegarde) est à proscrire sur la table de production Plaud.
- Pas de description, pas de garde-fou.
