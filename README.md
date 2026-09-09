# mythai

Thai-Vokabeln fuer ein TRMNL-Display. `words.json` wird von der Plugin-Vorlage
abgeholt; ein GitHub-Workflow schreibt einmal taeglich die Auswahl des Tages
hinein.

## Aufbau

```
words.json          das einzige Artefakt, das TRMNL liest
scripts/select.py   die Auswahllogik
scripts/refresh.py  taeglicher Lauf (schreibt words.json)
scripts/thai.py     Konsonantenklasse und Silbenanalyse
scripts/audit.py    Qualitaetsbericht
scripts/migrate.py  einmalige Bereinigung des Altbestands
scripts/test_selection.py   Tests
```

## words.json

```jsonc
{
  "thai_words": [ /* der komplette Bestand */ ],
  "daily": {
    "date": "2026-09-09",
    "cycle": 3,            // wievielter Durchlauf durch den Bestand
    "day_in_cycle": 20,
    "cycle_days": 77,      // Tage, bis der Bestand einmal durch ist
    "words": [ /* die Woerter des Tages, vollstaendig eingebettet */ ]
  },
  "word_count": 383,
  "last_updated": 1788940540.13
}
```

Ein Eintrag:

```jsonc
{
  "thai": "คืน",
  "rtgs": "khuen",
  "pos": "Nomen/Verb",
  "gloss_de": "Nacht; zurueckgeben",
  "topic": "Zeit & Kalender",
  "example_th": "คืนนี้ ดาวสวยมาก",
  "example_de": "Heute Nacht sind die Sterne sehr schoen.",
  "tone": {
    "syllables": [
      { "glyph": "คืน", "class": "Tiefkonsonant",
        "syllable": "geschlossen", "length": "lang", "tone": "mittel" }
    ],
    "initial_class": "Tiefkonsonant",
    "rule_hint": "Tiefkonsonant + geschlossene Silbe + langer Vokal -> mittel",
    "source": "regelbasiert berechnet"
  },
  "forvo_slug": "คืน"
}
```

`tone.syllables` ist `null`, wenn der Ton nicht regelbasiert ableitbar ist
(mehrsilbige Woerter, Lehnwoerter). `tone.initial_class` steht immer.
`tone.source` ist dann `"unvollstaendig"` - diese Eintraege brauchen eine
Woerterbuchquelle, geraten wird nichts.

### Umstellung der TRMNL-Vorlage

Die Vorlage sollte jetzt `daily.words` rendern statt selbst im Bestand zu
suchen. Alte Felder und ihr Ersatz:

| alt                     | neu                                  |
| ----------------------- | ------------------------------------ |
| `tone_cheat[0]`         | `tone.initial_class`                 |
| `tone_cheat[1]`, `[2]`  | `tone.syllables[0].syllable/.length` |
| `syllables[].tone_name` | `tone.syllables[].tone`              |
| `tone_rule_hint`        | `tone.rule_hint`                     |
| `example_tone_guides`   | entfaellt                            |

`thai`, `rtgs`, `gloss_de`, `pos`, `example_th`, `example_de` und `forvo_slug`
heissen unveraendert.

`example_tone_guides` faellt ersatzlos weg: das Feld enthielt trotz seines
Namens nie eine Tonspur zum Beispielsatz, sondern das Stichwort mit einem
angehaengten Diakritikum (81 von 82 Faellen).

## Die Auswahl

Frueher stand in `words.json` nur ein Zeitstempel; die Auswahl passierte in der
Liquid-Vorlage, praktisch nur ueber `last_updated mod N`. Das hatte zwei
Folgen:

* Der Bestand lag in Lehrplan-Reihenfolge (alle Wochentage hintereinander, alle
  Farben hintereinander). Ein fortlaufender Ausschnitt zeigte darum immer einen
  ganzen Themenblock auf einmal.
* Die Schrittweite war konstant: `86400 mod 315 = 90`, und `ggT(90, 315) = 45`.
  Bei exakt taeglichem Lauf waren nur 7 verschiedene Startindizes erreichbar -
  35 von 315 Woertern, im Wochentakt wiederholt.

Jetzt entscheidet `scripts/select.py`, und zwar nur anhand des Datums:

1. Pro Zyklus wird ein **Deck** gebaut - eine Permutation des gesamten
   Bestands, in der jedes Thema gleichmaessig ueber die volle Laenge verteilt
   liegt statt in Bloecken.
2. Jeder Tag schneidet den naechsten Block von fuenf Woertern heraus.
3. Ein Nachlauf tauscht Themen-Dubletten innerhalb eines Tages weg.

Damit gilt: kein Wort wiederholt sich vor Ablauf eines Zyklus (77 Tage), die
fuenf Woerter eines Tages kommen aus fuenf verschiedenen Themen, aufeinander
folgende Tage ueberschneiden sich nicht, und jeder Zyklus mischt neu.
`scripts/test_selection.py` prueft genau diese Zusagen.

Weil die Auswahl nur vom Datum abhaengt, ist ein zweiter Lauf am selben Tag
folgenlos - der Workflow committet dann nichts.

## Lokal

```sh
python3 scripts/refresh.py --date 2026-09-09   # Auswahl fuer ein Datum zeigen
python3 scripts/audit.py                       # Qualitaetsbericht
python3 scripts/test_selection.py              # Tests
```
