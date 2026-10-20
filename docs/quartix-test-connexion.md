# Quartix - Test connexion

| | |
|---|---|
| ID n8n | `PROTVUjUQLOPHwcg` |
| Actif | non |
| Déclencheur | Manual Trigger « Lancer le test » |
| Export | `workflows/quartix-test-connexion.json` |

## Rôle
Outil de diagnostic : lit les identifiants Quartix dans la Data Table `quartix_acces`, s'authentifie sur QWS v2 (form-urlencoded) puis renvoie brut `/vehicles`, `/vehicles/live`, les trajets du jour et `/vehicles/management`.
Lecture seule ; le jeton n'est pas renvoyé en sortie.

## Services appelés
- Quartix QWS v2 — appels `this.helpers.httpRequest` dans le Code : `POST /auth` (CustomerID, UserName, Password, Application) puis `GET /vehicles`, `/vehicles/live`, `/vehicles/trips?StartDay=&EndDay=`, `/vehicles/management`. Aucune credential n8n utilisée.
- Data Tables n8n : `quartix_acces` (`NEpa7TDPMZep9rOI`) lecture (colonnes `customer_id`, `identifiant`, `mot_de_passe`, `application`).

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- **Mot de passe Quartix stocké en clair dans une Data Table** (`quartix_acces`) et lu dans le Code au lieu d'une credential n8n chiffrée : à migrer/supprimer. Les workflows de production (Positions, Historique, Durée sur place) utilisent déjà la credential « Custom Auth account » (`JVvofvrQJHHfTNQ3`) : ce test est obsolète et la table devrait être purgée.
- Méthode d'auth différente de la prod (form-urlencoded vs body JSON `{}` + custom auth) : le test ne valide pas la configuration réellement utilisée.
- Pas de timeout sur les `httpRequest` ; exécutions non sauvegardées.
- Sortie brute complète (positions live) sans filtrage.
