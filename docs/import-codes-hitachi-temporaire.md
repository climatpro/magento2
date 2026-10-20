# Import - Codes Hitachi (temporaire)

| | |
|---|---|
| ID n8n | `RYPWWGNG0nmH61VN` |
| Actif | non |
| Déclencheur | webhook POST /webhook/import-hitachi-5e7ba5a315866c5e (origine autorisée `https://aircloud-alarmcode.hitachiaircon.com`, exécution conditionnée à un jeton dans le body) |
| Export | `workflows/import-codes-hitachi-temporaire.json` |

## Rôle
Point d'entrée temporaire pour charger en masse des lignes de codes d'alarme Hitachi (modele, modele_norm, famille, p, codes) envoyées en JSON par un script côté navigateur depuis le site Hitachi, directement dans une Data Table. Renvoie `{ ok, n }`.

## Services appelés
- Data Table n8n : `9fowyCEpKBxx3ui1` (écriture, insertion bulk, mapping automatique)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Jeton d'authentification en dur dans l'option `onlyRunIf` du webhook (retiré de l'export : `<SECRET-RETIRE>`) ; à révoquer si le workflow est conservé.
- Workflow « temporaire », inactif, sans description : candidat à l'archivage.
- Insertion sans dédoublonnage : chaque POST ajoute des lignes, même identiques.
- Aucune validation du contenu des lignes (chaînes libres).
- Nom de la Data Table cible non visible dans l'export.
