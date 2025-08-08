#!/usr/bin/env python3
"""
build_seed_tree_curated.py

Combine your 30+ domains with each bucket and its small curated synonym list,
yielding a few thousand, high-precision seed phrases.
"""

from pathlib import Path

# 1. Your domains
domains = [
    "agriculture","architecture","art","automotive","business","culture","e-learning",
    "economics","education","engineering","entertainment","environment","fashion",
    "finance","food","government","healthcare","human resources","legal","marketing",
    "medical","news","real estate","retail","science","social media","sports",
    "technology","traffic","travel","weather"
]

# 2. Curated synonyms map (see above)
from pprint import pprint
manual_syns = {
  "poster":     ["placard","handbill","broadside","billboard","flier","leaflet","pamphlet"],
  "infographic":["chart","diagram","visualization","flowchart"],
  "chart":      ["graph","plot","diagram"],
  "diagram":    ["schematic","blueprint"],
  "notice":     ["announcement","bulletin","memo"],
  "sign":       ["signal","signboard"],
  "plaque":     ["tablet","memorial tablet"],
  "flyer":      ["leaflet","handbill"],
  "label":      ["tag","sticker"],
  "instruction":["guideline","manual"],
  "manual":     ["guide","handbook"],
  "brochure":   ["pamphlet","leaflet"],
  "leaflet":    ["flyer","pamphlet"],
  "pamphlet":   ["leaflet","brochure"],
  "advertisement":["ad","advert"],
  "billboard":  ["hoarding","signboard"],
  "document":   ["text file","written document"],
  "form":       ["application","template"],
  "certificate":["diploma","credential"],
  "menu":       ["bill of fare","menu card"],
  "template":   ["form","pattern"],
  "banner":     ["standard","streamer"],
}

# 3. Build seeds
seeds = set()
for d in domains:
    for bucket, syns in manual_syns.items():
        # always include the original "<domain> <bucket>"
        seeds.add(f"{d} {bucket}")
        # then synonyms:
        for s in syns:
            seeds.add(f"{d} {s}")

# 4. Write to your master seed file
out = Path("phase2_keywords/seed/english_seed_termsv1.txt")
out.parent.mkdir(exist_ok=True, parents=True)
with open(out, "w", encoding="utf-8") as f:
    for s in sorted(seeds):
        f.write(s + "\n")

print(f"→ Generated {len(seeds)} clean, high-yield seeds in {out}")