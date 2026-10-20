# Climapro - Mémos vocaux

| | |
|---|---|
| ID n8n | `VGZmIR5xPPzUFpMP` |
| Actif | oui |
| Déclencheur | webhook POST /webhook/climapro (node "Webhook Climapro", authentification par en-tête `X-Key`, credential "Climapro X-Key"), réponse texte via node "Repondre a l'iPhone" |
| Export | `workflows/climapro-memos-vocaux.json` |

## Rôle
Reçoit un mémo dicté depuis le raccourci iPhone (`note`, `appareil`, `lieu`, `lat`, `lon`, `date`), le fait classer par Haiku (type, domaine, destinataire, client, thème, objet, confiance), puis le range : tâche Todoist dans le bon projet/section/labels, ou note sur la fiche client Interfast si c'est une info client identifiable.
Suggère le client Interfast à moins de 200 m du lieu, gère les commandes de matériel, les films à voir, les cas « pro ou perso ? » et renvoie un message de confirmation à l'iPhone.

## Services appelés
- Anthropic (POST https://api.anthropic.com/v1/messages) — node "Classer (Haiku)", credential "Anthropic account 2" (`UtZzlYk97MvjuDan`), 2 essais
- Interfast (GET /v1/crm/search?name=… ; **POST /v1/client/{id}/activities/notes** — écriture d'une note client) — direct via HTTP Request, credential "Interfast API" (`GgJ5wsyGIUSWY0cN`)
- Todoist API (POST /api/v1/tasks, création de tâche ; node de secours vers la boîte de réception) — credential "Todoist account" (`feB4B4HQds0e2tFC`)
- IGN Géoplateforme (GET https://data.geopf.fr/geocodage/search, sans credential, timeout 4 s) — node "Geocoder le lieu"
- Data Tables n8n : `clients_gps` (`xrWuLpFXi8qQWU86`) — lecture (node "Clients GPS") ; `images_tableau` (`gkJQL9liZvE8M2Op`) — lecture (node "Icones existantes", pour donner à Haiku la liste des icônes disponibles)

## Modèle IA
Anthropic `claude-haiku-4-5-20251001` (requête construite dans le node "Preparer", complétée par "Precisions commande", envoyée par "Classer (Haiku)", max_tokens 500) : classe le mémo et renvoie un JSON (type, domaine, destinataire, client, titre, echeance, urgent, resume, confiance, theme, perso_possible, objet).

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Seul point d'**écriture Interfast** de cette liste (note sur fiche client) ; `onError: continueErrorOutput` bascule vers une tâche "à rattacher" si l'écriture échoue.
- Identité de Laurent déduite du nom d'appareil en dur (`'iphone klb'`) : tout autre appareil est traité comme « équipe » ; un appareil renommé change le rangement sans alerte.
- Identifiants Todoist (5 projets, 8 sections) en dur et dupliqués dans 3 nodes ("Router", "Theme", "Films") et dans "Climapro - Ranger mémo".
- Adresses personnelles en dur dans le code ("impasse du moulin", "chemin de dandon") et prompt contenant des informations privées (holding, SCI, famille).
- Prompt système réparti sur deux nodes ("Preparer" + "Precisions commande") : les clés `perso_possible` et `objet` n'existent que si le second node s'exécute.
- Si Haiku ne répond pas ou renvoie un JSON illisible (`continueRegularOutput`), tout va en « À trier » / boîte de réception sans message d'erreur explicite.
- "Geocoder le lieu" est appelé même quand l'iPhone fournit déjà `lat`/`lon` (appel inutile) ; `alwaysOutputData` + `continueRegularOutput` partout : pannes silencieuses (IGN, Data Table, Interfast).
- Correspondance client Interfast par recherche de nom et exigence d'un candidat unique : homonymes → tâche "à rattacher" systématique.
- Le modèle `claude-haiku-4-5-20251001` est plus ancien que celui des autres workflows (`claude-haiku-5-5`) : à harmoniser.
- Pas de `timezone` dans les settings (le code force Europe/Paris manuellement).
