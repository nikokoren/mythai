# -*- coding: utf-8 -*-
"""Tests fuer die Reihenfolge und fuer die Datenqualitaet von words.json."""
import json
import sys
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.select import (WINDOW, build_order, cycle_for, day_index,
                            interleave, pick_index)
from scripts.thai import CLASS_DE, analyze_monosyllable, consonant_class

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "words.json").read_text(encoding="utf-8"))
WORDS = DATA["thai_words"]
N = len(WORDS)


def topics_of(seq):
    return [WORDS[i]["topic"] for i in seq]


class TestReihenfolge(unittest.TestCase):
    """Die Vorlage laeuft mit einem Schritt pro Tag durch thai_words.

    Was hier ueber die Reihenfolge gilt, gilt damit direkt ueber die Tage.
    """

    def test_ist_eine_permutation(self):
        order = build_order(WORDS, cycle=0)
        self.assertEqual(sorted(order), list(range(N)),
                         "es darf nichts verloren gehen und nichts doppelt sein")

    def test_deterministisch(self):
        self.assertEqual(build_order(WORDS, 7), build_order(WORDS, 7))

    def test_zyklen_mischen_neu(self):
        self.assertNotEqual(build_order(WORDS, 7), build_order(WORDS, 8))

    def test_kein_thema_zweimal_im_fenster(self):
        """Der eigentliche Fehler von vorher: neun Farben hintereinander."""
        for cycle in (0, 1, 54):
            order = build_order(WORDS, cycle)
            t = topics_of(order)
            for i in range(len(t) - WINDOW + 1):
                fenster = t[i:i + WINDOW]
                self.assertEqual(len(set(fenster)), len(fenster),
                                 f"Zyklus {cycle}, Position {i}: {fenster}")

    def test_gelieferte_datei_haelt_das_ein(self):
        """Nicht nur die Funktion - auch das, was tatsaechlich ausgeliefert wird."""
        t = [w["topic"] for w in WORDS]
        for i in range(len(t) - WINDOW + 1):
            fenster = t[i:i + WINDOW]
            self.assertEqual(len(set(fenster)), len(fenster),
                             f"words.json, Position {i}: {fenster}")

    def test_themen_liegen_weit_auseinander(self):
        """Ueber das harte Fenster hinaus: mittlerer Abstand gleicher Themen."""
        letzte, abstaende = {}, []
        for i, w in enumerate(WORDS):
            if w["topic"] in letzte:
                abstaende.append(i - letzte[w["topic"]])
            letzte[w["topic"]] = i
        self.assertGreater(sum(abstaende) / len(abstaende), 10)

    def test_interleave_allein_reicht_fast(self):
        """Die Reparatur soll Feinschliff sein, nicht das eigentliche Mischen."""
        t = topics_of(interleave(WORDS, 0))
        kollisionen = sum(1 for i in range(len(t) - 1) if t[i] == t[i + 1])
        self.assertLess(kollisionen, N * 0.02)


class TestTagesauswahl(unittest.TestCase):
    """Die Arithmetik der Vorlage, hier nachgebaut."""

    def test_ein_schritt_pro_tag(self):
        d = date(2026, 9, 9)
        self.assertEqual(pick_index(d + timedelta(days=1), N),
                         (pick_index(d, N) + 1) % N)

    def test_ein_zyklus_zeigt_jedes_wort_genau_einmal(self):
        start = date(2026, 9, 9)
        gesehen = Counter(pick_index(start + timedelta(days=k), N) for k in range(N))
        self.assertEqual(set(gesehen), set(range(N)))
        self.assertEqual(max(gesehen.values()), 1)

    def test_aufeinanderfolgende_tage_andere_themen(self):
        start = date(2026, 9, 9)
        for k in range(400):
            d = start + timedelta(days=k)
            a = WORDS[pick_index(d, N)]["topic"]
            b = WORDS[pick_index(d + timedelta(days=1), N)]["topic"]
            self.assertNotEqual(a, b, f"{d} und Folgetag beide {a}")

    def test_daily_passt_zum_index(self):
        d = DATA["daily"]
        self.assertEqual(d["word"]["thai"], WORDS[d["index"]]["thai"])
        self.assertEqual(d["index"], pick_index(date.fromisoformat(d["date"]), N))
        self.assertEqual(d["day_index"], day_index(date.fromisoformat(d["date"])))

    def test_zyklus_im_kopf_passt(self):
        self.assertEqual(DATA["cycle"],
                         cycle_for(date.fromisoformat(DATA["daily"]["date"]), N))
        self.assertEqual(DATA["word_count"], N)


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
            self.assertEqual((w.get("tone") or {}).get("initial_class"),
                             CLASS_DE[consonant_class(w["thai"])], w["thai"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
