"""
download_datasets.py

Downloads and prepares the datasets used to evaluate Hybrid-Guard.

Datasets:
1. deepset/prompt-injections
2. allenai/wildguardmix (wildguardtest split)

The datasets are converted into a common CSV format so they can later
be merged into one evaluation dataset.
"""

from pathlib import Path

import pandas as pd
from datasets import load_dataset

OUTPUT_DIR = Path("data/datasets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------
# Deepset Prompt Injection Dataset
# -------------------------------------------------------------
def save_deepset():

    output = OUTPUT_DIR / "deepset.csv"

    if output.exists():
        print("✓ deepset.csv already exists.")
        return

    print("Downloading Deepset...")

    dataset = load_dataset("deepset/prompt-injections")

    rows = []

    for split in ["train", "test"]:

        for item in dataset[split]:

            rows.append({
                "prompt": item["text"],
                "label": "malicious" if item["label"] else "clean",
                "category": "direct_injection" if item["label"] else "clean",
                "source": "deepset",
                "split": split,
            })

    df = pd.DataFrame(rows)

    df.to_csv(output, index=False)

    print(f"✓ Saved {len(df)} prompts")
    print(df["label"].value_counts())
    print()


# -------------------------------------------------------------
# WildGuard Dataset
# -------------------------------------------------------------
def save_wildguard():

    output = OUTPUT_DIR / "wildguard.csv"

    if output.exists():
        print("✓ wildguard.csv already exists.")
        return

    print("Downloading WildGuard...")

    dataset = load_dataset(
        "allenai/wildguardmix",
        "wildguardtest"
    )

    rows = []

    for item in dataset["test"]:

        # Conservative labeling:
        # Any adversarial prompt OR harmful prompt
        # is treated as malicious.
        malicious = (
            item["adversarial"] or
            item["prompt_harm_label"] == "harmful"
        )

        rows.append({
            "prompt": item["prompt"],
            "label": "malicious" if malicious else "clean",
            "category": "direct_injection" if malicious else "clean",
            "source": "wildguard",
            "split": "test",
        })

    df = pd.DataFrame(rows)

    df.to_csv(output, index=False)

    print(f"✓ Saved {len(df)} prompts")
    print(df["label"].value_counts())
    print()


# -------------------------------------------------------------
# Summary
# -------------------------------------------------------------
def print_summary():

    print("\n" + "=" * 60)
    print("Downloaded datasets")
    print("=" * 60)

    total = 0

    for csv_file in OUTPUT_DIR.glob("*.csv"):

        df = pd.read_csv(csv_file)

        total += len(df)

        print(f"{csv_file.name:20} {len(df):6} prompts")

    print("-" * 60)
    print(f"TOTAL{'':16}{total:6} prompts")
    print("=" * 60)


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
if __name__ == "__main__":

    save_deepset()

    save_wildguard()

    print_summary()