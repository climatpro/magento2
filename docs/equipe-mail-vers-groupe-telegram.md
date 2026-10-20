# Equipe - Mail vers groupe Telegram

| | |
|---|---|
| ID n8n | `SCv8Qb03TbUB56NM` |
| Actif | non |
| Déclencheur | cron « toutes les 5 minutes » (Schedule Trigger) |
| Export | `workflows/equipe-mail-vers-groupe-telegram.json` |

## Rôle
Relaie dans le groupe Telegram de l'équipe les mails Gmail étiquetés « Telegram » (texte nettoyé + vraies pièces jointes, logos de signature ignorés), trace une ligne « Mail transfere » dans le fil équipe, puis bascule le libellé Gmail vers « Telegram-envoyé ». Un seul envoi par conversation (message le plus récent).

## Services appelés
- Gmail — getAll (libellé `Label_37`, 10 max, pièces jointes téléchargées), removeLabels `Label_37`, addLabels `Label_38` ; credential « Gmail account » (`QkVJEJmojKI4yW63`)
- Telegram — sendMessage (HTML) et sendDocument dans le groupe ; credential « Bot Telegram - groupe climatpro » (`gQjbmvis03Oi1VtD`)
- Data Table n8n : equipe_messages `JtuuDgi9yHe84lHj` (lecture du chat_id via la dernière ligne `source = telegram` ; insertion d'une ligne `source = mail`, `traite = true`)

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow jamais publié (`activeVersionId` null) : inactif, à activer ou à archiver.
- Identifiants de libellés Gmail en dur (`Label_37`, `Label_38`) : cassent si les libellés sont recréés.
- Bascule des libellés (branche « fin ») indépendante du succès des envois Telegram : un mail dont l'envoi échoue est quand même marqué « envoyé » et perdu.
- `onError: continueRegularOutput` sur « Publier la piece jointe » et « Enregistrer dans le fil » : échecs silencieux.
- Détection des logos par regex sur le nom (`CID_`, `image\d`, `Outlook-`, `logo`) ou taille < 40 Ko : une vraie photo légère peut être écartée, un logo mal nommé passer.
- Taille des pièces jointes calculée en parsant la chaîne `fileSize` (« 1.2 MB ») ; seuil 45 Mo.
- Coupure du corps sur une regex RGPD/disclaimer (fr/en) : fragile selon les signatures.
- Limite 10 mails par passage ; le chat_id dépend de l'existence d'une ligne `telegram` dans la table (sinon exception).
