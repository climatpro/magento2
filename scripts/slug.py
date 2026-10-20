#!/usr/bin/env python3
"""Nom de fichier stable pour un workflow n8n (ASCII, minuscules, tirets).
Les noms en double recoivent le suffixe --<id>."""
import json, re, sys, unicodedata

def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "sans-nom"

def slug_map(workflows):
    """workflows: liste de dicts avec id et name -> {id: slug}"""
    base = {w["id"]: slug(w["name"]) for w in workflows}
    counts = {}
    for s in base.values():
        counts[s] = counts.get(s, 0) + 1
    return {wid: (s if counts[s] == 1 else f"{s}--{wid}") for wid, s in base.items()}

if __name__ == "__main__":
    wfs = json.load(open(sys.argv[1]))
    for wid, s in slug_map(wfs).items():
        print(wid, s)
