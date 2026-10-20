# Bot - Bilan hebdo

| | |
|---|---|
| ID n8n | `4ZLozTo8dtEjTUwG` |
| Actif | oui |
| Déclencheur | cron `0 20 8 * * 1` (lundi 8h20, Schedule Trigger "Lundi 8h20", pas de timezone fixée dans le workflow) |
| Export | `workflows/bot-bilan-hebdo.json` |

## Rôle
Chaque lundi, lit le journal Google Sheet du bot (7 derniers jours, hors lignes `workflow = brief`), compte les questions par utilisateur, repère celles jugées hors sujet/sensibles (regex sur la question ou refus dans la réponse) et les quotas atteints, puis envoie un bilan texte en Telegram à tous les utilisateurs `admin` actifs de `bot_users` (Laurent).

## Services appelés
- Google Sheets — lecture "Journal Bot ClimatPro" (doc `1AYGI1KRBJrVBRiE9VIcfq6i6-0Tcz0HF9Mjan12wJmg`, onglet gid 282010760 "Untitled"), credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Telegram — sendMessage, credential "Telegram account" (`thfKrKcwKcCWoR9V`)
- Data Tables n8n lues : `bot_users` (`MAaqIFX2KBiCvHFa`)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Regex `/limite de 30 questions/` pour détecter les quotas, alors que "Bot - Assistant" envoie "limite de 150 questions" : les quotas atteints ne sont jamais comptés (colonne toujours à 0).
- Pas de `timezone` dans les settings du workflow : l'heure du cron dépend du fuseau de l'instance n8n (le code, lui, force Europe/Paris).
- Lit tout le journal à chaque fois (`Lire journal` sans filtre) : temps et quota API Sheets croissants avec l'historique.
- Détection "hors sujet ou sensible" par regex (prix, facture, iban, mot de passe…) : approximative et dupliquée de "Detecter alerte" du Bot - Assistant.
- Onglet ciblé par gid avec nom en cache "Untitled" : fragile si le Sheet est réorganisé.
- `Lire journal` en `alwaysOutputData` : un journal vide ou illisible produit un bilan "Aucune question." sans alerte.
