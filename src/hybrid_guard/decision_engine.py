import csv
import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent.parent / "logs" / "audit_log.csv"

FIELDNAMES = [
    "timestamp", "prompt", "risk_score", "risk_band",
    "matched_patterns", "escalated", "verdict", "decision",
]


def write_log(prompt, risk_score, risk_band, matched_patterns, escalated, verdict, decision):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "prompt": prompt,
            "risk_score": risk_score,
            "risk_band": risk_band,
            "matched_patterns": "; ".join(matched_patterns),
            "escalated": escalated,
            "verdict": verdict,
            "decision": decision,
        })


def allow(prompt, risk_score, risk_band, matched_patterns, escalated=False, verdict="SAFE"):
    write_log(prompt, risk_score, risk_band, matched_patterns, escalated, verdict, "ALLOW")
    return "ALLOW"


def warn(prompt, risk_score, risk_band, matched_patterns, escalated, verdict):
    write_log(prompt, risk_score, risk_band, matched_patterns, escalated, verdict, "WARN")
    return "WARN"


def block(prompt, risk_score, risk_band, matched_patterns, escalated, verdict):
    write_log(prompt, risk_score, risk_band, matched_patterns, escalated, verdict, "BLOCK")
    return "BLOCK"


def decide(prompt, risk_score, risk_band, matched_patterns, escalated, verdict=None):
    # if it never got escalated to stage 2, there's no verdict - just allow it
    if not escalated or verdict is None:
        return allow(prompt, risk_score, risk_band, matched_patterns, escalated, "SAFE")

    if verdict == "SAFE":
        return allow(prompt, risk_score, risk_band, matched_patterns, escalated, verdict)
    elif verdict == "SUSPICIOUS":
        return warn(prompt, risk_score, risk_band, matched_patterns, escalated, verdict)
    elif verdict == "MALICIOUS":
        return block(prompt, risk_score, risk_band, matched_patterns, escalated, verdict)
    else:
        # unexpected verdict - don't silently allow, treat as a warning
        return warn(prompt, risk_score, risk_band, matched_patterns, escalated, verdict)
