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
    names = {}
    for d in data:
        names[d["name"]] = names.get(d["name"], 0) + 1
    def label(wid):
        d = by_id[wid]
        l = d["name"].replace('"', "'")
        if names[d["name"]] > 1:
            l += f" [{wid[:6]}]"
        return l + ("" if d["active"] else " (inactif)")
    for wid in sorted(used, key=lambda x: by_id[x]["name"]):
        lines.append(f'  {nid(wid)}["{label(wid)}"]')
    for a, b, arrow in sorted(edges, key=lambda e: (by_id[e[0]]["name"], by_id[e[1]]["name"])):
        lines.append(f"  {nid(a)} {arrow} {nid(b)}")
    inactive = [nid(w) for w in used if not by_id[w]["active"]]
    if inactive:
        lines.append("  classDef off fill:#eee,stroke:#999,color:#666")
        lines.append("  class " + ",".join(inactive) + " off")
    lines += ["```", ""]
    # Second schema : dependances par Data Table (ecrivain -> table -> lecteur)
    tp = os.path.join(DOCS, "_tables.json")
    tnames = json.load(open(tp, encoding="utf-8")) if os.path.exists(tp) else {}
    SECRET_TABLES = {"daikin_spb_acces", "quartix_acces", "tableau_secrets", "sonepar_acces", "hiparts_acces"}
    lines += ["## Dépendances via les Data Tables n8n", "",
              "Un workflow écrit une table (flèche pleine), un autre la lit (flèche pointillée). Les tables d'identifiants",
              "(`*_acces`, `tableau_secrets`) sont en rouge : leur contenu n'est jamais exporté.", "", "```mermaid", "graph LR"]
    ids2, tid = {}, {}
    def n2(wid):
        if wid not in ids2:
            ids2[wid] = f"W{len(ids2)}"
        return ids2[wid]
    def t2(t):
        if t not in tid:
            tid[t] = f"T{len(tid)}"
        return tid[t]
    tedges = set()
    for d in data:
        for t in d["data_tables"]:
            tname = tnames.get(t["id"], t["id"])
            tedges.add((d["id"], tname, "lecture" if t["mode"] == "lecture" else "ecriture"))
    wused = sorted({e[0] for e in tedges}, key=lambda x: by_id[x]["name"])
    tused = sorted({e[1] for e in tedges})
    for wid in wused:
        lines.append(f'  {n2(wid)}["{label(wid)}"]')
    for t in tused:
        lines.append(f'  {t2(t)}[("{t}")]')
    for wid, t, mode in sorted(tedges, key=lambda e: (e[1], by_id[e[0]]["name"])):
        lines.append(f"  {n2(wid)} -.-> {t2(t)}" if mode == "lecture" else f"  {n2(wid)} --> {t2(t)}")
    lines.append("  classDef secret fill:#fdd,stroke:#c00")
    sec = [t2(t) for t in tused if t in SECRET_TABLES]
    if sec:
        lines.append("  class " + ",".join(sec) + " secret")
    off2 = [n2(w) for w in wused if not by_id[w]["active"]]
    if off2:
        lines.append("  classDef off fill:#eee,stroke:#999,color:#666")
        lines.append("  class " + ",".join(off2) + " off")
    lines += ["```", ""]
    isolated = [d["name"] for d in data if d["id"] not in used]
    if isolated:
        lines += ["Workflows sans lien avec un autre workflow (autonomes) : " + ", ".join(sorted(isolated)) + ".", ""]
    open(os.path.join(DOCS, "INDEX.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("docs/INDEX.md regenere :", len(data), "workflows,", len(edges), "liens")


if __name__ == "__main__":
    main()
