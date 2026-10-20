# Outil - Dispo Daikin

| | |
|---|---|
| ID n8n | `di2cU3TRSnyS2BdQ` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `reference`, `modele`, `mots_cles`, `role`) ; plus un « Test manuel » (Manual Trigger + « Donnees test » : modèle FTXM35R2V1B, mots-clés PCB, role admin) |
| Export | `workflows/outil-dispo-daikin.json` |

## Rôle
Outil `dispo_daikin` du bot : se connecte au portail Daikin Spare Parts Bank, cherche une pièce par référence ou par modèle + mots-clés (vue éclatée, synonymes FR→EN), et renvoie référence, remplacement, stock France/Belgique (avec date), prix indicatif client (prix catalogue × 1,30) et, pour le rôle admin, le prix catalogue.

## Services appelés
- Portail Daikin Spare Parts Bank en HTTP Request (défaut `https://www.spb-dev.daikin.co.jp`, surchargeable par `url_base`) : `/gsdb/login.asp` (POST identifiants), `/gsdb/spb/spb_modelSearch.asp`, `/gsdb/spb/partslist.asp`, `/gsdb/spb/spb_partsDetail.asp` — cookie de session géré à la main
- Data Table n8n lue : `pU9JwmOAxlYmPcvL` (nom déduit de la description : `daikin_spb_acces` ; colonnes identifiant, mot_de_passe, url_base)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « dispo_daikin »

## Points fragiles
- Identifiant et mot de passe du portail Daikin stockés en clair dans une Data Table n8n (pas une credential n8n) et envoyés en formulaire POST.
- URL par défaut `spb-dev.daikin.co.jp` = portail de test Daikin (le code lui-même avertit « stock probablement ancien »).
- Tout le parsing repose sur des regex sur HTML/JS embarqué (`'unitName' : '…'`, `rowRe` sur JSON inline, date « France ») : casse au moindre changement du portail.
- Tous les HTTP en `neverError` + `onError: continueRegularOutput` : échecs silencieux, détectés seulement par des heuristiques (`timed out`, absence de cookie).
- Marge 1,30 en dur ; prix catalogue exposé dès que l'appelant passe `role = admin` (non vérifié ici).
- Limites fixes : 3 candidats détaillés, 120 lignes de liste, timeouts 30 s.
- Nodes de test laissés dans un workflow actif, avec `role: 'admin'` en dur.
