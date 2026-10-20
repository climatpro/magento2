# Outil - Camions

| | |
|---|---|
| ID n8n | `NXr5qAKWTQU0nVoY` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `date_debut` (string), `jours` (number)) |
| Export | `workflows/outil-camions.json` |

## Rôle
Outil du bot Telegram : calcule, par demi-journée et sur 1 à 14 jours, la disponibilité des 2 camions (Christophe et Axel) à partir des interventions et RDV Interfast. Règle de Laurent codée en dur : ensemble ou un seul au travail = 1 camion libre ; chacun de son côté = aucun. Renvoie un texte `resultat`.

## Services appelés
- Interfast (ops `events_jour` et `rdv_jour`, techniciens 5069/9965/5198) — via le sous-workflow « Interfast - Lecture »
- Data Tables n8n : aucune

## Modèle IA
Aucun (calcul 100 % en code JavaScript).

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes « Lire interventions » et « Lire RDV »

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « camions »

## Points fragiles
- IDs techniciens en dur (Christophe = 5069, Axel = 9965 et 5198) dans deux nodes ; à mettre à jour à chaque changement d'équipe.
- Les deux appels Interfast sont en `onError: continueRegularOutput` : si Interfast est injoignable, le code renvoie « 2 camions libres » sans signaler l'erreur.
- Date hors de la fenêtre [-30 j ; +120 j] ou invalide silencieusement remplacée par aujourd'hui ; `jours` plafonné à 14 sans avertir.
- Regex d'extraction du lieu `(\d{5})[\s,]+(.+)$` sur l'adresse : fragile si l'adresse ne contient pas de code postal.
- Valeurs magiques `codeHoraire` 3 (journée) et 4 (à caler) et seuil 12h30 (750 min) en dur.
- Dépend du format de réponse de « Interfast - Lecture » (`ok`, `data.items`, `technicianIds`, `lifecycleState`).
