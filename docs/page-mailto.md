# Page - Mailto

| | |
|---|---|
| ID n8n | `zRZHM0b8qyaYTHTy` |
| Actif | oui |
| Déclencheur | webhook GET `/webhook/mailto?to=&cc=&s=&b=` (réponse via node Respond to Webhook, HTML) |
| Export | `workflows/page-mailto.json` |

## Rôle
Page du bot : renvoie une mini-page HTML (noindex, no-store) qui redirige au chargement vers un lien `mailto:` pré-rempli (destinataire, copie, objet, corps) afin d'ouvrir la messagerie du téléphone. Utilisée par le bouton "Envoyer par email" de Bot - Assistant.

## Services appelés
aucun (génération HTML pure)

## Modèle IA
Aucun

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Endpoint public sans authentification : n'importe qui peut fabriquer une page de redirection `mailto:` hébergée sur n8n.climatpro.fr (objet et corps libres jusqu'à 3 000 caractères).
- `to` et `cc` nettoyés par regex `[a-zA-Z0-9@._+-]` : un seul destinataire possible, pas de validation d'adresse.
- Corps tronqué à 3 000 caractères ; les liens `mailto:` longs peuvent être refusés par certains clients mail.
- Dépend du navigateur intégré Telegram qui doit autoriser le schéma `mailto:` (sinon seul le bouton manuel fonctionne).
