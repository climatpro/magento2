# Alertes — état au 20/10/2026

Lecture seule : rien n'a été modifié sur le serveur. Chaque point renvoie à la fiche du workflow dans `docs/`.
Ordre : du plus urgent au moins urgent.

## 0. Le dépôt GitHub `climatpro/magento2` est PUBLIC

Constaté le 20/10/2026 après le premier push. Les secrets (clés, jetons, mots de passe, credentials) sont bien retirés des exports.
Mais les workflows contiennent d'autres données qui n'ont rien à faire en public :

- les **coordonnées GPS du domicile** du gérant (`MAISON` dans [Quartix - Historique](quartix-historique.md)) ;
- des **adresses personnelles** et des informations privées (holding, SCI, famille) dans [Climapro - Mémos vocaux](climapro-memos-vocaux.md) ;
- le **domaine n8n** et la liste des chemins de webhook. Certains webhooks ne sont protégés que par leur chemin, par exemple `fiche-contact-iphone-k7q2` et `devis-mail-valider` ;
- les identifiants Telegram, les prénoms des techniciens, les identifiants de dossiers Drive et de Sheets.

**À faire tout de suite** : passer le dépôt en privé (GitHub > Settings > General > Danger Zone > Change visibility).
Ensuite, changer le chemin des webhooks protégés seulement par leur nom, et sortir l'adresse du domicile du code.

## 1. Sécurité

| Gravité | Workflow | Problème | Action proposée |
|---|---|---|---|
| Haute | [Outil - Sonepar](outil-sonepar.md) (actif) | Clé `x-cle` du webhook écrite en dur dans le code du node « Entree ». Le webhook donne d'office le rôle admin. Même clé que Claude - Pieces detachees. | Déplacer la clé dans un credential Header Auth, puis la changer (elle a circulé dans les exports). |
| Haute | [Claude - SCAN vers MAIL pour PJ](claude-scan-vers-mail-pour-pj.md) (inactif) | Webhook sans aucune authentification qui envoie un mail depuis la boîte ClimatPro. | Archiver, ou ajouter une auth avant toute réactivation. |
| Moyenne | [Import - Codes Hitachi (temporaire)](import-codes-hitachi-temporaire.md) (inactif) | Jeton en dur dans l'option `onlyRunIf` du webhook. | Archiver (import terminé). |
| Moyenne | [Claude - Pieces detachees](claude-pieces-detachees.md) (inactif) | Même clé `x-cle` en dur que Sonepar. | Voir Sonepar. |
| Moyenne | Tables `daikin_spb_acces`, `hiparts_acces`, `sonepar_acces`, `quartix_acces`, `tableau_secrets` | Mots de passe et jetons (browserless, bot Telegram, secret de cookie) en clair dans des Data Tables, lisibles par tout workflow. | Migrer vers des credentials n8n. `quartix_acces` n'est plus utilisé en prod : à vider. |
| Moyenne | [Outil - Fiche contact iPhone](outil-fiche-contact-iphone.md), [Page - Mailto](page-mailto.md), [Climapro - Devis acceptes par mail](climapro-devis-acceptes-par-mail.md) (lien Valider) | Webhooks publics protégés seulement par un chemin difficile à deviner ou un jeton `Math.random()`. | Acceptable à court terme ; ajouter une signature HMAC comme sur le tableau de bord. |
| Basse | [Outil - Fiche contact iPhone](outil-fiche-contact-iphone.md) | Jeton du bot Telegram dans l'URL HTTP, donc visible dans l'historique des exécutions. | Passer par le node Telegram et son credential. |

## 2. Modèles IA

Tous les identifiants Claude utilisés sont **valides** aujourd'hui ; aucun n'est retiré. Deux familles sont d'ancienne génération,
et une version publiée tourne encore sur Gemini alors que le brouillon est passé à Claude.

| Workflow | Actif | Modèle | Constat |
|---|---|---|---|
| [Climapro - Mémos vocaux](climapro-memos-vocaux.md) | oui | `claude-haiku-4-5-20251001` | Génération précédente. Haiku 5.5 coûte environ 10 fois moins cher ($0,10 / $0,50 par million de jetons contre $1 / $5). |
| [Prix achat fournisseurs - Extraction factures](prix-achat-fournisseurs-extraction-factures-hac-econology.md) | oui | `claude-haiku-4-5-20251001` | Idem. Gros volume (lots de 40 PDF par nuit) : c'est là que la migration rapporte le plus. |
| [Archives factures - Extraction index](archives-factures-extraction-index.md) | non | `claude-haiku-4-5-20251001` | Idem, si relancé. |
| [Outil - Expert diagnostic](outil-expert-diagnostic.md) | oui | `claude-sonnet-5` | Génération précédente. `claude-sonnet-5-5` est au même prix. |
| [Outil - Code defaut Hitachi](outil-code-defaut-hitachi.md) | oui | `claude-sonnet-5` | Idem. |
| [📧 Factures Gmail → Google Drive v3](factures-gmail-google-drive-climatpro-v3-recup-drive.md) | oui | publié : `gemini-2.5-flash` ; brouillon : `claude-haiku-5-5` | **Le passage à Claude Haiku n'a jamais été publié.** La prod tourne sur Gemini avec une clé API en paramètre d'URL. |
| [Tri scans Brother](tri-scans-brother.md), [TEST - Gemini audio](test-gemini-audio-a-supprimer.md) | non | `gemini-2.5-flash` | Inactifs. |
| [Plaud vers Interfast CRM](plaud-vers-interfast-crm.md) | oui | `claude-sonnet-5-5` | La description dit « Haiku » : la doc est fausse, pas le modèle. Sonnet est-il voulu ? C'est 20 fois le prix de Haiku 5.5. |

Points techniques à garder en tête lors d'une migration vers Haiku 5.5 / Sonnet 5.5 : `budget_tokens` est refusé,
le préremplissage de la réponse est refusé, `tool_choice` forcé est refusé sur Sonnet 5.5. Les workflows qui appellent
l'API en HTTP direct (`anthropic-version` en dur) sont à relire un par un.

## 3. Credentials

- **Aucun node ne référence un credential manquant.** Les 16 credentials utilisés existent tous sur le serveur.
- `Unnamed credential` (type MCP OAuth2) est celui de Plaud dans [Plaud vers Interfast CRM](plaud-vers-interfast-crm.md) : à renommer « Plaud MCP » pour s'y retrouver.
- Cinq credentials ne sont utilisés par **aucun** workflow : `Google Drive account` (le premier), `Google Gemini(PaLM) Api account`, `… account 3`, `… account 4`, `… account 5`. `Query Auth account` n'est utilisé que par la version publiée de Factures Gmail (clé Gemini) et deviendra inutile une fois le brouillon Claude publié. Candidats au ménage.
- Deux credentials Anthropic coexistent (`Anthropic account` et `Anthropic account 2`). Les workflows sur Haiku 4.5 et Plaud utilisent le premier, tous les autres le second. Vérifier que les deux clés pointent sur le même compte de facturation.
- Sonepar, hi-parts, browserless et Daikin n'ont pas de credential n8n : leurs identifiants sont dans des Data Tables (section 1). Interfast et Quartix (prod) passent bien par des credentials.

## 4. Doublons et restes à archiver

| Workflow inactif | Doublon de / raison | Recommandation |
|---|---|---|
| [Bot - Brief 18h](bot-brief-18h--Lw8Dv81qmxIMwXVI.md) `Lw8Dv8…` | V1 du brief actif `ZivtrX…` | Archiver. |
| [Interfast - Lecture](interfast-lecture--MOZo7wkYxjOghKVZ.md) `MOZo7w…` | V1 du sous-workflow actif `Qgn9xL…`, même nom | Archiver **après** le brief V1 (c'est son seul appelant). |
| [Bot - Questions (V2)](bot-questions-v2.md) | Remplacé par Bot - Assistant ; même bot Telegram, conflit de webhook s'il est réactivé | Archiver. |
| [Assistant ClimatPro — Identification Laurent](assistant-climatpro-identification-laurent.md) | Squelette vide (1 node) | Archiver. |
| [Interfast — Test connexion GET](interfast-test-connexion-get.md), [Quartix - Test connexion](quartix-test-connexion.md) | Tests ponctuels | Archiver. |
| [TEMP - Nettoyage plaud_traites](temp-nettoyage-plaud-traites.md), [TEST - Banc WhatsApp](test-banc-whatsapp-haiku-vs-sonnet-a-supprimer.md), [TEST - Gemini audio](test-gemini-audio-a-supprimer.md) | Marqués « à supprimer » | Archiver. |
| [Tri scans Brother](tri-scans-brother.md) | Recouvre Factures Gmail → Drive (même Sheet de suivi) ; plusieurs bugs (dédup cassée, renommage sans effet) | Archiver, ou corriger avant réactivation. |
| [Quartix - Duree sur place](quartix-duree-sur-place-lecture-seule.md) | Logique dupliquée avec Quartix - Historique | Garder si utile, sinon archiver. |
| [Import - Codes Hitachi (temporaire)](import-codes-hitachi-temporaire.md) | Import ponctuel terminé | Archiver. |

Les quatre workflows « Archives factures » et « Equipe - Mail vers groupe Telegram » sont inactifs mais récents (16-19/10) : ce sont des chantiers en cours, pas des doublons.

## 5. Incohérences repérées en passant

- **Quota du bot jamais compté dans le bilan.** [Bot - Bilan hebdo](bot-bilan-hebdo.md) cherche « limite de 30 questions », alors que [Bot - Assistant](bot-assistant.md) écrit « limite de 150 questions ».
- **Technicien 5198 = Axel ou Julien selon l'outil.** Axel dans Outil - Camions et Outil - Detail RDV, Julien dans Outil - Fiche client. Les identifiants techniciens sont copiés en dur dans au moins 6 workflows.
- **Deux versions publiées ≠ brouillon** : Outil - Sonepar et Factures Gmail → Drive. Ce que vous voyez dans l'éditeur n'est pas ce qui tourne. L'export garde les deux (`versionPubliee` dans le JSON).
- **Erreurs silencieuses partout.** La majorité des appels Interfast sont en `onError: continueRegularOutput` : une panne Interfast se lit « aucun client trouvé » ou « 2 camions libres ». Aucun workflow n'a d'`errorWorkflow`. Un workflow d'erreur unique qui prévient Laurent sur Telegram couvrirait tout.
- **Pagination à nombre de pages fixe** : plusieurs workflows lisent « toutes » les interventions ou fiches avec un nombre de pages figé (15, 32, 40 pages de 100), sans vérifier que la dernière page est incomplète. Aujourd'hui, [Climapro - Clients sans entretien](climapro-clients-sans-entretien.md) lit 20 pages pleines sur 40 : pas encore de perte, mais aucune alerte le jour où la limite sera atteinte. Voir `proposals/clients-sans-entretien.md`.
