# Climapro - Devis acceptes par mail

| | |
|---|---|
| ID n8n | `9eDmOWAeUc9LwYlM` |
| Actif | oui |
| Déclencheur | 2 déclencheurs : cron toutes les 15 min (node "Toutes les 15 min") + webhook GET /webhook/devis-mail-valider (node "Lien valider", sans authentification, protégé par un jeton à usage unique) |
| Export | `workflows/climapro-devis-acceptes-par-mail.json` |

## Rôle
Toutes les 15 min, lit les mails reçus des 3 derniers jours, garde ceux qui parlent d'un devis avec un mot d'accord, demande à Haiku si le client accepte un devis, vérifie le devis dans Interfast et, si l'acceptation est claire, l'ajoute à la table `devis_a_planifier` (source `mail`). En cas de doute, envoie un Telegram à Laurent avec un bouton "Valider" (lien webhook à jeton).
En parallèle, ferme les lignes "mail" dont le devis a été annulé, refusé ou soldé dans Interfast.

## Services appelés
- Gmail API (GET /gmail/v1/users/me/messages avec `q=in:inbox newer_than:3d -from:me`, max 60 ; GET message `format=full`) — direct via HTTP Request, credential "Gmail account" (`QkVJEJmojKI4yW63`)
- Anthropic (POST https://api.anthropic.com/v1/messages) — node "Analyser (Haiku)", credential "Anthropic account 2" (`UtZzlYk97MvjuDan`)
- Interfast (GET /v1/billing/quotations?name=… ; GET /v1/billing/quotations/{id}) — direct via HTTP Request, credential "Interfast API" (`GgJ5wsyGIUSWY0cN`)
- Telegram (sendMessage vers chat `1857340429`, HTML, bouton URL) — nodes "Telegram - doute (bouton)" / "Telegram - doute", credential "Telegram account" (`thfKrKcwKcCWoR9V`)
- Data Tables n8n : `devis_mails` (`kX8WPJnw2JlUsq51`) — lecture, insert, update ; `devis_a_planifier` (`0U759buKi8psn4V5`) — lecture (filtre `source=mail`, `planifie=false`) et upsert sur `reference`

## Modèle IA
Anthropic `claude-haiku-5-5` (node "Analyser (Haiku)", max_tokens 400) : répond en JSON `{accepte, certain, reference, raison}` pour dire si le nouveau message accepte un devis ClimatPro.

## Sous-workflows appelés
aucun (le lien "Valider" rappelle ce même workflow par son webhook)

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Modèle `claude-haiku-5-5` (Haiku 5.5, génération actuelle, identifiant valide). Si l'API renvoie une erreur, `onError: continueRegularOutput` masque l'erreur et tout mail candidat est marqué `fait` avec "reponse illisible" (jamais relu).
- Webhook GET `devis-mail-valider` sans authentification : sécurité fondée uniquement sur le jeton 24 caractères généré par `Math.random()` (non cryptographique).
- Description du workflow tronquée ("Ferme les lignes ma…").
- Pré-filtre regex très large (`\bok\b`, `command`, `confirm`, `valid`…) : beaucoup de mails partent chez Haiku ; inversement les adresses `climatpro.fr`, `inter-fast`, `klb.fr`, `noreply` sont exclues en dur.
- La table `devis_mails` reçoit **tous** les mails lus (y compris `hors_sujet`) et n'est jamais purgée : croissance illimitée, et `Lire mails traites` la relit intégralement toutes les 15 min.
- Limites en dur : 60 messages listés, 25 traités par passage ; un pic de courrier retarde l'analyse.
- Node "Devis clos ?" apparie les réponses Interfast aux lignes par **index** : si un appel est en erreur (continueRegularOutput), le décalage ferme potentiellement la mauvaise ligne.
- `onError: continueRegularOutput` sur Gmail-lire, Haiku, Devis Interfast, Statut devis, Telegram : pannes silencieuses.
- Chat Telegram de Laurent (`1857340429`) et URL n8n (`https://n8n.climatpro.fr/webhook/devis-mail-valider`) en dur dans le code.
- Les regex de répartition CHRISTOPHE / LAURENT sont copiées 3 fois (nodes "Decider", "Ligne (lien)" et le workflow "Devis signes a planifier") : divergence probable à la prochaine modification.
- Pas de `timezone` dans les settings (dates en UTC par défaut).
- Un doute sans devis identifié n'a pas de bouton : si Laurent passe le devis en Accepté dans Interfast, c'est l'autre workflow qui le reprend ; la ligne `devis_mails` reste en statut `doute` pour toujours.
