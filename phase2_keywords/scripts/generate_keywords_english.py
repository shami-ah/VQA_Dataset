#!/usr/bin/env python3
"""
expand_keywords_offline.py

Goal: Expand a pruned seed list (e.g., 1,400 "<domain> <bucket/syn>") into
~15k high-yield search phrases WITHOUT any API calls.

Strategy:
- Attach curated prefixes/suffixes that reliably surface images WITH TEXT
  (printable, template, pdf, A4, editable, etc.)
- Avoid nonsense like "form form" or repeating the bucket.
- Cap expansions per seed so we don't explode the list.

Input:
  phase2_keywords/seed/english_seed_terms_pruned.txt
Output:
  phase2_keywords/expanded/keywords_english_master_offline.txt
"""

from pathlib import Path

# Buckets/synonyms we used when pruning (used to classify each seed)
BUCKET_GROUPS = {
    "poster_like": {
        "tokens": {"poster","placard","broadside","banner","billboard","advertisement","ad","commercial"},
        "prefixes": ["printable","editable","A4","A3","US letter","pdf"],
        "suffixes": ["template","design","layout","mockup","sample","example"],
    },
    "diagram_like": {
        "tokens": {"infographic","flowchart","diagram","chart","graph","plot","schematic","blueprint","visualization"},
        "prefixes": ["printable","editable","vector","svg","pdf","HD"],
        "suffixes": ["template","design","layout","sample","example","guide"],
    },
    "doc_like": {
        "tokens": {"document","paper","text file","form","application","certificate","diploma","credential","menu","menu card"},
        "prefixes": ["printable","editable","blank","fillable","A4","pdf"],
        "suffixes": ["template","sample","example","blank form","fillable form","official"],
    },
    "label_sign_like": {
        "tokens": {"label","tag","sticker","plaque","tablet","sign","signboard","signal","notice","bulletin","memo","announcement"},
        "prefixes": ["printable","editable","vector","svg","pdf","laminated"],
        "suffixes": ["template","sticker sheet","set","sample","example","guide"],
    },
    "brochure_like": {
        "tokens": {"brochure","leaflet","flyer","pamphlet","handbill"},
        "prefixes": ["printable","editable","A4","US letter","pdf","tri-fold"],
        "suffixes": ["template","bi-fold","tri-fold template","mockup","sample","example"],
    },
}

# Fallback if a seed doesn't match any known bucket (rare)
DEFAULT_PREFIXES = ["printable","editable","pdf","A4","sample","template"]
DEFAULT_SUFFIXES = ["template","sample","example","design","layout","guide"]

# Safety filters to avoid weird combos
BAD_SUFFIX_IF_CONTAINS = {
    "form": {"form", "blank form", "fillable form"},
    "menu": {"menu", "menu card"},
    "poster": {"poster"},
}

MAX_PREFIXES_PER_SEED = 6
MAX_SUFFIXES_PER_SEED = 6

def classify_seed(seed: str) -> dict:
    """
    Return the BUCKET_GROUPS entry that matches the seed (by token present),
    else None.
    """
    s = seed.lower()
    for group in BUCKET_GROUPS.values():
        for tok in group["tokens"]:
            if f" {tok} " in f" {s} ":
                return group
    return None

def generate_for_seed(seed: str) -> list[str]:
    group = classify_seed(seed)
    prefixes = group["prefixes"] if group else DEFAULT_PREFIXES
    suffixes = group["suffixes"] if group else DEFAULT_SUFFIXES

    out = set()

    # Prefix forms: "printable education poster"
    for p in prefixes[:MAX_PREFIXES_PER_SEED]:
        out.add(f"{p} {seed}")

    # Suffix forms: "education poster template"
    seed_l = seed.lower()
    blocked = set()
    for key, bads in BAD_SUFFIX_IF_CONTAINS.items():
        if key in seed_l:
            blocked |= {b.lower() for b in bads}

    added = 0
    for sfx in suffixes:
        if added >= MAX_SUFFIXES_PER_SEED:
            break
        if sfx.lower() in blocked:
            continue
        # avoid duplicating the bucket word itself (e.g., "... poster poster")
        if any(sfx.lower() == t for t in seed_l.split()):
            continue
        out.add(f"{seed} {sfx}")
        added += 1

    # (Optional) two-modifier pattern for extra lift on posters/diagrams:
    # printable + template (kept short, still high-yield)
    if group in (BUCKET_GROUPS["poster_like"], BUCKET_GROUPS["diagram_like"]):
        out.add(f"printable {seed} template")
        out.add(f"{seed} template pdf")

    return sorted(out)

def main():
    base = Path(__file__).resolve().parents[2]  # repo root
    in_file = base / "phase2_keywords" / "seed" / "english_seed_terms_pruned.txt"
    out_dir = base / "phase2_keywords" / "expanded"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "keywords_english_master_offline.txt"

    seeds = [l.strip() for l in in_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Loaded {len(seeds)} seeds from {in_file}")

    all_terms = []
    for s in seeds:
        all_terms.extend(generate_for_seed(s))

    # Deduplicate while preserving order
    seen, master = set(), []
    for t in all_terms:
        k = t.lower()
        if k and k not in seen:
            seen.add(k)
            master.append(t)

    out_file.write_text("\n".join(master), encoding="utf-8")
    print(f"✓ Wrote {len(master)} expanded keywords → {out_file}")

if __name__ == "__main__":
    main()