# report.json — schema for `scripts/build_report.py`

Read this before writing `report.json`. The builder rejects a file that is missing any of the 10 skeleton sections.

## Top level

```json
{
  "lang": "en",                       // "en" (default) or "fr" — localises headings, legend, captions prefix
  "meta": {
    "title": "The software layer of <sector> in <geography>",
    "subtitle": "Market depth, value distribution, players, customer segments and the 5 trends to 2035",
    "kicker": "MARKET DEEP DIVE · PRELIMINARY REPORT",   // optional
    "project": "<optional project / mandate name>",
    "version": "Version 1",
    "date": "<today, written out>",
    "author": "<user's name>",
    "footer": "<short title for the page footer>",
    "fx_note": "FX used: 1.10 $/€."                      // optional, appended to the confidence legend
  },
  "kpis": [ {"value": "€1,600bn", "label": "Total market\n(geo, year)"} ],   // 8 tiles on the cover (4x2)
  "kpis_title": "The market in 8 numbers",
  "kpis_source": "Publisher A, Publisher B — details and confidence in the report",
  "sections": { "summary": {...}, "scope": {...}, "value_chain": {...}, "depth_growth": {...},
                "demand": {...}, "players": {...}, "moves": {...}, "segments": {...},
                "trends": {...}, "implications": {...} },
  "sources": [ "Publisher — Title (date) — URL", "..." ]
}
```

Each section: `{"heading": "<optional override>", "blocks": [ ... ]}`. Omit `heading` to use the localised default.

## Blocks

| type | fields | use |
|---|---|---|
| `paragraph` | `text`, optional `lead` (bold run-in) | Prose. End factual sentences with a confidence tag `[A]`/`[B]`/`[C]`. |
| `note` | `text` | Small grey italic caveat under a table or exhibit. |
| `heading` | `text`, `level` (2 or 3) | Sub-section. |
| `bullets` | `items`: strings or `["Bold lead — ", "rest"]`; `numbered` | Lists. |
| `callout` | `title`, `items` (strings) | Blue box: key findings, first-principles reading. |
| `table` | `header`, `rows`, `widths` (cm, sum ≈ 17), `size` (pt, default 8.3) | Player tables, sizing tables, gap table. |
| `exhibit` | `chart` (spec below), `caption`, `width` (cm, default 17) | Every chart. Numbered automatically. |
| `page_break` | — | Avoid. The builder already breaks after the cover, the summary and before the annex. |

## Chart specs (`exhibit.chart`)

Common fields: `type`, `id` (unique, used as filename), `title` (**the insight, as a sentence**), `subtitle`, `source`.
Colours are slot indexes into the validated palette (0 blue, 1 orange, 2 aqua, 3 yellow, 4 magenta, 5 green, 6 violet, 7 red) or `"neutral"` (grey). Keep one meaning per colour within a chart; name it in `legend`.

| type | required fields | optional | typical exhibit |
|---|---|---|---|
| `hbar` | `labels`, `values` | `colors`, `fmt` (e.g. `"{:.1f} %"`), `log`, `xlabel`, `legend` `[[label, colour]]`, `note` `{text,x,y,ha,box}`, `height` | Value pools (log), margins by link, CAGR comparison, top vendors |
| `bars` | `labels`, `values` | `colors`, `fmt`, `xlabel`, `ylabel`, `legend`, `note` | Firm-size distribution |
| `grouped_bars` | `categories`, `series` `[{name, values, color}]` (null = gap) | `fmt`, `ylabel`, `note` | Segment size year A vs year B; adoption vs benchmark |
| `line_forecast` | `series` `[{name, x, y, forecast_from, label_at, color}]` | `ylabel`, `ymax`, `fmt`, `note` | Installed base / market size, actual solid + forecast dashed |
| `dotplot` | `points` `[{label, value, color}]` | `fmt`, `xlabel` | **Mandatory**: dispersion of sizing estimates across sources |
| `deals` | `deals` `[{x (year.fraction), value, label, cat, dx, dy}]` | `categories`, `ylabel`, `undisclosed` (text) | M&A map, log scale |
| `position_map` | `points` `[{name, x 0–10, y 0–10, cat, highlight, dx, dy}]`, `xlabel`, `ylabel` | `quadrants` `{tl,tr,bl,br}`, `categories` | Positioning map — always tagged [C] in subtitle |
| `heatmap` | `columns`, `rows` `[[player, [0–3,...]]]` | — | Players × customer segments (0 none … 3 core) |
| `timeline` | `events` `[{x, date, text, cat}]` | `categories` | Regulatory / technology calendar |
| `stacked_share` | `bars` `[{label, parts: [[name, value, colour]]}]` | `xlabel`, `note` | Composition (channels, networks) |
| `panels` | `panels` `[{title, labels, values, colors, fmt}]` | `height` | Two related measures side by side (**never a dual axis**) |
| `tiles` | `items` `[{value, label}]` | `cols`, `color` | Hero numbers (cover KPIs are built automatically from `kpis`) |

## Minimal example of one section

```json
"depth_growth": {"blocks": [
  {"type": "exhibit", "caption": "Consensus sizes, software only.",
   "chart": {"type": "grouped_bars", "id": "e03_sizes",
             "title": "A ~€8bn software market that adds ~€5bn by 2030",
             "subtitle": "Consensus estimate by segment, software only",
             "source": "Publisher A (2025); Publisher B; our calculations [B]",
             "categories": ["Segment 1", "Segment 2"],
             "series": [{"name": "2025", "values": [4.5, 1.6], "color": 0},
                        {"name": "2030", "values": [7.3, 2.8], "color": 1}],
             "fmt": "€{:.1f}bn", "ylabel": "€ billions"}},
  {"type": "table", "header": ["Segment", "2025", "2030", "CAGR", "Basis / confidence"],
   "rows": [["Segment 1", "≈ €4.5bn", "≈ €7.3bn", "10%", "Publisher A, units × ARPU [B]"]],
   "widths": [3.6, 2.6, 2.6, 1.6, 6.6]}
]}
```
