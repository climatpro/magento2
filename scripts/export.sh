#!/usr/bin/env bash
# Export lecture seule de tous les workflows n8n vers workflows/<nom>.json
#
# Pre-requis : N8N_URL (ex. https://n8n.exemple.fr) et N8N_API_KEY dans l'environnement.
# N'ecrit RIEN sur le serveur : uniquement des GET /api/v1/workflows.
# Les Data Tables ne sont PAS exportees (certaines contiennent des mots de passe).
#
# Usage : scripts/export.sh            # export complet
#         scripts/export.sh --check    # verifie seulement l'acces API
set -euo pipefail

: "${N8N_URL:?N8N_URL manquant (ex. export N8N_URL=https://n8n.exemple.fr)}"
: "${N8N_API_KEY:?N8N_API_KEY manquant}"
N8N_URL="${N8N_URL%/}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/workflows"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

api() { curl -sS --fail -H "X-N8N-API-KEY: $N8N_API_KEY" -H "Accept: application/json" "$N8N_URL/api/v1$1"; }

if [[ "${1:-}" == "--check" ]]; then
  api "/workflows?limit=1" >/dev/null && echo "OK : API n8n joignable en lecture." && exit 0
fi

# 1. Liste complete (pagination par curseur), nodes exclus pour aller vite
cursor=""
: > "$TMP/list.ndjson"
while :; do
  page="$(api "/workflows?limit=100&excludePinnedData=true${cursor:+&cursor=$cursor}")"
  echo "$page" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); [print(json.dumps(w)) for w in d["data"]]' >> "$TMP/list.ndjson"
  cursor="$(echo "$page" | python3 -I -c 'import json,sys; print(json.load(sys.stdin).get("nextCursor") or "")')"
  [[ -z "$cursor" ]] && break
done
python3 -I -c 'import json,sys; print(json.dumps([json.loads(l) for l in open(sys.argv[1])]))' "$TMP/list.ndjson" > "$TMP/list.json"
n="$(python3 -I -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$TMP/list.json")"
echo "$n workflow(s) trouve(s)."

# 2. Export unitaire, nettoyage, nom de fichier stable
mkdir -p "$OUT"
python3 -I "$ROOT/scripts/slug.py" "$TMP/list.json" | while read -r id slug; do
  api "/workflows/$id?excludePinnedData=true" > "$TMP/$id.json"
  python3 -I "$ROOT/scripts/clean_workflow.py" "$TMP/$id.json" "$OUT/$slug.json"
  echo "  -> workflows/$slug.json"
done

# 3. Signaler les fichiers orphelins (workflow supprime ou renomme sur le serveur)
python3 -I "$ROOT/scripts/slug.py" "$TMP/list.json" | awk '{print $2".json"}' | sort > "$TMP/expected.txt"
ls "$OUT" | sort > "$TMP/present.txt"
if orphans="$(comm -13 "$TMP/expected.txt" "$TMP/present.txt")" && [[ -n "$orphans" ]]; then
  echo "Fichiers presents dans workflows/ mais absents du serveur (a supprimer a la main ?) :"
  echo "$orphans" | sed 's/^/  /'
fi
echo "Termine. Relancer scripts/check_export.py pour les controles."
