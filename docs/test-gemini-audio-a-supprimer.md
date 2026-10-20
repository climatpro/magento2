# TEST - Gemini audio (a supprimer)

| | |
|---|---|
| ID n8n | `EpLk9dpFfWTMW3Y6` |
| Actif | non |
| Déclencheur | Manual Trigger « Test » |
| Export | `workflows/test-gemini-audio-a-supprimer.json` |

## Rôle
Test temporaire de transcription audio par Gemini pour le bot : télécharge un fichier d'exemple (`Example.ogg` sur Wikimedia) puis le transcrit.
Aucune donnée ClimatPro, aucune sortie persistée.

## Services appelés
- HTTP Request `GET https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg` (User-Agent `ClimatProBot/1.0 (contact@climatpro.fr)`), réponse en fichier binaire.
- Google Gemini — node « Transcrire » (`@n8n/n8n-nodes-langchain.googleGemini`, audio → transcribe), credential « Google Gemini(PaLM) Api account 2 » (`dbBozPeQkcHzKBdI`).
- Data Tables n8n : aucune.

## Modèle IA
Google `models/gemini-2.5-flash`, node « Transcrire » : transcription audio.

## Sous-workflows appelés
aucun

## Appelé par
Aucun autre workflow exporté ne l'appelle (déclencheur autonome, ou appel externe : Claude, iPhone, navigateur).

## Points fragiles
- Workflow de test marqué « a supprimer », inactif depuis le 2026-10-09.
- Paramètres contradictoires dans « Transcrire » : `inputType: binary` **et** `audioUrls` renseigné (reliquat).
- URL d'exemple en dur ; adresse e-mail de contact exposée dans le User-Agent.
