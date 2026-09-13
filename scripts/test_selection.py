# -*- coding: utf-8 -*-
"""Tests fuer die Reihenfolge und fuer die Datenqualitaet von words.json."""
import json
import sys
import unittest
from collections import Counter
import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.refresh import (PAYLOAD_MAX, REVEAL_HOUR, payload_for,
                            phase_at, today)
from scripts.select import (WINDOW, build_order, cycle_for, day_index,
                            interleave, pick_index)
from scripts.thai import CLASS_DE, analyze_monosyllable, consonant_class

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "words.json").read_text(encoding="utf-8"))
WORDS = DATA["thai_words"]
N = len(WORDS)


PAYLOAD_PATH = ROOT / "trmnl.json"


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

    def test_daily_ist_das_was_die_vorlage_rendert(self):
        """Die Vorlage liest daily.word direkt - der Block muss stimmen."""
        d = DATA["daily"]
        self.assertIn("word", d)
        for feld in ("thai", "rtgs", "gloss_de", "example_th", "example_de"):
            self.assertTrue(d["word"].get(feld), f"daily.word.{feld} fehlt")

    def test_last_updated_ist_gesetzt(self):
        """TRMNL erzeugt nur bei geaenderten Nutzdaten einen neuen Screen.

        Der daily-Block aendert sich taeglich und traegt das allein; der
        Zeitstempel bleibt als ausdrueckliches Signal daneben stehen.
        """
        self.assertIsInstance(DATA.get("last_updated"), float)
        self.assertGreater(DATA["last_updated"], 1_700_000_000)

    def test_taeglicher_lauf_aendert_die_nutzdaten(self):
        """Zwei aufeinanderfolgende Tage muessen verschiedene Nutzdaten ergeben."""
        a, b = date(2026, 3, 1), date(2026, 3, 2)
        self.assertNotEqual(pick_index(a, N), pick_index(b, N))
        self.assertNotEqual(WORDS[pick_index(a, N)], WORDS[pick_index(b, N)])

    def test_daily_passt_zum_index(self):
        d = DATA["daily"]
        self.assertEqual(d["word"]["thai"], WORDS[d["index"]]["thai"])
        self.assertEqual(d["index"], pick_index(date.fromisoformat(d["date"]), N))
        self.assertEqual(d["day_index"], day_index(date.fromisoformat(d["date"])))

    def test_daily_liegt_nicht_in_der_zukunft(self):
        """Ein Datum aus der Zukunft in words.json legt einen Tag still.

        Passiert beim Testen mit --date: wird so ein Stand committet, findet
        der Lauf am naechsten Tag nichts zu aendern, die Nutzdaten bleiben
        gleich - und TRMNL erzeugt keinen neuen Screen. Genau das ist am
        11.09.2026 passiert.
        """
        d = date.fromisoformat(DATA["daily"]["date"])
        self.assertLessEqual(d, today(), "daily.date liegt in der Zukunft")

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


class TestNutzdaten(unittest.TestCase):
    """trmnl.json ist, was das Display abholt.

    words.json ist mit 383 Eintraegen ueber 240 KB gross - TRMNL lehnt ueber
    100 KB ab und setzt das Plugin auf "degraded". Die Vorlage liest seit dem
    daily-Block nur noch den Eintrag des Tages, also geht auch nur der raus.
    """

    def setUp(self):
        self.assertTrue(PAYLOAD_PATH.exists(),
                        "trmnl.json fehlt - refresh.py laufen lassen")
        self.text = PAYLOAD_PATH.read_text(encoding="utf-8")
        self.payload = json.loads(self.text)

    def test_bleibt_klein(self):
        size = len(self.text.encode("utf-8"))
        self.assertLessEqual(size, PAYLOAD_MAX,
                             f"{size} Bytes - da geht wohl der Bestand mit")

    def test_ohne_bestand(self):
        self.assertNotIn("thai_words", self.payload)

    def test_deckt_sich_mit_words_json(self):
        """Sonst zeigt das Display etwas anderes als der Bestand hergibt."""
        self.assertEqual(self.payload, payload_for(DATA))

    def test_traegt_was_die_vorlage_liest(self):
        w = self.payload["daily"]["word"]
        for feld in ("thai", "example_th", "gloss_de", "example_de"):
            self.assertTrue(str(w.get(feld, "")).strip(), feld)

    def test_phase_ist_dabei(self):
        """Ohne das Feld faellt die Vollansicht auf ihre eigene Uhr zurueck."""
        self.assertIn(self.payload.get("phase"), ("vormittag", "nachmittag"))

    def test_phase_ist_ein_wort_kein_wahrheitswert(self):
        """In Liquid sind false und nil in Vergleichen nicht zu trennen.

        Ein `false` im Payload waere von "Feld fehlt" nicht zu unterscheiden
        und wuerde jeden Vormittag still in den Rueckfallzweig laufen.
        """
        self.assertIsInstance(self.payload["phase"], str)

    def test_zeitstempel_ist_dabei(self):
        """Die einzige Aenderung, an der TRMNL einen neuen Screen erkennt."""
        self.assertIsInstance(self.payload.get("last_updated"), (int, float))


class TestPhase(unittest.TestCase):
    """Die Vollansicht nimmt ab 12 Uhr lokal Deutsch dazu."""

    def test_umschlagpunkt(self):
        tz = ZoneInfo("Europe/Vienna")
        for h, erwartet in [(0, "vormittag"), (11, "vormittag"),
                            (12, "nachmittag"), (23, "nachmittag")]:
            with self.subTest(stunde=h):
                m = datetime(2026, 9, 13, h, 30, tzinfo=tz)
                self.assertEqual(phase_at(m), erwartet)

    def test_genau_auf_zwoelf(self):
        tz = ZoneInfo("Europe/Vienna")
        self.assertEqual(phase_at(datetime(2026, 9, 13, 11, 59, tzinfo=tz)),
                         "vormittag")
        self.assertEqual(phase_at(datetime(2026, 9, 13, 12, 0, tzinfo=tz)),
                         "nachmittag")

    def test_cron_trifft_zwoelf_in_beiden_halbjahren(self):
        """Keine feste UTC-Stunde trifft ganzjaehrig 12 Uhr lokal.

        Darum zwei Eintraege im Workflow. Umgeschaltet wird beim ersten Lauf,
        der "nachmittag" rechnet; ein spaeterer findet die Phase schon gesetzt,
        aendert nichts und committet nicht. Zu pruefen ist also: der frueheste
        Treffer liegt in beiden Halbjahren auf 12:0x lokal, und kein Lauf
        rechnet "nachmittag", bevor es 12 ist.
        """
        wf = (ROOT / ".github/workflows/refresh.yml").read_text(encoding="utf-8")
        crons = re.findall(r"cron: '([^']+)'", wf)
        self.assertIn("5 10 * * *", crons)
        self.assertIn("5 11 * * *", crons)

        tz = ZoneInfo("Europe/Vienna")
        for tag, kennung in [(datetime(2026, 1, 15), "Winter"),
                             (datetime(2026, 7, 15), "Sommer")]:
            treffer = []
            for stunde in (10, 11):
                utc = tag.replace(hour=stunde, minute=5, tzinfo=timezone.utc)
                lokal = utc.astimezone(tz)
                if phase_at(lokal) == "nachmittag":
                    treffer.append(lokal)
            with self.subTest(kennung):
                self.assertTrue(treffer, f"{kennung}: kein Lauf schaltet um")
                erster = min(treffer)
                self.assertEqual(erster.hour, REVEAL_HOUR,
                                 f"{kennung}: schaltet um {erster:%H:%M} lokal, "
                                 f"nicht um 12:0x")
                for t in treffer:
                    self.assertGreaterEqual(t.hour, REVEAL_HOUR, kennung)


if __name__ == "__main__":
    unittest.main(verbosity=2)
