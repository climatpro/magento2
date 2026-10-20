# ClimatPro — sauvegarde et documentation n8n

Dépôt de sauvegarde **lecture seule** de l'instance n8n de ClimatPro.

| Dossier | Contenu |
|---|---|
| `workflows/` | Un JSON nettoyé par workflow (sans pinData, staticData ni secret). Importable dans n8n. |
| `docs/` | Une fiche par workflow + `INDEX.md` (tableau + schéma des dépendances) + `ALERTES.md`. |
| `scripts/` | `export.sh` relance l'export complet ; `check_export.py` contrôle les fichiers. |
| `proposals/` | Propositions non déployées (ex. « clients posés sans entretien »). |

## Relancer l'export

```bash
export N8N_URL=https://votre-n8n.exemple.fr
export N8N_API_KEY=...        # jamais dans un fichier, jamais commité
scripts/export.sh --check     # teste l'accès
scripts/export.sh             # exporte dans workflows/
python3 -I scripts/check_export.py > /dev/null   # contrôles (0 erreur attendu)
python3 -I scripts/build_index.py                # régénère docs/INDEX.md
```

Le script n'envoie que des requêtes `GET` à l'API n8n. Les Data Tables ne sont jamais exportées
(certaines contiennent des identifiants).
