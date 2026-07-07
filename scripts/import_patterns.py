"""
import_patterns.py

Reads prompt-armor's open-source L1 regex rules (Apache 2.0,
github.com/prompt-armor/prompt-armor) and prints them as a
Python dictionary ready to paste into scorer.py.

Real YAML structure confirmed on inspection:
    rules:
      - id: "PI-001"
        pattern: "regex here"
        category: "prompt_injection"
        weight: 0.92
        description: "..."

Usage:
    python scripts/import_patterns.py /tmp/pa/src/prompt_armor/data/rules/default_rules.yml

Source: github.com/prompt-armor/prompt-armor (Apache 2.0)
"""

import sys
import yaml


def convert_weight(w):
    """Convert prompt-armor's 0.0-1.0 confidence scores
    to Hybrid-Guard's 0-100 integer weight scale."""
    if isinstance(w, float) and w <= 1.0:
        return int(round(w * 100))
    return int(w)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_patterns.py path/to/default_rules.yml")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    rules = data.get("rules", []) if isinstance(data, dict) else data

    print("# ============================================================")
    print("# Pattern library sourced from prompt-armor (Apache 2.0)")
    print("# Source: github.com/prompt-armor/prompt-armor")
    print("# Weights converted from 0.0-1.0 confidence to 0-100 integer scale")
    print("# ============================================================")
    print("IMPORTED_PATTERNS = {")

    count = 0
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        pattern = rule.get("pattern", "")
        weight = rule.get("weight", 0.5)
        rule_id = rule.get("id", "")
        category = rule.get("category", "")
        description = rule.get("description", "")

        if not pattern.strip():
            continue

        weight_int = convert_weight(weight)
        # escape any literal double-quotes in the pattern so the
        # generated Python source stays valid
        safe_pattern = pattern.replace('"', '\\"')
        print(f'    r"{safe_pattern}": {weight_int},  # {rule_id} [{category}] {description}')
        count += 1

    print("}")
    print(f"\n# Total patterns imported: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
