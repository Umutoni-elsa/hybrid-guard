import re
import base64
import codecs
import unicodedata

ZERO_WIDTH = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"]

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
            pass

    if decoded_bits:
        return text + " " + " ".join(decoded_bits)
    return text


def try_decode_hex(text):
    candidates = re.findall(r"\b(?:[0-9a-fA-F]{2}){8,}\b", text)
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
    rotated = codecs.encode(text, "rot13")
    if rotated != text:
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

    decoded = try_decode_hex(prompt)
    if decoded != prompt:
        actions.append("decoded hex")
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
