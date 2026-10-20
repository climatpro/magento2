# Bot - Brief 18h (ZivtrXedkHo5phMD)

| | |
|---|---|
| ID n8n | `ZivtrXedkHo5phMD` |
| Actif | oui |
| Déclencheur | 2 crons (timezone Europe/Paris) : "Chaque soir 18h" `0 0 18 * * 0-5` (dimanche à vendredi 18h00) et "Chaque matin 8h15" `0 15 8 * * 1-5` (lundi à vendredi 8h15) |
| Export | `workflows/bot-brief-18h--ZivtrXedkHo5phMD.json` |

## Rôle
Le soir : lit le planning Interfast du lendemain (lundi si vendredi), met en cache un résumé matériel par devis (Haiku), enrichit chaque RDV (détail intervention, fiche client, mémoire client), puis envoie en Telegram : à chaque technicien actif (`brief_18h`) ses interventions, et aux admins l'alerte camions (Christophe/Axel ensemble ou séparés) + mémo clients. Le matin : récap planning du jour par équipe aux admins. Chaque envoi est journalisé dans le Google Sheet "Journal Bot ClimatPro".

## Services appelés
- Interfast — uniquement via le sous-workflow "Interfast - Lecture" (ops `events_jour`, `rdv_jour`, `devis_par_ref`, `devis`, `intervention`, `client`)
- Anthropic — HTTP Request POST https://api.anthropic.com/v1/messages (node "Résumer matériel (Haiku)"), credential prédéfinie "Anthropic account 2" (`UtZzlYk97MvjuDan`), timeout 30 s
- Telegram — sendMessage HTML, credential "Telegram account" (`thfKrKcwKcCWoR9V`)
- Google Sheets — append "Journal Bot ClimatPro" (doc `1AYGI1KRBJrVBRiE9VIcfq6i6-0Tcz0HF9Mjan12wJmg`, gid 282010760), credential "Google Sheets account" (`fKAETwT6ij09juV8`)
- Data Tables n8n : `cache_devis` (`F66omRHgUbs2aeoL`) lecture + écriture (upsert sur `ref`) ; `bot_users` (`MAaqIFX2KBiCvHFa`) lecture

## Modèle IA
Anthropic `claude-haiku-5-5` dans le node HTTP "Résumer matériel (Haiku)" : résume en une ligne (≤ 120 car.) le matériel à charger à partir des lignes d'un devis signé, résultat stocké dans `cache_devis`.

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes Execute Workflow "Lire planning", "Lire RDV", "Chercher devis", "Lire devis", "Lire intervention", "Lire client"
- Outil - Memoire client (`99B4KwoLPMWmJuNc`) via node Execute Workflow "Mémoire client"

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Identifiants techniciens Interfast codés en dur (`JULIEN 5198`, `AXEL 9965`, `LAURENT 5066`, `CHRISTOPHE 5069`) et remappage automatique Julien → Axel : à corriger à chaque changement d'équipe.
- Ordre d'exécution critique : les branches "cache matériel" et "brief" partent du même node ; le brief lit le cache après, en s'appuyant sur l'ordre v1 des connexions (sticky note "Tourne AVANT le bas"). Un réagencement casse le matériel du brief ("pas encore résumé").
- `cache_devis` : un résumé `ok` n'est jamais rafraîchi (devis modifié après mise en cache = matériel périmé) ; statut `introuvable`/`erreur` re-tenté à chaque run.
- "Préparer interventions" lève une exception si Interfast est KO : aucun message, aucune alerte.
- "Lire client" et "Mémoire client" lisent `$('Journée vide ?').item` (appariement par item) après des Execute Workflow en `onError: continueRegularOutput` : décalage possible.
- Logique "vendredi → lundi" dupliquée dans 4 endroits (expressions des 2 nodes Lire planning/RDV, Rédiger briefs, Ajuster vendredi) avec rustines regex sur l'en-tête.
- Cron du soir inclut le dimanche (`0-5`) : les techniciens sont exclus par le code (`!dimanche`), seuls les admins reçoivent.
- Journal Google Sheet : copie intégrale des briefs (téléphones et notes clients) dans un Sheet.
- Messages tronqués à 4 000 caractères ("... (suite tronquée)") sans découpage multi-messages.
- Sticky note partiellement obsolète (ne mentionne pas le run du matin ni Mémoire client ni l'alerte camions).
