# TRMNL-Recipe

`recipe.liquid` ist die Markup-Vorlage, wie sie im TRMNL-Plugin hinterlegt ist -
hier abgelegt, damit die andere Haelfte des Systems versioniert ist.

## Sie braucht keine Aenderung

Die Vorlage waehlt selbst aus:

```liquid
{%- assign day_index   = local_time | divided_by: 86400 -%}
{%- assign pick_index  = day_index | plus: daily_seed | modulo: pool_size -%}
{%- assign selected_item = pool[pick_index] -%}
```

Ein Schritt pro Tag durch `thai_words`. Die Reihenfolge der Datei ist damit die
Reihenfolge der Tage - und genau dort setzt die Bereinigung an
(`scripts/select.py`). Die Vorlage laeuft weiter auf lokaler Zeit und wechselt
um lokal Mitternacht.

Alle Felder, die die Vorlage liest - `thai`, `example_th`, `gloss_de`,
`example_de`, `forvo_slug` - heissen unveraendert.

## Was sie noch nicht zeigt

`rtgs` (Umschrift) und `tone` (Tonanalyse) stehen in jedem Eintrag, werden aber
nirgends gerendert. Wer sie sehen will, haengt unter das Thai-Wort:

```liquid
{%- if selected_item.rtgs -%}
  <div class="w--full">
    <span class="label label--underline">{{ selected_item.rtgs }}</span>
  </div>
{%- endif -%}

{%- if selected_item.tone.syllables -%}
  <div class="w--full">
    <span class="description">
      {%- for s in selected_item.tone.syllables -%}
        {{ s.glyph }} - {{ s.tone }}{% unless forloop.last %} / {% endunless %}
      {%- endfor -%}
    </span>
  </div>
{%- endif -%}
```

`tone.syllables` ist `null`, wo der Ton nicht regelbasiert ableitbar ist; die
Bedingung faengt das ab. `tone.initial_class` steht dagegen immer.

---

## Warum die Quadrant-Ansicht nicht skaliert hat

`recipe-fit.liquid` ist die korrigierte Fassung. Gemessen wurde mit
`harness/render.py` gegen das echte Framework-CSS und -JS.

Die Layout-Box gibt das Framework selbst vor - auf einem 800x480-Geraet:

```
.view--quadrant .layout:has(+.title_bar)
  height  = quadrant-h (225px) - title-bar-small (32px) = 193px
  padding = gap (10px)
  -> nutzbar 365 x 173 px
```

Der Fitter (`fitValue` in plugins.js) arbeitet so:

* Er misst gegen `element.parentElement` - aber **nur in der Breite**.
* Die Hoehe kommt ausschliesslich aus `data-value-fit-max-height`. Es gibt
  keinen Modus, in dem er die Hoehe des Elternelements benutzt.
* **Ohne** dieses Attribut setzt er `white-space: nowrap` und schrumpft bis
  auf 8px, damit alles auf eine Zeile passt.
* Er wird nie groesser als die CSS-Groesse, mit der er startet.

Daraus die vier Fehler:

1. **Das Kopfwort hatte kein `max-height`.** Also `nowrap`: lange Woerter
   wurden winzig statt umzubrechen, und die Hoehe war voellig unbeschraenkt.
   Bei kurzen Woertern blieb es bei `value--xxlarge` = 96px, was mit
   Zeilenhoehe 1,35 schon 130px belegt - `belegt 200/193px`, also
   abgeschnitten.

2. **`display: inline`.** `getBoundingClientRect()` liefert bei einem
   inline-Element die Schriftbox (rund 1,1 x Schriftgrad), belegt wird im
   Layout aber die Zeilenhoehe (1,35 bis 1,5 x). Der Fitter haelt sein
   Budget also ein und der Block laeuft trotzdem ueber. `display: block`
   macht gemessene und belegte Hoehe identisch.

3. **Die Ceilings waren teils zu niedrig.** `value--base` fuer den Satz im
   Quadranten heisst: der Fitter kann nie groesser werden, auch wenn Platz
   da ist. In der Vollansicht blieb der Text dadurch bei 38px in einer
   411px hohen Box.

4. **Der Fitter zieht die Zeilenhoehe beim Schrumpfen Richtung 1,2** - er
   interpoliert von der Ausgangs-Ratio dorthin. Fuer Thai ist das zu eng;
   Tonzeichen und untere Vokale werden angeschnitten. `line-height: 1.5
   !important` im Stylesheet schlaegt die Inline-Zeilenhoehe des Fitters,
   und weil das Element ein Block ist, rechnet er trotzdem richtig.

Ausserdem stand bei `@font-face` `font-display: swap`, obwohl der Kommentar
daneben `block` begruendet. Mit `swap` kann der Fitter gegen die
Fallback-Metrik messen und die Thai-Schrift erscheint erst danach.

### Was die korrigierte Fassung macht

* `display: block` und `data-value-fit-max-height` auf **beiden** Elementen.
* Hohe Ceilings (`--value-xxxlarge-font-size` / `--value-xxlarge-font-size`),
  damit das Hoehenbudget bindet und nicht die Klasse.
* Ein kleines Skript misst die echte Innenhoehe des Layouts und verteilt sie
  56/44 auf Kopfwort und Satz. Damit stimmt es in allen vier Views und auf
  jedem Geraet, ohne gepflegte Pixelzahlen. Faellt das Skript aus, greifen
  die Zahlen aus Abschnitt 5 der Markup.
* `px--2` als seitlicher Abstand, sonst klebt das Wort am Rand.

Gemessen, jeweils `belegt/verfuegbar`:

| Fall                       | vorher              | nachher      |
| -------------------------- | ------------------- | ------------ |
| quadrant, kurzes Wort      | 200/193 UEBERLAUF   | 193/193      |
| quadrant, langes Wort      | 193/193, Satz 30px  | 193/193      |
| full                       | Text bei 38px       | 128px / 96px |
