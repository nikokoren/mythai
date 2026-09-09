# -*- coding: utf-8 -*-
"""Tests fuer die Auswahl und fuer die Datenqualitaet von words.json."""
import json
import sys
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.select import DEFAULT_COUNT, cycle_length, selection_for
from scripts.thai import analyze_monosyllable, consonant_class, CLASS_DE

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "words.json").read_text(encoding="utf-8"))["thai_words"]
START = date(2026, 1, 1)


def picks(day, count=DEFAULT_COUNT):
    idx, _ = selection_for(WORDS, day, count)
    return idx


class TestSelection(unittest.TestCase):
    def test_deterministisch(self):
        day = date(2026, 5, 17)
        self.assertEqual(picks(day), picks(day))

    def test_richtige_anzahl(self):
        for i in range(0, 200, 7):
            self.assertEqual(len(picks(START + timedelta(days=i))), DEFAULT_COUNT)

    def test_keine_dublette_am_selben_tag(self):
        for i in range(200):
            p = picks(START + timedelta(days=i))
            self.assertEqual(len(set(p)), len(p))

    def test_ein_zyklus_deckt_den_ganzen_bestand_ab(self):
        days = cycle_length(len(WORDS), DEFAULT_COUNT)
        seen = Counter()
        for i in range(days):
            seen.update(picks(START + timedelta(days=i)))
        self.assertEqual(set(seen), set(range(len(WORDS))),
                         "jedes Wort muss genau einmal pro Zyklus vorkommen")
        self.assertEqual(max(seen.values()), 1, "kein Wort doppelt im Zyklus")

    def test_themen_innerhalb_eines_tages_verschieden(self):
        topics = {w["topic"] for w in WORDS}
        self.assertGreaterEqual(len(topics), DEFAULT_COUNT)
        for i in range(300):
            day = START + timedelta(days=i)
            t = [WORDS[j]["topic"] for j in picks(day)]
            self.assertEqual(len(set(t)), len(t), f"Thema doppelt am {day}: {t}")

    def test_keine_ueberschneidung_an_folgetagen(self):
        for i in range(200):
            a = set(picks(START + timedelta(days=i)))
            b = set(picks(START + timedelta(days=i + 1)))
            self.assertFalse(a & b)

    def test_zyklen_mischen_neu(self):
        days = cycle_length(len(WORDS), DEFAULT_COUNT)
        a = picks(START)
        b = picks(START + timedelta(days=days))
        self.assertNotEqual(a, b, "ein neuer Zyklus muss anders mischen")

    def test_keine_lehrplan_naehe(self):
        """Der eigentliche Fehler von vorher: benachbarte Indizes am selben Tag.

        Bei fortlaufender Indexauswahl liegen die gezogenen Indizes dicht
        beieinander. Hier muessen sie weit gestreut sein.
        """
        n = len(WORDS)
        spans = []
        for i in range(150):
            p = sorted(picks(START + timedelta(days=i)))
            spans.append(p[-1] - p[0])
        durchschnitt = sum(spans) / len(spans)
        self.assertGreater(durchschnitt, n * 0.5,
                           f"Auswahl liegt zu dicht beieinander: {durchschnitt:.0f} von {n}")


class TestDaten(unittest.TestCase):
    def test_pflichtfelder(self):
        for w in WORDS:
            for k in ("thai", "rtgs", "pos", "gloss_de", "topic",
                      "example_th", "example_de", "forvo_slug"):
                self.assertTrue(w.get(k), f"{w.get('thai')}: {k} fehlt")

    def test_keine_dubletten(self):
        c = Counter(w["thai"] for w in WORDS)
        self.assertEqual([k for k, v in c.items() if v > 1], [])

    def test_stichwort_steht_im_beispiel(self):
        for w in WORDS:
            self.assertIn(w["thai"], w["example_th"], w["thai"])

    def test_tonangaben_stimmen_mit_der_regel_ueberein(self):
        for w in WORDS:
            t = w.get("tone")
            if not t or not t.get("syllables"):
                continue
            a = analyze_monosyllable(w["thai"])
            self.assertIsNotNone(a, w["thai"])
            s = t["syllables"][0]
            self.assertEqual(s["tone"], a["tone"], w["thai"])
            self.assertEqual(s["class"], CLASS_DE[a["class"]], w["thai"])

    def test_anlautklasse_immer_gesetzt(self):
        for w in WORDS:
            if w["thai"] == "Wi-Fi":
                continue
            self.assertEqual(w["tone"]["initial_class"],
                             CLASS_DE[consonant_class(w["thai"])], w["thai"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
