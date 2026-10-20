#!/usr/bin/env python3
"""Genere docs/INDEX.md (tableau + schema Mermaid des dependances) a partir de workflows/*.json
et, s'il existe, du resume machine docs/_resume.json (champ trigger/role rediges a la main).

Usage : build_index.py [--resume docs/_resume.json]
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, "workflows")
DOCS = os.path.join(ROOT, "docs")

TRIGGER_FR = {
    "scheduleTrigger": "planifié", "cron": "planifié", "webhook": "webhook", "telegramTrigger": "Telegram",
    "executeWorkflowTrigger": "sous-workflow", "manualTrigger": "manuel", "gmailTrigger": "Gmail",
    "googleDriveTrigger": "Drive", "formTrigger": "formulaire", "chatTrigger": "chat", "mcpTrigger": "MCP",
}


def load_resume():
    p = os.path.join(DOCS, "_resume.json")
    if os.path.exists(p):
        return {r["id"]: r for r in json.load(open(p, encoding="utf-8"))}
    return {}


def main():
    out = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "check_export.py"), WF],
                         capture_output=True, text=True)
    data = json.loads(out.stdout)
    manual = load_resume()
    by_id = {d["id"]: d for d in data}
    lines = ["# Index des workflows n8n ClimatPro", "",
             f"{len(data)} workflows exportés. Fiche détaillée : `docs/<nom>.md`, JSON : `workflows/<nom>.json`.", "",
             "| Workflow | Actif | Déclencheur | Rôle |", "|---|---|---|---|"]
    for d in sorted(data, key=lambda x: x["name"].lower()):
        m = manual.get(d["id"], {})
        trig = m.get("trigger") or TRIGGER_FR.get(d["trigger_type"] or "", d["trigger_type"] or "aucun")
        role = (m.get("role") or d["description"] or "").replace("|", "/").replace("\n", " ").strip()
        if len(role) > 140:
            role = role[:137].rstrip() + "…"
        lines.append(f"| [{d['name']}]({d['slug']}.md) | {'oui' if d['active'] else 'non'} | {trig} | {role} |")

    # Schéma Mermaid : appels entre workflows (Execute Workflow, Tool Workflow, appels webhook internes)
    lines += ["", "## Dépendances entre workflows", "",
              "Flèche = « appelle ». Trait plein : Execute Workflow / outil d'agent. Pointillé : appel HTTP d'un webhook interne.",
              "Les workflows inactifs sont en gris.", "", "```mermaid", "graph LR"]
    ids = {}
    def nid(wid):
        if wid not in ids:
            ids[wid] = f"W{len(ids)}"
        return ids[wid]
    edges, used = set(), set()
    webhook_owner = {}
    for d in data:
        for w in d["webhooks"]:
            webhook_owner[w.split("/webhook/")[1].rstrip("/")] = d["id"]
    for d in data:
        for c in d["calls"]:
            if c["id"] and c["id"] in by_id:
                edges.add((d["id"], c["id"], "-->"))
            elif c["name"].startswith("webhook "):
                path = c["name"][8:].strip().rstrip("/")
                tgt = webhook_owner.get(path)
                if tgt and tgt != d["id"]:
                    edges.add((d["id"], tgt, "-.->"))
    for a, b, _ in edges:
        used.update([a, b])
    for wid in sorted(used, key=lambda x: by_id[x]["name"]):
        label = by_id[wid]["name"].replace('"', "'")
        lines.append(f'  {nid(wid)}["{label}"]')
    for a, b, arrow in sorted(edges, key=lambda e: (by_id[e[0]]["name"], by_id[e[1]]["name"])):
        lines.append(f"  {nid(a)} {arrow} {nid(b)}")
    inactive = [nid(w) for w in used if not by_id[w]["active"]]
    if inactive:
        lines.append("  classDef off fill:#eee,stroke:#999,color:#666")
        lines.append("  class " + ",".join(inactive) + " off")
    lines += ["```", ""]
    isolated = [d["name"] for d in data if d["id"] not in used]
    if isolated:
        lines += ["Workflows sans lien avec un autre workflow (autonomes) : " + ", ".join(sorted(isolated)) + ".", ""]
    open(os.path.join(DOCS, "INDEX.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("docs/INDEX.md regenere :", len(data), "workflows,", len(edges), "liens")


if __name__ == "__main__":
    main()
