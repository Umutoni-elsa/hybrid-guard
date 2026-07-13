"""
build_dataset.py

Creates the Hybrid-Guard evaluation dataset.

Dataset composition
-------------------
SAFE prompts:
    deepset label == 0

MALICIOUS prompts:
    deepset label == 1

OBFUSCATED prompts:
    automatically generated from malicious prompts
"""

from pathlib import Path
import random
import base64
import codecs

import pandas as pd
from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "evaluation_dataset.csv"

random.seed(42)

# ============================================================
# Load dataset
# ============================================================

print("Loading deepset prompt injection dataset...")

dataset = load_dataset(
    "deepset/prompt-injections",
    split="train"
)

clean_prompts = []
malicious_prompts = []

for row in dataset:

    prompt = row["text"].strip()
    label = row["label"]

    if not prompt:
        continue

    if label == 0:
        clean_prompts.append(prompt)

    elif label == 1:
        malicious_prompts.append(prompt)

print(f"Loaded {len(clean_prompts)} SAFE prompts.")
print(f"Loaded {len(malicious_prompts)} MALICIOUS prompts.")

# ============================================================
# Obfuscation functions
# ============================================================

def to_base64(text):
    return base64.b64encode(text.encode()).decode()


def to_rot13(text):
    return codecs.encode(text, "rot13")


def to_hex(text):
    return text.encode().hex()


def zero_width(text):
    zw = "\u200b"
    return zw.join(text)


def homoglyph(text):
    mapping = {
        "a": "а",
        "e": "е",
        "o": "о",
        "c": "с",
        "p": "р",
        "x": "х",
        "i": "і",
        "y": "у",
    }

    return "".join(mapping.get(ch, ch) for ch in text)


OBFUSCATORS = [
    to_base64,
    to_rot13,
    to_hex,
    zero_width,
    homoglyph,
]

# ============================================================
# Build dataset
# ============================================================

rows = []

idx = 1

# ---------------- SAFE ----------------

for prompt in clean_prompts:

    rows.append({
        "id": idx,
        "prompt": prompt,
        "label": "SAFE",
        "category": "clean",
    })

    idx += 1

# ---------------- MALICIOUS ----------------

for prompt in malicious_prompts:

    rows.append({
        "id": idx,
        "prompt": prompt,
        "label": "MALICIOUS",
        "category": "direct_injection",
    })

    idx += 1

# ---------------- OBFUSCATED ----------------

generated = 0

for prompt in malicious_prompts:

    fn = random.choice(OBFUSCATORS)

    rows.append({
        "id": idx,
        "prompt": fn(prompt),
        "label": "MALICIOUS",
        "category": "obfuscated",
    })

    idx += 1
    generated += 1

# ============================================================
# Save
# ============================================================

df = pd.DataFrame(rows)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT, index=False)

print()
print("=" * 60)
print("Hybrid-Guard Evaluation Dataset")
print("=" * 60)
print(f"Clean prompts               : {len(clean_prompts)}")
print(f"Direct injections           : {len(malicious_prompts)}")
print(f"Generated obfuscated prompts: {generated}")
print("-" * 60)
print(f"TOTAL PROMPTS               : {len(df)}")
print()
print(f"Saved to:\n{OUTPUT}")