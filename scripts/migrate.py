# -*- coding: utf-8 -*-
"""Einmalige Bereinigung von words.json.

- fuehrt die beiden Alt-Schemata zu einem zusammen
- entfernt Dubletten (Glossen werden zusammengefuehrt)
- ersetzt die vier unzuverlaessigen Tonfelder durch ein berechnetes `tone`
- ergaenzt `topic`, fehlende `pos` und fehlende `rtgs`
- haengt die neuen Eintraege aus vocab_new an
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.thai import CLASS_DE, analyze_monosyllable, consonant_class
from scripts.overrides import GLOSS_FIX, NOTES, POS_OVERRIDE, RTGS_B, RTGS_FIX
from scripts.topics import topic_for
from scripts.vocab_new import NEW_WORDS

ROOT = Path(__file__).resolve().parent.parent
WORDS = ROOT / "words.json"

FIELD_ORDER = ["thai", "rtgs", "pos", "gloss_de", "topic",
               "example_th", "example_de", "tone", "forvo_slug", "notes"]


def guess_pos(word, gloss):
    if word in POS_OVERRIDE:
        return POS_OVERRIDE[word]
    first = gloss.split(";")[0].strip()
    if not first:
        return "unbekannt"
    if first[0].isupper():
        return "Nomen"
    if first.endswith("en") or first.endswith("n"):
        return "Verb"
    return "Adjektiv"


def build_tone(word):
    """Berechnete Tonangabe - oder None, wenn nicht eindeutig ableitbar."""
    a = analyze_monosyllable(word)
    if not a:
        cls = consonant_class(word)
        if cls is None:
            return None
        # mehrsilbig: nur die Klasse des Anlauts ist verlaesslich
        return {
            "syllables": None,
            "initial_class": CLASS_DE[cls],
            "rule_hint": None,
            "source": "unvollstaendig",
        }
    hint = (f"{CLASS_DE[a['class']]} + "
            f"{'geschlossene' if a['final'] else 'offene'} Silbe + "
            f"{'langer' if a['length'] == 'long' else 'kurzer'} Vokal"
            f"{' + Tonzeichen ' + a['tone_mark'] if a['tone_mark'] else ''}"
            f" -> {a['tone']}")
    return {
        "syllables": [{
            "glyph": word,
            "class": CLASS_DE[a["class"]],
            "syllable": "geschlossen" if a["final"] else "offen",
            "length": "lang" if a["length"] == "long" else "kurz",
            "tone": a["tone"],
        }],
        "initial_class": CLASS_DE[a["class"]],
        "rule_hint": hint,
        "source": "regelbasiert berechnet",
    }


def merge_gloss(a, b):
    parts = []
    for chunk in (a + "; " + b).split(";"):
        chunk = chunk.strip()
        if chunk and chunk not in parts:
            parts.append(chunk)
    return "; ".join(parts)


def normalize(word, rtgs, pos, gloss, topic, ex_th, ex_de):
    fix = GLOSS_FIX.get(word, {})
    if "thai" in fix:
        # Schreibweise auch im Beispielsatz nachziehen
        ex_th = ex_th.replace(word, fix["thai"])
        word = fix["thai"]
    entry = {
        "thai": word,
        "rtgs": RTGS_FIX.get(word, rtgs),
        "pos": pos,
        "gloss_de": gloss,
        "topic": topic,
        "example_th": ex_th,
        "example_de": ex_de,
        "tone": build_tone(word),
        "forvo_slug": fix.get("forvo_slug", word),
    }
    if word in NOTES:
        entry["notes"] = NOTES[word]
    return {k: entry[k] for k in FIELD_ORDER if k in entry}


def main():
    raw = json.loads(WORDS.read_text(encoding="utf-8"))
    by_word = {}
    order = []
    stats = {"merged": 0}

    for i, e in enumerate(raw["thai_words"]):
        word = e["thai"]
        rtgs = e.get("rtgs") or RTGS_B.get(word, "")
        pos = e.get("pos") or guess_pos(word, e["gloss_de"])
        topic = topic_for(i, word)
        entry = normalize(word, rtgs, pos, e["gloss_de"], topic,
                          e["example_th"], e["example_de"])
        key = entry["thai"]
        if key in by_word:
            prev = by_word[key]
            prev["gloss_de"] = merge_gloss(prev["gloss_de"], entry["gloss_de"])
            if not prev["rtgs"]:
                prev["rtgs"] = entry["rtgs"]
            stats["merged"] += 1
            continue
        by_word[key] = entry
        order.append(key)

    added = 0
    for word, rtgs, pos, gloss, topic, ex_th, ex_de in NEW_WORDS:
        if word in by_word:
            raise SystemExit(f"Neues Wort kollidiert mit Bestand: {word}")
        by_word[word] = normalize(word, rtgs, pos, gloss, topic, ex_th, ex_de)
        order.append(word)
        added += 1

    words = [by_word[k] for k in order]
    raw["thai_words"] = words
    WORDS.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")

    computed = sum(1 for w in words if w["tone"] and w["tone"]["syllables"])
    print(f"Eintraege: {len(words)} (Dubletten zusammengefuehrt: {stats['merged']}, "
          f"neu: {added})")
    print(f"Ton regelbasiert berechnet: {computed}, "
          f"nur Anlautklasse: {len(words) - computed}")


if __name__ == "__main__":
    main()
