#!/usr/bin/env python3
"""Nettoie un export de workflow n8n pour Git.

- supprime pinData, staticData et les champs volatils (versionId, scopes, ...)
- ne garde des credentials que la reference {id, name} (jamais de valeur)
- masque les valeurs qui ressemblent a un secret ecrit en dur
- trie les cles et indente : diff stable d'un export a l'autre

Usage : clean_workflow.py <entree.json> <sortie.json>
        clean_workflow.py --stdin <sortie.json>
"""
import json, re, sys

KEEP = ["id", "name", "active", "description", "createdAt", "updatedAt",
        "settings", "tags", "nodes", "connections", "nodeGroups", "meta"]
DROP_IN_NODE = {"webhookId"}  # identifiant volatil regenere a l'import

# Cle de parametre dont la valeur en dur est un secret (nom exact, pas "outputKey" ni "keyName")
SECRET_KEY = re.compile(r"^(x-)?(api[-_]?key|key|token|secret|password|mot_de_passe|passwd|authorization|bearer|access[-_]?token|bot[-_]?token|x-cle|x-key)$", re.I)
# Nom d'en-tete / de parametre HTTP (paire {name, value}) considere comme sensible
SECRET_NAME = re.compile(r"(api[-_]?key|x-cle|x-key|token|secret|password|authorization|bearer)", re.I)
SECRET_VALUE = [
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"),     # jeton bot Telegram
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),       # cle Anthropic
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),          # cle Google
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),            # jeton GitHub
    re.compile(r"\bxox[abp]-[A-Za-z0-9-]{20,}"),       # jeton Slack
]
REDACTED = "<SECRET-RETIRE>"


def redact_str(s: str) -> str:
    for rx in SECRET_VALUE:
        s = rx.sub(REDACTED, s)
    return s


def scrub(obj, parent_key=""):
    """Parcours recursif : masque les valeurs en dur sous des cles sensibles."""
    if isinstance(obj, dict):
        out = {}
        # Paire {name, value} des parametres HTTP (headers / query)
        if "name" in obj and "value" in obj and isinstance(obj.get("name"), str) \
                and SECRET_NAME.search(obj["name"]) and isinstance(obj.get("value"), str) \
                and obj["value"] and not obj["value"].startswith("="):
            obj = dict(obj, value=REDACTED)
        for k, v in obj.items():
            if k in DROP_IN_NODE:
                continue
            if isinstance(v, str) and SECRET_KEY.match(k) and v and not v.startswith("="):
                out[k] = REDACTED
            else:
                out[k] = scrub(v, k)
        return out
    if isinstance(obj, list):
        return [scrub(x, parent_key) for x in obj]
    if isinstance(obj, str):
        return redact_str(obj)
    return obj


def clean(raw: dict) -> dict:
    wf = raw.get("workflow", raw)  # forme API REST ou forme connecteur MCP
    out = {k: wf[k] for k in KEEP if k in wf}
    out["tags"] = [t["name"] if isinstance(t, dict) else t for t in out.get("tags", [])]
    nodes = []
    for n in out.get("nodes", []):
        n = dict(n)
        if "credentials" in n:  # ne garder que la reference
            n["credentials"] = {t: {"id": c.get("id"), "name": c.get("name")} for t, c in n["credentials"].items()}
        nodes.append(scrub(n))
    out["nodes"] = sorted(nodes, key=lambda n: (n.get("name", ""), n.get("id", "")))
    out["connections"] = scrub(out.get("connections", {}))
    # Version publiee differente du brouillon : on la garde (c'est elle qui tourne)
    av = wf.get("activeVersion") or {}
    if av and av.get("sameAsDraft") is False and av.get("nodes"):
        pub = {k: av[k] for k in ("nodes", "connections", "nodeGroups") if k in av}
        pub["nodes"] = sorted([scrub(dict(n, credentials={t: {"id": c.get("id"), "name": c.get("name")}
                                                          for t, c in (n.get("credentials") or {}).items()}))
                               for n in pub["nodes"]], key=lambda n: (n.get("name", ""), n.get("id", "")))
        pub["connections"] = scrub(pub.get("connections", {}))
        out["versionPubliee"] = pub
        out["_note"] = "versionPubliee = version active sur le serveur, differente du brouillon (nodes/connections)."
    return out


def main():
    if sys.argv[1] == "--stdin":
        raw = json.load(sys.stdin)
        dst = sys.argv[2]
    else:
        raw = json.load(open(sys.argv[1], encoding="utf-8"))
        dst = sys.argv[2]
    data = clean(raw)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
