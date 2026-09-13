# mythai

Thai-Vokabeln fuer ein TRMNL-Display. `words.json` ist der Bestand,
`trmnl.json` das Wort des Tages - die kleine Datei, die das Display abholt.
Ein GitHub-Workflow schreibt beide taeglich.

## Aufbau

```
words.json          der Bestand (Quelle der Wahrheit, wird nicht ausgeliefert)
trmnl.json          das Wort des Tages - das holt TRMNL ab
scripts/select.py   die Reihenfolge (der eigentliche Hebel)
scripts/refresh.py  taeglicher Lauf (schreibt beide Dateien)
scripts/thai.py     Konsonantenklasse und Silbenanalyse
scripts/audit.py    Qualitaetsbericht
scripts/migrate.py  einmalige Bereinigung des Altbestands
scripts/test_selection.py   Tests
trmnl/              die TRMNL-Vorlage und was sie erwartet
```

## Warum zwei Dateien

TRMNL lehnt Nutzdaten ueber 100 KB ab und setzt das Plugin dann auf
"degraded" - es holt gar nichts mehr, bis man die Gesundheit von Hand
zuruecksetzt. `words.json` ist mit 383 Eintraegen ueber 240 KB gross; allein
die Tonanalysen machen 78 KB aus.

Die Vorlage braucht davon nichts. Seit sie `daily.word` liest, ist der Bestand
im Payload totes Gewicht:

```
words.json   247 KB   Bestand, Tonanalysen, Beispielsaetze - alles
trmnl.json   ~0,7 KB  ein Eintrag, ein Zeitstempel
```

Ein Test haelt `trmnl.json` unter 8 KB. Reisst der, ist versehentlich wieder
der Bestand mitgegangen.

**Die Polling-URL des Plugins zeigt auf `trmnl.json`:**

```
https://raw.githubusercontent.com/nikokoren/mythai/main/trmnl.json
```

Die Reihenfolge beim Umstellen zaehlt: erst die Markup einspielen, die
`daily.word` liest, dann die URL umhaengen. Andersherum steht kurz "No Data"
auf dem Display, weil die alte Markup in `trmnl.json` kein `thai_words`
findet.

## words.json

```jsonc
{
  "thai_words": [ /* der komplette Bestand */ ],
  "phase": "vormittag",   // ab 12 Uhr lokal "nachmittag" (nur Vollansicht)
  "daily": {              // was heute drankommt
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

### Wann das Display wechselt

TRMNL erzeugt einen Screen **nur dann neu, wenn sich die Nutzdaten geaendert
haben** ("skips generating screens if the merge variables are the same between
requests"). Der Wechsel haengt also nicht an einer Rechnung in der Vorlage,
sondern daran, wann dieser Workflow `words.json` schreibt.

Darum:

* Die Vorlage rechnet nichts mehr selbst, sie liest `daily.word`. Vorher stand
  dort `day_index modulo N` aus lokaler Zeit - das sah nach lokalem Mitternacht
  aus, entschied aber nichts, weil der Screen ohnehin erst beim naechsten
  Datei-Wechsel neu erzeugt wurde. Zwei Uhren, von denen nur eine zaehlt.
* Der Cron laeuft um **23:05 UTC**: 00:05 MEZ im Winter, 01:05 MESZ im Sommer,
  also ganzjaehrig kurz nach lokaler Mitternacht. `TRMNL_TZ` (Europe/Vienna)
  sorgt dafuer, dass `daily.date` dabei das lokale Datum traegt und nicht das
  von UTC.
* `last_updated` bleibt. Der `daily`-Block aendert sich taeglich und traegt den
  Wechsel schon allein, aber der Zeitstempel steht als ausdrueckliches Signal
  daneben - genau dafuer war er urspruenglich da.

### Zweimal am Tag, nicht einmal und nicht 24-mal

Die Vollansicht zeigt bis 12 Uhr nur Thai und nimmt danach die deutsche
Bedeutung und den deutschen Satz dazu. Das ist eine zweite Aenderung der
Nutzdaten und braucht darum einen zweiten Lauf.

Der Workflow lief urspruenglich stuendlich (`'0 * * * *'`, trotz des Kommentars
"Midnight UTC"). Ich hatte das auf einen Lauf gekuerzt und die 23 anderen fuer
wirkungslos gehalten - sie waren es nicht: einer davon hat jeden Tag die
Mittagsumschaltung ausgeloest. Mit nur einem Lauf wird der Screen kurz nach
Mitternacht gezeichnet und danach nicht mehr, und Deutsch erscheint nie.

Jetzt drei Cron-Eintraege, aber **zwei Renderings pro Tag**:

| Cron (UTC)    | im Winter   | im Sommer   | was passiert                |
| ------------- | ----------- | ----------- | --------------------------- |
| `5 23 * * *`  | 00:05 MEZ   | 01:05 MESZ  | neues Wort, Phase vormittag |
| `5 10 * * *`  | 11:05 MEZ   | 12:05 MESZ  | im Sommer die Umschaltung   |
| `5 11 * * *`  | 12:05 MEZ   | 13:05 MESZ  | im Winter die Umschaltung   |

Zwei Mittags-Eintraege, weil keine feste UTC-Stunde in beiden Halbjahren 12 Uhr
trifft. Der jeweils falsche laeuft ins Leere: `refresh.py` rechnet `phase` aus
der echten lokalen Zeit, findet nichts geaendert, schreibt nicht und committet
nicht - also auch kein Rendering. Im Winter rechnet der 10:05-Lauf noch
"vormittag", im Sommer findet der 11:05-Lauf "nachmittag" schon gesetzt vor.
So steht die Umschaltung ganzjaehrig auf 12:05 lokal.

Verzoegert GitHub einen Lauf um ein, zwei Stunden - das kommt regelmaessig vor -
wird die Umschaltung spaeter, nie frueher: entschieden wird nach der Uhr zum
Zeitpunkt des Laufs, nicht nach der geplanten Zeit.

### phase ist ein Wort, kein Wahrheitswert

Im Payload steht `"phase": "vormittag"` bzw. `"nachmittag"`, nicht `true`/`false`.
In Liquid sind `false` und `nil` in Vergleichen nicht auseinanderzuhalten; ein
`false` im Payload waere von "Feld fehlt" nicht zu unterscheiden und wuerde die
Vorlage jeden Vormittag still in den Rueckfallzweig laufen lassen.

Die Umschaltung faellt aus demselben Grund im Workflow und nicht in der Vorlage:
die Vorlage kann die Stunde ausrechnen so oft sie will, zu sehen ist, was beim
letzten Schreiben der Datei galt.

**Nur die Vollansicht.** Die Quadranten-Vorlage zeigt Thai-Wort und Thai-Satz,
zu jeder Tageszeit, und liest `phase` gar nicht.

### Kein Stand aus der Zukunft in words.json

Weil der Lauf nur schreibt, wenn sich etwas aendert, legt ein vorausgeschriebenes
`daily` genau den Tag stumm, auf den es lautet: der Lauf findet nichts zu tun,
die Nutzdaten bleiben gleich, das Display behaelt das Wort vom Vortag. So ist
der 11.09.2026 ausgefallen - ein Probelauf mit `--date` war versehentlich mit
eingecheckt worden.

Zwei Riegel dagegen: `refresh.py` bricht bei einem Datum in der Zukunft ab, und
`test_selection.py` faellt durch, wenn `daily.date` in der Zukunft liegt. Der
Workflow laesst die Tests vor dem Schreiben laufen, faellt in dem Fall also
sichtbar aus, statt still nichts zu tun.

## Lokal

```sh
python3 scripts/refresh.py --date 2026-09-20 --dry-run --preview 14   # vorschauen
python3 scripts/refresh.py --reorder           # Reihenfolge neu mischen
python3 scripts/audit.py                       # Qualitaetsbericht
python3 scripts/test_selection.py              # Tests
```

`--dry-run` rechnet ueber eine Kopie und laesst `words.json` in Ruhe. Fuer alles,
was in der Zukunft liegt, ist es Pflicht - ohne bricht der Lauf ab.
