# outreach.json schema

`build_outreach_doc.py` renders this. Keys are optional — omit a block and it disappears.

```jsonc
{
  "title": "EPI / Wero — migration angle",
  "angle": "Sell our scheme-migration expertise ahead of the iDEAL → Wero cutover.",
  "date": "13 July 2026",
  "file_slug": "EPI_MIGRATION_ANGLE",

  // The whole strategy on one screen. One row per target.
  "at_a_glance": {
    "columns": ["Target", "Objective", "Best route", "When"],
    "rows": [
      ["Ralf Müller (CPTO)", "20-min call on merchant reconciliation", "Comment → email", "This week"],
      ["Amir Sadr-Azodi (CIO)", "Meet at the Amsterdam summit", "Public event", "30 Sep 2026"]
    ]
  },

  "targets": [
    {
      "name": "Ralf Müller",
      "title": "Chief Product & Technology Officer, EPI",
      "objective": "A 20-minute call on merchant-side reconciliation before the Dutch cutover.",
      "read": "One or two sentences: what he cares about right now, and why that opens a door.",

      // Ranked by real probability. Include the non-viable ones with a reason — that's information.
      "routes": [
        {"route": "Public commentary → email", "odds": "Best",
         "why": "He posts on LinkedIn and replies in threads. Being a known name before the ask roughly doubles the odds."},
        {"route": "Warm introduction", "odds": "Not viable",
         "why": "No identifiable shared connection found. Revisit if the user has a contact at Worldline or Nexi."}
      ],

      // Dated, sourced, with the access route. If nothing found, say so — it redirects the plan.
      "where_they_will_be": [
        {"event": "Payments Leaders Summit", "date": "30 Sep – 1 Oct 2026", "city": "Amsterdam",
         "their_role": "EPI keynote: 'Wero in practice: migrating the Netherlands'",
         "access": "Paid conference, ~€1.5k [C]. Sponsor/side events often free.",
         "approach": "Catch him after the session, not in the coffee scrum. Open with a question about the migration, not about you.",
         "source": "epicompany.eu events page [A]"}
      ],

      // 3–4 touches. Each has a purpose and its own message.
      "sequence": [
        {
          "day": "D+0",
          "purpose": "Signal — become a name he has seen, ask for nothing",
          "channel": "LinkedIn comment",
          "destination": "https://linkedin.com/in/…",
          "subject": null,
          "body": "The actual comment. Short. Adds something he didn't say.",
          "note": "Optional: timing or delivery detail."
        },
        {
          "day": "D+5",
          "purpose": "Approach — the real message",
          "channel": "Email",
          "destination": "ralf.mueller@epicompany.eu (62% — umlaut trap; fallback ralf.muller@…, 50%)",
          "subject": "the merchant side of the iDEAL migration",
          "body": "Under 120 words. Dated reference → relevance → offer → small ask. Use [brackets] for the user's own experience.",
          "note": "Tue–Thu, 07:00–08:00 CET."
        }
      ],

      // One tip, and WHY it works. A rule the user understands is one they can adapt.
      "tip": {
        "tip": "Ask for his opinion, not his time.",
        "why": "People who decline meetings will answer a sharp question — and an answered question is already a relationship."
      }
    }
  ],

  "source_log": {
    "columns": ["Claim", "Source", "Date", "Tag"],
    "rows": [["Amsterdam keynote", "epicompany.eu/events", "Jul 2026", "[A]"]]
  }
}
```

## Rules the renderer assumes

- **`odds`** drives the colour: `"Best"` / `"High"` → green, `"Medium"` → amber, `"Low"` / `"Not viable"` → rust. Be honest; the colour is a promise.
- **Every `sequence` entry needs a `destination`.** An email address (with its confidence), a URL, or a venue and moment. A message with nowhere to go isn't a plan.
- **`[brackets]`** mark what only the user can supply. Never fill them with invention.
- **Budget**: a target should fit in 1–2 pages. `read` ≤ 300 chars, each `why` ≤ 180, each `body` ≤ 700 (cold email ≤ 120 words), `tip.why` ≤ 200.
