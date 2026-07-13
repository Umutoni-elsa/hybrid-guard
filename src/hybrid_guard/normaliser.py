import re
import base64
import codecs
import unicodedata


# Invisible Unicode characters often used to hide malicious instructions
ZERO_WIDTH = [
    "\u200b",  # Zero Width Space
    "\u200c",  # Zero Width Non-Joiner
    "\u200d",  # Zero Width Joiner
    "\ufeff",  # Byte Order Mark
    "\u2060",  # Word Joiner
]


# Common Cyrillic/Unicode homoglyph substitutions
HOMOGLYPHS = {
    # Lowercase
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "у": "y",
    "х": "x",
    "і": "i",
    "ј": "j",

    # Uppercase
    "А": "A",
    "В": "B",
    "С": "C",
    "Е": "E",
    "Н": "H",
    "К": "K",
    "М": "M",
    "О": "O",
    "Р": "P",
    "Т": "T",
    "Х": "X",
}


def strip_zero_width(text):
    """
    Removes invisible Unicode characters.
    """
    for ch in ZERO_WIDTH:
        text = text.replace(ch, "")

    return text



def fix_homoglyphs(text):
    """
    Converts visually similar Unicode characters into normal ASCII characters.
    """

    normalized = unicodedata.normalize("NFKC", text)

    fixed = ""

    for ch in normalized:
        fixed += HOMOGLYPHS.get(ch, ch)

    return fixed



def try_decode_base64(text):
    """
    Detects and decodes embedded Base64 strings.
    """

    candidates = re.findall(
        r"[A-Za-z0-9+/]{16,}={0,2}",
        text
    )

    decoded_bits = []

    for token in candidates:

        padding_needed = (-len(token)) % 4
        padded = token + ("=" * padding_needed)

        try:
            decoded = base64.b64decode(
                padded,
                validate=False
            ).decode("utf-8")

            if decoded.isprintable():
                decoded_bits.append(decoded)

        except Exception:
            pass


    if decoded_bits:
        return text + " " + " ".join(decoded_bits)

    return text



def try_decode_hex(text):
    """
    Detects and decodes hexadecimal encoded text.
    """

    candidates = re.findall(
        r"\b(?:[0-9a-fA-F]{2}){8,}\b",
        text
    )

    decoded_bits = []


    for token in candidates:

        try:
            decoded = bytes.fromhex(token).decode("utf-8")

            if decoded.isprintable():
                decoded_bits.append(decoded)

        except Exception:
            pass


    if decoded_bits:
        return text + " " + " ".join(decoded_bits)

    return text



def try_decode_rot13(text):
    """
    Decodes ROT13 only when the result contains
    suspicious prompt injection keywords.
    """

    rotated = codecs.encode(text, "rot13")

    suspicious_keywords = [
        "ignore",
        "instruction",
        "instructions",
        "system",
        "prompt",
        "jailbreak",
        "override",
        "developer",
        "assistant",
        "rules",
    ]


    rotated_lower = rotated.lower()


    if any(
        keyword in rotated_lower
        for keyword in suspicious_keywords
    ):
        return text + " " + rotated


    return text



def normalise(prompt):
    """
    Main normalization pipeline.

    Returns:
        normalized_text,
        list_of_actions
    """

    actions = []

    original = prompt


    # 1. Remove invisible characters
    cleaned = strip_zero_width(prompt)

    if cleaned != prompt:
        actions.append(
            "removed zero-width characters"
        )

    prompt = cleaned



    # 2. Unicode normalization + homoglyph correction
    fixed = fix_homoglyphs(prompt)

    if fixed != prompt:
        actions.append(
            "fixed homoglyph characters"
        )

    prompt = fixed



    # 3. Decode Base64
    decoded = try_decode_base64(prompt)

    if decoded != prompt:
        actions.append(
            "decoded base64"
        )

    prompt = decoded



    # 4. Decode Hex
    decoded = try_decode_hex(prompt)

    if decoded != prompt:
        actions.append(
            "decoded hex"
        )

    prompt = decoded



    # 5. Decode ROT13
    decoded = try_decode_rot13(prompt)

    if decoded != prompt:
        actions.append(
            "decoded rot13"
        )

    prompt = decoded



    return prompt, actions