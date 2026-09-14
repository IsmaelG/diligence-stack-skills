# people.json schema

`build_people_doc.py` renders this. Every key is optional — omit a section and it disappears rather than showing an empty shell.

```jsonc
{
  "company": "EPI / Wero",
  "subtitle": "EPI Company SE · Brussels · bank consortium, 18 shareholders",
  "date": "13 July 2026",

  // 3–4 bullets: who really decides, where the tension is, the shortest way in.
  "power_read": [
    "Weimert is the face; Müller is the throat of the operation — he owns whether e-commerce ships.",
    "..."
  ],

  "org_chart": {
    "title": "Org chart — highlighted = carded below",
    // parent must match another node's id. Root has parent: null.
    // highlight: true => dark box. Use it for the people who get cards.
    "nodes": [
      {"id": "board",    "name": "Joachim Schmalzl", "title": "Chairman",  "parent": null,     "highlight": true},
      {"id": "ceo",      "name": "Martina Weimert",  "title": "CEO",       "parent": "board",  "highlight": true},
      {"id": "cpto",     "name": "Ralf Müller",      "title": "CPTO",      "parent": "ceo",    "highlight": true},
      {"id": "cmso",     "name": "L. Francesconi",   "title": "CMSO",      "parent": "ceo",    "highlight": false}
    ],
    "caption": "Reporting lines per The Org (unverified) cross-checked against EPI releases [C]."
  },

  "people": [
    {
      "name": "Ralf Müller",
      "title": "Chief Product & Technology Officer",
      "initials": "RM",                 // optional; auto-derived from the name if absent
      "photo_path": null,               // local file → embedded. Only way to get a real photo in.
      "photo_url": "https://...jpg",    // public headshot → rendered as a 'photo' link
      "linkedin": "https://linkedin.com/in/...",
      "location": "Brussels [B]",       // office/city only. Never a home address.
      "reports_to": "CEO Martina Weimert — directly",
      "tenure": "Since 2021 [C]",
      "prior": "Ex-…",

      "why_they_matter": "One sharp sentence. The reason this card exists.",

      "who_they_are":  ["The operator they are, and the problem they were hired to solve."],
      "track_record":  ["Concrete, attributable. Shipped, turned around, signed, built. Failures too."],
      "hierarchy":     "Prose. Reporting line, org size, budget if knowable — and what that implies.",

      // allies / counterweights / convictions: {point, evidence}. Evidence is not optional —
      // it is the only thing separating this from gossip.
      "allies":        [{"point": "Claim.", "evidence": "The hire, the reorg, the co-sponsored initiative [B]."}],
      "counterweights":[{"point": "Structural tension, not personal animosity.", "evidence": "What the record shows [B]."}],
      "convictions":   [{"point": "What they publicly believe.", "evidence": "Quote it. Date it. Source it [B]."}],

      // First entry = best guess. 1–2 fallbacks after it.
      "emails": [
        {"address": "ralf.muller@epicompany.eu", "confidence": 80,
         "basis": "firstname.lastname pattern confirmed by 2 press contacts at the domain"},
        {"address": "r.muller@epicompany.eu",    "confidence": 45,
         "basis": "fallback: f.lastname, seen at some Belgian PIs"}
      ],

      "hook_message": {
        "subject": "Short, concrete, curiosity-shaped",
        "body": "3–4 sentences. Dated reference to something they said or shipped, relevant scar tissue, something offered, a small ask.",
        "why_it_works": "One line, so the user can adapt it rather than send it blind."
      }
    }
  ],

  "email_pattern": {
    "pattern": "firstname.lastname@epicompany.eu",
    "evidence": "Confirmed by: media@… (role), and 2 named contacts in the Jun-2026 press releases.",
    "caveat": "Domain also hosts epibv.… for the Dutch entity — a Netherlands-based person may sit there instead."
  },

  "source_log": {
    "columns": ["Claim", "Source", "Date", "Tag"],
    "rows": [["…", "…", "…", "[B]"]]
  },

  "footer_note": "Optional override of the default legend."
}
```

## Rules the renderer assumes

- **Confidence colours**: ≥75% renders green, 55–74% amber, <55% rust. Score the pattern honestly — an inflated number is worse than a low one, because the user will act on it.
- **One card per page.** Don't try to cram; if a person doesn't fill a card, they probably shouldn't have one.
- **Order the people by influence, not rank.** The digital owner leads. The card order is itself a recommendation.
- **`photo_path` is the only route to a real photo** — images can't be downloaded from the web. Without it, the card shows a coloured initials disc plus a link.
