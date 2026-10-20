# Quartix - Duree sur place (lecture seule)

| | |
|---|---|
| ID n8n | `mT1ui2kYOVnAJdLM` |
| Actif | non |
| Déclencheur | webhook GET `/webhook/quartix-trajets-jour` (query `jour=AAAA-MM-JJ`, `immat`, réponse = dernier node) + Manual Trigger « Test manuel » |
| Export | `workflows/quartix-duree-sur-place-lecture-seule.json` |

## Rôle
Pour un jour et une immatriculation donnés (défaut : aujourd'hui, `FL 192 RP` = Vivaro blanc des techniciens), lit les trajets Quartix du véhicule et calcule les arrêts (≥ 5 min, hors dépôt) avec heure d'arrivée/départ, durée, et totaux par lieu.
Sert à facturer le temps réellement passé sur place plutôt que celui du bon d'intervention. Lecture seule.

## Services appelés
- Quartix QWS v2 — HTTP Request `POST https://qws.quartix.net/v2/api/auth` (body `{}`, credential « Custom Auth account » `JVvofvrQJHHfTNQ3`, type httpCustomAuth) puis, dans le Code node via `this.helpers.httpRequest` avec header `AccessToken` : `GET /vehicles`, `GET /vehicles/trips?StartDay=&EndDay=`.
- Data Tables n8n : aucune.

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow **inactif** : le webhook `/webhook/quartix-trajets-jour` n'est pas exposé ; s'il est activé, le webhook GET est **sans authentification** et renvoie les positions/arrêts d'un véhicule (données personnelles de géolocalisation).
- Immatriculation par défaut `FL 192 RP` et regex dépôt (`/^climatpro$/i`, `/Chem(in|\.) de Dandon/i`) en dur.
- Logique arrêts/dépôt dupliquée avec « Quartix - Positions » (`1bkcX6ADhHRwDbMF`) et « Quartix - Historique » (`cOF8qLkXSnyAfyth`) : trois copies à maintenir.
- « Auth Quartix » en `onError: continueRegularOutput` + `neverError` : géré dans le Code (retour `erreur: Connexion Quartix refusee`), mais aucune alerte.
- Le dernier arrêt de la journée (pas de trajet suivant) est ignoré (`if (!dep) continue`) : un arrêt en cours n'apparaît pas.
- Mélange de casse `VehicleID` (trips) / `VehicleId` (vehicles) : dépend du format exact de réponse Quartix, sans lecture insensible à la casse contrairement à « Quartix - Historique ».
- Timeouts 15 s (auth) / 20 s (GET), pas de pagination.
