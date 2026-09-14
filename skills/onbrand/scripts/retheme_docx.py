#!/usr/bin/env python3
"""onbrand path B — recolour an existing .docx when there is no source doc.json.

    python3 retheme_docx.py in.docx --theme themes/example-brand.json --out out.docx [--fonts safe|brand]

Walks the OOXML and maps every colour it finds onto the nearest theme colour of comparable
lightness, so text that was dark stays dark and fills that were pale stay pale. Swaps fonts
in styles, runs and the theme font scheme.

Limits, state them to the user:
  - charts embedded as images keep their original colours (rebuild them from data instead)
  - a document whose palette is already near-monochrome has little for this to grab
Prefer apply_theme.py whenever the source JSON exists.
"""

import argparse
import json
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_theme import chroma, dist, hexs, hsl, lstar, mix_on_white  # noqa: E402

WHITE = "#FFFFFF"
HEXVAL = re.compile(r'(w:(?:val|fill|color|themeColor)="|<a:srgbClr val=")([0-9A-Fa-f]{6})(")')
FONTATTR = re.compile(r'(w:(?:ascii|hAnsi|cs|eastAsia)=")([^"]+)(")')


def pool_of(theme):
    c = theme["colors"]
    out = [c[k] for k in ("ink", "muted", "accent", "accent_fill", "band_fill", "band_text",
                          "header_fill", "zebra", "callout", "hairline")]
    out += list(theme["semantic"].values())
    out += list((theme.get("semantic_band") or {}).values())
    light = theme.get("semantic_light") or {
        k: mix_on_white(v, 0.18) for k, v in theme["semantic"].items()}
    out += list(light.values())
    out += theme.get("chart", [])
    out.append(WHITE)
    seen, uniq = set(), []
    for h in out:
        h = "#" + hexs(h)
        if h not in seen:
            seen.add(h); uniq.append(h)
    return uniq


def nearest(h, pool):
    """Lightness first — dark text must stay dark — then hue, so a pale green quadrant lands on
    the brand's pale green and not on whatever cream happens to be closest in RGB. Without the
    hue term a SWOT's red/green/neutral coding collapses into one colour."""
    hh, _, _ = hsl(h)
    ch = chroma(h)

    def hue_gap(p):
        if ch < 0.02 or chroma(p) < 0.02:
            return 0.0 if ch < 0.02 else 180.0     # source neutral: hue is irrelevant
        d = abs(hsl(p)[0] - hh) % 360
        return min(d, 360 - d)

    return min(pool, key=lambda p: abs(lstar(p) - lstar(h)) * 12
               + hue_gap(p) * 1.4 + dist(p, h) * 0.02)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--theme", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fonts", choices=["safe", "brand"], default="safe")
    a = ap.parse_args()

    theme = json.load(open(a.theme))
    pool = pool_of(theme)
    font = theme["font"]["brand"] if a.fonts == "brand" else theme["font"]["fallback"]

    mapped, images = {}, 0
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    with zipfile.ZipFile(a.docx) as zin, zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml") and (
                    item.filename.startswith("word/") or item.filename.startswith("ppt/")):
                x = data.decode("utf-8")

                def crepl(m):
                    h = "#" + m.group(2).upper()
                    if h in ("#FFFFFF", "#AUTO"):
                        return m.group(0)
                    n = nearest(h, pool)
                    mapped[h] = n
                    return m.group(1) + hexs(n) + m.group(3)

                x = HEXVAL.sub(crepl, x)
                x = FONTATTR.sub(lambda m: m.group(1) + font + m.group(3), x)
                data = x.encode("utf-8")
            elif re.search(r"\.(png|jpe?g|emf|wmf|svg)$", item.filename, re.I):
                images += 1
            zout.writestr(item, data)

    print(f"theme: {theme.get('brand')}  ({a.fonts} fonts -> {font})")
    for k in sorted(mapped, key=lstar):
        print(f"  {k} -> {mapped[k]}")
    if images:
        print(f"  WARNING: {images} embedded image(s) untouched — any chart in them still "
              f"carries the old palette. Rebuild those from data if they matter.")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
