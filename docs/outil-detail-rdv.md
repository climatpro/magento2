# Outil - Detail RDV

| | |
|---|---|
| ID n8n | `0bCdxnRh9exHqvvM` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrée `event_id`) |
| Export | `workflows/outil-detail-rdv.json` |

## Rôle
Outil du bot : renvoie le détail complet d'une intervention Interfast (référence, type, date/horaire, client, adresse et consignes d'accès, techniciens, devis lié, description, compte-rendu, statut) sous forme de texte `resultat`.

## Services appelés
- Interfast (op `intervention`, id = event_id) — via le sous-workflow « Interfast - Lecture »
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via node « Lire intervention »

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « detail_rdv »

## Points fragiles
- Table `NOMS` en dur (5066 Laurent, 5069 Christophe, 9965 Axel, 5198 Axel) incohérente avec « Outil - Fiche client » où 5198 = Julien.
- « Lire intervention » en `onError: continueRegularOutput` : une panne Interfast renvoie « Pas de detail disponible » (indiscernable d'un id inconnu).
- Troncatures en dur : description 1500 caractères, compte-rendu 800.
- Dépend des champs enrichis par « Interfast - Lecture » (`dateParis`, `heureParis`, `horaireLibelle`) : tout changement du sous-workflow casse l'affichage de la date.
