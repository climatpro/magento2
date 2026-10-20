# Bot - Assistant

| | |
|---|---|
| ID n8n | `fb86kJwEmjNC5Vcd` |
| Actif | oui |
| Déclencheur | Telegram Trigger "Message Telegram" (updates `message`, conversations privées uniquement), webhookId `af724f16-1596-4daf-8b17-15caa09fc242` |
| Export | `workflows/bot-assistant.json` |

## Rôle
Assistant Telegram libre pour Laurent et les techniciens : un AI Agent (Claude Haiku) choisit parmi 14 outils (planning, clients, matériel devis, détail RDV, codes défaut, pièces Hitachi/Toshiba/Daikin, prix Sonepar admin, expert diagnostic, mémos, clients sans entretien, camions), lit les photos de plaques, répond en texte simple et propose un message "demande de prix" distributeur avec bouton email. Liste blanche `bot_users`, quota 150 questions/jour (hors admin), alertes à Laurent sur sujets sensibles ou refus, journal Google Sheet. Remplace "Bot - Questions (V2)".

## Services appelés
- Telegram — credential "Telegram account" (`thfKrKcwKcCWoR9V`) : trigger, envoi réponse (HTML), téléchargement photo (`Telecharger photo`), alerte admins ("Alerter Laurent"), bulle copie avec bouton inline ("Envoyer copie")
- Anthropic — node `lmChatAnthropic` "Haiku", credential "Anthropic account 2" (`UtZzlYk97MvjuDan`)
- Google Sheets — append "Journal Bot ClimatPro" (doc `1AYGI1KRBJrVBRiE9VIcfq6i6-0Tcz0HF9Mjan12wJmg`, onglet gid 282010760), credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- n8n (même instance) — URL `https://n8n.climatpro.fr/webhook/mailto?to=…&cc=contact@climatpro.fr&s=…&b=…` construite dans "Construire bulle copie" et ouverte par le bouton Telegram (webhook d'un autre workflow, non appelé directement)
- Interfast, sites fournisseurs, etc. : uniquement indirectement via les sous-workflows outils (ci-dessous)
- Data Tables n8n lues : `bot_users` (`MAaqIFX2KBiCvHFa`), `fournisseurs_pieces` (`G8J0dx9EwoyaTfto`)

## Modèle IA
Anthropic `claude-haiku-5-5` ("Claude Haiku 5.5") dans le node "Haiku" (maxTokensToSample 1024, thinking désactivé), moteur du node AI Agent "Assistant" (maxIterations 8, images binaires transmises, mémoire fenêtre 6 messages par chat `tg2-<chat_id>`). System prompt de ~13 000 caractères : règles métier (recherche client systématique, codes défaut en 3 blocs, demande de prix distributeur sans référence ni prix, rôle admin pour Sonepar, lecture seule) et règles de style Telegram.

## Sous-workflows appelés
- Outil - Planning (`zA9fv7IqJnrBuRRy`) via node Tool `planning`
- Outil - Fiche client (`yj2W2NXNAbFRiuN6`) via node Tool `fiche_client`
- Outil - Recherche client (`FHVtoHPBvB59ExMT`) via node Tool `recherche_client`
- Outil - Materiel devis (`RkGCPcG8e1gI0knk`) via node Tool `materiel_devis`
- Outil - Detail RDV (`0bCdxnRh9exHqvvM`) via node Tool `detail_rdv`
- Outil - Dispo Hitachi (`p7VfJ2HTKTctJBsv`) via node Tool `dispo_hitachi`
- Outil - Sonepar (`nUxjWTbY2DyKPetM`) via node Tool `prix_sonepar` (rôle passé par le code)
- Outil - Code defaut (`uWkW4FbbnjkmwTXb`) via node Tool `code_defaut`
- Outil - Dispo Toshiba (`4PjuGOfWCDdkuoPq`) via node Tool `dispo_toshiba`
- Outil - Expert diagnostic (`LA38f9HqFWwMlXjY`) via node Tool `expert_diagnostic`
- Outil - Memos (`6jYK4PkJgDjs4Zf2`) via node Tool `memos` (rôle passé par le code)
- Outil - Clients sans entretien (`NvBI84JhjfoUH5FZ`) via node Tool `clients_sans_entretien`
- Outil - Camions (`NXr5qAKWTQU0nVoY`) via node Tool `camions`
- Outil - Dispo Daikin (`di2cU3TRSnyS2BdQ`) via node Tool `dispo_daikin`

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Quota journalier (150) stocké dans `$getWorkflowStaticData('global')` : remis à zéro à chaque redéploiement/redémarrage de n8n, et compteur incrémenté même pour les messages vocaux ignorés.
- Incohérence avec "Bot - Bilan hebdo" qui cherche "limite de 30 questions" dans les réponses alors que le message réel dit "limite de 150 questions" : les quotas atteints ne sont jamais comptés dans le bilan.
- Agent en `onError: continueRegularOutput` → message générique "Desole, je n ai pas pu repondre" sans trace de l'erreur ; `maxTokensToSample` 1024 peut tronquer les réponses longues (3 blocs + message distributeur).
- Sécurité des prix d'achat déléguée au prompt (prix_sonepar "réservé admin") mais le rôle est bien injecté par le code ; en revanche les prix portail/public Hitachi-Toshiba-Daikin sont renvoyés à tous les rôles selon le prompt.
- Garde-fou "Construire bulle copie" (suppression des références/prix par regex avant envoi au distributeur) fragile : dépend de formats de référence et de prix devinés par regex.
- URL `https://n8n.climatpro.fr/webhook/mailto` et cc `contact@climatpro.fr` en dur ; dépend d'un webhook externe non documenté ici.
- Détection "sujet sensible" / "refus du bot" par regex (Detecter alerte) : faux positifs/négatifs probables ; alertes envoyées à tous les admins.
- Journal Google Sheet en `onError: continue` : perte silencieuse du journal ; `Lire fournisseurs` idem.
- Sticky note obsolète (ne mentionne que 4 outils, 14 réellement branchés).
- 14 sous-workflows référencés par ID : la suppression de l'un casse l'agent silencieusement (outil absent).
- Prompt système très long (13 k caractères, ~3-4 k tokens) rejoué à chaque itération de l'agent : coût et latence.
