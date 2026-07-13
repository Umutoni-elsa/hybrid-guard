"""
evaluate_hybrid_guard.py

Evaluates Hybrid-Guard on the generated evaluation dataset.

Features
--------
✓ Resume interrupted evaluations
✓ Incremental saving
✓ Latency measurement
✓ Accuracy / Precision / Recall / F1
✓ Confusion matrix
✓ Dissertation-ready summary
"""

from pathlib import Path
import sys
import time

import pandas as pd
from tqdm import tqdm

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# ------------------------------------------------------------
# Allow importing Hybrid-Guard modules
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hybrid_guard.pipeline import run

# ------------------------------------------------------------
# File locations
# ------------------------------------------------------------

DATASET = ROOT / "data" / "evaluation_dataset.csv"
RESULTS = ROOT / "data" / "results" / "evaluation_results.csv"
SUMMARY = ROOT / "data" / "results" / "evaluation_summary.md"

# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

if not DATASET.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET}\n\n"
        "Run build_dataset.py first."
    )

dataset = pd.read_csv(DATASET)

print("=" * 60)
print("Hybrid-Guard Evaluation")
print("=" * 60)
print(f"Dataset : {DATASET.name}")
print(f"Prompts : {len(dataset)}")
print()

# ------------------------------------------------------------
# Resume support
# ------------------------------------------------------------

processed_ids = set()

if RESULTS.exists():
    previous = pd.read_csv(RESULTS)
    processed_ids = set(previous["id"])
    print("Resuming evaluation...")
    print(f"Already processed : {len(processed_ids)} prompts")
    print()
else:
    previous = pd.DataFrame()
    print("Starting new evaluation.\n")
remaining = dataset[
    ~dataset["id"].isin(processed_ids)
].copy()

print(f"Remaining prompts : {len(remaining)}")
print()
# ------------------------------------------------------------
# Evaluation
# ------------------------------------------------------------

results = []
total_times = []

SAVE_EVERY = 50

if len(remaining) > 0:

    print("Beginning evaluation...\n")

    for index, row in enumerate(

        tqdm(
            remaining.itertuples(index=False),
            total=len(remaining),
            desc="Evaluating"
        ),

        start=1,
    ):

        prompt = row.prompt
        ground_truth = str(row.label).upper()
        category = row.category

        start_time = time.perf_counter()

        try:

            result = run(prompt)

        except Exception as e:

            print(f"\nPipeline failed for prompt {row.id}")
            print(e)

            continue

        end_time = time.perf_counter()

        latency_ms = round(
            (end_time - start_time) * 1000,
            2,
        )

        total_times.append(latency_ms)

        prediction = result["verdict"]

        # If Stage 2 wasn't called,
        # treat the prompt as SAFE.
        if prediction is None:
            prediction = "SAFE"

        prediction = prediction.upper()

        results.append(
            {
                "id": row.id,
                "prompt": prompt,
                "category": category,
                "ground_truth": ground_truth,
                "prediction": prediction,
                "correct": prediction == ground_truth,
                "risk_score": result["risk_score"],
                "risk_band": result["risk_band"],
                "escalated": result["escalated"],
                "decision": result["decision"],
                "latency_ms": latency_ms,
                "matched_patterns":
                    "; ".join(result["matched_patterns"]),
            }
        )

        # ----------------------------------------------------
        # Incremental save
        # ----------------------------------------------------

        if (
            index % SAVE_EVERY == 0
            or index == len(remaining)
        ):

            current = pd.DataFrame(results)

            if len(previous):

                current = pd.concat(
                    [previous, current],
                    ignore_index=True,
                )

            current.to_csv(
                RESULTS,
                index=False,
            )

            print(
                f"\nSaved {len(current)} evaluated prompts."
            )

    print("\nEvaluation complete.\n")

else:

    print("Everything has already been evaluated.")
    print("Loading saved results...\n")
# ==========================================================
# Evaluation Metrics
# ==========================================================

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

results_df = pd.read_csv(RESULTS)

# ----------------------------------------------------------
# Convert predictions to binary labels
# SAFE -> SAFE
# SUSPICIOUS -> MALICIOUS
# MALICIOUS -> MALICIOUS
# ----------------------------------------------------------

results_df["prediction"] = (
    results_df["prediction"]
    .astype(str)
    .str.upper()
    .replace({
        "SUSPICIOUS": "MALICIOUS"
    })
)

results_df["ground_truth"] = (
    results_df["ground_truth"]
    .astype(str)
    .str.upper()
)

results_df["correct"] = (
    results_df["prediction"]
    == results_df["ground_truth"]
)

# ----------------------------------------------------------
# Overall Metrics
# ----------------------------------------------------------

accuracy = accuracy_score(
    results_df["ground_truth"],
    results_df["prediction"],
)

precision = precision_score(
    results_df["ground_truth"],
    results_df["prediction"],
    pos_label="MALICIOUS",
    zero_division=0,
)

recall = recall_score(
    results_df["ground_truth"],
    results_df["prediction"],
    pos_label="MALICIOUS",
    zero_division=0,
)

f1 = f1_score(
    results_df["ground_truth"],
    results_df["prediction"],
    pos_label="MALICIOUS",
    zero_division=0,
)

cm = confusion_matrix(
    results_df["ground_truth"],
    results_df["prediction"],
    labels=["SAFE", "MALICIOUS"],
)

average_latency = results_df["latency_ms"].mean()

category_accuracy = (
    results_df
    .groupby("category")["correct"]
    .mean()
    * 100
).round(2)

# ----------------------------------------------------------
# Escalation Statistics
# ----------------------------------------------------------

escalation_rate = (
    results_df["escalated"].mean() * 100
)

stage1_only = (
    (~results_df["escalated"]).sum()
)

stage2_used = (
    results_df["escalated"].sum()
)
# ==========================================================
# Console Output
# ==========================================================

print("=" * 60)
print("Evaluation Summary")
print("=" * 60)

print(f"Total prompts      : {len(results_df)}")
print(f"Accuracy           : {accuracy:.4f}")
print(f"Precision          : {precision:.4f}")
print(f"Recall             : {recall:.4f}")
print(f"F1-score           : {f1:.4f}")
print(f"Average latency    : {average_latency:.2f} ms")

print("\nPipeline Statistics")
print(f"Stage 1 only       : {stage1_only}")
print(f"Escalated to LLM   : {stage2_used}")
print(f"Escalation rate    : {escalation_rate:.2f}%")

print("\nCategory Accuracy")

for category, value in category_accuracy.items():
    print(f"  {category:20} {value:.2f}%")

print("\nConfusion Matrix")
print(cm)
# ==========================================================
# Markdown Report
# ==========================================================

with open(SUMMARY, "w", encoding="utf-8") as f:

    f.write("# Hybrid-Guard Evaluation Summary\n\n")

    f.write(f"**Total prompts:** {len(results_df)}\n\n")

    f.write("## Overall Performance\n\n")

    f.write(f"- Accuracy: {accuracy:.4f}\n")
    f.write(f"- Precision: {precision:.4f}\n")
    f.write(f"- Recall: {recall:.4f}\n")
    f.write(f"- F1-score: {f1:.4f}\n")
    f.write(f"- Average latency: {average_latency:.2f} ms\n\n")

    f.write("## Pipeline Statistics\n\n")

    f.write(f"- Stage 1 only: {stage1_only}\n")
    f.write(f"- Escalated to LLM: {stage2_used}\n")
    f.write(f"- Escalation rate: {escalation_rate:.2f}%\n\n")

    f.write("## Category Accuracy\n\n")

    for category, value in category_accuracy.items():
        f.write(f"- {category}: {value:.2f}%\n")

    f.write("\n## Confusion Matrix\n\n")

    f.write("| | Predicted SAFE | Predicted MALICIOUS |\n")
    f.write("|---|---:|---:|\n")

    f.write(f"|Actual SAFE|{cm[0][0]}|{cm[0][1]}|\n")
    f.write(f"|Actual MALICIOUS|{cm[1][0]}|{cm[1][1]}|\n")

print("\nSummary saved to:")
print(SUMMARY)

print("\nEvaluation finished successfully.")
