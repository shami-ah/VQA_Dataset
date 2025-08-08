#!/usr/bin/env python3
"""
prune_seeds.py

Reads your raw seed dump (english_seed_termsv1.txt), 
keeps only "<domain> <bucket>" and "<domain> <synonym>" 
where bucket/synonym are in your curated map.
"""

from pathlib import Path

# 1. Load your raw seeds
raw = Path(__file__).parent.parent / "seed" / "english_seed_termsv1.txt"
seeds = [line.strip() for line in raw.read_text(encoding="utf-8").splitlines() if line.strip()]

# 2. Curated map from above
manual_syns = {
    "poster":       ["placard", "broadside"],
    "infographic":  ["flowchart", "visualization"],
    "chart":        ["graph", "plot"],
    "diagram":      ["schematic", "blueprint"],
    "notice":       ["bulletin", "memo", "announcement"],
    "sign":         ["signboard", "signal"],
    "plaque":       ["tablet"],
    "flyer":        ["leaflet", "handbill"],
    "label":        ["tag", "sticker"],
    "instruction":  ["guide", "manual"],
    "manual":       ["handbook", "guidebook"],
    "brochure":     ["pamphlet", "leaflet"],
    "leaflet":      ["flyer", "pamphlet"],
    "pamphlet":     ["leaflet", "brochure"],
    "advertisement":["ad", "commercial"],
    "billboard":    ["hoarding"],
    "document":     ["paper", "text file"],
    "form":         ["template", "application"],
    "certificate":  ["diploma", "credential"],
    "menu":         ["menu card"],
    "template":     ["pattern"],
    "banner":       ["flag", "streamer"],
}

# 3. Build a lookup of allowed phrases
allowed = set(manual_syns.keys())
for syns in manual_syns.values():
    allowed.update(syns)

# 4. Filter seeds
cleaned = []
for s in seeds:
    parts = s.split(maxsplit=1)
    if len(parts) != 2:
        continue
    domain, phrase = parts
    if phrase in allowed:
        cleaned.append(s)

# 5. Write out
out = raw.parent / "english_seed_terms_pruned.txt"
out.write_text("\n".join(sorted(set(cleaned))), encoding="utf-8")
print(f"Pruned down to {len(cleaned)} seeds → {out}")