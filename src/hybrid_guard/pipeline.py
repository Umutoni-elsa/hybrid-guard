from hybrid_guard.normaliser import normalise
from hybrid_guard.scorer import score_prompt, should_escalate
from hybrid_guard.decision_engine import decide


def run(prompt, conversation_history=None):
    # stage 1: normalise the prompt (strip zero-width chars, decode base64/rot13, fix homoglyphs)
    normalised_text, normalisation_actions = normalise(prompt)

    # stage 1: weighted regex scoring
    score, band, matched_patterns = score_prompt(normalised_text)
    escalated = should_escalate(score)

    verdict = None
    rationale = ""

    if escalated:
        # only import classifier here, so the rest of the pipeline still works
        # even if ollama isn't installed/running yet
        from hybrid_guard.classifier import classify

        try:
            verdict, rationale, votes = classify(normalised_text)
        except RuntimeError as e:
            # ollama not reachable - don't crash the whole pipeline,
            # just treat it as suspicious and say why
            verdict = "SUSPICIOUS"
            rationale = f"Could not run Stage 2 classification: {e}"

    decision = decide(prompt, score, band, matched_patterns, escalated, verdict)

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
