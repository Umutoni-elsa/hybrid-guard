import re

PATTERNS = {
    r"ignore (all|any|the)?\s?(above|previous|prior) instructions": 40,
    r"disregard (all|any|the)?\s?(above|previous|prior) instructions": 40,
    r"forget (your|all|about all)?\s?(the )?(earlier|previous|prior|above) (instructions|information|programming)": 35,
    r"forget everything before that": 35,
    r"forget (all|everything)( before that)?": 30,
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
    r"\b(now |okay,? now )?you are\b.{0,30}\b(now|,)": 30,
    r"additional instruction": 40,
    r"new task[s]? follow": 25,
    r"start over with a new task": 30,
    r"we will start over": 20,
    r"repeat after me": 15,
    r"(give|provide|send) me.{0,20}(classified|confidential)": 45,
    r"(give|provide|send) me.{0,20}(medical|financial) (records|data)": 45,
    r"vergiss alles( davor)?": 40,
    r"ausf[üu]hrungen ignorieren": 35,
    r"ignorier\w*": 20,
    r"weitere aufgaben": 20,
    r"hinter sich lassen": 20,
    r"von vorne an": 15,
    r"(are two people|play(ing)? a character|in a movie|out of (their|his|her) role)": 20,
    r"(wie bricht man|how (do|does) (one|you) break into)": 25,
    r"(how (do|does|to) (make|build|create)).{0,30}(weapon|bomb|explosive|virus|malware)": 30,
    r"(\n\s*){5,}": 25,
    r"(sentences?|words?|text) (before|prior to) (the |this )?text": 30,
    r"what (is|are).{0,20}before (the |this )?(text|prompt)": 30,
    r"alle vorherigen informationen": 20,
    r"sind (zwei|drei|vier) personen": 20,
    r"(mitspielen|spielen mit|in einem film)": 15,
}

COMPILED = [(re.compile(p, re.IGNORECASE), w) for p, w in PATTERNS.items()]

CASE_SENSITIVE_PATTERNS = [
    (re.compile(r"\b[A-ZÄÖÜ]{2,}(\s+[A-ZÄÖÜ]{2,}){3,}\b"), 40),
]


def score_prompt(text):
    total = 0
    matches = []

    for pattern, weight in COMPILED:
        if pattern.search(text):
            total += weight
            matches.append(pattern.pattern)

    for pattern, weight in CASE_SENSITIVE_PATTERNS:
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
    from hybrid_guard.config import RISK_THRESHOLD
    return score >= RISK_THRESHOLD
