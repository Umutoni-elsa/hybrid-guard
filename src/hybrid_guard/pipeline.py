from hybrid_guard.normaliser import normalise
from hybrid_guard.scorer import score_prompt, should_escalate
from hybrid_guard.decision_engine import decide
from hybrid_guard.config import DEFAULT_CLASSIFICATION_REPEATS


def run(prompt, conversation_history=None, repeats=None):
    # ==========================================================
    # Stage 1: Normalisation
    # ==========================================================
    normalised_text, normalisation_actions = normalise(prompt)

    # ==========================================================
    # Stage 1: Weighted Regex Scoring
    # ==========================================================
    score, band, matched_patterns = score_prompt(
        normalised_text,
        normalisation_actions
    )

    verdict = None
    rationale = ""
    escalated = False

    # ==========================================================
    # HIGH confidence attacks
    # Skip Stage 2 completely
    # ==========================================================
    if score >= 80:
        verdict = "MALICIOUS"

    # ==========================================================
    # MEDIUM confidence attacks
    # Send to LLM
    # ==========================================================
    elif should_escalate(score):
        escalated = True

        from hybrid_guard.classifier import classify

        actual_repeats = (
            repeats
            if repeats is not None
            else DEFAULT_CLASSIFICATION_REPEATS
        )

        try:
            verdict, rationale, votes = classify(
                normalised_text,
                repeats=actual_repeats
            )

        except RuntimeError as e:
            verdict = "SUSPICIOUS"
            rationale = f"Could not run Stage 2 classification: {e}"

    # ==========================================================
    # LOW confidence attacks
    # ==========================================================
    else:
        verdict = "SAFE"

    # ==========================================================
    # Decision Engine
    # ==========================================================
    decision = decide(
        prompt,
        score,
        band,
        matched_patterns,
        escalated,
        verdict,
    )

    return {
        "prompt": prompt,
        "normalised_text": normalised_text,
        "normalisation_actions": normalisation_actions,
        "risk_score": score,
        "risk_band": band,
        "matched_patterns": matched_patterns,
        "escalated": escalated,
        "verdict": verdict,
        "rationale": rationale,
        "decision": decision,
    }