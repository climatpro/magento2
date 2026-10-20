# TEST - Banc WhatsApp Haiku vs Sonnet (a supprimer)

| | |
|---|---|
| ID n8n | `HJKoe6RKxIEKlKSt` |
| Actif | non |
| Déclencheur | webhook POST `/webhook/banc-whatsapp` (body `{ lots: [{ jour, texte }] }`, réponse immédiate « onReceived ») |
| Export | `workflows/test-banc-whatsapp-haiku-vs-sonnet-a-supprimer.json` |

## Rôle
Banc d'essai : pour chaque lot de messages du groupe Telegram interne (par journée), récupère le planning Interfast du jour, puis envoie le même prompt « notes client » à deux modèles Claude (Haiku et Sonnet) et compare les notes extraites et les tokens consommés.
Sert à choisir le modèle du workflow de production de synthèse des messages d'équipe ; aucun résultat n'est stocké (visible seulement dans l'exécution).

## Services appelés
- Interfast — via le sous-workflow « Interfast - Lecture », op `events_jour`, params `{ date, jours: 1 }` (node « Lire planning »).
- Anthropic API — HTTP Request `POST https://api.anthropic.com/v1/messages` (node « Analyser », header `anthropic-version: 2023-06-01`, batching 4 / 1 s, timeout 120 s), credential « Anthropic account 2 » (`UtZzlYk97MvjuDan`).
- Data Tables n8n : aucune.

## Modèle IA
Anthropic `claude-haiku-5-5` et `claude-sonnet-5-5` (liste dans le node Code « Croiser », appel dans « Analyser ») : extraction des informations utiles à la fiche client depuis les messages Telegram + planning, réponse JSON `{ notes: [...] }`, max_tokens 3000.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via node « Lire planning » (Execute Workflow, mode each)

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow de test marqué « a supprimer » ; inactif, mais s'il est activé le webhook POST est **public sans authentification** et déclenche des appels Anthropic payants.
- Modèles `claude-haiku-5-5` et `claude-sonnet-5-5` : identifiants valides.
- Prompt système dupliqué du workflow de production (dérive possible) ; contient les prénoms des techniciens en dur.
- « Lire planning » et « Analyser » en `onError: continueRegularOutput` ; « Planning » et « Resultats » apparient les items par index (`res[i]`, `src[i]`) : un item manquant décale tous les résultats.
- Résultats uniquement dans la sortie du dernier node (pas de Sheet / table) ; `responseMode: onReceived` donc l'appelant ne reçoit rien.
