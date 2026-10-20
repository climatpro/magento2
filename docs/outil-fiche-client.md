# Outil - Fiche client

| | |
|---|---|
| ID n8n | `yj2W2NXNAbFRiuN6` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrée `client_id`) |
| Export | `workflows/outil-fiche-client.json` |

## Rôle
Outil du bot : fiche client Interfast en texte (nom, contacts avec téléphones/mails, note fiche, adresses, 12 dernières interventions avec techniciens et statut). Sert aussi de source d'historique à « Outil - Expert diagnostic ».

## Services appelés
- Interfast (ops `client`, `client_adresses`, `client_events`, id = client_id) — via le sous-workflow « Interfast - Lecture », trois appels séquentiels
- Data Tables n8n : aucune

## Modèle IA
Aucun.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes « Lire fiche », « Lire adresses », « Lire historique »

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « fiche_client »
- [Outil - Expert diagnostic](outil-expert-diagnostic.md) — node « Historique client »

## Points fragiles
- Table `NOMS` en dur (5066 Laurent, 5069 Christophe, 9965 Axel, 5198 Julien) : 5198 = Julien ici mais Axel dans « Outil - Camions » et « Outil - Detail RDV ».
- Les trois appels sont en `onError: continueRegularOutput` : une panne Interfast renvoie « Client introuvable » (indiscernable d'un id inexistant), ou une fiche sans adresses/historique sans le signaler.
- Renvoie téléphones, e-mails et commentaires de contact en clair au bot (données personnelles transmises ensuite au modèle de l'assistant).
- Trois appels séquentiels à « Interfast - Lecture » : latence cumulée.
- Limites fixes : 6 contacts, 5 adresses, 12 interventions, note fiche 300 caractères.
- Dépend des structures `clientParticular` / `clientProfessional` / `clientOwnersAssociation` et de `data.items` renvoyées par « Interfast - Lecture ».
