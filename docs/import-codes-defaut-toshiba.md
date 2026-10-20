# Import - Codes defaut Toshiba

| | |
|---|---|
| ID n8n | `IPXbHTthWpMfQimp` |
| Actif | oui |
| Déclencheur | cron mensuel : le 1er du mois à 06:07 (Schedule Trigger) |
| Export | `workflows/import-codes-defaut-toshiba.json` |

## Rôle
Scrape chaque mois la page publique des codes défaut Toshiba France et met à jour (upsert marque + code_cle) la Data Table `codes_defaut` : code, désignation, notes constructeur, source, date de mise à jour. La colonne `notes_climatpro` n'est pas touchée.

## Services appelés
- Site fournisseur — GET https://espacepro.toshiba-confort.fr/codes-defauts/ (HTML, sans authentification, timeout 60 s)
- Data Table n8n : codes_defaut `ko1b5qPW0nF5yYBm` (écriture, upsert sur marque + code_cle)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Extraction par regex sur le HTML (`class="wrapper-resultat-code"`, `code="…"`, `designation-code`, `note-code`) : casse à la moindre refonte de la page.
- Garde-fou : exception si moins de 100 codes lus (import annulé, pas de notification).
- Aucun `onError` ni alerte : un échec n'est visible que dans les exécutions n8n.
- Upsert ligne par ligne (plusieurs centaines de codes) : lent et partiel en cas d'interruption.
- La colonne `notes` (constructeur) est écrasée à chaque import ; seule `notes_climatpro` est préservée.
