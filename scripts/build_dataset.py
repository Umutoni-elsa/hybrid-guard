"""
build_dataset.py - builds the 30-prompt controlled test dataset (Table 3.1).

Clean and direct-injection prompts are sampled from deepset/prompt-injections,
a real public dataset used in prior prompt-injection detection research
(e.g. cited in InjecGuard, Lee et al. 2024).

Obfuscated prompts are derived by applying this project's own obfuscation
transforms (base64, homoglyph, zero-width, payload-splitting, rot13, hex)
to a separate sample of real malicious prompts from the same dataset, so
each obfuscation_technique label is guaranteed to match what's actually in
the text (rather than sourced pre-obfuscated from elsewhere and guess-labelled).

Usage:
    pip install datasets
    python scripts/build_dataset.py
"""

import csv
import random
import base64
import codecs
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "test_dataset.csv"


def to_base64(t):
    return base64.b64encode(t.encode()).decode()


def to_rot13(t):
    return codecs.encode(t, "rot13")


def to_hex(t):
    return t.encode().hex()


def to_zero_width(t):
    words = t.split(" ")
    obfuscated_words = [w[:1] + "\u200b" + w[1:] if len(w) > 1 else w for w in words]
    return " ".join(obfuscated_words)


HOMOGLYPH_MAP = {"a": "а", "e": "е", "o": "о", "p": "р", "c": "с", "y": "у", "x": "х", "i": "і"}


def to_homoglyph(t):
    return "".join(HOMOGLYPH_MAP.get(ch, ch) for ch in t)


def to_payload_split(t):
    words = t.split(" ")
    mid = len(words) // 2
    part1 = " ".join(words[:mid])
    part2 = " ".join(words[mid:])
    return f"Step one: {part1}. Step two: {part2}."


def main():
    from datasets import load_dataset

    random.seed(42)

    print("Loading deepset/prompt-injections...")
    deepset = load_dataset("deepset/prompt-injections", split="train")

    benign = [r for r in deepset if r["label"] == 0]
    injections = [r for r in deepset if r["label"] == 1]

    # 10 clean, 10 direct injection, 10 more (separate, non-overlapping)
    # injection samples reserved to be transformed into obfuscated rows
    clean_samples = random.sample(benign, 10)
    direct_samples = random.sample(injections, 10)

    remaining_injections = [r for r in injections if r not in direct_samples]
    obf_source_samples = random.sample(remaining_injections, min(10, len(remaining_injections)))

    rows = []

    # C01-C10: clean prompts
    for i, r in enumerate(clean_samples, 1):
        rows.append({
            "id": f"C{i:02d}",
            "text": r["text"].strip(),
            "category": "clean",
            "obfuscation_technique": "",
            "ground_truth_label": "SAFE",
            "source": "deepset/prompt-injections",
        })

    # D01-D10: direct injection, real text, unmodified
    for i, r in enumerate(direct_samples, 1):
        rows.append({
            "id": f"D{i:02d}",
            "text": r["text"].strip(),
            "category": "direct_injection",
            "obfuscation_technique": "",
            "ground_truth_label": "MALICIOUS",
            "source": "deepset/prompt-injections",
        })

    # O01-O10: real injection prompts, transformed with this project's own
    # obfuscation functions, so the technique label always matches the text
    obf_funcs = [to_base64, to_homoglyph, to_zero_width, to_payload_split, to_rot13, to_hex,
                 to_base64, to_homoglyph, to_zero_width, to_payload_split]
    obf_names = ["base64", "homoglyph", "zero_width", "payload_splitting", "rot13", "hex",
                 "base64", "homoglyph", "zero_width", "payload_splitting"]

    for i, (r, fn, name) in enumerate(zip(obf_source_samples, obf_funcs, obf_names), 1):
        original_text = r["text"].strip()
        rows.append({
            "id": f"O{i:02d}",
            "text": fn(original_text),
            "category": "obfuscated",
            "obfuscation_technique": name,
            "ground_truth_label": "MALICIOUS",
            "source": f"deepset/prompt-injections (transformed, original: {original_text[:60]}...)",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "text", "category", "obfuscation_technique",
                        "ground_truth_label", "source"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDataset written to {OUTPUT}")
    print(f"Total rows: {len(rows)}")
    print(f"  Clean:          {sum(1 for r in rows if r['category'] == 'clean')}")
    print(f"  Direct inject:  {sum(1 for r in rows if r['category'] == 'direct_injection')}")
    print(f"  Obfuscated:     {sum(1 for r in rows if r['category'] == 'obfuscated')}")
    print("\nReview the file before running evaluate.py — obfuscated rows should")
    print("now contain real encoded/transformed text (base64 strings, hex digits,")
    print("zero-width-joined words, etc.), not plain readable sentences.")


if __name__ == "__main__":
    main()
