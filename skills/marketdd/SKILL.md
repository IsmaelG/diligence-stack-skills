---
name: marketdd
description: Market due diligence — a sourced, chart-heavy deep dive on a whole sector or software category in a given geography, delivered as a Word report plus PDF. Covers market depth and growth, how value is split along the value chain, the players in each segment, M&A and capital moves, the customer segments each player targets, and the 5 customer trends for the next 5–10 years, with every figure confidence-tagged. Use this skill whenever the user says "marketdd", "market DD", "market due diligence", "market deep dive", "market map", "sector study", or asks to size a market, map the players or the value chain, list the vendors active in a space, or understand where a market is heading — and run it automatically from /duediligence when the target's market has no recent market report. English by default; French when the user asks for it.
---

# Market Due Diligence (/marketdd)

Produce a first market report a principal can use to understand a sector in depth before an M&A, investment or strategy decision: **the numbers that matter, where the value sits, who plays where, who they sell to, and what will move the market over the next 5–10 years.**

The method borrows from long-form "first principles" deep dives: start from the physical activity and the money, climb to the software layer, then to the players and the forces that move them. Every exhibit title states an insight, not a topic. The rigour comes from the diligence stack: every number carries a source and an `[A]/[B]/[C]` confidence tag, and what we could not find is reported as a finding.

## Inputs to settle first

Ask only what you cannot infer (use the question tool when available, one round):

1. **Market perimeter** — the sector or software category, and how wide (e.g. only the core system, or also adjacent tools). Propose a broad and a narrow option.
2. **Geography** — default: the region the user works in.
3. **Mandate** — standalone market study, or context for a target/deal (then section 10 links back to it).
4. **Language** — **English by default**; French if the user asks ("en français", "in French", `lang=fr`). Do not switch language just because the user writes in another language — ask if unsure.

When called from `/duediligence`, skip the questions: perimeter = the target's primary market, geography = its home region, mandate = the target, language = the language of the memo.

## Output

`<OUTPUT_DIR>/<SECTOR>_marketdd.docx` and `<SECTOR>_marketdd.pdf`, where `<OUTPUT_DIR>` is the same output folder `/duediligence` uses (or the folder the user named for the project). `SECTOR` is short, uppercase, underscores (`HR_SOFTWARE_EU_marketdd.docx`). If that folder is not reachable, write to the working folder and say where the files landed. Typical length 15–20 pages with 15–20 exhibits.

## The order of work matters

Research completely, *then* build. Budget ≈ 70 % research, 20 % argument, 10 % rendering.

### Step 1 — Research (four passes, in parallel if sub-agents exist)

Follow `references/sources.md` (source hierarchy, triangulation rules, per-section evidence checklist). The four passes:

1. **Sizing** — each software segment (global and regional), CAGR, installed base / penetration where unit-driven, structure statistics (number of buyers by size class, digital adoption vs all sectors).
2. **Players A** — the core category: vendors active in the geography, HQ, owner, scale, priority customer segment, analyst positioning (Magic Quadrant etc.), M&A.
3. **Players B** — adjacent / operational categories inside the perimeter: same fields.
4. **Value chain, trends, customers** — size of the underlying activity, turnover and margin per link, regulation calendar, technology adoption, customer segmentation, deal multiples, funding.

Non-negotiables:
- **Never invent a number.** No figure without a source you opened. Derived figures show the formula and are `[B]`; your assumptions are `[C]`.
- **Anchor + dispersion.** Pick one anchor source per segment (stable definition, regional split) and show every other estimate on a `dotplot` exhibit.
- **Global ≠ regional**, base year and currency always stated.
- Aim for **40+ named players** across segments; mark anything you could not verify.
- If the search budget runs out, stop, list what is unverified, and carry it into the "what we don't know" table.

### Step 2 — Structure the argument (the fixed skeleton)

The report always has these 10 sections, in this order (the builder enforces it):

| # | Key | What it must do | Core exhibits |
|---|---|---|---|
| 1 | `summary` | 1 paragraph thesis; callout "N findings in numbers" (7 max, each tagged); the 5 trends in one line each; one bold line on the implication | cover KPI tiles (8) |
| 2 | `scope` | Definitions table of every building block in the perimeter (what it does, typical buyer, examples); source list with tags | sizing-dispersion `dotplot` |
| 3 | `value_chain` | Size of each link from the underlying activity to the software layer; margins per link; a "first principles" callout on why value migrates | value pools `hbar` (log), margins `hbar` |
| 4 | `depth_growth` | Consensus size today and in 5 years per segment (table with basis/confidence); growth vs the underlying activity; installed base if relevant | `grouped_bars`, CAGR `hbar`, `line_forecast`, top-vendors `hbar` |
| 5 | `demand` | How many buyers, by size class, and their share of turnover; geography; digital adoption gap; demand drivers | `bars`, `hbar`, `grouped_bars`, `panels` |
| 6 | `players` | One table per segment: player, HQ, owner, scale, priority customer; analyst positioning table; positioning map | `position_map` [C] |
| 7 | `moves` | 3–5 capital patterns (roll-ups, PE platforms, non-software entrants, customers verticalising…); deal table | `deals`, multiples `hbar` |
| 8 | `segments` | Why the same activity has several software buyers; table per customer segment (size, what it buys, criterion #1, cycle & ticket [C], priority players) | players × segments `heatmap` |
| 9 | `trends` | Exactly **5 customer trends** for 5–10 years; each = dated facts + a number + "what it changes for the customer" bullets | one exhibit per trend (`timeline`, `grouped_bars`, `tiles`, `panels`, `stacked_share`) |
| 10 | `implications` | So-what for the mandate (or for new entrants if standalone); "what we don't know" table (question, why it matters, source to close it); next steps | — |

Writing rules:
- Declarative sentences; each factual sentence ends with its tag.
- Exhibit titles are claims ("Software captures under 2 % of the value it runs"), subtitles say what is plotted, sources are on the chart.
- Customer segments are defined by **who pays**, not by vertical buzzwords; for each player say which segment is its **core target** and which are opportunistic.
- Trends are **customer** trends (what buyers will need or be forced to do), not vendor features.
- Keep any company-, deal- or client-specific content in section 10 and in `meta.project`; sections 1–9 must stand on their own as a market study.

### Step 3 — Render

1. Write `report.json` (schema: `references/report-schema.md` — read it first). Chart specs sit inside `exhibit` blocks.
2. Render: `python3 scripts/build_report.py report.json --out <OUTPUT_DIR>/<SECTOR>_marketdd.docx`
   The script renders the charts (matplotlib, validated colour-blind-safe palette), builds the Word file, converts it to PDF with LibreOffice and prints the fill ratio of every page.
3. **Check the layout.** If the script prints `LAYOUT WARNING`, fix the cause (a manual `page_break`, an oversized table before an exhibit) and re-render. Then look at the pages: render them to images (`pdftoppm -r 40`) and inspect the charts for overlapping labels; adjust `dx`/`dy` on `deals` and `position_map` points or shorten labels, and re-render.
4. Deliver both files and summarise in 5–7 lines: the headline numbers, the 5 trends, and the 1–2 findings that change the user's framing.

Don't hand-roll python-docx or chart code — the scripts exist so every market report looks the same and tokens go to research.

## Chaining

- **From `/duediligence`**: runs automatically (no questions) when no `*_marketdd` report on the target's market younger than 6 months exists in the output folder. Its key numbers feed the memo's strategy section and competitor exhibit.
- **Into `/productdd` / `/technicaldd`**: the players table and positioning map give the competitive set; the segments heatmap gives the ICP to test.
- **Into `/onbrand`**: the Word file can be re-skinned like any other deliverable.

## Reference files

- `references/report-schema.md` — `report.json` structure, block types and the 12 chart types with their fields.
- `references/sources.md` — source hierarchy, tagging rules, triangulation, per-section evidence checklist, research-pass split.
- `scripts/build_report.py` — JSON → DOCX + PDF + layout check. Requires `python-docx`, `matplotlib`, `numpy`, `Pillow`, LibreOffice (`soffice`) and `pdftoppm` (poppler).
- `scripts/charts.py` — chart library (usable standalone: `python3 charts.py specs.json out_dir --lang fr`).
