---
name: companypeople
description: Maps the key people at a company — especially whoever really owns digital — into a compact Word document with an org chart and one deep-dive card per person. Each card covers who they are, what they've actually done, where they sit in the hierarchy, their allies and counterweights, their public convictions, why they matter to you, their location, a professional email address with a confidence score (plus fallback variants), and a short opening message written to get a reply. Use this skill whenever the user says "CompanyPeople", or asks who to talk to at a company, who runs digital there, how to reach an executive, who the decision-makers are, how to get a meeting, or wants a people map / stakeholder map / exec profile ahead of a call. Takes either a company name or an existing due-diligence document as input.
---

# CompanyPeople

A due-diligence memo tells you whether a company is worth your time. This tells you **who to talk to and what to say to them.**

Output: one Word document at
`{output folder}/COMPANY_NAME_people.docx`

(`{output folder}` is `/mnt/user-data/outputs/` in the Claude app — write there and call `present_files` — or a folder the user has named. If neither is available, write to the working folder and say where it landed. Ship the .docx alone — keep scratch files in a temp directory.)

## Two ways in

**Given a due-diligence doc** (`COMPANY_NAME_duedil.docx`): read it first. It already contains the exec table, the digital owner, the ownership structure and the strategic tensions. Extract those, then go deeper on the people. Don't redo the company research — build on it. The duedil tells you *what* the company is fighting about; this document tells you *who* is fighting.

**Given only a company name**: establish the basics yourself — what the company does, who owns it, what it's currently trying to achieve. You need that context or you can't judge which people matter. Then proceed.

## Who makes the cut: 5–8 people

Not the org chart's top eight — **the eight who matter to the conversation you're about to have.** Ruthless selection is the whole value; a card on someone irrelevant costs you the attention you needed for someone who wasn't.

Include:

- The **digital owner** — the CDO/CPTO/CTO/CIO, or whoever actually controls the platform and the roadmap. Always card them, always first among the operators.
- The **decision-maker with the budget** — often not the same person. The gap between these two is usually where deals die.
- The **CEO** — even if you'll never meet them, because their priorities set everyone else's.
- The **blockers and the champions** — whoever would have to say yes, and whoever would benefit from it.
- The **useful outsider** — a board member, a chairman, an investor's representative. Often the fastest route in.

Exclude anyone you can't say something specific about. An empty card is a confession.

## The research, per person

Go deep. A card is only worth its page if it tells the reader things they couldn't have guessed.

**Who they are** — the actual career, not the title. Where they were before, what they were hired to do, what kind of operator they are (a builder? a cost-cutter? a diplomat?). People are hired to solve a specific problem: name the problem.

**What they've done** — concrete, attributable achievements. Products shipped, businesses turned around, deals signed, teams built. Also the failures, if public. A CV of successes is a press release, not intelligence.

**Where they sit** — reporting line, size of org, budget if knowable. A CDO reporting to the COO has a fraction of the power of one reporting to the CEO, and that single fact should change how you approach them.

**Allies and counterweights** — this is the section where most people-maps turn into fiction, so hold the line: *only what the public record shows.* Legitimate evidence: people they've hired from previous employers (loyalty travels), people they've worked alongside for years, public co-sponsorship of an initiative, a reorganisation that expanded one remit at another's expense, a documented disagreement, a resignation that followed a decision. Frame counterweights as **structural tension**, not personal animosity — "her remit overlaps his on the platform roadmap; the 2025 reorg moved data science from his org to hers" is useful and true. "They hate each other" is neither. If the record is silent, write "no public signal" — that is a finding, not a gap.

**Public convictions** — what they've actually said, on the record: interviews, keynotes, LinkedIn posts, earnings calls, op-eds. Quote them. A person's public position is the single most reliable predictor of what they'll respond to, and it's the raw material for the opening message. Date every quote.

**Why they matter to you** — one sentence, sharp. The reason this card exists.

## Email: infer the pattern, then score your confidence

Never invent an address and never present a guess as a fact. Work the problem in this order:

1. **Find real examples** of the company's email format. They are published more often than people think: press-release media contacts, conference speaker listings, academic papers, regulatory filings, PDF metadata, GitHub commits, job-posting reply addresses, support pages.
2. **Derive the pattern** — `firstname.lastname@`, `f.lastname@`, `firstinitiallastname@`, `firstname@`. Note the domain carefully: many groups have a corporate domain distinct from the consumer brand.
3. **Apply it** to your person, then generate 1–2 fallback variants using the next most common patterns.
4. **Score it honestly.** Confidence is about the *pattern*, not your hope:

| Confidence | When |
|---|---|
| 90–95% | Pattern confirmed by 3+ independent examples at the same domain; name spelled unambiguously |
| 75–89% | Pattern confirmed by 1–2 examples; or 3+ examples but the name has ambiguity (accents, particles, double-barrelled, common surname) |
| 55–74% | No confirmed example — pattern assumed from country/sector norm, or the company has multiple observed patterns |
| < 55% | Speculative. Present it, label it, and say what would confirm it. |

Give the **basis** for every address in one line: "pattern confirmed by 3 press contacts at the domain". A confidence score without a basis is decoration.

Two rules that keep this legitimate and useful: **professional addresses only** — never a personal account (gmail, private domains) even if you find one; and **office/city location only** — never a home address. Both are the line between a sales brief and something you'd be embarrassed to be caught holding.

## Photos

You cannot download images from the web. Do not try, and do not fabricate one.

What to do instead, in order of preference:
1. **Company/press page headshot**: put the direct image URL in `photo_url` — the card renders a clickable link.
2. **LinkedIn or public/social profile**: same, into `linkedin` or `photo_url`.
3. The card auto-generates a **coloured initials avatar** so the layout still reads well.

If the user drops headshot files into a folder, pass the local path in `photo_path` and the script embeds them properly. Mention this option once in your summary — it's the only way to get real photos into the document.

## The message that lands

Every card ends with a short opening message — an email or LinkedIn note the user could send *today*. This is the payload of the whole document.

It works when it proves you paid attention to **this specific person** and not to their company's boilerplate. It fails when it could be sent to anyone in their sector.

Build it from something they said or shipped, with a date. Then make it useful to them, not to you. And keep it short — three or four sentences; every extra line lowers the reply rate.

**Weak:** "I'd love to connect and explore synergies around your digital transformation journey."

**Strong:** "You told the Payments Leaders Summit in September that migrating iDEAL was 'the hardest thing EPI will ever do'. We've moved two national schemes onto a new rail and the thing that nearly broke us was the merchant reconciliation, not the consumer side. Happy to share what we learned, no pitch — 20 minutes?"

The difference: a dated, specific reference; a claim to relevant scar tissue; something offered rather than asked; a small, concrete ask.

Write `why_it_works` for each message in one line, so the user can adapt it rather than send it blind.

## Build the document

Research fully, *then* render.

1. Write findings to `people.json` — schema in `references/people-schema.md`, read it before writing.
2. Render: `python3 scripts/build_people_doc.py people.json --out <path>/COMPANY_NAME_people.docx`

The script draws the org chart (highlighting the people who have cards), lays out each card, generates avatars, and formats the email table and message box. Don't hand-roll python-docx.

**Structure:**

1. **Header band** — company, date, one-line read on the power structure
2. **Org chart** — the reporting reality, with carded people highlighted. Show the reporting *line*, since that's the point.
3. **The power read** — 3–4 bullets: who really decides, where the tension sits, the shortest route in
4. **One card per person** — the digital owner first, then by influence, not by rank
5. **Email pattern note** — how the addresses were derived, so the reader can judge them
6. **Source log** — claim, source, date, confidence tag

### One card, one page

A card that spills onto a second page stops being a card. The trap is length, not count: three sprawling bullets overflow a page just as surely as ten short ones, so the budget below is in **characters**, and it is the one that actually binds.

| Block | Ceiling |
|---|---|
| Why they matter | 1 sentence, ~180 chars |
| Who they are | 2–3 bullets, ≤ 360 chars each |
| Track record | 3 bullets, ≤ 240 chars each |
| Position in hierarchy | 2 sentences, ≤ 300 chars total |
| Public convictions | 3 bullets; `point` ≤ 70 chars, `evidence` ≤ 140 |
| Allies | 2, same limits (renders in a narrow column — be terse) |
| Counterweights | 2, same limits |
| Emails | 2–3 rows |
| Message | `body` ≤ 470 chars, `why_it_works` ≤ 130 |

If a person deserves more than this, that's a signal they deserve a **conversation**, not a longer card. Cut to the ceiling; the reader is standing outside a meeting room, not doing a literature review.

Check it after rendering: convert in a temp directory and confirm the page count is `1 (chart) + N people + 1 (pattern/sources)`. If it's higher, a card overran — trim and re-render. The PDF is scaffolding; ship the .docx alone.

Confidence tags, as in the duedil: `[A]` filed/official, `[B]` company-stated or credible press, `[C]` inferred.

## Tone

You're writing for someone who will walk into a room with these people. Be specific, be fair, and be honest about what you don't know. Never invent a quote, a relationship, or an address — one fabricated detail, discovered in the room, destroys the credibility of the entire document and the person carrying it.

## Reference files

- `references/people-schema.md` — the JSON the renderer expects. Read before writing `people.json`.
- `references/research-playbook.md` — where to find career history, email pattern examples, public statements, and reporting lines. Read it when a person's trail goes cold.
