# Quartix - Positions

| | |
|---|---|
| ID n8n | `1bkcX6ADhHRwDbMF` |
| Actif | oui |
| Déclencheur | cron "chaque minute" (Schedule Trigger), filtré dans le Code « Fenetre et cadence » : lun–ven 8h15–19h00 Paris, 1 min si un véhicule roule sinon 5 min ; + Manual Trigger « Test manuel » |
| Export | `workflows/quartix-positions.json` |

## Rôle
Lit Quartix (véhicules, position live, trajets du jour, échéances révision/assurance/CT) et calcule pour chaque véhicule l'état courant (en route, vitesse, adresse, dépôt, km du jour) et, pour le Vivaro blanc `FL 192 RP` uniquement, les arrêts ≥ 5 min hors dépôt (y compris l'arrêt en cours).
Résultat upserté en une ligne `cle = 'etat'` (JSON) dans la Data Table `quartix_etat`, lue par le tableau de bord. Lecture seule côté Quartix.

## Services appelés
- Quartix QWS v2 — HTTP Request `POST https://qws.quartix.net/v2/api/auth` (credential « Custom Auth account » `JVvofvrQJHHfTNQ3`) puis dans le Code : `GET /vehicles`, `/vehicles/live`, `/vehicles/trips?StartDay=&EndDay=`, `/vehicles/management`.
- Data Tables n8n : `quartix_etat` (`45PSs7FELv97nkCn`) écriture (upsert sur `cle = etat`).

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Trigger « chaque minute » 24/7 (≈ 1440 exécutions/jour) dont la plupart sortent vides ; la cadence réelle repose sur `$getWorkflowStaticData('global')` (`dernier`, `enRoute`, `bloque`) — état perdu/instable si le workflow est republié ou si plusieurs exécutions se chevauchent.
- Après un refus d'authentification : pause de 30 min et erreur écrite dans la table, mais **aucune alerte** ; « Auth Quartix » en `onError: continueRegularOutput`.
- Exécutions non sauvegardées (`saveDataErrorExecution: none`, `saveDataSuccessExecution: none`) : impossible de diagnostiquer a posteriori.
- Immatriculation suivie `FL 192 RP` et regex dépôt (`/^climatpro$/i`, `/Chem(in|\.) de Dandon/i`) en dur ; `enRoute` déduit de `Speed > 0` ou `LastEventDescription !== 'Ignition-Off'` (dépend des libellés Quartix).
- Parsing de `LocationText` par regex `^.*? à ` / ` depuis .*$` (format texte Quartix, francophone).
- Mélange `VehicleId` / `VehicleID` selon les endpoints, sans lecture insensible à la casse.
- Logique arrêts/dépôt dupliquée avec « Quartix - Historique » et « Quartix - Duree sur place ».
- « Test manuel » saute « Fenetre et cadence » mais écrit quand même `s.dernier`/`s.enRoute` (effet de bord sur la cadence auto).
