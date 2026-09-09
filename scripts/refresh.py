# -*- coding: utf-8 -*-
"""Taeglicher Lauf.

Zwei Aufgaben:

1. Die Reihenfolge von `thai_words` neu mischen, wenn ein Zyklus durch ist
   (oder sich der Bestand geaendert hat). Die Vorlage laeuft mit
   `day_index modulo N` genau dieser Reihenfolge entlang - sie muss dafuer
   nicht angepasst werden.
2. `daily` schreiben: was heute drankommt. Rein informativ - die Vorlage
   rechnet ihren Index selbst aus lokaler Zeit aus und wechselt darum um
   lokal Mitternacht, nicht um 00:05 UTC.
"""
import argparse
import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.select import build_order, cycle_for, day_index, pick_index

ROOT = Path(__file__).resolve().parent.parent
WORDS = ROOT / "words.json"


def refresh(path=WORDS, day=None, force_reorder=False):
    data = json.loads(path.read_text(encoding="utf-8"))
    words = data["thai_words"]
    day = day or datetime.now(timezone.utc).date()
    total = len(words)
    cycle = cycle_for(day, total)

    reordered = False
    if force_reorder or data.get("cycle") != cycle or data.get("word_count") != total:
        words = [words[i] for i in build_order(words, cycle)]
        data["thai_words"] = words
        reordered = True

    idx = pick_index(day, total)
    daily = {
        "date": day.isoformat(),
        "day_index": day_index(day),
        "index": idx,
        "word": words[idx],
    }

    changed = reordered or data.get("daily") != daily or data.get("cycle") != cycle
    if not changed:
        return data, False, reordered

    data["daily"] = daily
    data["cycle"] = cycle
    data["word_count"] = total
    data["last_updated"] = time.time()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return data, True, reordered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="ISO-Datum statt heute")
    ap.add_argument("--reorder", action="store_true",
                    help="Reihenfolge neu mischen, auch mitten im Zyklus")
    ap.add_argument("--preview", type=int, default=0,
                    help="so viele Folgetage zusaetzlich anzeigen")
    args = ap.parse_args()
    day = date.fromisoformat(args.date) if args.date else None
    data, changed, reordered = refresh(day=day, force_reorder=args.reorder)

    d = data["daily"]
    w = d["word"]
    status = "neu gemischt" if reordered else ("geschrieben" if changed else "unveraendert")
    print(f"{d['date']}  Index {d['index']}/{data['word_count']}  Zyklus {data['cycle']}  ({status})")
    print(f"  {w['thai']}  {w['rtgs']}  -  {w['gloss_de']}  [{w['topic']}]")

    if args.preview:
        from datetime import timedelta
        words = data["thai_words"]
        print("\n  Folgetage:")
        for k in range(1, args.preview + 1):
            nxt = date.fromisoformat(d["date"]) + timedelta(days=k)
            i = pick_index(nxt, len(words))
            n = words[i]
            print(f"    {nxt}  {n['thai']:<16} {n['gloss_de']:<26} [{n['topic']}]")


if __name__ == "__main__":
    main()
