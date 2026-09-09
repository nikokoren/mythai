# mythai

Thai-Vokabeln fuer ein TRMNL-Display. `words.json` wird von der Plugin-Vorlage
abgeholt, die sich daraus jeden Tag ein Wort zieht. Ein GitHub-Workflow haelt
die Datei taeglich aktuell.

## Aufbau

```
words.json          das einzige Artefakt, das TRMNL liest
scripts/select.py   die Reihenfolge (der eigentliche Hebel)
scripts/refresh.py  taeglicher Lauf (schreibt words.json)
scripts/thai.py     Konsonantenklasse und Silbenanalyse
scripts/audit.py    Qualitaetsbericht
scripts/migrate.py  einmalige Bereinigung des Altbestands
scripts/test_selection.py   Tests
trmnl/              die TRMNL-Vorlage und was sie erwartet
```

## words.json

```jsonc
{
  "thai_words": [ /* der komplette Bestand */ ],
  "daily": {              // informativ; die Vorlage rechnet selbst
    "date": "2026-09-10",
    "day_index": 20706,   // Tage seit der Unix-Epoche
    "index": 24,          // day_index modulo word_count
    "word": { /* der Eintrag von heute */ }
  },
  "cycle": 54,            // wievielter Durchlauf durch den Bestand
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

### Was sich fuer die TRMNL-Vorlage aendert

Nichts, was sie liest. `thai`, `example_th`, `gloss_de`, `example_de` und
`forvo_slug` heissen unveraendert; die Vorlage rendert die vier alten
Tonfelder ohnehin nicht. Wer sie doch anzeigen will, findet in
`trmnl/README.md` einen Baustein. Zuordnung alt zu neu:

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

Die Auswahl passiert in der TRMNL-Vorlage, nicht hier:

```liquid
day_index  = local_time / 86400          # Tage seit der Unix-Epoche
pick_index = (day_index + daily_seed) modulo N
selected   = thai_words[pick_index]
```

Das ist **ein Schritt pro Tag durch das Array**. Die Reihenfolge der Datei ist
damit die Reihenfolge der Tage. Solange `thai_words` nach Lehrplan sortiert war
(alle Wochentage hintereinander, alle Farben hintereinander), kam genau das auf
dem Display an - Anfang September neun Tage lang eine Farbe nach der anderen:

```
2026-09-03  Index 224  ขาว      weiss
2026-09-04  Index 225  ดำ       schwarz
2026-09-05  Index 226  แดง      rot
...
2026-09-09  Index 230  ชมพู     rosa
```

Der Hebel ist also die **Reihenfolge**, nicht die Auswahl. `scripts/select.py`
legt den Bestand so, dass die Themen gleichmaessig ineinander verschraenkt
liegen:

1. Jedes Wort bekommt eine Position innerhalb seines Themas, gleichmaessig
   ueber die volle Laenge verteilt; danach sortiert liegen die Themen
   verschraenkt statt in Bloecken.
2. Ein Nachlauf tauscht uebrig gebliebene Naehe weg: innerhalb von fuenf
   aufeinanderfolgenden Positionen kommt kein Thema zweimal vor.

Das Ergebnis ist eine Permutation - es geht nichts verloren und nichts kommt
doppelt. Ueber einen Zyklus (383 Tage) erscheint jedes Wort genau einmal, und
jeder neue Zyklus mischt neu. `scripts/refresh.py` mischt nur am Zyklusende
neu; an allen anderen Tagen schreibt es lediglich `daily`.

**Die Vorlage muss dafuer nicht angepasst werden.** Sie rechnet ihren Index
weiter selbst aus lokaler Zeit aus und wechselt darum um lokal Mitternacht -
nicht um 00:05 UTC, wenn der Workflow laeuft. Siehe `trmnl/README.md`.

Der Workflow lief vorher stuendlich (`'0 * * * *'`, trotz des Kommentars
"Midnight UTC") und schrieb dabei ausser `last_updated` nichts. Da die Vorlage
`last_updated` gar nicht liest, waren das 24 wirkungslose Commits pro Tag.
Jetzt: `'5 0 * * *'`, ein Commit.

## Lokal

```sh
python3 scripts/refresh.py --date 2026-09-09 --preview 14   # zwei Wochen vorschauen
python3 scripts/refresh.py --reorder           # Reihenfolge neu mischen
python3 scripts/audit.py                       # Qualitaetsbericht
python3 scripts/test_selection.py              # Tests
```
