#!/usr/bin/env python3
"""onbrand — turn extracted brand tokens into a document theme, under contrast rules.

    python3 make_theme.py tokens.json --brand "Meridian Partners" --short the brand --out theme.json
    python3 make_theme.py --check theme.json

The classifier proposes; you decide. It is reliable on neutrals and lightness ordering and
has no opinion about which of two chromatics a company considers primary. Read the report,
edit the theme, re-run --check.

See references/role-mapping.md for the doctrine this implements.
"""

import argparse
import json
import re
import sys

# --------------------------------------------------------------- colour maths
def parse_hex(s):
    if not isinstance(s, str):
        return None
    m = re.search(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b", s.strip())
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexs(h):
    return h.lstrip("#").upper()


def luminance(h):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hsl(h):
    r, g, b = [v / 255.0 for v in rgb(h)]
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        hh = ((g - b) / d) % 6
    elif mx == g:
        hh = (b - r) / d + 2
    else:
        hh = (r - g) / d + 4
    return hh * 60, s, l


def chroma(h):
    """Absolute colourfulness, 0..1. HSL saturation lies at the extremes — a near-black like
    #010506 reports 0.71 saturation — so every neutral/chromatic split uses this instead."""
    r, g, b = rgb(h)
    return (max(r, g, b) - min(r, g, b)) / 255.0


def lstar(h):
    y = luminance(h)
    return 116 * (y ** (1 / 3)) - 16 if y > 0.008856 else 903.3 * y


def blend(a, b, t):
    """t of b mixed into a."""
    ra, rb = rgb(a), rgb(b)
    return "#%02X%02X%02X" % tuple(round(x * (1 - t) + y * t) for x, y in zip(ra, rb))


def boost(h, k):
    """Lighten while keeping the hue: scale channels, don't wash toward a tint."""
    return "#%02X%02X%02X" % tuple(min(255, round(c * k)) for c in rgb(h))


def mix_on_white(h, alpha):
    r, g, b = rgb(h)
    return "#%02X%02X%02X" % tuple(round(c * alpha + 255 * (1 - alpha)) for c in (r, g, b))


def dist(a, b):
    """Perceptual-ish distance: weighted RGB, adequate for nearest-role matching."""
    (r1, g1, b1), (r2, g2, b2) = rgb(a), rgb(b)
    rm = (r1 + r2) / 2
    return ((2 + rm / 256) * (r1 - r2) ** 2 + 4 * (g1 - g2) ** 2
            + (2 + (255 - rm) / 256) * (b1 - b2) ** 2) ** 0.5


WHITE = "#FFFFFF"

# --------------------------------------------------------------- token reading
SEMANTIC_PATTERNS = {
    "error": r"error|danger|negative|red",
    "warning": r"warning|caution|amber|alert",
    "success": r"success|positive|green|ok\b",
}


def read_tokens(tok):
    """Return (candidates, semantics, fonts). candidates: hex -> weight."""
    cand, semantics = {}, {}
    raw_vars = tok.get("vars", {}) or {}

    # Resolve one level of var(--x) indirection so aliases inherit their target's value.
    direct = {k: parse_hex(v) for k, v in raw_vars.items()}
    resolved = dict(direct)
    for k, v in raw_vars.items():
        if resolved.get(k):
            continue
        m = re.match(r"var\((--[^)\\,]+)", v.replace("\\", ""))
        if m:
            resolved[k] = direct.get(m.group(1))

    for name, hx in resolved.items():
        if not hx:
            continue
        clean = name.lower().replace("\\", "")
        # Declared design tokens outrank observed pixels; brand-namespaced ones outrank the rest.
        w = 3_000_000 if re.search(r"brand|primary|accent", clean) else 1_500_000
        for role, pat in SEMANTIC_PATTERNS.items():
            if re.search(pat, clean):
                dark = "dark" in clean
                semantics.setdefault(role, {})["dark" if dark else "light"] = hx
                w = 0  # a semantic colour is never a brand candidate
        if w:
            cand[hx] = max(cand.get(hx, 0), w)

    total_bg = sum(w for _, w in tok.get("bg", [])) or 1
    for hx, w in tok.get("bg", []):
        hx = parse_hex(hx)
        if hx:
            cand[hx] = max(cand.get(hx, 0), 1_000_000 * w / total_bg)
    for hx, w in tok.get("fg", []):
        hx = parse_hex(hx)
        if hx:
            cand[hx] = max(cand.get(hx, 0), 300_000 * w / max(1, sum(x for _, x in tok.get("fg", []))))

    fonts = [f for f, _ in tok.get("fonts", [])]
    return cand, semantics, fonts


def clean_font(spec):
    first = spec.split("|")[0].split(",")[0].strip().strip('"').strip("'")
    # Webflow exports names like 'Plus Jakarta Sans Variablefont Wght'
    first = re.sub(r"\s*(variablefont|wght|variable font)\s*", " ", first, flags=re.I).strip()
    return first


FALLBACKS = [
    (r"anton|impact|oswald|bebas|teko|archivo black|black|condensed", "Arial Black"),
    (r"georgia|garamond|times|serif|playfair|merriweather|lora", "Georgia"),
    (r"mono|code|courier", "Consolas"),
]


def read_type(tok, body_font, head_font):
    """The heading ladder decides the DISPLAY role: family, case and tracking.

    Colour alone never makes a document look like a brand — a brand is recognised by its
    display face and how it is set. Anton, uppercase, at -2% tracking is more 'the brand' than any
    hex value in their palette."""
    levels = tok.get("type") or []
    display, case, tracking, leading = head_font, "upper", -0.02, 1.10
    if levels:
        top = levels[0]
        display = clean_font(top.get("family") or head_font)
        case = "upper" if (top.get("transform") == "uppercase") else "none"
        tracking = float(top.get("tracking") or 0)
        leading = float(top.get("leading") or 1.15)
        # body tracking: the smallest heading is the closest proxy for running text
        body_lv = next((l for l in reversed(levels)
                        if clean_font(l.get("family", "")).lower() != display.lower()), None)
        if body_lv:
            body_font = clean_font(body_lv["family"]) or body_font
    return {
        "body": body_font,
        "body_fallback": fallback_for(body_font),
        "display": display,
        "display_fallback": fallback_for(display),
        "display_case": case,
        "display_tracking": round(max(-0.06, min(0.12, tracking)), 4),
        "display_leading": round(leading, 2),
    }


def fallback_for(name):
    for pat, fb in FALLBACKS:
        if re.search(pat, name, re.I):
            return fb
    return "Calibri"


# --------------------------------------------------------------- role assignment
DEFAULT_SEMANTICS = {"error": "#8C2F2A", "warning": "#8A6D1F", "success": "#1C5E38"}


def build_theme(tok, brand, short):
    cand, semantics, fonts = read_tokens(tok)
    if not cand:
        sys.exit("No colours found in tokens.json — extract again or hand-write the theme.")

    notes = []
    # Declared design tokens beat observed pixels: a stray #FAFAFA painted by a widget is not
    # part of the brand. Fall back to everything only if the site declares too little.
    declared = {h: w for h, w in cand.items() if w >= 1_000_000}
    work = declared if len(declared) >= 5 else cand
    if work is declared:
        notes.append(f"working from {len(declared)} declared tokens; observed-only colours "
                     f"were kept for chart fill-in")

    order = [h for h, _ in sorted(work.items(), key=lambda kv: -kv[1])]
    neutrals = [h for h in order if chroma(h) < 0.06]
    chromatics = [h for h in order if chroma(h) >= 0.15 and 18 <= lstar(h) <= 92]
    by_l = lambda xs: sorted(xs, key=lstar)

    # band_fill — their dark ground. Prefer a brand near-black over generic #000000.
    darks = [h for h in by_l(neutrals) if lstar(h) < 22]
    branded_darks = [h for h in darks if h != "#000000"]
    band_fill = (branded_darks or darks or [order[0]])[0]

    lights = [h for h in sorted(neutrals, key=lstar, reverse=True) if lstar(h) > 90
              and h != WHITE]
    band_text = lights[0] if lights and contrast(lights[0], band_fill) >= 7 else WHITE

    # ink — darkest brand neutral clearing 12:1, but not the band colour and not pure black
    ink_pool = [h for h in by_l(neutrals)
                if contrast(h, WHITE) >= 12 and h not in ("#000000", band_fill)]
    ink = ink_pool[0] if ink_pool else (band_fill if contrast(band_fill, WHITE) >= 12 else "#1A1A1A")

    # muted — mid neutral in the legible band, highest-weighted (i.e. most brand-declared)
    muted_pool = [h for h in order if h in neutrals and 4.5 <= contrast(h, WHITE) <= 10.5]
    muted = muted_pool[0] if muted_pool else "#6B6B6B"

    # accent_fill — the signature colour: the most-weighted genuinely colourful token
    sig = [h for h in chromatics if chroma(h) >= 0.30]
    accent_fill = sig[0] if sig else (chromatics[0] if chromatics else band_fill)

    # accent — ink-grade. The signature colour only if it can carry text on white.
    if contrast(accent_fill, WHITE) >= 4.5:
        accent = accent_fill
    else:
        passing = [h for h in chromatics if contrast(h, WHITE) >= 4.5]
        accent = passing[0] if passing else band_fill
        notes.append(
            f"{accent_fill} is {contrast(accent_fill, WHITE):.1f}:1 on white — unusable as ink; "
            f"kept as accent_fill (a block colour), accent went to {accent}")

    # table neutrals — the two lightest declared tints, header darker than zebra
    tints = [h for h in sorted(neutrals, key=lstar, reverse=True)
             if h != WHITE and contrast(h, WHITE) <= 1.30]
    zebra = tints[0] if tints else "#F7F7F7"
    header_fill = tints[1] if len(tints) > 1 else (tints[0] if tints else "#EDEDED")
    if contrast(zebra, WHITE) > contrast(header_fill, WHITE):
        header_fill, zebra = zebra, header_fill
    if contrast(zebra, WHITE) > 1.06:
        zebra = mix_on_white(header_fill, 0.35)
        notes.append("zebra was too dark for print — lightened to a 35% tint of header_fill")

    # callout ground: their light section ground if they have one, else a faint accent tint.
    # A brand that alternates dark and cream grounds should get the cream, not a yellow wash.
    callout = header_fill if contrast(header_fill, WHITE) <= 1.30 else \
        mix_on_white(accent_fill if accent_fill != band_fill else accent, 0.10)
    hairline = mix_on_white(muted, 0.35)

    # `rule` is the signature colour used as a LINE — hairlines carry no text, so the
    # 4.5:1 bar that pushed the loud colour out of `accent` does not apply here. This is
    # how a brand whose accent failed on white still gets its colour onto every page.
    rule = accent_fill if chroma(accent_fill) >= 0.15 else accent
    # the signature colour as text ON the dark band (the brand highlight words inside black headlines)
    on_band_accent = accent_fill if contrast(accent_fill, band_fill) >= 4.5 else band_text
    # secondary text on the dark band: present but subordinate to the headline
    on_band_muted = blend(band_text, band_fill, 0.26)

    # semantics — theirs if published, else defaults. Brand never takes a semantic slot.
    sem, sem_light = {}, {}
    for role, default in DEFAULT_SEMANTICS.items():
        got = semantics.get(role, {})
        pick = got.get("dark") or got.get("light")
        if pick and contrast(pick, WHITE) < 4.5:
            pick = None
        sem[role] = pick or default
        if pick:
            notes.append(f"{role} band uses the brand's own system colour {pick}")
        # the pale end of the scale: their published tint if there is one, else a tint of ours.
        pale = got.get("light")
        if pale and contrast(pale, WHITE) > 1.6:
            pale = None          # too dark to be the pale end
        sem_light[role] = pale or mix_on_white(sem[role], 0.24)

    # A semantic colour used as a full-width BAND must separate from the header band, or the
    # reader sees two black stripes and loses the verdict. Their error-dark is often near-black.
    sem_band = {}
    for role, v in sem.items():
        b, k = v, 1.0
        while contrast(b, band_fill) < 2.2 and contrast(band_text, boost(v, k + 0.1)) >= 5.0:
            k += 0.1
            b = boost(v, k)
        if b != v:
            notes.append(f"{role} band lightened {v} -> {b} (hue kept) so it separates from "
                         f"the header band")
        sem_band[role] = b

    # 0-5 score ramp. Built from the PALE system colours — tinting a near-black brand red
    # gives grey, and a grey scorecard tells the reader nothing.
    ramp = {
        "0": sem_light["error"], "1": sem_light["error"],
        "2": sem_light["warning"], "3": sem_light["warning"],
        "4": sem_light["success"], "5": blend(sem_light["success"], sem["success"], 0.22),
    }

    # charts — accent, accent_fill, remaining chromatics, then a neutral ramp descending
    series, seen = [], set()
    for c in [accent, accent_fill] + chromatics:
        if c and c not in seen:
            series.append(c); seen.add(c)
    for n in sorted(neutrals, key=lstar):
        if n not in seen and 22 < lstar(n) < 90:
            series.append(n); seen.add(n)
    series = series[:6]
    for i in range(1, len(series)):
        if abs(lstar(series[i]) - lstar(series[i - 1])) < 15:
            notes.append(f"chart series {i} and {i + 1} differ by <15 L* — they will merge in "
                         f"greyscale; reorder or replace one")
            break

    body_font = clean_font(fonts[0]) if fonts else "Calibri"
    head_font = body_font
    for f in fonts:
        c = clean_font(f)
        if c.lower() != body_font.lower():
            head_font = c
            break

    return {
        "brand": brand,
        "short": short or brand,
        "source": tok.get("site", ""),
        "colors": {
            "ink": ink, "muted": muted, "accent": accent, "accent_fill": accent_fill,
            "band_fill": band_fill, "band_text": band_text,
            "header_fill": header_fill, "zebra": zebra, "callout": callout,
            "hairline": hairline, "rule": rule, "on_band_accent": on_band_accent,
            "on_band_muted": on_band_muted,
        },
        "semantic": sem,
        "semantic_light": sem_light,
        "semantic_band": sem_band,
        "score_ramp": ramp,
        "chart": series,
        "font": {
            "brand": body_font, "brand_heading": head_font,
            "fallback": fallback_for(body_font),
            "fallback_heading": fallback_for(head_font),
        },
        "type": read_type(tok, body_font, head_font),
        "notes": notes,
    }


# --------------------------------------------------------------- checking
CHECKS = [
    ("ink on white", lambda c, s: contrast(c["ink"], WHITE), ">=", 12),
    ("muted on white", lambda c, s: contrast(c["muted"], WHITE), ">=", 4.5),
    ("accent on white", lambda c, s: contrast(c["accent"], WHITE), ">=", 4.5),
    ("band_text on band_fill", lambda c, s: contrast(c["band_text"], c["band_fill"]), ">=", 7),
    ("text on accent_fill", lambda c, s: max(contrast(c["ink"], c["accent_fill"]),
                                          contrast(c["band_text"], c["accent_fill"])), ">=", 4.5),
    ("ink on callout", lambda c, s: contrast(c["ink"], c["callout"]), ">=", 7),
    ("ink on header_fill", lambda c, s: contrast(c["ink"], c["header_fill"]), ">=", 7),
    ("zebra vs white", lambda c, s: contrast(c["zebra"], WHITE), "<=", 1.06),
    ("on_band_accent on band", lambda c, s: contrast(c["on_band_accent"], c["band_fill"]),
     ">=", 4.5),
    ("rule vs white", lambda c, s: contrast(c["rule"], WHITE), ">=", 1.5),
    ("on_band_muted on band", lambda c, s: contrast(c["on_band_muted"], c["band_fill"]),
     ">=", 4.5),
    ("header_fill vs white", lambda c, s: contrast(c["header_fill"], WHITE), "<=", 1.30),
    ("error on white", lambda c, s: contrast(s["error"], WHITE), ">=", 4.5),
    ("verdict band vs header band", lambda c, s: min(
        contrast(s.get("_band_" + k, s[k]), c["band_fill"]) for k in
        ("error", "warning", "success")), ">=", 2.2),
    ("warning on white", lambda c, s: contrast(s["warning"], WHITE), ">=", 4.5),
    ("success on white", lambda c, s: contrast(s["success"], WHITE), ">=", 4.5),
]


def check(theme):
    c = theme["colors"]
    s = dict(theme["semantic"])
    for k, v in (theme.get("semantic_band") or {}).items():
        s["_band_" + k] = v
    fails = 0
    print(f"\ncontrast — {theme.get('brand','')}")
    for label, fn, op, target in CHECKS:
        v = fn(c, s)
        ok = v >= target if op == ">=" else v <= target
        fails += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label:<26} {v:6.2f}:1  (need {op} {target})")
    ls = [lstar(x) for x in theme["chart"]]
    for i in range(1, len(ls)):
        if abs(ls[i] - ls[i - 1]) < 15:
            print(f"  WARN  chart series {i}/{i+1} differ by {abs(ls[i]-ls[i-1]):.0f} L* "
                  f"(<15 — merges in greyscale)")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens", nargs="?", help="tokens.json from extract_tokens.js")
    ap.add_argument("--check", metavar="THEME", help="check an existing theme instead")
    ap.add_argument("--brand", default="")
    ap.add_argument("--short", default="")
    ap.add_argument("--out")
    a = ap.parse_args()

    if a.check:
        with open(a.check) as f:
            t = json.load(f)
        sys.exit(1 if check(t) else 0)

    if not a.tokens:
        ap.error("give tokens.json, or --check theme.json")
    with open(a.tokens) as f:
        raw = f.read()
    tok = json.loads(raw)
    if isinstance(tok, str):          # browser tools return a JSON string
        tok = json.loads(tok)

    theme = build_theme(tok, a.brand, a.short)
    out = a.out or "theme.json"
    with open(out, "w") as f:
        json.dump(theme, f, indent=1)

    print(f"wrote {out}")
    print(json.dumps({**theme["colors"], **{"semantic": theme["semantic"]},
                      "chart": theme["chart"], "font": theme["font"]}, indent=1))
    for n in theme["notes"]:
        print(f"  note: {n}")
    check(theme)
    print("\nReview the roles above against references/role-mapping.md before rendering.")


if __name__ == "__main__":
    main()
