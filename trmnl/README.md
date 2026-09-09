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
