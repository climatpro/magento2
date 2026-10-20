# Interfast - Lecture

| | |
|---|---|
| ID n8n | `Qgn9xL6dGSAcq4Zv` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger, entrées `op` string et `params` object) |
| Export | `workflows/interfast-lecture--Qgn9xL6dGSAcq4Zv.json` |

## Rôle
Point d'accès unique en lecture seule à Interfast pour le bot Telegram et les automatisations : traduit une opération nommée (`events_jour`, `rdv_jour`, `intervention`, `client`, `client_adresses`, `client_events`, `client_activites`, `client_recherche`, `devis`, `devis_par_ref`, `devis_client[_signes]`) en GET Interfast, puis nettoie les champs sensibles (prix d'achat, coûts horaires, données perso) et enrichit les événements (dateParis, heureParis, codeHoraire, horaireLibelle, technicianIds, sousContrat). Sortie `{ ok, op, statusCode, data | erreur }`.

## Services appelés
- Interfast — direct via HTTP Request, credential « Interfast API » (`GgJ5wsyGIUSWY0cN`) : GET /v1/events, /v1/intervention/{id}, /v1/client/{id}, /v1/client/{id}/addresses, /v1/client/{id}/events, /v1/client/{id}/activities, /v1/crm/search, /v1/billing/quotations, /v1/billing/quotations/{id}

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Lire client »
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Lire intervention »
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Lire RDV »
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Lire devis »
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Lire planning »
- [Bot - Brief 18h](bot-brief-18h--ZivtrXedkHo5phMD.md) — node « Chercher devis »
- [Bot - Questions (V2)](bot-questions-v2.md) (inactif) — node « Lire interventions du jour »
- [Bot - Questions (V2)](bot-questions-v2.md) (inactif) — node « Lire RDV du jour »
- [Bot - Questions (V2)](bot-questions-v2.md) (inactif) — node « Lire client »
- [Equipe - Notes Interfast](equipe-notes-interfast.md) — node « Lire planning du jour »
- [Outil - Camions](outil-camions.md) — node « Lire RDV »
- [Outil - Camions](outil-camions.md) — node « Lire interventions »
- [Outil - Detail RDV](outil-detail-rdv.md) — node « Lire intervention »
- [Outil - Fiche client](outil-fiche-client.md) — node « Lire adresses »
- [Outil - Fiche client](outil-fiche-client.md) — node « Lire fiche »
- [Outil - Fiche client](outil-fiche-client.md) — node « Lire historique »
- [Outil - Materiel devis](outil-materiel-devis.md) — node « Lire devis »
- [Outil - Materiel devis](outil-materiel-devis.md) — node « Chercher devis »
- [Outil - Memoire client](outil-memoire-client.md) — node « Lire fiche »
- [Outil - Memoire client](outil-memoire-client.md) — node « Lire activites »
- [Outil - Memoire client](outil-memoire-client.md) — node « Lire rapports »
- [Outil - Memoire client](outil-memoire-client.md) — node « Lire historique »
- [Outil - Planning](outil-planning.md) — node « Lire RDV »
- [Outil - Planning](outil-planning.md) — node « Lire interventions »
- [Outil - Recherche client](outil-recherche-client.md) — node « Chercher client »
- [Page - Tableau technicien](page-tableau-technicien.md) — node « Lire interventions »
- [Page - Tableau technicien](page-tableau-technicien.md) — node « Lire RDV »
- [Quartix - Historique](quartix-historique.md) — node « RDV du jour »
- [Quartix - Historique](quartix-historique.md) — node « Interventions du jour »
- [TEST - Banc WhatsApp Haiku vs Sonnet (a supprimer)](test-banc-whatsapp-haiku-vs-sonnet-a-supprimer.md) (inactif) — node « Lire planning »

## Points fragiles
- Pagination figée à la page 0 (events : count 100 ; client_events : 50 ; recherche : 10 ; devis : 20) : au-delà, les résultats sont silencieusement tronqués.
- `op` inconnue ou paramètre invalide → exception (throw) remontée à l'appelant, pas de retour `ok:false`.
- Astuce `qs()` : un tableau à 1 élément est dupliqué (`technicians=x&technicians=x`) pour forcer un tableau côté API ; dépend du comportement d'Interfast.
- Convention interne « codeHoraire = dernier chiffre des minutes » (1 approx., 2 demi-journée, 3 journée, 4 à caler) : fragile si la saisie dans Interfast ne la respecte pas.
- Sticky note incomplète (ops `client_activites`, `client_recherche`, `devis_client` absentes).
- Doublon de nom avec `MOZo7wkYxjOghKVZ` (inactif) : confusion possible dans le sélecteur Execute Workflow.
- Timeout 15 s ; date par défaut = J+1 Paris (pas aujourd'hui).
