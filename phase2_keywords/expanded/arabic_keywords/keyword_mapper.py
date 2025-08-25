#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deterministic (non-AI) English → Arabic keyword mapper.
- 1:1 alignment: preserves line count & order
- Arabic output with acronyms preserved exactly (3D, PDF, ...)
- Arabic digits (٠١٢٣٤٥٦٧٨٩) applied only OUTSIDE acronyms
- Trailing NORMAL comma ',' at end of every line (matches English file)
- Taxonomy retained via phrase & word maps from glossary
- Writes a QA report listing lines with leftover Latin tokens (non-whitelisted)

Usage:
  python keyword_mapper.py \
      --input "/path/to/english_keywords_cleaned_comma_19k.txt" \
      --output "/path/to/arabic_keywords_19k.txt" \
      --glossary "/path/to/glossary_ar.json" \
      --report "/path/to/qa_report.txt"
"""

import argparse
import json
import re
import sys
from pathlib import Path


def load_glossary(path: Path):
    g = json.loads(path.read_text(encoding="utf-8"))
    g.setdefault("acronyms", [])
    g.setdefault("digit_convert", True)
    g.setdefault("phrase_map", [])
    g.setdefault("word_map", {})
    g.setdefault("feminine_heads", [])
    return g


def arabic_digitize(s: str, acronyms):
    """
    Convert ASCII digits to Arabic-Indic digits ONLY outside whitelisted acronyms.
    Prevents the '__ACR_3D__' → '__ACR_٣D__' masking bug.
    """
    if not acronyms:
        return s.translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))

    AR_MAP = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

    # 1) Mask acronyms (exact tokens, word boundaries)
    pat = r'(?<!\w)(' + '|'.join(map(re.escape, acronyms)) + r')(?!\w)'
    masked = re.sub(pat, lambda m: f"__ACR__{m.group(1)}__", s)

    # 2) Convert digits only OUTSIDE placeholders
    parts = re.split(r'(__ACR__.*?__)', masked)
    parts = [p if p.startswith('__ACR__') else p.translate(AR_MAP) for p in parts]
    out = ''.join(parts)

    # 3) Unmask back to original acronyms
    out = re.sub(r'__ACR__(.*?)__', r'\1', out)
    return out


def apply_phrase_map(s: str, phrase_map):
    for pattern, rep in phrase_map:
        s = re.sub(pattern, rep, s, flags=re.IGNORECASE)
    return s


def tokenize(s: str):
    # simple whitespace tokenization is enough for our deterministic rules
    return s.split()


def map_word(tok: str, word_map: dict, acronyms: set):
    """
    Keep unknown tokens (do NOT drop): better for recall in search engines.
    Acronyms are preserved as-is. Known tokens map via word_map.
    """
    if tok in acronyms:
        return tok
    low = tok.lower()
    if low in word_map:
        return word_map[low]
    # Keep unknown token as-is (no transliteration, no dropping)
    return tok


def place_academic(text: str, feminine_heads: list):
    """
    If the special marker '__ACADEMIC__' is present, insert 'أكاديمي/أكاديمية'
    after the first recognized head noun for natural Arabic order.
    """
    if "__ACADEMIC__" not in text:
        return text
    t = text.replace("__ACADEMIC__", "").strip()
    heads = feminine_heads + [
        "أجندة","تقويم","بطاقة","شهادة","قائمة","مخطط","دليل","وثيقة","ملف","مجلد","خريطة",
        "ملصق","فاتورة","إيصال","سجل","إشعار","تصريح","بيان","جدول","رسم","مواصفات",
        "برنامج","كتيب","تعليمات","لافتة","لوحة"
    ]
    for h in heads:
        idx = t.find(h)
        if idx != -1:
            end = idx + len(h)
            adj = " أكاديمية" if h in feminine_heads else " أكاديمي"
            return t[:end] + adj + t[end:]
    return "أكاديمي " + t


def process_line(en_line: str, acro: set, phrase_map, word_map, feminine_heads: list, digit_convert: bool):
    """
    Process one English keyword line → Arabic line.
    - Apply phrase map
    - Token map with glossary (keep unknowns)
    - Place 'academic' adjective correctly
    - Convert digits outside acronyms
    - Ensure trailing normal comma ','
    - If mapping collapses to empty, fall back to original English tokens (then comma)
    """
    original = en_line.strip()
    s = original.rstrip(",")  # drop trailing comma for processing
    s = apply_phrase_map(s, phrase_map)

    toks = tokenize(s)
    out = []
    academic = False
    for t in toks:
        if t.lower() == "academic":
            academic = True
            continue
        mapped = map_word(t, word_map, acro)
        if mapped:
            out.append(mapped)

    text = " ".join(out).strip()
    if academic:
        text = place_academic(text, feminine_heads)

    text = re.sub(r"\s{2,}", " ", text).strip()

    # If mapping yielded nothing, fall back to the original (keeps alignment & recall)
    if not text:
        text = s

    if digit_convert and text:
        text = arabic_digitize(text, acro)

    # Ensure trailing NORMAL comma (not Arabic comma)
    if not text.endswith(","):
        text += ","

    return text


def run(input_path: Path, output_path: Path, glossary_path: Path, report_path: Path = None):
    g = load_glossary(glossary_path)
    acro = set(g["acronyms"])
    phrase_map = g["phrase_map"]
    word_map = g["word_map"]
    feminine_heads = g["feminine_heads"]
    digit_convert = bool(g["digit_convert"])

    lines = [ln.rstrip("\n") for ln in input_path.read_text(encoding="utf-8").splitlines()]
    out_lines, latin_report = [], []

    for idx, ln in enumerate(lines, 1):
        ar = process_line(ln, acro, phrase_map, word_map, feminine_heads, digit_convert)
        out_lines.append(ar)
        # QA: leftover Latin tokens (excluding whitelisted acronyms)
        residual = re.findall(r"[A-Za-z]+", ar)
        residual = [x for x in residual if x not in acro]
        if residual:
            latin_report.append((idx, ln, ar, residual))

    output_path.write_text("\n".join(out_lines), encoding="utf-8")

    if report_path:
        with report_path.open("w", encoding="utf-8") as f:
            f.write("Leftover Latin QA report (non-whitelisted):\n")
            for i, src, dst, res in latin_report:
                f.write(f"{i}: {src} ==> {dst} :: {res}\n")

    print(f"[DONE] {len(lines)} lines mapped → {output_path}")
    if report_path:
        print(f"[QA] Report lines with non-whitelisted Latin tokens: {len(latin_report)} → {report_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to english_keywords_cleaned_comma_19k.txt")
    ap.add_argument("--output", required=True, help="Path to output Arabic file")
    ap.add_argument("--glossary", required=True, help="Path to glossary_ar.json")
    ap.add_argument("--report", default="", help="Optional QA report path")
    args = ap.parse_args()

    run(
        Path(args.input),
        Path(args.output),
        Path(args.glossary),
        Path(args.report) if args.report else None
    )


if __name__ == "__main__":
    main()