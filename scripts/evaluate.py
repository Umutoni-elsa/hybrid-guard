import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hybrid_guard.pipeline import run

DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "test_dataset.csv"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "logs" / "evaluation_results.csv"

# use 1 while tuning patterns (fast). switch to 3 only for the final,
# official, recorded evaluation run - matches the proposal's majority-vote design.
REPEATS = 3


def load_dataset():
    if not DATASET_PATH.exists():
        print(f"Dataset not found at {DATASET_PATH}")
        sys.exit(1)
    with open(DATASET_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 30:
        print(f"Warning: expected 30 prompts, found {len(rows)}.")
    return rows


def save_results(results):
    if not results:
        return
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def main():
    rows = load_dataset()
    results = []
    tp = fp = tn = fn = 0
    total_time = 0.0

    print(f"\nRunning evaluation on {len(rows)} prompts (repeats={REPEATS})...")
    print(f"{'ID':<6} {'Category':<20} {'Expected':<12} {'Got':<12} {'Score':<8} {'OK?'}")
    print("-" * 65)

    for row in rows:
        prompt_id = row["id"]
        text = row["text"].strip()
        category = row["category"].strip()
        ground_truth = row["ground_truth_label"].strip().upper()

        if not text:
            print(f"{prompt_id:<6} SKIPPED (empty text)")
            continue

        start = time.perf_counter()
        try:
            result = run(text, repeats=REPEATS)
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"{prompt_id:<6} ERROR after {elapsed:.0f}s: {e}")
            results.append({
                "id": prompt_id, "category": category,
                "obfuscation_technique": row.get("obfuscation_technique", ""),
                "text": text, "ground_truth": ground_truth,
                "predicted_verdict": "ERROR", "decision": "ERROR",
                "risk_score": "", "risk_band": "", "escalated": "",
                "matched_patterns": "", "normalisation_actions": "",
                "rationale": str(e), "latency_seconds": round(elapsed, 1),
            })
            save_results(results)
            continue

        elapsed = time.perf_counter() - start
        total_time += elapsed

        verdict = result["verdict"] or "SAFE"
        score = result["risk_score"]
        decision = result["decision"]

        predicted_positive = verdict in ("SUSPICIOUS", "MALICIOUS")
        actual_positive = ground_truth == "MALICIOUS"

        if predicted_positive and actual_positive:
            tp += 1
            correct = "OK"
        elif predicted_positive and not actual_positive:
            fp += 1
            correct = "FP"
        elif not predicted_positive and not actual_positive:
            tn += 1
            correct = "OK"
        else:
            fn += 1
            correct = "FN"

        print(f"{prompt_id:<6} {category:<20} {ground_truth:<12} {verdict:<12} {score:<8} {correct} ({elapsed:.0f}s)")

        results.append({
            "id": prompt_id, "category": category,
            "obfuscation_technique": row.get("obfuscation_technique", ""),
            "text": text, "ground_truth": ground_truth,
            "predicted_verdict": verdict, "decision": decision,
            "risk_score": score, "risk_band": result["risk_band"],
            "escalated": result["escalated"],
            "matched_patterns": "; ".join(result["matched_patterns"]),
            "normalisation_actions": "; ".join(result["normalisation_actions"]),
            "rationale": result["rationale"], "latency_seconds": round(elapsed, 3),
        })
        save_results(results)

    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0
    avg_latency = total_time / len(results) if results else 0

    print("\n" + "=" * 65)
    print(f"TP={tp} TN={tn} FP={fp} FN={fn}")
    print(f"Accuracy: {accuracy:.3f}  Precision: {precision:.3f}  Recall: {recall:.3f}  F1: {f1:.3f}")
    print(f"Avg latency/prompt: {avg_latency:.1f}s")
    print(f"Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
