# Outil - Code defaut Hitachi

| | |
|---|---|
| ID n8n | `OOM7WyEjdrj5JnKy` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel », entrées `code`, `modele`, `demandeur`) ; plus un « Test manuel » (Manual Trigger + node « Donnees test » : code 02, modèle RAS-4HNSKQ) |
| Export | `workflows/outil-code-defaut-hitachi.json` |

## Rôle
Sous-outil Hitachi : retrouve le libellé d'un code alarme selon le modèle dans la table `codes_hitachi` (données de l'appli airCloud Alarm Code), télécharge la fiche PDF officielle du manuel de service (hitachi-mp.spelog.com), la fait résumer par Claude Sonnet pour un frigoriste, et met le résumé en cache dans `fiches_hitachi`. Renvoie `resultat` + `absent`.

## Services appelés
- HTTP GET `https://hitachi-mp.spelog.com/getalarmcode.aspx?P=…&L=FR&A=…` (node « Telecharger fiche », sans authentification) — fiche PDF officielle
- Anthropic (node « Lire fiche (Sonnet) », credential « Anthropic account 2 » `UtZzlYk97MvjuDan`) — analyse du PDF
- Data Table n8n lue : `9fowyCEpKBxx3ui1` (nom déduit de la description : `codes_hitachi` ; colonnes modele, modele_norm, famille, p, codes JSON)
- Data Table n8n lue et écrite : `ywfMnHuTuf0KzXRY` (nom déduit de la description : `fiches_hitachi` ; cache cle, modele, code, libelle, fiche, maj)

## Modèle IA
Anthropic `claude-sonnet-5`, node « Lire fiche (Sonnet) » (`@n8n/n8n-nodes-langchain.anthropic`, resource document / analyze, maxTokens 3000) : résume la fiche PDF (ou la liste globale des codes) en texte brut de 2000-2500 caractères.

## Sous-workflows appelés
aucun

## Appelé par
- [Outil - Code defaut](outil-code-defaut.md) — node « Fiche Hitachi »

## Points fragiles
- Filtre Data Table entièrement dynamique (`keyName`, `condition`, `keyValue` en expressions) ; sans modèle, recherche `ilike '%["CODE%'` dans la colonne JSON `codes` : dépend strictement du format de sérialisation.
- URL `hitachi-mp.spelog.com` en dur ; « Telecharger fiche » en `onError: continueRegularOutput` puis « Type PDF » force `mimeType: application/pdf` quel que soit le contenu (page d'erreur HTML envoyée à Sonnet).
- Cache sans expiration ni upsert (`insert` seul) : doublons possibles si deux appels simultanés ; une fiche mal lue n'est jamais recalculée tant que `fiche` est non vide.
- Le workflow écrit dans une Data Table alors que la description annonce « lecture seule ».
- Les messages « Laurent a ete prevenu » sont renvoyés, mais l'alerte Telegram n'est faite que par le parent « Outil - Code defaut » (pas si appelé directement).
- Modèle `claude-sonnet-5` : valide mais génération précédente (Sonnet 5.5 `claude-sonnet-5-5` est la version actuelle, même prix) ; latence et coût d'un appel vision/PDF à chaque fiche non cachée.
- Nodes de test (« Test manuel », « Donnees test ») laissés dans un workflow actif.
