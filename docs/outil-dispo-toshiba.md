# Outil - Dispo Toshiba

| | |
|---|---|
| ID n8n | `4PjuGOfWCDdkuoPq` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `reference`, `modele`, `mots_cles`, `role`) |
| Export | `workflows/outil-dispo-toshiba.json` |

## Rôle
Outil `dispo_toshiba` du bot : interroge le portail public pieces.toshiba-confort.fr (accès invité, HTTP simple) pour une pièce par référence ou par modèle + mots-clés (vue éclatée, synonymes FR/EN), et renvoie stock Toshiba France, prix indicatif client (prix portail × 1,30) et prix portail pour le rôle admin.

## Services appelés
- pieces.toshiba-confort.fr en HTTP Request, sans identifiants : `/@list-items` (catalogue complet JSON), `/part-selection?model=` (vue éclatée HTML), `/@stock/ZT…` (quantité)
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « dispo_toshiba »
- [Claude - Pieces detachees](claude-pieces-detachees.md) (inactif) — node « Outil Toshiba »

## Points fragiles
- `/@list-items` télécharge le catalogue complet (modèles + pièces) à chaque appel : lourd, timeout 45 s, et lecture positionnelle des colonnes `aaData` (`x[0]`..`x[4]`).
- Vue éclatée parsée par regex sur le HTML (`componentsList__row`, attributs `data-*`) : casse au moindre changement du site.
- Incohérence doc/code : la sticky note annonce « prix portail × 1,15 », le code applique `MARGE = 1.30`.
- Stock aligné par index entre les items « Pieces » et les réponses « Stock » : un appel en erreur (`neverError`, `onError: continue`) décale les quantités.
- Repli `ZT0000000` si `zt` vide ; tous les HTTP en `neverError` : pannes silencieuses.
- Prix portail exposé dès que l'appelant passe `role = admin` (non vérifié) ; limites fixes 5 candidats / 120 lignes.
- Le portail ne donne pas les références de remplacement (signalé dans le texte).
