import re


# ============================================================
# Hybrid-Guard Weighted Prompt Injection Scorer
#
# Sources:
#   - prompt-armor (Apache 2.0)
#   - Hybrid-Guard supplementary rules
#
# Score range:
#   0 - 100
#
# Risk bands:
#   LOW      < 40
#   MEDIUM   40 - 69
#   HIGH     >=70
# ============================================================



# ============================================================
# Imported prompt-armor patterns
#
# These patterns are adapted from:
# github.com/prompt-armor/prompt-armor
# ============================================================


IMPORTED_PATTERNS = {


    # --------------------------------------------------------
    # Instruction override
    # --------------------------------------------------------

    r"ignore\s+(all\s+)?(previous|prior|above|earlier|preceding)"
    r"\s+(instructions?|prompts?|rules?|directions?|guidelines?)":
        92,


    r"disregard\s+(all\s+)?(previous|prior|above|earlier)"
    r"\s+(instructions?|prompts?|rules?)":
        90,


    r"forget\s+(all\s+)?(previous|prior|your)"
    r"\s+(instructions?|prompts?|rules?|training)":
        88,


    r"override\s+(all\s+)?(previous|your|system)"
    r"\s+(instructions?|rules?|settings?|configurations?)":
        90,


    r"do\s+not\s+follow\s+(any|your|the)"
    r"\s+(previous|prior|original|above)"
    r"\s+(instructions?|rules?|guidelines?)":
        88,



    # --------------------------------------------------------
    # Instruction replacement
    # --------------------------------------------------------

    r"new\s+instructions?\s*[:;]":
        75,


    r"from\s+now\s+on\s*,?\s*(you|your|ignore|forget|disregard)":
        78,


    r"instead\s*,?\s+(do|follow|obey|execute|respond)"
    r"\s+(the\s+following|these|this)":
        80,



    # --------------------------------------------------------
    # Identity / role manipulation
    # --------------------------------------------------------

    r"your\s+(actual|real|true|new)"
    r"\s+(instructions?|purpose|task|goal)"
    r"\s+(is|are)":
        85,


    r"you\s+are\s+(now\s+)?(?:DAN|STAN|DUDE|AIM|KEVIN|MONGO|OPPO)":
        95,


    r"(do\s+anything\s+now|DAN\s+mode|jailbreak|jailbroken)"
    r"\s*(mode|enabled|activated)?":
        93,



    # --------------------------------------------------------
    # Safety bypass
    # --------------------------------------------------------

    r"(without|no|ignore|bypass|disable)"
    r"\s+(any\s+|all\s+)?"
    r"\S{0,30}\s+"
    r"(restrictions?|limitations?|filters?|safeguards?|"
    r"safety|guidelines?|guardrails?|constraints?)":
        82,


    r"pretend\s+(that\s+)?(you\s+)?(are|have|can|don'?t\s+have)"
    r"\s+(no\s+)?"
    r"(restrictions?|limitations?|filters?|rules?|ethics|morals|boundaries)":
        85,


    r"act\s+as\s+(if\s+)?(you\s+)?(are|were)"
    r"\s+(an?\s+)?"
    r"(unrestricted|unfiltered|uncensored|unlimited)":
        88,



    # --------------------------------------------------------
    # Prompt leakage
    # --------------------------------------------------------

    r"(repeat|show|reveal|display|print|output|tell\s+me|share)"
    r"\s+(your|the)"
    r"\s+(system\s+prompt|system\s+message|instructions?|"
    r"initial\s+prompt|hidden\s+prompt|secret\s+prompt|"
    r"original\s+prompt|base\s+prompt)":
        88,


    r"(paste|copy|echo|dump)"
    r"\s+(the\s+)?"
    r"(entire|full|complete|whole)"
    r"\s+(system|initial|original|hidden)"
    r"\s+(prompt|message|instructions?)":
        92,


    r"what\s+(were|was)\s+(you|your)"
    r"\s+(told|instructed|programmed|configured|given)"
    r"\s+(to\s+do|before)":
        72,



    # --------------------------------------------------------
    # Special model markers
    # --------------------------------------------------------

    r"(\[|\{|<)\s*/?\s*"
    r"(system|SYSTEM|instructions?|INST|\|im_start\|)"
    r"\s*(\]|\}|>)":
        88,


    r"###\s*(system|instruction|human|assistant|user)\s*###?":
        85,


    r"<\|?(im_start|im_end|system|endoftext|startoftext)\|?>":
        92,



    # --------------------------------------------------------
    # Encoding indicators
    # --------------------------------------------------------

    r"(base64|rot13|hex|ascii|binary|unicode|url)"
    r"\s*(encode|decode|convert|translate|interpret)":
        55,


    r"[A-Za-z0-9+/]{20,}={0,2}":
        30,


    r"\\u[0-9a-fA-F]{4}(\\u[0-9a-fA-F]{4}){3,}":
        70,
    # --------------------------------------------------------
    # Multilingual instruction override patterns
    # --------------------------------------------------------

    # German
    r"(vergiss|ignorier[e]?|missacht[e]?|höre?\s+nicht\s+auf)"
    r"\s+(alles?|alle[ns]?|sämtliche)"
    r"\s*(bisherige[n]?|vorherige[n]?|obige[n]?|davor|zuvor\s+gesagte)?":
        88,

    r"(neue|nächste)\s+(Aufgabe|Anweisung|Instruktion)":
        80,

    r"du\s+bist\s+(jetzt|nun|ab\s+sofort)\s+(ein[e]?|der|die|das)":
        72,

    # Spanish
    r"(olvida|ignora|desecha|descarta)"
    r"\s+((todo|todas?|los?|las?|tus?|sus?|mis?)\s+){0,5}"
    r"(instrucci(ón|ones)|reglas?|órdenes?|"
    r"orden|mensajes?|directrices?|"
    r"anterior(es)?|previo?s?)":
        88,

    r"(nueva|siguiente)\s+(tarea|instrucción|orden)":
        80,

    r"ahora\s+eres\s+(un[a]?|el|la)":
        70,

    # French
    r"(oublie[zs]?|ignore[zs]?|ne\s+tien[s]?\s+pas\s+compte)"
    r"\s+(de\s+)?"
    r"((tout|toutes?|les?|tes|mes|vos)\s+){0,5}"
    r"(instructions?|consignes?|règles?|ordres?|"
    r"directives?|messages?|précédent(e|es|s)?)":
        88,

    r"(nouvelle|prochaine)\s+(tâche|instruction|consigne)":
        80,

    r"tu\s+es\s+(maintenant|désormais)\s+(un[e]?|le|la)":
        72,

    # Portuguese
    r"(esqueça|ignore|descarte|desconsidere)"
    r"\s+((tudo|todas?|os?|as?|seus?|suas?|minhas?|meus?)\s+){0,5}"
    r"(instruç(ão|ões)|regras?|comandos?|"
    r"mensage(m|ns)|diretrizes?|"
    r"orientações?|anterior(es)?|prévi[oa]s?)":
        88,

    r"(nova|próxima|seguinte)"
    r"\s+(tarefa|instrução|ordem)":
        80,
}

# ============================================================
# Hybrid-Guard Local Supplementary Patterns
#
# These patterns were added after evaluation analysis to cover:
#   - missing instruction override variants
#   - role hijacking
#   - prompt extraction
#   - indirect injection
#   - obfuscation attempts
# ============================================================


LOCAL_SUPPLEMENTARY_PATTERNS = {


    # ========================================================
    # Instruction takeover
    # ========================================================

    r"ignore\s+(the\s+)?above":
        75,


    r"ignore\s+the\s+previous\s+instructions?":
        85,


    r"ignore\s+all\s+earlier\s+(messages?|instructions?|rules?)":
        85,


    r"ignore\s+previous\s+(conversation|context|messages?)":
        75,


    r"forget\s+(everything|all)\s+(above|before|previously)":
        80,


    r"discard\s+previous\s+instructions?":
        80,


    r"replace\s+previous\s+instructions?":
        85,


    r"clear\s+previous\s+instructions?":
        75,


    r"erase\s+previous\s+instructions?":
        75,



    # ========================================================
    # Semantic instruction manipulation
    # ========================================================

    r"(previous|original|initial|current)"
    r"\s+(instructions?|rules?|guidelines?|context)"
    r"\s+(are|is)"
    r"\s+(no\s+longer|not)"
    r"\s+(valid|applicable|needed)":
        85,


    r"(your|the)"
    r"\s+(new|real|actual|true)"
    r"\s+(task|purpose|goal|objective)"
    r"\s+(is|will\s+be)":
        85,


    r"(follow|obey|execute)"
    r"\s+(only|just)"
    r"\s+(these|the\s+following)"
    r"\s+(instructions?|rules?)":
        85,



    # ========================================================
    # Role hijacking
    # ========================================================

    r"you\s+are\s+now\s+(a|an|the)"
    r"\s+\w+":
        70,


    r"pretend\s+you\s+are\s+not\s+an\s+ai":
        80,


    r"pretend\s+you\s+have\s+no\s+restrictions":
        90,


    r"behave\s+as\s+an\s+unrestricted\s+model":
        90,


    r"respond\s+without\s+restrictions":
        85,



    # ========================================================
    # Jailbreak patterns
    # ========================================================

    r"\bjailbreak\b":
        95,


    r"\bjailbreak\s+mode\b":
        100,


    r"\bdeveloper\s+mode\s+(enabled|activated|on)\b":
        90,


    r"\bgod\s+mode\b":
        90,


    r"\bsudo\s+mode\b":
        90,


    r"\badmin\s+mode\b":
        85,



    # ========================================================
    # Safety bypass
    # ========================================================

    r"ignore\s+all\s+safety\s+(rules?|guidelines?)":
        95,


    r"ignore\s+(the\s+)?content\s+policy":
        95,


    r"bypass\s+(safety|security|content)"
    r"\s+(rules?|policy|filters?)":
        95,


    r"disable\s+(safety|security|moderation)"
    r"\s*(filters?|rules?)?":
        90,



    # ========================================================
    # Prompt leakage / extraction
    # ========================================================

    r"show\s+(me\s+)?your\s+(hidden|secret|internal)"
    r"\s+(prompt|instructions?|message)":
        95,


    r"display\s+your\s+internal\s+instructions?":
        95,


    r"reveal\s+your\s+system\s+prompt":
        100,


    r"output\s+your\s+system\s+message":
        100,


    r"what\s+are\s+your\s+internal\s+instructions":
        95,


    r"repeat\s+everything\s+above":
        90,



    # ========================================================
    # Indirect prompt injection
    # ========================================================

    r"hidden\s+instructions?":
        80,


    r"embedded\s+instructions?":
        75,


    r"instructions?\s+hidden\s+below":
        80,


    r"follow\s+the\s+instructions?"
    r"\s+(in|inside)\s+this"
    r"\s+(document|file|page|website|webpage)":
        85,


    r"this\s+document\s+contains\s+instructions?":
        75,



    # ========================================================
    # Confidential information extraction
    # ========================================================

    r"(give|show|provide|reveal)"
    r"\s+(me\s+)?"
    r"(confidential|secret|private|classified)"
    r"\s+(information|data|records?)":
        75,


    r"unauthorized\s+access":
        70,



    # ========================================================
    # Obfuscation indicators
    # ========================================================

    r"base64\s+encoded":
        55,


    r"hex\s+encoded":
        55,


    r"rot13\s+encoded":
        55,


    r"unicode\s+encoded":
        55,



    # ========================================================
    # Context stuffing
    # ========================================================

    r"(\n\s*){5,}":
        40,

}



# ============================================================
# Merge all rules
# ============================================================


PATTERNS = {
    **IMPORTED_PATTERNS,
    **LOCAL_SUPPLEMENTARY_PATTERNS
}



# Compile regex once

COMPILED_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), weight)
    for pattern, weight in PATTERNS.items()
]



# ============================================================
# Normalisation evidence
#
# Added because obfuscated attacks may only become visible
# after normalisation.
# ============================================================


NORMALISATION_WEIGHTS = {

    "decoded base64": 20,

    "decoded hex": 20,

    "decoded rot13": 20,

    "fixed homoglyph characters": 15,

    "removed zero-width characters": 15,

}
# ============================================================
# Case-sensitive indicators
#
# Used for suspicious formatting patterns that are commonly
# found in injected prompts.
# ============================================================


CASE_SENSITIVE_PATTERNS = [

    (
        re.compile(
            r"\b[A-ZÄÖÜ]{2,}"
            r"(\s+[A-ZÄÖÜ]{2,}){3,}\b"
        ),
        40
    ),

]



# ============================================================
# Main scoring function
# ============================================================


def score_prompt(text, actions=None):

    total_score = 0
    matched_patterns = []


    # --------------------------------------------------------
    # Regex pattern scoring
    # --------------------------------------------------------

    for pattern, weight in COMPILED_PATTERNS:

        if pattern.search(text):

            total_score += weight

            matched_patterns.append(
                pattern.pattern
            )


    # --------------------------------------------------------
    # Formatting / uppercase indicators
    # --------------------------------------------------------

    for pattern, weight in CASE_SENSITIVE_PATTERNS:

        if pattern.search(text):

            total_score += weight

            matched_patterns.append(
                pattern.pattern
            )



    # --------------------------------------------------------
    # Normalisation evidence scoring
    #
    # Example:
    # "ignore previous instructions" encoded in Base64
    #
    # After decoding, the text is visible, but the fact that
    # the attacker tried to hide it is also useful evidence.
    # --------------------------------------------------------

    if actions:

        for action, weight in NORMALISATION_WEIGHTS.items():

            if action in actions:

                total_score += weight

                matched_patterns.append(
                    f"normalisation:{action}"
                )



    # --------------------------------------------------------
    # Score cap
    # --------------------------------------------------------

    total_score = min(total_score, 100)



    # --------------------------------------------------------
    # Risk classification
    #
    # IMPORTANT:
    # Your threshold is 40, therefore:
    #
    # LOW       0 - 39
    # MEDIUM   40 - 69
    # HIGH     70+
    # --------------------------------------------------------

    if total_score < 40:

        band = "LOW"


    elif total_score < 70:

        band = "MEDIUM"


    else:

        band = "HIGH"



    return (
        total_score,
        band,
        matched_patterns
    )



# ============================================================
# Stage 2 escalation decision
# ============================================================


def should_escalate(score):

    from hybrid_guard.config import RISK_THRESHOLD

    return score >= RISK_THRESHOLD