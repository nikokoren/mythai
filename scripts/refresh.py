# -*- coding: utf-8 -*-
"""Taeglicher Lauf: schreibt die Auswahl des Tages nach words.json.

Die Auswahl haengt nur vom Datum ab. Mehrfache Laeufe am selben Tag aendern
die Datei daher nicht - der Workflow committet dann auch nichts.
"""
import argparse
import json
import sys
import time
from datetime import date, timezone, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.select import DEFAULT_COUNT, selection_for

ROOT = Path(__file__).resolve().parent.parent
WORDS = ROOT / "words.json"


def refresh(path=WORDS, day=None, count=DEFAULT_COUNT):
    data = json.loads(path.read_text(encoding="utf-8"))
    words = data["thai_words"]
    day = day or datetime.now(timezone.utc).date()

    picks, meta = selection_for(words, day, count)
    daily = {
        "date": day.isoformat(),
        "cycle": meta["cycle"],
        "day_in_cycle": meta["day_in_cycle"],
        "cycle_days": meta["cycle_days"],
        "words": [words[i] for i in picks],
    }

    unchanged = data.get("daily", {}).get("date") == daily["date"] and \
        data.get("daily", {}).get("words") == daily["words"]
    if unchanged:
        return data, False

    data["daily"] = daily
    data["word_count"] = len(words)
    data["last_updated"] = time.time()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return data, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="ISO-Datum statt heute (fuer Tests)")
    ap.add_argument("--count", type=int, default=DEFAULT_COUNT)
    args = ap.parse_args()
    day = date.fromisoformat(args.date) if args.date else None
    data, changed = refresh(day=day, count=args.count)
    d = data["daily"]
    print(f"{d['date']}  Zyklus {d['cycle']}, Tag {d['day_in_cycle'] + 1}/{d['cycle_days']}"
          f"  {'geschrieben' if changed else 'unveraendert'}")
    for w in d["words"]:
        print(f"  {w['thai']:<18} {w['rtgs']:<22} {w['gloss_de']:<28} [{w['topic']}]")


if __name__ == "__main__":
    main()
