# -*- coding: utf-8 -*-
"""Kleine Thai-Hilfsbibliothek: Konsonantenklasse und Silbenanalyse.

Bewusst konservativ: `analyze_monosyllable` liefert nur dann ein Ergebnis,
wenn das Wort vollstaendig als eine einzelne Silbe geparst werden kann.
Fuer alles andere gibt es None - lieber keine Angabe als eine falsche.
"""

HIGH = set("ขฃฉฐถผฝศษสห")
MID = set("กจฎฏดตบปอ")
LOW = set("คฅฆงชซฌญ�ฑฒณทธนพฟภมยรลวฬฮ")
CONSONANTS = HIGH | MID | LOW

# Sonoranten, die von einem stummen ห (bzw. อ) "angefuehrt" werden koennen
SONORANTS = set("งญณนมยรลวฬ")

LEADING_VOWELS = set("เแโใไ")
TONE_MARKS = set("่้๊๋")
THANTHAKHAT = "์"
# Vokalzeichen ueber/unter der Zeile
ABOVE_BELOW = set("ิีึืุูั็ํ")
AFTER = set("ะาำๅ")

CLASS_DE = {"high": "Hochkonsonant", "mid": "Mittelkonsonant", "low": "Tiefkonsonant"}

# Endkonsonanten-Kategorien
STOP_FINALS = set("กขคฆจฉชซฌฎฏฐฑฒดตถทธบปพฟภศษส")  # -k, -t, -p  => "tot"
SONORANT_FINALS = set("งนณญรลฬมยว")                  # -ng, -n, -m, -y, -w => "lebendig"


def consonant_class(word):
    """Klasse des Anfangskonsonanten (beruecksichtigt ห-นำ und อ-นำ)."""
    for i, ch in enumerate(word):
        if ch not in CONSONANTS:
            continue
        nxt = word[i + 1] if i + 1 < len(word) else ""
        # ห นำ: หน หม หย หร หล หว หง หญ  -> Silbe verhaelt sich wie hoch
        if ch == "ห" and nxt in SONORANTS:
            return "high"
        # อ นำ: อย (อย่า อยู่ อย่าง อยาก) -> verhaelt sich wie mittel
        if ch == "อ" and nxt == "ย":
            return "mid"
        if ch in HIGH:
            return "high"
        if ch in MID:
            return "mid"
        return "low"
    return None


# Vokalmuster einer Silbe: (Muster mit '@' als Platzhalter fuer den Anlaut,
# '#' fuer den Endkonsonanten), Laenge
# Reihenfolge = Prioritaet beim Matchen (laengere Muster zuerst).
_VOWELS = [
    ("เ@ือ", "long"), ("เ@ีย", "long"), ("เ@อ", "long"), ("เ@า", "short"),
    ("แ@ะ", "short"), ("เ@ะ", "short"), ("โ@ะ", "short"), ("เ@าะ", "short"),
    ("@ัวะ", "short"), ("@ัว", "long"), ("@ือ", "long"), ("@ัะ", "short"),
    ("แ@", "long"), ("เ@", "long"), ("โ@", "long"), ("ใ@", "short"), ("ไ@", "short"),
    ("@ำ", "short"), ("@ะ", "short"), ("@า", "long"),
    ("@ิ", "short"), ("@ี", "long"), ("@ึ", "short"), ("@ื", "long"),
    ("@ุ", "short"), ("@ู", "long"), ("@ั", "short"), ("@็", "short"),
    ("เ@็", "short"), ("แ@็", "short"), ("โ@็", "short"),
    ("@อ", "long"), ("@ว", "long"), ("@ร", "long"),  # @ร: "จร" -> -on, selten; @อ: ขอ, พ่อ
    ("@", "short"),  # inhaerenter Vokal (โ-ะ / เ-าะ), z.B. คน, จบ
]


def _strip_tone_mark(word):
    mark = ""
    out = []
    for ch in word:
        if ch in TONE_MARKS:
            if mark:
                return None, None  # zwei Tonzeichen -> keine Einzelsilbe
            mark = ch
        else:
            out.append(ch)
    return "".join(out), mark


def _split_initial(bare):
    """Gibt (anlaut, rest) zurueck; beruecksichtigt Cluster und Vorsilben-Vokale."""
    lead = ""
    i = 0
    if bare and bare[0] in LEADING_VOWELS:
        lead = bare[0]
        i = 1
    if i >= len(bare) or bare[i] not in CONSONANTS:
        return None
    first = bare[i]
    i += 1
    initial = first
    # stummes ห / อ
    if first in ("ห", "อ") and i < len(bare) and bare[i] in SONORANTS:
        # nur wenn danach noch Substanz kommt
        if len(bare) > i + 1 or lead:
            initial += bare[i]
            i += 1
    # echte Cluster: กร กล กว ปร ปล พร พล คร คล ตร ...
    elif i < len(bare) and bare[i] in set("รลว") and i + 1 < len(bare):
        if first in set("กขคตปผพบฟดจ"):
            initial += bare[i]
            i += 1
    return lead, initial, bare[i:]


def analyze_monosyllable(word):
    """Analysiert `word` als Einzelsilbe.

    Rueckgabe: dict(class, live_dead, length, tone, tone_mark) oder None,
    wenn das Wort keine sauber parsbare Einzelsilbe ist.
    """
    if not word or any(ch == THANTHAKHAT for ch in word):
        return None
    if any(ch not in CONSONANTS and ch not in LEADING_VOWELS and ch not in TONE_MARKS
           and ch not in ABOVE_BELOW and ch not in AFTER for ch in word):
        return None

    bare, mark = _strip_tone_mark(word)
    if bare is None:
        return None
    split = _split_initial(bare)
    if not split:
        return None
    lead, initial, rest = split

    pattern = lead + "@" + rest
    length = None
    final = ""
    for vowel, vlen in _VOWELS:
        if pattern == vowel:
            length, final = vlen, ""
            break
        # Muster + genau ein Endkonsonant
        if vowel.endswith("@") and pattern.startswith(vowel) and len(pattern) == len(vowel) + 1:
            cand = pattern[len(vowel):]
            if cand in CONSONANTS:
                length, final = vlen, cand
                break
        if pattern.startswith(vowel) and len(pattern) == len(vowel) + 1:
            cand = pattern[-1]
            if cand in CONSONANTS:
                length, final = vlen, cand
                break
    if length is None:
        return None
    # -ะ und -็ koennen keinen Endkonsonanten tragen
    if final and ("ะ" in pattern[:len(pattern) - 1] or "็" == pattern[-2:-1]):
        pass

    cls = consonant_class(word)
    if final in STOP_FINALS:
        live = "dead"
    elif final in SONORANT_FINALS:
        live = "live"
    elif final == "":
        # offene Silbe: kurz = tot, lang = lebendig
        # Ausnahme: -ำ, ไ-, ใ-, เ-า gelten als lebendig
        live = "live" if (length == "long" or pattern.endswith("ำ")
                          or lead in ("ไ", "ใ") or pattern.endswith("เ@า")) else "dead"
    else:
        return None

    tone = _tone(cls, live, length, mark)
    if tone is None:
        return None
    return {
        "class": cls,
        "live_dead": live,
        "length": length,
        "final": final,
        "tone_mark": mark,
        "tone": tone,
    }


def _tone(cls, live, length, mark):
    if mark == "่":
        return {"mid": "tief", "high": "tief", "low": "fallend"}[cls]
    if mark == "้":
        return {"mid": "fallend", "high": "fallend", "low": "hoch"}[cls]
    if mark == "๊":
        return "hoch" if cls == "mid" else None
    if mark == "๋":
        return "steigend" if cls == "mid" else None
    if live == "live":
        return {"mid": "mittel", "high": "steigend", "low": "mittel"}[cls]
    # tote Silbe
    if cls == "mid":
        return "tief"
    if cls == "high":
        return "tief"
    return "hoch" if length == "short" else "fallend"
