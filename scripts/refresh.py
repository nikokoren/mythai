# -*- coding: utf-8 -*-
"""Taeglicher Lauf.

Laeuft kurz nach lokaler Mitternacht (siehe TRMNL_TZ und den Cron im
Workflow). Zwei Aufgaben:

1. Die Reihenfolge von `thai_words` neu mischen, wenn ein Zyklus durch ist
   (oder sich der Bestand geaendert hat). Die Vorlage laeuft mit
   `day_index modulo N` genau dieser Reihenfolge entlang - sie muss dafuer
   nicht angepasst werden.
2. `daily` schreiben: was heute drankommt.
3. `trmnl.json` schreiben - die kleine Datei, die das Display abholt. Sie
   enthaelt nur den Eintrag des Tages. `words.json` ist mit 383 Eintraegen
   ueber 240 KB gross und reisst TRMNLs 100-KB-Grenze; die Vorlage liest
   daraus seit dem daily-Block ohnehin nur noch `daily.word`.
"""
import argparse
import json
import os
import sys
import tempfile
import time
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.select import build_order, cycle_for, day_index, pick_index

ROOT = Path(__file__).resolve().parent.parent
WORDS = ROOT / "words.json"

# Was das Display abholt. words.json bleibt der Bestand und die Quelle der
# Wahrheit, wird aber nicht mehr ausgeliefert.
PAYLOAD = ROOT / "trmnl.json"

# TRMNL lehnt ueber 100 KB ab und setzt das Plugin auf "degraded". Der Riegel
# liegt bewusst weit darunter: die Nutzdaten sind ein einzelner Eintrag, alles
# darueber hiesse, dass versehentlich wieder der Bestand mitgeht.
PAYLOAD_MAX = 8 * 1024

# Zeitzone, in der "heute" bestimmt wird. Der Workflow laeuft kurz nach lokaler
# Mitternacht; nur mit derselben Zone traegt daily.date dann auch das lokale
# Datum. Ueber TRMNL_TZ setzbar, damit die Sommerzeit nicht von Hand
# nachgepflegt werden muss.
TZ = os.environ.get("TRMNL_TZ", "UTC")


def now(tz=None):
    return datetime.now(ZoneInfo(tz or TZ))


def today(tz=None):
    return now(tz).date()


# Ab wann die Vollansicht Deutsch dazunimmt (lokale Stunde).
REVEAL_HOUR = 12


def phase_at(moment):
    """Vormittag oder Nachmittag - danach richtet sich die Vollansicht.

    Die Entscheidung faellt hier und nicht in der Vorlage, weil nur der
    Dateischreibzeitpunkt zaehlt: TRMNL zeichnet einen Screen erst neu, wenn
    sich die Nutzdaten geaendert haben. Die Vorlage kann die Stunde ausrechnen
    so oft sie will - gezeigt wird, was beim letzten Schreiben galt.

    Ein Wort und keine Wahrheitswert: in Liquid sind `false` und `nil` in
    Vergleichen nicht auseinanderzuhalten, ein `false` im Payload waere von
    "Feld fehlt" nicht zu unterscheiden und wuerde jeden Vormittag still in
    den Rueckfallzweig laufen.
    """
    return "nachmittag" if moment.hour >= REVEAL_HOUR else "vormittag"


class ZukunftsDatum(Exception):
    """Ein Stand fuer morgen wuerde den Lauf von morgen stilllegen.

    Der Lauf schreibt nur, wenn sich etwas aendert - das ist der Ausloeser
    fuer TRMNL. Steht das Datum von morgen schon in der Datei, findet der
    Lauf morgen nichts zu tun, die Nutzdaten bleiben gleich, und das Display
    behaelt das Wort von heute. Genau so ist der 11.09.2026 ausgefallen.
    """


def payload_for(data):
    """Die Nutzdaten fuers Display: ein Eintrag, kein Bestand.

    Dieselben Schluessel wie in words.json, damit die Vorlage unveraendert
    `daily.word` liest. `last_updated` muss mit: es ist die Aenderung, an der
    TRMNL erkennt, dass ein neuer Screen faellig ist.
    """
    return {
        "daily": data["daily"],
        "phase": data["phase"],
        "last_updated": data["last_updated"],
        "word_count": data["word_count"],
        "cycle": data["cycle"],
    }


def write_payload(data, path=PAYLOAD):
    text = json.dumps(payload_for(data), indent=2, ensure_ascii=False) + "\n"
    size = len(text.encode("utf-8"))
    if size > PAYLOAD_MAX:
        raise PayloadZuGross(
            f"{path.name} waere {size} Bytes gross, erlaubt sind {PAYLOAD_MAX}. "
            f"Geht da der ganze Bestand mit?")
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
        return True
    return False


class PayloadZuGross(Exception):
    """Die Datei fuers Display ist ueber das Budget gewachsen."""


def refresh(path=WORDS, moment=None, force_reorder=False, allow_future=False,
            payload_path=PAYLOAD):
    data = json.loads(path.read_text(encoding="utf-8"))
    words = data["thai_words"]
    moment = moment or now()
    day = moment.date()
    if not allow_future and day > today():
        raise ZukunftsDatum(
            f"{day} liegt in der Zukunft - das wuerde den Lauf an diesem Tag "
            f"stilllegen. Zum Probieren --dry-run nehmen.")
    total = len(words)
    cycle = cycle_for(day, total)

    reordered = False
    if force_reorder or data.get("cycle") != cycle or data.get("word_count") != total:
        words = [words[i] for i in build_order(words, cycle)]
        data["thai_words"] = words
        reordered = True

    phase = phase_at(moment)
    idx = pick_index(day, total)
    daily = {
        "date": day.isoformat(),
        "day_index": day_index(day),
        "index": idx,
        "word": words[idx],
    }

    changed = (reordered or data.get("daily") != daily
               or data.get("cycle") != cycle
               or data.get("phase") != phase)
    if not changed:
        # Auch dann nachziehen: fehlt trmnl.json oder ist sie aus dem Tritt,
        # muss sie geschrieben werden, sonst holt das Display einen alten Stand.
        if payload_path is not None and write_payload(data, payload_path):
            return data, True, reordered
        return data, False, reordered

    data["daily"] = daily
    data["phase"] = phase
    data["cycle"] = cycle
    data["word_count"] = total
    data["last_updated"] = time.time()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    if payload_path is not None:
        write_payload(data, payload_path)
    return data, True, reordered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date",
                    help="ISO-Datum oder -Zeitpunkt statt jetzt, z.B. 2026-09-13 "
                         "oder 2026-09-13T14:00 (Zukunft nur mit --dry-run). "
                         "Ohne Uhrzeit gilt 00:00, also vormittags.")
    ap.add_argument("--dry-run", action="store_true",
                    help="nur rechnen und anzeigen, nichts schreiben")
    ap.add_argument("--tz", help=f"Zeitzone fuer 'heute' (Standard: {TZ})")
    ap.add_argument("--reorder", action="store_true",
                    help="Reihenfolge neu mischen, auch mitten im Zyklus")
    ap.add_argument("--preview", type=int, default=0,
                    help="so viele Folgetage zusaetzlich anzeigen")
    args = ap.parse_args()
    if args.date:
        moment = datetime.fromisoformat(args.date)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=ZoneInfo(args.tz or TZ))
    else:
        moment = now(args.tz)

    if args.dry_run:
        # ueber eine Kopie, damit die echte Datei garantiert unberuehrt bleibt
        tmp = Path(tempfile.mkdtemp()) / WORDS.name
        tmp.write_bytes(WORDS.read_bytes())
        data, changed, reordered = refresh(path=tmp, moment=moment,
                                           force_reorder=args.reorder,
                                           allow_future=True,
                                           payload_path=tmp.with_name("trmnl.json"))
    else:
        try:
            data, changed, reordered = refresh(moment=moment,
                                               force_reorder=args.reorder)
        except (ZukunftsDatum, PayloadZuGross) as e:
            print(f"Abgebrochen: {e}", file=sys.stderr)
            return 1

    d = data["daily"]
    w = d["word"]
    status = "neu gemischt" if reordered else ("geschrieben" if changed else "unveraendert")
    if args.dry_run:
        status += ", nur Probe"
    print(f"{d['date']}  Index {d['index']}/{data['word_count']}  Zyklus {data['cycle']}  ({status})")
    print(f"  {w['thai']}  {w['rtgs']}  -  {w['gloss_de']}  [{w['topic']}]")
    print(f"  {moment:%H:%M} lokal = {data['phase']} -> Vollansicht "
          f"{'mit Deutsch' if data['phase'] == 'nachmittag' else 'nur Thai'}")
    if not args.dry_run:
        print(f"  {PAYLOAD.name}: {PAYLOAD.stat().st_size} Bytes "
              f"(Grenze bei TRMNL: 100 KB)")

    if args.preview:
        from datetime import timedelta
        words = data["thai_words"]
        print("\n  Folgetage:")
        for k in range(1, args.preview + 1):
            nxt = date.fromisoformat(d["date"]) + timedelta(days=k)
            i = pick_index(nxt, len(words))
            n = words[i]
            print(f"    {nxt}  {n['thai']:<16} {n['gloss_de']:<26} [{n['topic']}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
