# -*- coding: utf-8 -*-
"""Rendert Plugin-Markup im echten TRMNL-Framework und misst das Ergebnis.

Vorbereitung (einmalig, im selben Verzeichnis):

    pip install playwright
    curl -sSLO https://usetrmnl.com/css/latest/plugins.css
    curl -sSLO https://usetrmnl.com/js/latest/plugins.js

Dann `render(markup, samples, "out.png", view="quadrant")`. `markup` ist die
Plugin-Markup ohne Liquid, mit __WORD__ und __SENT__ als Platzhalter.
`report()` zeigt Schriftgroessen und ob der Inhalt in die Layout-Box passt -
`belegt 200/193px UEBERLAUF` heisst, es wird abgeschnitten.

Der Pfad zu Chromium unten muss ggf. angepasst werden.
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent

PAGE = """<!doctype html>
<html class="trmnl"><head><meta charset="utf-8">
<link rel="stylesheet" href="plugins.css">
<style>html,body{margin:0;padding:0}</style>
</head>
<body class="trmnl">
  <div class="screen __SCREEN__">
    __WRAP_OPEN__
      __CELLS__
    __WRAP_CLOSE__
  </div>
<script src="plugins.js"></script>
</body></html>"""


WRAPPERS = {
    "full":            ("", ""),
    "half_horizontal": ("", ""),
    "half_vertical":   ("", ""),
    "quadrant":        ('<div class="mashup mashup--2x2">', "</div>"),
}


def render(markup, samples, out_png, view="quadrant", screen="screen--og",
           size=(800, 480)):
    cells = "".join(
        f'<div class="view view--{view}">{markup.replace("__WORD__", w).replace("__SENT__", s)}</div>'
        for w, s in samples)
    o, c = WRAPPERS[view]
    html = (PAGE.replace("__CELLS__", cells).replace("__WRAP_OPEN__", o)
            .replace("__WRAP_CLOSE__", c).replace("__SCREEN__", screen))
    (HERE / "page.html").write_text(html, encoding="utf-8")

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                              args=["--force-device-scale-factor=1"])
        pg = b.new_page(viewport={"width": size[0], "height": size[1]})
        pg.goto((HERE / "page.html").as_uri())
        pg.wait_for_timeout(2500)
        try:
            pg.evaluate("window.terminalize && window.terminalize()")
        except Exception:
            pass
        pg.wait_for_timeout(1500)

        data = pg.evaluate("""() => [...document.querySelectorAll('.view')].map(v => {
          const layout = v.querySelector('.layout');
          const lr = layout.getBoundingClientRect();
          const cs = getComputedStyle(layout);
          const padT = parseFloat(cs.paddingTop), padB = parseFloat(cs.paddingBottom);
          const inner = { top: lr.top + padT, bottom: lr.bottom - padB };
          const read = sel => {
            const el = v.querySelector(sel); if (!el) return null;
            const r = el.getBoundingClientRect();
            const c = getComputedStyle(el);
            return { text: el.textContent.trim().slice(0,24),
                     px: Math.round(parseFloat(c.fontSize)*10)/10,
                     lh: Math.round(parseFloat(c.lineHeight)*10)/10,
                     w: Math.round(r.width), h: Math.round(r.height),
                     top: Math.round(r.top), bottom: Math.round(r.bottom) };
          };
          const word = read('.thai--headword'), sent = read('.thai--sentence');
          // Wahrheit: passt der Inhalt in die Layout-Box?
          const overflow = layout.scrollHeight > layout.clientHeight + 1
                        || layout.scrollWidth  > layout.clientWidth + 1;
          return { layoutH: Math.round(lr.height), layoutW: Math.round(lr.width),
                   innerH: Math.round(inner.bottom - inner.top),
                   used: layout.scrollHeight, box: layout.clientHeight,
                   word, sent, overflow };
        })""")
        pg.screenshot(path=str(HERE / out_png))
        b.close()
    return data


def report(title, data):
    print(f"\n### {title}")
    for d in data:
        print(f"  layout {d['layoutW']}x{d['layoutH']}  belegt {d['used']}/{d['box']}px"
              f"{'   UEBERLAUF' if d['overflow'] else ''}")
        for k in ("word", "sent"):
            e = d[k]
            if e:
                print(f"    {k:5} {e['px']:>5}px  lh {e['lh']:>5}  "
                      f"{e['w']:>3}x{e['h']:<3}  {e['text']}")
