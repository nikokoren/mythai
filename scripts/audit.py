# -*- coding: utf-8 -*-
"""Qualitaetsbericht ueber words.json. Bricht bei harten Fehlern mit Code 1 ab."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.thai import CLASS_DE, consonant_class

ROOT = Path(__file__).resolve().parent.parent
PFLICHT = ("thai", "rtgs", "pos", "gloss_de", "topic",
           "example_th", "example_de", "forvo_slug")


def main():
    data = json.loads((ROOT / "words.json").read_text(encoding="utf-8"))
    words = data["thai_words"]
    fehler = []

    dubletten = [k for k, v in Counter(w["thai"] for w in words).items() if v > 1]
    if dubletten:
        fehler.append(f"Dubletten: {dubletten}")

    for w in words:
        fehlend = [k for k in PFLICHT if not w.get(k)]
        if fehlend:
            fehler.append(f"{w['thai']}: Felder fehlen {fehlend}")
        if w["thai"] not in w["example_th"]:
            fehler.append(f"{w['thai']}: Stichwort fehlt im Beispielsatz")
        klasse = consonant_class(w["thai"])
        if klasse and (w.get("tone") or {}).get("initial_class") != CLASS_DE[klasse]:
            fehler.append(f"{w['thai']}: Anlautklasse stimmt nicht")

    themen = Counter(w["topic"] for w in words)
    berechnet = sum(1 for w in words if (w.get("tone") or {}).get("syllables"))

    print(f"Eintraege            {len(words)}")
    print(f"Themen               {len(themen)}")
    print(f"Ton berechnet        {berechnet}")
    print(f"nur Anlautklasse     {len(words) - berechnet}  (mehrsilbig, Ton nicht "
          f"regelbasiert ableitbar)")
    print()
    for t, n in themen.most_common():
        print(f"  {n:>4}  {t}")

    if fehler:
        print("\nFEHLER:")
        for f in fehler:
            print("  " + f)
        return 1
    print("\nKeine Fehler.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
