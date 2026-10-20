# Outil - Dispo Hitachi

| | |
|---|---|
| ID n8n | `p7VfJ2HTKTctJBsv` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `reference`, `role`, `modele`, `mots_cles`) |
| Export | `workflows/outil-dispo-hitachi.json` |

## Rôle
Outil `dispo_hitachi` du bot : pilote un Chromium headless (browserless) qui se connecte à hi-parts.fr, cherche une pièce par référence (mode « ref ») ou par modèle + mots-clés dans les vues éclatées (mode « modele »), et renvoie désignation, référence de remplacement, verdict de disponibilité, prix indicatif client (prix public × 1,15) et prix public pour le rôle admin. Durée ~10 s.

## Services appelés
- browserless (`http://browserless:3000/function?token=…`, conteneur Docker du VPS) — exécute un script Puppeteer généré par les nodes « Preparer script » / « Preparer modele »
- hi-parts.fr (catalogue Hitachi, via le navigateur) : `Login.aspx`, `/mvc/Search/SearchItems`, `/mvc/Search/GetUsesCasesItem`, `/mvc/Search/SearchProducts`, `ListSchema.aspx`, `FicheSchema.aspx`, `FicheProduit.aspx`, ajax `GetNomenclature`
- Data Table n8n lue : `hiparts_acces` (`VrTMPgLga7GykpX2` ; identifiant, mot_de_passe, browserless_token)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « dispo_hitachi »
- [Claude - Pieces detachees](claude-pieces-detachees.md) (inactif) — node « Outil Hitachi »

## Points fragiles
- Identifiants hi-parts et token browserless stockés en clair dans une Data Table ; le token passe en query string de l'URL et le mot de passe est injecté dans le `context` du script Puppeteer.
- Scraping fragile : sélecteurs ASP.NET (`TextBoxLOGIN`, `LinkValider`), regex sur HTML (`ImageSTOCK`, `labelpuht`, `LabelRefSubstitution`, « Prix unitaire HT »), endpoints internes du site.
- Nodes HTTP en `neverError` mais sans `onError` : browserless injoignable (connexion refusée) fait échouer le workflow.
- Timeouts longs (90 s mode ref, 120 s mode modèle) ; le mode modèle enchaîne jusqu'à 8 vues éclatées et des dizaines de requêtes dans le navigateur.
- « Preparer modele » sérialise une fonction avec `script.toString()` et contient une regex avec caractères combinants littéraux (`[̀-ͯ]`) sensible à l'encodage.
- Marge 1,15 en dur ; prix public exposé dès que l'appelant passe `role = admin` (non vérifié).
- Node « Entree » lit aussi `query`/`body` (reliquat d'un ancien déclencheur webhook) ; URL browserless en dur.
