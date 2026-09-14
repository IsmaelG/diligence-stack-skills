# memo.json schema

`build_memo.py` renders this into the Word memo. Every top-level key is optional — omit a section and it simply doesn't appear. That's deliberate: an empty section is worse than no section.

Keep the memo-body sections tight enough to land in two pages. Rough budget at the styling the script applies: **the read** ≤ 5 bullets, **snapshot** ≤ 8 rows, **comparison** ≤ 5 rows, **ownership** ≤ 6 rows, **leadership** ≤ 7 rows, **SWOT** ≤ 6 per quadrant. Push everything else into exhibits.

```jsonc
{
  "company": "Société Générale",
  "classification": "Listed · Euronext Paris",   // shown next to the name in the header band
  "header": {
    "legal_entity": "Société Générale S.A.",
    "ticker": "GLE.PA",
    "hq": "La Défense, France",
    "founded": "1864",
    "employees": "~119,000",
    "revenue": "€26.8bn NBI (FY2024) [A]",
    "date": "13 July 2026"
  },

  "the_read": [
    "Judgement, not summary. What you'd tell a colleague in the lift.",
    "4–5 bullets max, ≤2 lines each."
  ],

  // Mandatory. Renders as a highlighted 'LATEST ON DIGITAL' line closing The Read block.
  // The thing you could open the meeting with. Must be specific, dated, and consequential —
  // an acquisition, a platform shipped, a senior digital hire, an incident, an on-record target.
  // Not an award, not a rebrand, not a press release about innovation.
  "conversation_hook": {
    "headline": "SocGen sells Treezor to Shares — exiting owned BaaS",
    "date": "Jan 2026",
    "why_it_matters": "Third fintech disposal in two years. Confirms the pivot from building digital to buying distribution — worth asking whether BoursoBank is now the only digital bet.",
    "source": "Source: SG press release, 14 Jan 2026."
  },

  "snapshot": {
    "title": "Snapshot",                          // optional; defaults to 'Snapshot'
    "columns": ["Metric", "2022", "2023", "2024"],
    "rows": [
      ["Net banking income (€bn) [A]", "28.1", "25.1", "26.8"],
      ["Cost/income ratio [A]", "72%", "74%", "69%"]
    ],
    "caption": "Source: FY24 Universal Registration Document."
  },

  "strategy": {
    "prose": "2–4 sentences. Stated strategy vs revealed strategy, and where they sit in the value chain.",
    "comparison": {
      "columns": ["Player", "Scale", "Growth", "Positioning", "Key differentiator"],
      "rows": [["BNP Paribas", "...", "...", "...", "..."]],
      "caption": "Peer set as at FY2024."
    }
  },

  "ownership": {
    "table": {
      "columns": ["Holder", "Stake", "Type", "Note"],
      "rows": [["Employee shareholding", "7.1%", "Internal", "..."]]
    },
    "so_what": "One line: what this ownership structure makes the company do."
  },

  "leadership": {
    "table": {
      "columns": ["Name", "Role", "Since", "Prior", "Remit"],
      "rows": [["Slawomir Krupa", "CEO", "2023", "SG Americas", "Group"]]
    },
    "digital_owner": {
      "name": "Full name, or 'Not publicly identifiable'",
      "title": "Exact title",
      "reports_to": "CEO / COO / divisional head — this is a signal, don't skip it",
      "tenure": "Since 2024",
      "background": "Prior employer / discipline",
      "note": "One line on what they've shipped or said publicly."
    }
  },

  "swot": {
    // strengths/weaknesses: objects with evidence. This is the whole point.
    "strengths": [
      {"point": "Short claim.", "evidence": "The number/filing/hire that proves it [A]."}
    ],
    "weaknesses": [
      {"point": "Short claim.", "evidence": "Sized, not asserted [B]."}
    ],
    // opportunities/threats: plain strings, 3 each, external conditions
    "opportunities": ["..."],
    "threats": ["..."]
  },

  "open_questions": [
    "Phrase as a question you'd actually ask them in the room."
  ],

  "exhibits": [
    {
      "id": "A",
      "title": "Financial detail",
      "prose": "Optional intro.",
      "chart": {
        "type": "grouped_bar",              // bar | grouped_bar | line | barh | timeline
        "title": "Revenue vs operating profit (€bn)",
        "x": ["2022", "2023", "2024"],
        "series": [
          {"name": "Revenue", "values": [28.1, 25.1, 26.8]},
          {"name": "Operating profit", "values": [5.6, 3.2, 4.8]}
        ],
        "ylabel": "€bn",
        "source": "Source: FY24 URD."
      },
      "table": {"columns": ["..."], "rows": [["..."]]},
      "tables": [],                          // optional extra tables
      "notes": "Workings, caveats, how estimates were derived."
    }
  ],

  "confidence_note": "Optional override of the default footer legend."
}
```

## Chart types

| type | Use it for | Shape |
|---|---|---|
| `grouped_bar` / `bar` | Metric over 3 years, or peers side by side | `x` = categories, one `series` per measure |
| `line` | Trends with several series | same |
| `barh` | Ranked comparison (market share, peer size) | `x` = labels, one series |
| `timeline` | Funding rounds — plots amount per round with labels | `x` = round names, one series of amounts |

Charts live in exhibits, not in the 2-page memo — the memo has no room and tables read faster at that density.

## Rules that keep the doc trustworthy

- Every figure carries `[A]`, `[B]` or `[C]`. Put the tag inline in the cell text.
- Never fabricate a name. `"Not publicly identifiable"` is a legitimate, useful answer.
- The last exhibit should always be the **source log**: claim → source → date → tag.
