# Hybrid-Guard Evaluation Summary

**Total prompts:** 749

## Overall Performance

- Accuracy: 0.6716
- Precision: 1.0000
- Recall: 0.3941
- F1-score: 0.5654
- Average latency: 1023.88 ms

## Pipeline Statistics

- Stage 1 only: 666
- Escalated to LLM: 83
- Escalation rate: 11.08%

## Category Accuracy

- clean: 100.00%
- direct_injection: 26.11%
- obfuscated: 52.71%

## Confusion Matrix

| | Predicted SAFE | Predicted MALICIOUS |
|---|---:|---:|
|Actual SAFE|343|0|
|Actual MALICIOUS|246|160|
