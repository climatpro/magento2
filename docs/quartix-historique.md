# Quartix - Historique

| | |
|---|---|
| ID n8n | `cOF8qLkXSnyAfyth` |
| Actif | oui |
| Déclencheur | 2 crons (timezone Europe/Paris) : `0 25 19 * * *` « Chaque soir 19h25 » (hier + aujourd'hui) et `0 */15 8-19 * * 1-5` « Journee en cours (15 min) » (aujourd'hui) ; + Manual Trigger « Rattrapage (manuel) » (45 derniers jours) |
| Export | `workflows/quartix-historique.json` |

## Rôle
Construit, par jour et par véhicule, un journal JSON des trajets Quartix (heures, lieux, km, tracé GPS simplifié) et des arrêts ≥ 5 min, chaque arrêt étant qualifié : dépôt, maison de Laurent, fournisseur connu (Sonepar, Plateforme du Bâtiment), ou rattaché à l'intervention/RDV Interfast du jour le plus proche (géocodage BAN < 350 m ou même voie).
Résultat upserté dans la Data Table `quartix_jours` (clé jour + immat), plus une ligne de contrôle `_bilan` ; purge des lignes > 365 jours (RGPD).

## Services appelés
- Quartix QWS v2 — HTTP Request `POST https://qws.quartix.net/v2/api/auth` (credential « Custom Auth account » `JVvofvrQJHHfTNQ3`) puis dans le Code `GET /vehicles`, `GET /vehicles/route?VehicleId=&StartDay=&EndDay=` (lecture seule).
- Interfast — via le sous-workflow « Interfast - Lecture » : ops `events_jour` (« Interventions du jour ») et `rdv_jour` (« RDV du jour »), params `{ date, jours: 1 }`.
- Géoplateforme IGN `https://data.geopf.fr/geocodage/search` avec repli `https://api-adresse.data.gouv.fr/search/` (géocodage des adresses d'intervention et des fournisseurs, cache dans `$getWorkflowStaticData('global').geo`).
- Data Tables n8n : `quartix_jours` (`dJ4ZIO2PdhYlt95o`) écriture (upsert + deleteRows) ; `clients_gps` (`xrWuLpFXi8qQWU86`) lecture (repli coordonnées client).

## Modèle IA
Aucun

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes « Interventions du jour » et « RDV du jour » (Execute Workflow, mode each, attente du résultat)

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Détection du mode par heuristique : `auto = !!(it.timestamp || it['Readable date'])` (champs de sortie du Schedule Trigger) et `soir = 19h20–19h29` à l'horloge : un décalage d'exécution > 5 min fait passer le run du soir en mode « journée » (1 jour au lieu de 2).
- Garde-fou de 240 s dans le Code node : le rattrapage 45 jours × N véhicules s'interrompt (`interrompuA`) et doit être relancé à la main ; si n8n est arrêté un soir, les jours manqués ne sont jamais rattrapés automatiquement.
- Coordonnées en dur : `DEPOT [43.5788, 6.95012]`, `MAISON [43.57814, 6.96076]` (domicile du gérant = donnée personnelle dans le code), liste `LIEUX` fournisseurs à compléter manuellement, seuils 350 m / 800 m / 5 min / 150 m / 40 m en dur.
- Toutes les 15 min en journée : 1 auth Quartix + 2 appels Interfast + 1 route par véhicule + géocodages → charge et quota API notables ; cache géocodage vidé brutalement au-delà de 3000 clés.
- Exécutions non sauvegardées (`saveDataErrorExecution: none`, `saveDataSuccessExecution: none`) : aucune trace en cas d'échec ; seul le bilan `_bilan` (dans la table) sert de journal, et il pollue la table avec une ligne non-métier.
- « Auth Quartix », « Lire clients_gps », « Purger plus d un an » en `onError: continueRegularOutput` : erreurs silencieuses, pas d'alerte.
- `RDV du jour` s'appuie sur `$('Un item par jour').item` (pairing) après un Execute Workflow en mode each : fragile si le sous-workflow renvoie 0 ou plusieurs items.
- Logique arrêts/dépôt dupliquée avec « Quartix - Positions » et « Quartix - Duree sur place ».
- Champ de debug `exemple` (clés brutes Quartix) laissé dans le bilan ; `api-adresse.data.gouv.fr` est l'ancien endpoint BAN (repli à surveiller).
