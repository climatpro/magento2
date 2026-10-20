# Outil - Expert diagnostic

| | |
|---|---|
| ID n8n | `LA38f9HqFWwMlXjY` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `marque`, `modele`, `code`, `symptomes`, `client_id`) ; plus un « Test manuel » (Manual Trigger + « Donnees test » : Toshiba RAS-B10E2KVG-E code 0011) |
| Export | `workflows/outil-expert-diagnostic.json` |

## Rôle
« Expert » du bot (architecture standardiste/experts) : pour une panne complexe, assemble la fiche officielle du code (table `codes_defaut` + notes terrain), les symptômes du technicien et l'historique client (via « Outil - Fiche client », contacts/adresses retirés), puis demande à Claude Sonnet de classer les hypothèses et l'ordre des contrôles, sans mémoire. Renvoie un texte `resultat`.

## Services appelés
- Anthropic (node « Sonnet », credential « Anthropic account 2 » `UtZzlYk97MvjuDan`)
- Interfast — indirectement via le sous-workflow « Outil - Fiche client »
- Data Table n8n lue : `codes_defaut` (`ko1b5qPW0nF5yYBm`)

## Modèle IA
Anthropic `claude-sonnet-5`, node « Sonnet » (`lmChatAnthropic`, maxTokens 6000, `thinkingMode: adaptive`, `effort: medium`) branché sur la chaîne LLM « Expert » (`chainLlm`, prompt système « expert diagnostic ClimatPro », texte = contexte assemblé).

## Sous-workflows appelés
- Outil - Fiche client (`yj2W2NXNAbFRiuN6`) via node « Historique client »

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « expert_diagnostic »

## Points fragiles
- Hitachi non géré : pas de détection `/^hit/` ni de table `codes_hitachi` ; un code Hitachi donne « Pas de base de codes defaut » alors que « Outil - Code defaut » le couvre.
- Node « Fiche code » duplique la logique « Analyse » d'« Outil - Code defaut » (variantes 04/E04, sous-codes) : deux copies à maintenir ; libellé « Consignes Toshiba » appliqué aussi aux notes Daikin.
- Filtrage des données personnelles de l'historique par regex sur les lignes « Contact : » / « Adresse : » uniquement : une « Note fiche » ou un titre d'intervention peut contenir des coordonnées envoyées au modèle.
- « Expert » et « Historique client » en `onError: continueRegularOutput` : réponse de repli générique en cas d'erreur API.
- Modèle `claude-sonnet-5` : valide mais génération précédente (Sonnet 5.5 même prix) ; thinking adaptatif + 6000 tokens = latence et coût par appel.
- Nodes de test laissés dans un workflow actif.
