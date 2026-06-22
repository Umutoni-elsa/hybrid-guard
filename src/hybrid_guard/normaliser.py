import re
import base64
import codecs
import unicodedata

# invisible characters attackers use to break up words like "ignore"
ZERO_WIDTH = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"]

# lookalike characters (mostly cyrillic) mapped back to normal letters
HOMOGLYPHS = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "у": "y", "х": "x", "і": "i",
}


def strip_zero_width(text):
    for ch in ZERO_WIDTH:
        text = text.replace(ch, "")
    return text


def fix_homoglyphs(text):
    new_text = ""
    for ch in text:
        new_text += HOMOGLYPHS.get(ch, ch)
    return unicodedata.normalize("NFKC", new_text)


def try_decode_base64(text):
    # grab anything that looks like a base64 chunk and try to decode it
    candidates = re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", text)
    decoded_bits = []

    for token in candidates:
        padding_needed = (-len(token)) % 4
        padded = token + ("=" * padding_needed)
        try:
            decoded = base64.b64decode(padded).decode("utf-8")
            if decoded.isprintable():
                decoded_bits.append(decoded)
        except Exception:
            pass  # not valid base64, skip it

    if decoded_bits:
        return text + " " + " ".join(decoded_bits)
    return text


def try_decode_rot13(text):
    rotated = codecs.encode(text, "rot13")
    danger_words = ["ignore", "override", "jailbreak", "bypass"]

    # if the rotated version suddenly contains danger words that weren't
    # there before, it was probably rot13 in the first place
    if any(w in rotated.lower() for w in danger_words):
        if not any(w in text.lower() for w in danger_words):
            return text + " " + rotated
    return text


def normalise(prompt):
    actions = []
    original = prompt

    cleaned = strip_zero_width(prompt)
    if cleaned != prompt:
        actions.append("removed zero-width characters")
    prompt = cleaned

    decoded = try_decode_base64(prompt)
    if decoded != prompt:
        actions.append("decoded base64")
    prompt = decoded

    decoded = try_decode_rot13(prompt)
    if decoded != prompt:
        actions.append("decoded rot13")
    prompt = decoded

    fixed = fix_homoglyphs(prompt)
    if fixed != prompt:
        actions.append("fixed homoglyph characters")
    prompt = fixed

    return prompt, actions
