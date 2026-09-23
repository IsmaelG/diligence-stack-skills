"""marketdd chart library — renders JSON chart specs to PNG (matplotlib).

Every chart is a dict with at least: {"type", "id", "title"} and optional "subtitle", "source".
Titles should state the insight ("Software grows 6x faster than the activity it runs"),
not the topic ("Growth rates").

Supported types (see references/report-schema.md for the exact fields):
  tiles, hbar, bars, grouped_bars, line_forecast, dotplot, deals, position_map,
  heatmap, timeline, stacked_share, panels

Usage as a module:  render(spec, out_dir, lang) -> path to PNG
Usage as a CLI:     python3 charts.py specs.json out_dir [--lang en|fr]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap

# Validated categorical palette (fixed order, never cycled) + neutrals
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
NEUTRAL = "#b9b8b2"
INK, INK2, MUTED, GRID, SURF, TILE = "#0b0b0b", "#52514e", "#8a8983", "#e6e5e0", "#ffffff", "#f4f3ef"
SEQ = ["#cde2fb", "#9ec5f4", "#5598e7", "#256abf", "#104281"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False,
})

WORDS = {"en": {"source": "Source: ", "actual": "— actual   - - forecast", "legend_heat":
                "●● core target · ● secondary · · opportunistic · blank = not addressed"},
         "fr": {"source": "Source : ", "actual": "— réel   - - prévision", "legend_heat":
                "●● cœur de cible · ● cible secondaire · · opportuniste · vide = non adressé"}}


def col(i):
    """Colour by slot index; strings pass through (hex or 'neutral')."""
    if isinstance(i, str):
        return NEUTRAL if i == "neutral" else i
    return C[i % len(C)]


def _finish(fig, spec, out, lang, tight=True):
    h = fig.get_figheight()
    fig.text(0.01, 1 - 0.08 / h, spec["title"], ha="left", va="top", fontsize=12.5, fontweight="bold", color=INK)
    top = 1 - 0.42 / h
    if spec.get("subtitle"):
        fig.text(0.01, 1 - 0.36 / h, spec["subtitle"], ha="left", va="top", fontsize=9, color=INK2)
        top = 1 - 0.66 / h
    bot = 0.25 / h if spec.get("source") else 0.02
    if spec.get("source"):
        fig.text(0.01, 0.06 / h, WORDS[lang]["source"] + spec["source"], ha="left", fontsize=7.3, color=MUTED)
    if tight:
        fig.tight_layout(rect=(0, bot, 1, top))
    else:
        fig.subplots_adjust(left=0.01, right=0.99, top=top, bottom=bot + 0.02, wspace=0.06, hspace=0.12)
    path = Path(out) / f"{spec['id']}.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def _legend(ax, legend, loc="lower right"):
    if legend:
        ax.legend(handles=[Patch(color=col(c), label=l) for l, c in legend], loc=loc)


def _note(ax, spec):
    n = spec.get("note")
    if n:
        ax.text(n.get("x", 0.98), n.get("y", 0.1), n["text"], transform=ax.transAxes,
                ha=n.get("ha", "right"), fontsize=8.8, color=INK,
                bbox=dict(fc="#fdf0ea", ec=C[1], lw=0.8, boxstyle="round,pad=0.4") if n.get("box") else None)


def _fmt(v, fmt):
    return fmt.format(v)


# ---------------------------------------------------------------- types
def tiles(spec, out, lang):
    items = spec["items"]
    cols = spec.get("cols", min(4, len(items)))
    rows = int(np.ceil(len(items) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(10, 1.65 * rows + 0.3 + (0.3 if spec.get("source") else 0)))
    axs = np.atleast_1d(axs).flatten()
    for ax in axs:
        ax.axis("off")
    for ax, it in zip(axs, items):
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=TILE, zorder=0))
        ax.text(0.07, 0.56, it["value"], fontsize=17, fontweight="bold", color=col(spec.get("color", 0)), transform=ax.transAxes)
        ax.text(0.07, 0.12, it["label"], fontsize=8, color=INK2, transform=ax.transAxes, linespacing=1.3, wrap=True)
    return _finish(fig, spec, out, lang, tight=False)


def hbar(spec, out, lang):
    labels, vals = spec["labels"], spec["values"]
    colors = [col(c) for c in spec.get("colors", [0] * len(vals))]
    fig, ax = plt.subplots(figsize=(10, spec.get("height", 0.45 * len(vals) + 1.4)))
    y = np.arange(len(labels))[::-1]
    ax.barh(y, vals, color=colors, height=0.62, edgecolor=SURF, linewidth=1.5)
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.grid(axis="y", visible=False)
    fmt = spec.get("fmt", "{:,.0f}")
    if spec.get("log"):
        ax.set_xscale("log")
        for yi, v in zip(y, vals):
            ax.text(v * 1.12, yi, _fmt(v, fmt), va="center", fontsize=8.8)
        ax.set_xlim(min(vals) * 0.6, max(vals) * 4)
    else:
        m = max(vals)
        for yi, v in zip(y, vals):
            ax.text(v + m * 0.012, yi, _fmt(v, fmt), va="center", fontsize=8.8)
        ax.set_xlim(0, m * 1.15)
    ax.set_xlabel(spec.get("xlabel", ""))
    _legend(ax, spec.get("legend"), spec.get("legend_loc", "lower right"))
    _note(ax, spec)
    return _finish(fig, spec, out, lang)


def bars(spec, out, lang):
    """Simple vertical bars (e.g. distribution by size class)."""
    labels, vals = spec["labels"], spec["values"]
    colors = [col(c) for c in spec.get("colors", [0] * len(vals))]
    fig, ax = plt.subplots(figsize=(10, spec.get("height", 3.8)))
    b = ax.bar(labels, vals, color=colors, edgecolor=SURF, linewidth=1.5, width=0.6)
    fmt = spec.get("fmt", "{:,.0f}"); m = max(vals)
    for bi, v in zip(b, vals):
        ax.text(bi.get_x() + bi.get_width() / 2, v + m * 0.02, _fmt(v, fmt), ha="center", fontsize=8.5)
    ax.set_ylim(0, m * 1.18); ax.grid(axis="x", visible=False)
    ax.set_ylabel(spec.get("ylabel", "")); ax.set_xlabel(spec.get("xlabel", ""))
    _legend(ax, spec.get("legend"), spec.get("legend_loc", "upper right"))
    _note(ax, spec)
    return _finish(fig, spec, out, lang)


def grouped_bars(spec, out, lang):
    cats, series = spec["categories"], spec["series"]  # series: [{name, values, color}]
    n = len(series); w = 0.8 / n; x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(10, spec.get("height", 4)))
    fmt = spec.get("fmt", "{:,.1f}")
    m = max(v for s in series for v in s["values"] if v is not None)
    for k, s in enumerate(series):
        xs = [xi + (k - (n - 1) / 2) * w for xi, v in zip(x, s["values"]) if v is not None]
        vs = [v for v in s["values"] if v is not None]
        ax.bar(xs, vs, w, color=col(s.get("color", k)), label=s["name"], edgecolor=SURF, linewidth=1.5)
        for xi, v in zip(xs, vs):
            ax.text(xi, v + m * 0.02, _fmt(v, fmt), ha="center", fontsize=8.3)
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=8.8); ax.grid(axis="x", visible=False)
    ax.set_ylim(0, m * 1.2); ax.set_ylabel(spec.get("ylabel", ""))
    ax.legend(loc=spec.get("legend_loc", "upper right"))
    _note(ax, spec)
    return _finish(fig, spec, out, lang)


def line_forecast(spec, out, lang):
    """Actuals solid, forecast dashed. series: [{name, x, y, forecast_from, color}]"""
    fig, ax = plt.subplots(figsize=(10, spec.get("height", 3.9)))
    for k, s in enumerate(spec["series"]):
        x, y = s["x"], s["y"]; f = s.get("forecast_from")
        c = col(s.get("color", k))
        if f is not None and f in x:
            i = x.index(f)
            ax.plot(x[:i + 1], y[:i + 1], color=c, lw=2.2, marker="o", ms=5, label=s["name"])
            ax.plot(x[i:], y[i:], color=c, lw=2.2, ls="--", marker="o", ms=5, mfc=SURF)
        else:
            ax.plot(x, y, color=c, lw=2.2, marker="o", ms=5, label=s["name"])
        for xi, yi in zip(x, y):
            if xi in s.get("label_at", [x[0], x[-1]]):
                ax.text(xi, yi * 1.04 + 0.01 * max(y), _fmt(yi, spec.get("fmt", "{:,.1f}")), ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, spec.get("ymax", max(max(s["y"]) for s in spec["series"]) * 1.2))
    ax.set_ylabel(spec.get("ylabel", "")); ax.set_xticks(spec["series"][0]["x"])
    if len(spec["series"]) > 1:
        ax.legend(loc="upper left")
    ax.text(0.01, 0.95, WORDS[lang]["actual"], transform=ax.transAxes, fontsize=8, color=INK2)
    _note(ax, spec)
    return _finish(fig, spec, out, lang)


def dotplot(spec, out, lang):
    """Dispersion of estimates for the same quantity. points: [{label, value, color}]"""
    pts = spec["points"]
    fig, ax = plt.subplots(figsize=(10, 0.5 * len(pts) + 1.3))
    y = np.arange(len(pts))[::-1]; vals = [p["value"] for p in pts]
    ax.hlines(y, 0, vals, color=GRID, lw=2)
    ax.scatter(vals, y, s=90, color=[col(p.get("color", 0)) for p in pts], zorder=3, edgecolor=SURF, linewidth=2)
    fmt = spec.get("fmt", "{:,.2f}")
    for yi, v in zip(y, vals):
        ax.text(v + max(vals) * 0.03, yi, _fmt(v, fmt), va="center", fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels([p["label"] for p in pts]); ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(vals) * 1.22); ax.set_xlabel(spec.get("xlabel", ""))
    return _finish(fig, spec, out, lang)


def deals(spec, out, lang):
    """M&A map: x = year (float), y = value (log), bubble ~ value. deals: [{x, value, label, cat, dx, dy}]"""
    fig, ax = plt.subplots(figsize=(10, spec.get("height", 4.8)))
    vals = [d["value"] for d in spec["deals"]]
    for d in spec["deals"]:
        v = d["value"]
        ax.scatter(d["x"], v, s=40 + v / max(vals) * 180, color=col(d.get("cat", 0)), alpha=0.9, edgecolor=SURF, linewidth=2, zorder=3)
        ax.text(d["x"] + d.get("dx", 0), v * d.get("dy", 1.18), d["label"], fontsize=7.3, ha="center", color=INK)
    ax.set_yscale("log"); ax.set_ylim(min(vals) * 0.6, max(vals) * 2.4)
    xs = [d["x"] for d in spec["deals"]]; ax.set_xlim(int(min(xs)), int(max(xs)) + 1)
    ax.set_ylabel(spec.get("ylabel", ""))
    for i, name in enumerate(spec.get("categories", [])):
        ax.scatter([], [], color=col(i), label=name, s=50)
    if spec.get("categories"):
        ax.legend(loc="lower right")
    if spec.get("undisclosed"):
        ax.text(0.01, 0.03, spec["undisclosed"], transform=ax.transAxes, fontsize=7.5, color=INK2)
    return _finish(fig, spec, out, lang)


def position_map(spec, out, lang):
    """2x2 map (analyst judgement). points: [{name, x, y, cat, highlight}], axes 0-10."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for p in spec["points"]:
        hl = p.get("highlight", False)
        ax.scatter(p["x"], p["y"], s=110 if hl else 60, color=col(p.get("cat", 0)),
                   edgecolor=INK if hl else SURF, linewidth=1.4 if hl else 2, zorder=3)
        ax.text(p["x"] + 0.13 + p.get("dx", 0), p["y"] + 0.12 + p.get("dy", 0), p["name"], fontsize=8,
                fontweight="bold" if hl else "normal", color=INK)
    ax.axvline(5, color=GRID, lw=1.2); ax.axhline(5, color=GRID, lw=1.2)
    ax.set_xlim(0, 11.2); ax.set_ylim(0, 10.4); ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(spec["xlabel"]); ax.set_ylabel(spec["ylabel"])
    q = spec.get("quadrants", {})  # keys: tl, tr, bl, br
    pos = {"tl": (0.2, 10.2, "top"), "tr": (5.3, 10.2, "top"), "bl": (0.2, 0.2, "bottom"), "br": (7.0, 0.2, "bottom")}
    for k, txt in q.items():
        x, y, va = pos[k]
        ax.text(x, y, txt, fontsize=8.5, color=MUTED, va=va, style="italic")
    for i, name in enumerate(spec.get("categories", [])):
        ax.scatter([], [], color=col(i), label=name, s=50)
    if spec.get("categories"):
        ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93))
    return _finish(fig, spec, out, lang)


def heatmap(spec, out, lang):
    """Players x customer segments, intensity 0-3. rows: [[name, [v...]]]"""
    segs, rows = spec["columns"], spec["rows"]
    M = np.array([r[1] for r in rows])
    cmap = ListedColormap([TILE, SEQ[0], SEQ[2], SEQ[4]])
    fig, ax = plt.subplots(figsize=(10, 0.36 * len(rows) + 1.6))
    ax.imshow(M, cmap=cmap, vmin=0, vmax=3, aspect="auto")
    ax.set_xticks(range(len(segs))); ax.set_xticklabels(segs, fontsize=8); ax.xaxis.tick_top()
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(segs)), minor=True); ax.set_yticks(np.arange(-.5, len(rows)), minor=True)
    ax.grid(which="minor", color=SURF, linewidth=2.5); ax.tick_params(which="minor", length=0)
    mark = {0: "", 1: "·", 2: "●", 3: "●●"}
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, mark[int(M[i, j])], ha="center", va="center", fontsize=8, color=SURF if M[i, j] == 3 else INK)
    fig.text(0.01, 0.3 / fig.get_figheight(), WORDS[lang]["legend_heat"], fontsize=8, color=INK2)
    return _finish(fig, spec, out, lang)


def timeline(spec, out, lang):
    """events: [{x (float year), date, text, cat}]"""
    ev = spec["events"]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.axhline(0, color=INK2, lw=1.5)
    for i, e in enumerate(ev):
        up = 1 if i % 2 == 0 else -1
        c = col(e.get("cat", 0))
        ax.vlines(e["x"], 0, 0.55 * up, color=c, lw=1.5)
        ax.scatter(e["x"], 0, s=60, color=c, zorder=3, edgecolor=SURF, linewidth=2)
        ax.text(e["x"], 0.62 * up, f"{e['date']}\n{e['text']}", ha="center", va="bottom" if up > 0 else "top", fontsize=8)
    xs = [e["x"] for e in ev]
    ax.set_ylim(-1.6, 1.6); ax.set_xlim(min(xs) - 0.7, max(xs) + 0.8); ax.axis("off")
    for i, name in enumerate(spec.get("categories", [])):
        ax.scatter([], [], color=col(i), label=name)
    if spec.get("categories"):
        ax.legend(loc="lower right", ncol=len(spec["categories"]))
    return _finish(fig, spec, out, lang)


def stacked_share(spec, out, lang):
    """One or more horizontal 100%/absolute stacked bars. bars: [{label, parts: [[name, value, color]]}]"""
    bars_ = spec["bars"]
    fig, ax = plt.subplots(figsize=(10, 0.7 * len(bars_) + 1.6))
    for i, b in enumerate(bars_[::-1]):
        left = 0
        for name, v, c in b["parts"]:
            ax.barh([i], [v], left=[left], color=col(c), height=0.55, edgecolor=SURF, linewidth=2)
            ax.text(left + v / 2, i, f"{name}", ha="center", va="center", color=SURF, fontweight="bold", fontsize=8.5)
            left += v
    ax.set_yticks(range(len(bars_))); ax.set_yticklabels([b["label"] for b in bars_[::-1]])
    ax.grid(axis="y", visible=False); ax.set_xlabel(spec.get("xlabel", ""))
    _note(ax, spec)
    return _finish(fig, spec, out, lang)


def panels(spec, out, lang):
    """Side-by-side small multiples of simple bars (never a dual axis).
    panels: [{title, labels, values, colors, fmt}]"""
    ps = spec["panels"]
    fig, axs = plt.subplots(1, len(ps), figsize=(10, spec.get("height", 3.7)))
    for ax, p in zip(np.atleast_1d(axs), ps):
        vals = p["values"]; m = max(vals)
        b = ax.bar(p["labels"], vals, color=[col(c) for c in p.get("colors", [0] * len(vals))], width=0.55, edgecolor=SURF, linewidth=1.5)
        for bi, v in zip(b, vals):
            ax.text(bi.get_x() + bi.get_width() / 2, v + m * 0.03, _fmt(v, p.get("fmt", "{:,.0f}")), ha="center", fontsize=8.8)
        ax.set_ylim(0, m * 1.2); ax.grid(axis="x", visible=False)
        ax.set_title(p["title"], loc="left", fontsize=9.5, color=INK2)
    return _finish(fig, spec, out, lang)


TYPES = {f.__name__: f for f in [tiles, hbar, bars, grouped_bars, line_forecast, dotplot, deals,
                                  position_map, heatmap, timeline, stacked_share, panels]}


def render(spec, out_dir, lang="en"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    t = spec["type"]
    if t not in TYPES:
        raise ValueError(f"Unknown chart type '{t}'. Supported: {sorted(TYPES)}")
    return TYPES[t](spec, out_dir, lang)


if __name__ == "__main__":
    specs = json.load(open(sys.argv[1]))
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
    for s in (specs if isinstance(specs, list) else [specs]):
        print(render(s, sys.argv[2], lang))
