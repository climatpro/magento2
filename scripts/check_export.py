#!/usr/bin/env python3
"""Controles apres export + extraction des dependances.

- chaque fichier workflows/*.json est un JSON valide, nettoye (pas de pinData/staticData)
- toutes les connexions pointent vers un node existant
- aucun secret reconnaissable
- produit un resume machine (JSON sur stdout) : sous-workflows appeles, modeles IA,
  credentials, data tables, webhooks — utilise par build_index.py

Usage : check_export.py [workflows/] > resume.json
"""
import glob, json, os, re, sys

SECRET_VALUE = [
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
]
MODEL_RX = re.compile(r"\b(claude-[a-z0-9.-]+|gemini-[a-z0-9.-]+|gpt-[a-z0-9.-]+|o[134](?:-mini)?)\b")


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, v
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def analyse(path):
    wf = json.load(open(path, encoding="utf-8"))
    errs = []
    for bad in ("pinData", "staticData"):
        if bad in wf:
            errs.append(f"{bad} present")
    names = {n["name"] for n in wf.get("nodes", [])}
    for src, outs in wf.get("connections", {}).items():
        if src not in names:
            errs.append(f"connexion depuis node inconnu '{src}'")
        for lst in outs.values():
            for branch in lst:
                for c in branch or []:
                    if c.get("node") not in names:
                        errs.append(f"connexion vers node inconnu '{c.get('node')}'")
    text = json.dumps(wf, ensure_ascii=False)
    for rx in SECRET_VALUE:
        if rx.search(text):
            errs.append(f"secret potentiel ({rx.pattern})")

    calls, models, creds, tables, webhooks, trigger = [], [], {}, [], [], None
    for n in wf.get("nodes", []):
        t = n.get("type", "")
        p = n.get("parameters", {}) or {}
        if n.get("disabled"):
            continue
        if t in ("n8n-nodes-base.executeWorkflow", "@n8n/n8n-nodes-langchain.toolWorkflow"):
            w = p.get("workflowId")
            wid = w.get("value") if isinstance(w, dict) else w
            wname = w.get("cachedResultName") if isinstance(w, dict) else ""
            if wid:
                calls.append({"id": str(wid), "name": wname or "", "node": n["name"]})
        if t == "n8n-nodes-base.dataTable":
            d = p.get("dataTableId")
            did = d.get("value") if isinstance(d, dict) else d
            op = p.get("operation", "")
            tables.append({"id": str(did), "node": n["name"], "mode": "lecture" if op in ("get", "getAll", "rowGet") else "ecriture:" + str(op)})
        if t.startswith("@n8n/n8n-nodes-langchain.lmChat") or "lmChat" in t:
            m = p.get("model")
            mid = m.get("value") if isinstance(m, dict) else m
            models.append({"node": n["name"], "type": t, "model": str(mid or "(defaut node)")})
        if t == "n8n-nodes-base.httpRequest":
            url = str(p.get("url", ""))
            if "anthropic.com" in url or "generativelanguage.googleapis.com" in url or "openai.com" in url:
                body = json.dumps(p, ensure_ascii=False)
                found = MODEL_RX.findall(body + " " + url)
                models.append({"node": n["name"], "type": "httpRequest", "model": ", ".join(sorted(set(found))) or "(voir body)"})
            if "/webhook/" in url:
                calls.append({"id": "", "name": "webhook " + url.split("/webhook/")[1].split("?")[0].split("'")[0].split('"')[0], "node": n["name"]})
        if t == "n8n-nodes-base.webhook":
            webhooks.append(f"{p.get('httpMethod', 'GET')} /webhook/{p.get('path', '')}")
        if t.endswith("Trigger") or t.endswith("trigger"):
            trigger = trigger or t.split(".")[-1]
        for ctype, c in (n.get("credentials") or {}).items():
            creds[c.get("id")] = {"id": c.get("id"), "name": c.get("name"), "type": ctype}
    # modeles cites dans du texte (prompts, code) sans node LLM dedie
    for m in MODEL_RX.findall(text):
        if not any(m in x["model"] for x in models):
            models.append({"node": "(cite dans le code/prompt)", "type": "texte", "model": m})
    return {
        "id": wf.get("id"), "name": wf.get("name"), "slug": os.path.basename(path)[:-5],
        "active": wf.get("active"), "description": wf.get("description") or "",
        "trigger_type": trigger, "node_count": len(wf.get("nodes", [])),
        "calls": calls, "models": models, "credentials": list(creds.values()),
        "data_tables": tables, "webhooks": webhooks, "errors": errs,
    }


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "workflows"
    res = [analyse(p) for p in sorted(glob.glob(os.path.join(d, "*.json")))]
    nerr = sum(len(r["errors"]) for r in res)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"{len(res)} fichier(s), {nerr} erreur(s)", file=sys.stderr)
    for r in res:
        for e in r["errors"]:
            print(f"  {r['slug']}: {e}", file=sys.stderr)
    sys.exit(1 if nerr else 0)


if __name__ == "__main__":
    main()
