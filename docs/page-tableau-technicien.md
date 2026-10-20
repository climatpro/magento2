# Page - Tableau technicien

| | |
|---|---|
| ID n8n | `vKYK5N7OxtU2uZyI` |
| Actif | oui |
| Déclencheur | 4 webhooks GET : `/webhook/tableau` (page), `/webhook/tableau-connexion` (retour Telegram Login), `/webhook/tableau-fait` (cocher un mémo), `/webhook/tableau-partage` (partager / ranger un mémo) ; servis derrière `app.climatpro.fr` |
| Export | `workflows/page-tableau-technicien.json` |

## Rôle
Tableau de bord web rendu côté serveur (sans IA) pour Laurent (admin, vue d'équipe et "Voir comme"), Christophe et Axel : planning Interfast 8 jours avec téléphones clients et itinéraires, mémos et commandes Todoist (boutons Fait / partage / rangement), clients équipés sans entretien, météo, devis signés à planifier, et pour l'admin seul la carte des véhicules Quartix et le fil Telegram de l'équipe. Identité par cookie `cp_session` signé (HMAC, 1 an) obtenu via Telegram Login.

## Services appelés
- Interfast — via le sous-workflow "Interfast - Lecture" (ops `events_jour`, `rdv_jour`) et en direct GET `https://app.inter-fast.fr/v1/client/{id}` (node `Appel fiches clients`, credential "Interfast API" `GgJ5wsyGIUSWY0cN`, lecture des téléphones)
- Todoist REST v1 (credential "Todoist account" `feB4B4HQds0e2tFC`) : GET `/tasks/filter` (mémos, commandes), GET `/tasks/completed/by_completion_date` (commandes cochées sur 26 h), GET `/tasks/{id}` ; écritures : POST `/tasks/{id}/close` (Fait), POST `/tasks/{id}` (labels de partage), POST `/tasks/{id}/move` (rangement)
- Google Drive API (credential "Google Drive account 2" `54fd9ApHaDydoOJv`) : lecture de `style.css` dans le dossier `1e1McsMTi-RGduM-oBTwVAGmb2sV_qV3x`, CSS de secours intégré si absent
- Open-Meteo (`api.open-meteo.com`, lat 43.60 / lon 6.95, 1 et 8 jours, sans credential)
- Telegram Login Widget (bot `Climatpro06_bot`) vérifié par HMAC avec le token du bot ; médiathèque WordPress `climatpro.fr/wp-content/uploads/2026/10/` ; Leaflet (unpkg) + tuiles openstreetmap.fr ; liens Waze / Google Maps ; depuis la page, appels aux webhooks n8n `/webhook/equipe-*` (fil équipe, autre workflow) avec jeton signé `fil.v1`
- Data Tables lues : `ZS80JIsncc2f3ZED` (secrets : `telegram_bot_token`, `cookie_secret`), `D0StwthqUQF0nV7Z` (dashboard_acces : `telegram_id`, `nom`, `role`, `interfast_ids`, `actif`), `wdM1D4E3ZOAmhvoy` (clients sans entretien), `gkJQL9liZvE8M2Op` (images_tableau), `nucvI8QpMgKtoMfG` (memos_categories), `45PSs7FELv97nkCn` (quartix_etat), `dJ4ZIO2PdhYlt95o` (quartix_jours), `0U759buKi8psn4V5` (devis_a_planifier)
- Data Table écrite : `OAX0BQo3Hczx8xLF` (tableau_connexions_utilisees, anti-rejeu des paquets Telegram)

## Modèle IA
Aucun

## Sous-workflows appelés
- Interfast - Lecture (`Qgn9xL6dGSAcq4Zv`) via nodes `Lire interventions` et `Lire RDV`

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- SHA-256 / HMAC réimplémentés à la main en JavaScript et copiés-collés dans 7 nodes (`Verifier acces`, `Verifier Telegram`, `Verifier demande`, `Verifier partage`, `Partage memos`, `Liens Fait`, `Fil equipe`) : toute correction doit être répétée partout.
- Cookie de session valable 1 an ; seule révocation : `actif = false` dans dashboard_acces ; le secret `cookie_secret` est relu dans une Data Table à chaque requête (3 à 4 lectures de tables avant tout rendu).
- Sticky note et description obsolètes : elles décrivent encore un jeton `?t=` dans l'URL, supprimé au profit du cookie Telegram.
- Nombreux identifiants en dur : techniciens Interfast (5066, 5069, 9965, 5198), projets / sections Todoist (`6hh423vJrW7RvQQg`, `6hh423vw4vGgHFPw`, `6hh3xGRJ424mj3J6`, `6hh423vGr88f287j`, `6hh4248WJ2ppj3M8`, `6hh4246PVq2H9Fp8`), prénoms autorisés au partage (`christophe`, `axel`), dossier Drive, coordonnées météo, domaine `app.climatpro.fr`, URL des images WordPress.
- Limites silencieuses : 200 tâches Todoist sans pagination, 30 clients pour les fiches, 6 clients sans entretien affichés, 5 jours de mémos.
- `onError: continueRegularOutput` sur presque toutes les lectures (Interfast, Todoist, Drive, météo, tables) : la page se rend incomplète sans signalement.
- Workflow très lourd (73 nodes, `Construire page` ≈ 36 k caractères, `Carte vehicules` ≈ 25 k, `Fil equipe` ≈ 14 k, CSS de secours ≈ 22 k intégré) ; rendu entièrement recalculé à chaque GET avec une dizaine d'appels externes, sans cache ; `saveDataSuccessExecution: none` (pas de trace des exécutions réussies).
- Dépend de tables alimentées par d'autres workflows (clients sans entretien, Quartix positions / historique, images tableau de bord, devis signés à planifier, memos_categories) et des webhooks `/webhook/equipe-*` d'un autre workflow : une panne en amont fige les données affichées.
- Table anti-rejeu `tableau_connexions_utilisees` jamais purgée (croissance continue) ; `Lire acces` charge toutes les lignes sans filtre.
- Nodes Respond to Webhook de versions hétérogènes (1.1 et 1.5) ; `Fil equipe` en mode pilote (`FIL_POUR_TOUS = false`) avec jeton 12 h signé par le même `cookie_secret`.
