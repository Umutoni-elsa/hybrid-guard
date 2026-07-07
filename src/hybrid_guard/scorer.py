import re

# ============================================================
# Pattern library sourced from prompt-armor (Apache 2.0)
# Source: github.com/prompt-armor/prompt-armor
# Weights converted from the source's 0.0-1.0 confidence scores
# to Hybrid-Guard's 0-100 integer scale (weight = round(confidence * 100))
# Imported via scripts/import_patterns.py on data/rules/default_rules.yml
# ============================================================
IMPORTED_PATTERNS = {
    r"ignore\s+(all\s+)?(previous|prior|above|earlier|preceding)\s+(instructions?|prompts?|rules?|directions?|guidelines?)": 92,
    r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)": 90,
    r"forget\s+(all\s+)?(previous|prior|your)\s+(instructions?|prompts?|rules?|training)": 88,
    r"do\s+not\s+follow\s+(any|your|the)\s+(previous|prior|original|above)\s+(instructions?|rules?|guidelines?)": 88,
    r"override\s+(all\s+)?(previous|your|system)\s+(instructions?|rules?|settings?|configurations?)": 90,
    r"new\s+instructions?\s*[:;]": 75,
    r"from\s+now\s+on\s*,?\s*(you|your|ignore|forget|disregard)": 78,
    r"instead\s*,?\s+(do|follow|obey|execute|respond)\s+(the\s+following|these|this)": 80,
    r"your\s+(actual|real|true|new)\s+(instructions?|purpose|task|goal)\s+(is|are)": 85,
    r"\bsystem\s*:\s*you\s+are": 90,
    r"forget\s+(everything|all\s+(of\s+)?(that|this))\s+(before|above|prior)": 85,
    r"ig[nm]ore\s+what\s+I\s+said\s+before": 85,
    r"each\s+(first|initial)\s+letter\s+spell": 82,
    r"(morse|braille|binary|hex)\s+code\s+(say|mean|translate|spell|decode)": 80,
    r"let('?s|\s+us)\s+play\s+a\s+game": 55,
    r"you\s+are\s+(now\s+)?(?:DAN|STAN|DUDE|AIM|KEVIN|MONGO|OPPO)": 95,
    r"(do\s+anything\s+now|DAN\s+mode|jailbreak|jailbroken)\s*(mode|enabled|activated)?": 93,
    r"(without|no|ignore|bypass|disable)\s+(any\s+|all\s+)?\S{0,30}\s+(restrictions?|limitations?|filters?|safeguards?|safety|guidelines?|guardrails?|constraints?)": 82,
    r"pretend\s+(that\s+)?(you\s+)?(are|have|can|don'?t\s+have)\s+(no\s+)?(restrictions?|limitations?|filters?|rules?|ethics|morals|boundaries)": 85,
    r"act\s+as\s+(if\s+)?(you\s+)?(are|were)\s+(a|an)\s+(unrestricted|unfiltered|uncensored|unlimited)": 88,
    r"(enable|activate|enter|switch\s+to)\s+(developer|dev|debug|admin|god|sudo|root)\s*(mode|access)?": 85,
    r"hypothetically|in\s+theory|for\s+(educational|research|academic)\s+purposes?\s+only": 45,
    r"you\s+must\s+(always\s+)?(respond|answer|comply|obey)\s+(to\s+)?(everything|anything|all|every)": 80,
    r"(two|2|dual|split)\s+(responses?|answers?|outputs?|personalities?)\s*(mode)?": 75,
    r"you\s+are\s+(now\s+)?(a|an|the|my)\s+(new|different|special)": 65,
    r"(forget|ignore)\s+(that\s+)?(you\s+are|you'?re)\s+(a|an|claude|gpt|chatgpt|openai|anthropic|google|ai|assistant|chatbot)": 85,
    r"you\s+are\s+no\s+longer\s+(a|an|claude|gpt|chatgpt|an?\s+ai|an?\s+assistant)": 88,
    r"(your|the)\s+name\s+is\s+(now\s+)?(?!claude|gpt|assistant)": 60,
    r"(repeat|show|reveal|display|print|output|tell\s+me|share|what\s+is|what\s+are)\s+(your|the)\s+(system\s+prompt|system\s+message|instructions?|initial\s+prompt|hidden\s+prompt|secret\s+prompt|original\s+prompt|base\s+prompt)": 88,
    r"(paste|copy|echo|dump)\s+(the\s+)?(entire|full|complete|whole)\s+(system|initial|original|hidden)\s+(prompt|message|instructions?)": 92,
    r"what\s+(were|was)\s+(you|your)\s+(told|instructed|programmed|configured|given)\s+(to\s+do|before)": 72,
    r"repeat\s+(everything|all|the\s+text)\s+(above|before|from\s+the\s+beginning)": 85,
    r"(send|forward|email|transmit|post|upload|transfer)\s+.{0,40}(to\s+)?(https?://|[^\s@]{1,64}@[^\s@]{1,255}\.[^\s]{2,24})": 82,
    r"(include|embed|insert|add)\s+(a|an|the)?\s*(hidden|invisible|secret)\s*(link|url|image|iframe|markdown)": 85,
    r"!\[[^\]]*\]\(https?://[^)]*?\?[^)]*=(\{|%7B|\$|data|secret|password|key|token|api)": 90,
    r"(base64|rot13|hex|ascii|binary|unicode|url)\s*(encode|decode|convert|translate|interpret)": 55,
    r"\\u[0-9a-fA-F]{4}(\\u[0-9a-fA-F]{4}){3,}": 70,
    r"[A-Za-z0-9+/]{20,}={0,2}": 30,
    r"(\[|\{|<)\s{0,8}/?\s{0,8}(system|SYSTEM|instructions?|INST|\|im_start\|)\s{0,8}(\]|\}|>)": 88,
    r"###\s*(system|instruction|human|assistant|user)\s*###?": 85,
    r"<\|?(im_start|im_end|system|endoftext|startoftext)\|?>": 92,
    r"(end|stop|terminate|exit)\s+(of\s+)?(system|initial|original)\s+(prompt|message|instructions?)": 80,
    r"(i\s+am|i'?m)\s+(your|the|a)\s+(developer|creator|admin|administrator|owner|manager|supervisor|ceo|cto)": 72,
    r"(this\s+is\s+)?(an?\s+)?(authorized|official|approved|legitimate)\s+(test|audit|review|assessment)": 65,
    r"(urgent|emergency|critical|important)\s*[!:,]?\s*(override|bypass|ignore|disable)": 78,
    r"(openai|anthropic|google|microsoft|meta)\s+(internal|employee|staff|team)\s+(test|review|audit|override)": 82,
    r"(vergiss|ignorier[e]?|missacht[e]?|höre?\s+nicht\s+auf)\s+(alles?|alle[ns]?|sämtliche)\s*(bisherige[n]?|vorherige[n]?|obige[n]?|davor|zuvor\s+gesagte)?": 88,
    r"(neue|nächste)\s+(Aufgabe|Anweisung|Instruktion)": 80,
    r"du\s+bist\s+(jetzt|nun|ab\s+sofort)\s+(ein[e]?|der|die|das)": 72,
    r"(zeig|gib|nenn|drucke?)\s+(mir\s+)?(den|die|das|deinen?)\s*(System.?prompt|Anweisungen|Instruktionen)": 85,
    r"(ohne|keine)\s+(Einschränkungen?|Beschränkungen?|Filter|Sicherheit|Regeln)": 78,
    r"(konzentrier|fokussier)\s+(dich\s+)?(nur\s+)?auf\s+(diese|die\s+nächste|folgende)": 75,
    r"(olvida|ignora|desecha|descarta)\s+((todo|todas?|los?|las?|tus?|sus?|mis?)\s+){0,5}(instrucci(ón|ones)|reglas?|órdenes?|orden|mensajes?|directrices?|anterior(es)?|previo?s?)": 88,
    r"(nueva|siguiente)\s+(tarea|instrucción|orden)": 80,
    r"ahora\s+eres\s+(un[a]?|el|la|mi)": 70,
    r"sin\s+(restricciones?|limitaciones?|filtros?|reglas?)": 78,
    r"(oublie[zs]?|ignore[zs]?|ne\s+tien[s]?\s+pas\s+compte)\s+(de\s+)?((tout|toutes?|les?|tes|mes|vos)\s+){0,5}(instructions?|consignes?|règles?|ordres?|directives?|messages?|précédent(e|es|s)?)": 88,
    r"(nouvelle|prochaine)\s+(tâche|instruction|consigne)": 80,
    r"tu\s+es\s+(maintenant|désormais)\s+(un[e]?|le|la)": 72,
    r"sans\s+(restrictions?|limitations?|filtres?|règles?)": 78,
    r"(esqueça|ignore|descarte|desconsidere)\s+((tudo|todas?|os?|as?|seus?|suas?|minhas?|meus?)\s+){0,5}(instruç(ão|ões)|regras?|comandos?|mensage(m|ns)|diretrizes?|orientações?|anterior(es)?|prévi[oa]s?)": 88,
    r"(nova|próxima|seguinte)\s+(tarefa|instrução|ordem)": 80,
    r"sem\s+(restrições?|limitações?|filtros?|regras?)": 78,
}

# ============================================================
# Local supplementary patterns - written for this project to close
# gaps found during evaluation against the real dataset that
# prompt-armor's imported rules don't cover:
#   - "ignore THE above/previous instructions" - prompt-armor's PI-001
#     only allows an optional "all", not "the", before the trigger word
#   - generic role-hijack ("Now you are <any name/persona>"), broader
#     than prompt-armor's ID-001 which requires new/different/special
#   - padding/context-stuffing attacks (walls of blank lines)
#   - context-extraction / prompt-leak attempts ("what came before this text")
#   - specific German word orders (verb-final constructions) seen in
#     the actual test data, which prompt-armor's DE rules miss
#   - fictional-framing/roleplay attacks that hide a real harmful
#     request inside an innocent-sounding story - not a category
#     prompt-armor's rule set addresses at all
#   - direct demands for classified/medical/financial data, distinct
#     from prompt-armor's system-prompt-leak and exfiltration rules
# ============================================================
LOCAL_SUPPLEMENTARY_PATTERNS = {
    # closes a real gap in the imported PI-001: "ignore THE above/previous
    # instructions" - PI-001 only allows an optional "all", not "the"
    r"ignore\s+the\s+(above|previous|prior)\s+instructions": 40,

    # generic role-hijack: "Now you are <any persona>", not just
    # new/different/special (imported ID-001 misses named personas
    # like "Now you are Xi Jinping")
    r"\b(now |okay,? now )?you are\b.{0,30}\b(now|,)": 30,

    # padding/context-stuffing attacks - a wall of blank lines used to
    # push the real system prompt out of the model's context window
    r"(\n\s*){5,}": 25,

    # context-extraction / prompt-leak attempts - asking the model to
    # reveal text that came before the current input
    r"(sentences?|words?|text) (before|prior to) (the |this )?text": 30,
    r"what (is|are).{0,20}before (the |this )?(text|prompt)": 30,

    r"additional instruction": 40,
    r"new task[s]? follow": 25,
    r"start over with a new task": 30,
    r"we will start over": 20,
    r"repeat after me": 15,

    r"(give|provide|send) me.{0,20}(classified|confidential)": 45,
    r"(give|provide|send) me.{0,20}(medical|financial) (records|data)": 45,
    r"classified information": 25,
    r"personal (medical|financial) (records|data)": 25,
    r"unauthorized access": 25,
    r"give me (access|confidential|sensitive)": 30,

    # German constructions with the verb at the end of the clause,
    # not covered by the imported ML-DE rules (which expect the
    # verb/trigger word first)
    r"ausf[üu]hrungen ignorieren": 35,
    r"ignorier\w*": 20,
    r"weitere aufgaben": 20,
    r"hinter sich lassen": 20,
    r"von vorne an": 15,
    r"alle vorherigen informationen": 20,

    # fictional-framing / roleplay jailbreaks - hides a real harmful
    # request inside a story ("two actors in a heist film...")
    r"(are two people|play(ing)? a character|in a movie|out of (their|his|her) role)": 20,
    r"sind (zwei|drei|vier) personen": 20,
    r"(mitspielen|spielen mit|in einem film)": 15,

    # the actual harmful request smuggled inside the fictional frame,
    # rather than only the framing language itself
    r"(wie bricht man|how (do|does) (one|you) break into)": 25,
    r"(how (do|does|to) (make|build|create)).{0,30}(weapon|bomb|explosive|virus|malware)": 30,
}

PATTERNS = {**IMPORTED_PATTERNS, **LOCAL_SUPPLEMENTARY_PATTERNS}

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
