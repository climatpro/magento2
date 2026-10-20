# Climapro - Clients sans entretien

| | |
|---|---|
| ID n8n | `H7muVNYi1nx8vEFs` |
| Actif | oui |
| Déclencheur | cron quotidien 3h22 Europe/Paris (node "Chaque nuit 3h22") |
| Export | `workflows/climapro-clients-sans-entretien.json` |

## Rôle
Chaque nuit, relit toutes les interventions Interfast depuis 2018, repère par client la dernière installation terminée et le dernier entretien, et liste les clients avec une pose depuis 6 mois ou plus sans entretien (hors contrat de maintenance actif, hors entretien déjà planifié).
Résultat écrit dans la table `clients_sans_entretien`, lue par le bot (outil "Clients sans entretien").

## Services appelés
- Interfast (GET /v1/events, 40 pages × 100, `start=2018-01-01`, `end=+13 mois`, `archived=false`, `meeting=false`, `orderBy=start`) — direct via HTTP Request, credential "Interfast API" (`GgJ5wsyGIUSWY0cN`)
- Data Tables n8n : `clients_sans_entretien` (`wdM1D4E3ZOAmhvoy`) — upsert sur `client_id` (node "Enregistrer")

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Pagination limitée en dur : 40 pages × 100 = 4 000 interventions maximum, triées par date croissante depuis 2018 ; dès que l'historique dépasse ce volume, ce sont les interventions **les plus récentes** qui manquent (entretiens récents non vus, faux positifs).
- `onError: continueRegularOutput` sur l'appel Interfast : une page en erreur est ignorée silencieusement.
- Classification par regex sur `type`/`title` (install, pose, entretien, dépannage, dépose…) : un libellé atypique est mal classé ; "Toshiba" est exclu en dur comme nom de client.
- Upsert sans suppression : un client qui a depuis reçu un entretien reste dans la table avec un ancien `maj` ; le consommateur doit filtrer sur le dernier `maj` (dépendance implicite documentée seulement en commentaire du code).
- Seuils en dur : 6 mois sans entretien, 18 mois pour considérer un contrat actif, fenêtre +13 mois pour les entretiens planifiés.
- Pas d'alerte en cas de résultat vide (ex. Interfast indisponible) : la table n'est simplement pas rafraîchie.
