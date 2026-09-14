# doc.json schema

`build_product_doc.py` renders this. **Every top-level key is optional** — omit it and the section
disappears. That's deliberate, and it's why the same renderer serves `/productdd` (verdict +
scorecard + evidence) and `/valuecreation` (levers + 90-day plan): the two documents differ in
content, not in typography.

```jsonc
{
  "company": "Acme Ops",
  "classification": "Series A · vertical SaaS",   // sits next to the name in the band
  "doc_label": "Product due diligence",           // or "Value-creation plan"
  "header": {
    "product": "Field-ops workflow platform",
    "stage": "Series A", "round": "€12m", "ask": "€4m ticket",
    "arr": "€2.4m ARR [A]", "customers": "~310 accounts",
    "hq": "Lyon, France", "date": "8 September 2026"
  },

  // Coloured band, top of page 1. The call before the analysis.
  // call: Invest | Conditional | Pass  (colour is chosen from this word)
  "verdict": {
    "call": "Conditional",
    "conviction": "Medium",
    "one_liner": "One sentence. Why this call, not the adjacent one."
  },

  "the_read": ["Judgement, not summary. 3–5 bullets, ≤2 lines each."],

  "scorecard": {
    "title": "Product scorecard",
    "rows": [
      {"module": "PMF evidence", "score": 2, "weight": 3,
       "finding": "One line. The evidence, not the adjective.", "confidence": "[A]"}
    ],
    "total_note": "Read against the fund's bar — say what the bar is.",
    "caption": "optional"
  },

  // The analytical body. Order them yourself; 3–5 is the working range.
  "sections": [
    {
      "heading": "Product-market fit evidence",
      "prose": "≤4 sentences.",
      "bullets": ["plain string", {"point": "Bold claim.", "evidence": "muted proof [A]"}],
      "table": {"columns": ["..."], "rows": [["..."]], "caption": "..."},
      "tables": [],
      "so_what": "One italic line. The implication, not a restatement."
    }
  ],

  "red_flags": [
    {"flag": "Short name.", "severity": "high",        // high | medium | low
     "evidence": "Sized, sourced, tagged [A].",
     "mitigation": "What would change our mind — testable."}
  ],

  "open_questions": ["Phrased as you'd actually ask it in the room."],
  "questions_heading": "Questions for management",     // optional override

  "exhibits": [
    {
      "id": "A", "title": "Cohort retention",
      "prose": "optional intro",
      "chart": { /* one chart */ },
      "charts": [ /* or several */ ],
      "bullets": [], "table": {}, "tables": [],
      "notes": "Method, workings, caveats. Always state the method for computed exhibits."
    }
  ],

  "confidence_note": "optional override of the default footer legend"
}
```

## Chart types

| type | Use for | Shape |
|---|---|---|
| `line` | Retention curves, trends. Optional `"floor": 40` draws the claimed plateau | `x`, one `series` per line |
| `heatmap` | Cohort retention triangle | `y` = cohort labels, `matrix` = rows of %, ragged rows fine |
| `waterfall` | NRR bridge — first and last bars are terminal, middle bars float | one `series`, values `[base, +exp, −contr, −churn, ending]` |
| `bar` / `grouped_bar` | Metric over time, peers side by side | `x` = categories |
| `barh` | Ranked comparison | `x` = labels, one series |

`/cohortlab` emits `charts.logo_heatmap`, `charts.revenue_heatmap`, `charts.retention_curve` and
`charts.nrr_bridge` already in this shape — paste them straight into an exhibit.

Charts live in exhibits, never in the memo body: at memo density a table reads faster.

## Rules that keep the document trustworthy

- Every figure carries `[A]`, `[B]` or `[C]`, inline in the cell text.
- Never invent a number, a customer name, or a competitor's metric. `"not disclosed"` is a finding.
- Computed exhibits state their method in `notes`. A cohort chart without a stated definition of
  "active" is decoration.
- The last exhibit is always the source log: claim → source → date → tag.

## Added chart types and the data-gaps appendix

| type | Use for | Shape |
|---|---|---|
| `pyramid` | Market pyramid, apex = few actors / most value | `tiers: [{label, actors, value}]`, apex first |
| `positioning` | Competitive map | `points: [{name, x, y, size, highlight}]`, `xlabel`, `ylabel`, `quadrants: [TL, TR, BL, BR]`, axes 0–10 |

```jsonc
"data_gaps": [
  {"priority": 1, "what": "Customer × month revenue export, 36 months",
   "why": "PMF evidence, Segmentation — moves [B] to [A]",
   "from_whom": "CFO / RevOps", "how": "Data-room request; template supplied",
   "status": "requested 8 Sep"}
],
"data_gaps_intro": "optional override of the appendix intro line"
```

## Citing so the evidence gate can check you

`scripts/validate_doc.py` runs before the builder and fails the render if a claim can't be traced.
It works on **evidence units** — a table row, a scorecard row, a bullet, a paragraph — not on
individual cells, so a financials table needs the tag on the row label or in the caption, not in
every cell.

Give each source-log row a short id in its first column and cite it inline:

| Prefix | For |
|---|---|
| `S-01` | a document you hold (filing, invoice, contract, data-room file) |
| `I-01` | an interview (matches the `/interviewlog` ids) |
| `P-01` | a published source (press, analyst, registry page) |

`FY24 revenue €5.14m [A, S-03]` — the tag says how good the evidence is, the id says which
artifact. Either satisfies the gate; both is the standard. The gate also warns when a logged
source is never cited, which usually means research you did and then forgot to use.
