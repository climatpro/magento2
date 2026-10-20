# Outil - Code defaut

| | |
|---|---|
| ID n8n | `uWkW4FbbnjkmwTXb` |
| Actif | oui |
| Déclencheur | appel par sous-workflow (Execute Workflow Trigger « Appel outil », entrées `marque`, `code`, `modele`, `demandeur`) |
| Export | `workflows/outil-code-defaut.json` |

## Rôle
Outil `code_defaut` du bot : donne la signification d'un code défaut Toshiba ou Daikin depuis la Data Table `codes_defaut` (code exact, variantes d'affichage 04/E04, sous-codes, notes terrain ClimatPro) ; pour Hitachi, délègue au sous-outil « Outil - Code defaut Hitachi ». Si le code est introuvable, alerte les admins du bot sur Telegram.

## Services appelés
- Telegram (node « Alerter Laurent », credential « Telegram account » `thfKrKcwKcCWoR9V`) — alerte des admins si code absent
- Data Table n8n lue : `codes_defaut` (`ko1b5qPW0nF5yYBm`)
- Data Table n8n lue : `bot_users` (`MAaqIFX2KBiCvHFa`) — admins actifs avec telegram_id

## Modèle IA
Aucun dans ce workflow (le sous-outil Hitachi utilise `claude-sonnet-5`).

## Sous-workflows appelés
- Outil - Code defaut Hitachi (`OOM7WyEjdrj5JnKy`) via node « Fiche Hitachi »

## Appelé par
- [Bot - Assistant](bot-assistant.md) — node « code_defaut »

## Points fragiles
- Détection de la marque par regex sur le préfixe du modèle si `marque` absent : ordre Hitachi > Toshiba > Daikin, mais un modèle Hitachi « RAS-… » (ex. RAS-4HNSKQ, données de test du sous-outil) est classé Toshiba.
- Node « Fiche Hitachi » sans `onError` : une erreur du sous-outil fait échouer tout l'outil.
- Node « Alerter Laurent » en `onError: continueRegularOutput` : l'échec Telegram est silencieux alors que le texte renvoyé affirme « Laurent a ete prevenu ».
- Sticky note obsolète (ne parle que de Toshiba, cite un import mensuel « Import - Codes defaut Toshiba ») ; la fraîcheur de la table dépend de cet import non vérifié ici.
- Résultat tronqué à 6000 caractères ; sous-codes limités à 10.
- Logique « Analyse » dupliquée dans « Outil - Expert diagnostic » (node « Fiche code ») : à maintenir en double.
- Codes Daikin Altherma non couverts (le code le signale seulement).
