# Climapro - Images tableau de bord

| | |
|---|---|
| ID n8n | `awPLiSdGvFBFGK14` |
| Actif | oui |
| Déclencheur | cron toutes les 15 min (node "Toutes les 15 min") + déclencheur manuel (node "Lancer a la main") |
| Export | `workflows/climapro-images-tableau-de-bord.json` |

## Rôle
Toutes les 15 min, compare les images des dossiers Drive « Tableau de bord ClimatPro > images » et « > icones » (md5) avec la table `images_tableau`, envoie les nouvelles/modifiées dans la médiathèque WordPress climatpro.fr, supprime l'ancienne version WP et note l'URL finale dans la table (lue par "Page - Tableau technicien").
En parallèle, liste les objets dictés dans les mémos Todoist (`Icône : mot`) sans icône dans Drive et réécrit le fichier Drive `icones-a-creer.md` destiné à Codex.

## Services appelés
- WordPress climatpro.fr REST (GET /wp-json/wp/v2/users/me pour tester l'accès ; POST /wp/v2/media ; DELETE /wp/v2/media/{id}?force=true) — HTTP Request, credential "WordPress climatpro.fr" (`d1SeVJUDTXBOklWX`, Basic Auth / mot de passe d'application)
- Google Drive API (GET /drive/v3/files avec filtre sur 2 dossiers ; GET /files/{id}?alt=media ; PATCH /upload/drive/v3/files/1SHdNeJn1wMEY8QGPYKIGysZ9IeCbVDRK) — HTTP Request, credential "Google Drive account 2" (`54fd9ApHaDydoOJv`)
- Todoist API (GET /api/v1/tasks/filter `query=@memo`, limit 200) — HTTP Request, credential "Todoist account" (`feB4B4HQds0e2tFC`)
- Data Tables n8n : `images_tableau` (`gkJQL9liZvE8M2Op`) — lecture (node "Lire table images") et upsert sur `nom` (node "Enregistrer dans la table")

## Modèle IA
Aucun.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Identifiants Drive en dur : dossiers `1c2zZA2AqNarxkwsH62RQUXdK0r_RXqB_` et `1uIhYG4xxOMhXr9gCGLnoYrdfGSbV22FU` (dans 3 nodes), fichier `1SHdNeJn1wMEY8QGPYKIGysZ9IeCbVDRK` ; la note du node "Lister images Drive" cite un autre id (`1qaVFnDuR2Gd43MoBU3w06JHn7Gq28MTA`) : documentation incohérente.
- Description du workflow tronquée ("lue par Page - Tableau technici…").
- Pas de pagination Drive (`pageSize=200`, pas de `nextPageToken`) ni Todoist (`limit=200`).
- "Verifier WordPress" sans `onError` : si le mot de passe d'application expire, le workflow échoue toutes les 15 min (voulu, mais bruyant) ; "Envoyer dans WordPress" sans `onError` non plus.
- "Supprimer ancienne image WP" en `continueRegularOutput` : les échecs laissent des médias orphelins dans WordPress.
- "Mettre a jour icones-a-creer.md" en `continueRegularOutput` : un échec de réécriture passe inaperçu.
- Les SVG passent le filtre d'extension mais WordPress les refuse par défaut (échec d'upload bloquant).
- Dépend du format de réponse Todoist (`results`) et d'un motif texte `Icône : mot` écrit par "Climapro - Mémos vocaux" : couplage par convention.
- Deux déclencheurs (manuel + cron) sur la même chaîne : un lancement manuel pendant un passage cron peut uploader deux fois la même image.
