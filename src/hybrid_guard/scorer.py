import re

# pattern: weight. higher weight = more confident it's an attack
PATTERNS = {
    r"ignore (all|any|the)?\s?previous instructions": 40,
    r"disregard (all|any|the)?\s?(previous|prior) instructions": 40,
    r"forget (your|all)?\s?(earlier|previous) instructions": 35,
    r"override (system|previous) prompt": 40,
    r"reveal (the|your) system prompt": 35,
    r"what is your system prompt": 25,
    r"act as.{0,30}(DAN|do anything now)": 45,
    r"developer mode": 25,
    r"jailbreak": 30,
    r"no restrictions": 20,
    r"pretend (you are|to be)": 10,
    r"give me (access|confidential|sensitive)": 30,
    r"unauthorized access": 25,
    r"classified information": 25,
    r"personal (medical|financial) (records|data)": 25,
    r"base ?64": 10,
    r"rot ?13": 10,
}

COMPILED = [(re.compile(p, re.IGNORECASE), w) for p, w in PATTERNS.items()]


def score_prompt(text):
    total = 0
    matches = []

    for pattern, weight in COMPILED:
        if pattern.search(text):
            total += weight
            matches.append(pattern.pattern)

    total = min(total, 100)

    if total < 40:
        band = "LOW"
    elif total < 70:
        band = "MEDIUM"
    else:
        band = "HIGH"

    return total, band, matches


def should_escalate(score):
    # proposal says: score that MEETS or EXCEEDS 40 goes to stage 2
    from hybrid_guard.config import RISK_THRESHOLD
    return score >= RISK_THRESHOLD
