---
name: duediligence
description: Runs thorough due diligence on any company — listed corporate, private firm, or early-stage startup — and delivers a crisp 2-page Word memo with exhibits. Covers financials (or proxy signals when no financials exist), strategy and competitive positioning, ownership and investors, an evidence-backed SWOT weighted toward Strengths and Weaknesses, and the executive org chart with the digital leader identified. Use this skill whenever the user says "duediligence", "due dil", "due diligence", or asks you to research, assess, size up, brief them on, or prepare for a meeting with a company, prospect, target, competitor, partner, investor, or acquisition candidate — even if they never use the words "due diligence" and just say something like "what do I need to know about Acme before Thursday".
---

# Due Diligence

Produce a decision-grade company brief: two pages a busy person can read in five minutes, backed by exhibits they can dig into when a number surprises them.

The output is always a Word document at:
`{output folder}/COMPANY_NAME_duedil.docx`

(`{output folder}` is `/mnt/user-data/outputs/` in the Claude app — write there and call `present_files` so it appears as a download — or a folder the user has named, asked for once and reused. If neither is available, write to the working folder and tell the user where it landed. `COMPANY_NAME` is the common name, uppercase, spaces as underscores — `ACME_GROUP_duedil.docx`.)

## The order of work matters

Research completely, *then* build the document. Opening `build_memo.py` before you have the facts anchors you on layout when you should be anchored on truth. Do all six research passes below, write findings into a scratch `memo.json`, and only then render.

Budget roughly: 70% research, 20% structuring the argument, 10% rendering.

## Step 0 — Classify the target

The single most important early call, because it determines where the facts live:

- **Listed** (SocGen, Adyen) → audited financials exist. Go get them. Estimation is lazy here.
- **Large private / PE-backed** (Ingenico, Worldline carve-outs) → statutory filings exist in most jurisdictions. Slower to find, but real.
- **Consortium / JV / non-profit-ish vehicle** (EPI, Swift) → often no meaningful P&L. The story is in *who funded it, who governs it, and what they mandated it to do*. Governance is the financial statement.
- **Venture-backed startup** → no financials. Proxies are the entire game.
- **Pure digital player** → note this: it changes the "who owns digital" question (see Step 4).

State the classification explicitly in your head; it changes what "thorough" means.

## Step 0b — Market context (runs /marketdd)

Before Step 1, look in the output folder for a `*_marketdd.docx` covering the target's primary market and dated within the last 6 months.

- **None found** → run `/marketdd` on that market first, without asking questions: perimeter = the target's primary market, geography = its home region, mandate = this target, language = the language of this memo. It delivers its own Word + PDF report next to this memo.
- **Found** → reuse it.

Either way, the market report feeds Step 2: market size and growth, where the target sits in the value chain, the competitor set and their priority customer segments. Cite it in the source log (Exhibit F) as the market reference, and keep its confidence tags.

## Step 1 — Financials, or the best available proxy

For anything with real numbers, pull **3 years** of: revenue, growth, gross margin, EBIT/operating margin, net income, and the 2–3 metrics that actually matter in that industry (for a bank: NII, cost/income ratio, CET1, RoTE; for SaaS: ARR, NRR, CAC payback; for payments: TPV, take rate).

Industry-native metrics are what separate a real brief from a Wikipedia summary. If you're briefing on a bank and your table shows "gross margin", you've failed.

When there are no financials, run the **full proxy sweep** and reconstruct the picture:

| Signal | What it tells you | Where to look |
|---|---|---|
| Funding rounds, valuation, investor names | Scale, stage, conviction of smart money | Press releases, Crunchbase, trade press |
| Headcount + trend | Burn, momentum, whether they're growing or quietly shrinking | LinkedIn, company site |
| Open roles (which functions, which cities) | Strategy made visible — 12 payments-infra roles in Warsaw is a statement | Careers page, job boards |
| Pricing page / rate card | Business model, unit economics, positioning | Company site, resellers |
| Customer logos, case studies, integrations | Traction, ICP, distribution model | Site, partner directories |
| Governance: shareholders, board seats | Who actually controls it, and what they want out of it | Registries, press, own site |
| Product velocity | Changelogs, app-store release cadence, GitHub | App stores, docs |
| Regulatory filings, licences | Real, verifiable, often ignored by everyone else | Regulator registers |
| Patents, trademarks | Where they think their moat is | Espacenet, EUIPO |
| Traffic / downloads / app ranks | Demand-side proxy for consumer plays | Public estimators |

**Tag every figure.** Each number in the memo carries a confidence marker: `[A]` audited/filed, `[B]` company-stated or credible press, `[C]` estimated or inferred. An estimate flagged as an estimate is useful; an estimate dressed as a fact destroys trust in the whole document. Never blend the two.

## Step 2 — Strategy and competitive positioning

Answer four questions in plain language, no consulting fog:

1. **What are they actually trying to do** — their stated strategy, and (if different) their revealed strategy. Revealed strategy is what the capex, the hiring, and the acquisitions say. When stated and revealed diverge, that gap *is* the insight.
2. **Where do they sit** in the industry value chain? Who do they buy from, sell to, and depend on?
3. **How do they compare** to 3–5 named competitors on the dimensions the market actually rewards. Build a comparison table — scale, growth, positioning, key differentiator. Name real companies with real numbers.
4. **What's changing** in the industry that helps or hurts them.

## Step 3 — Ownership and investors

Who owns it, who controls it, and what they need out of it. These are three different questions and the answers often differ.

- Listed: top shareholders and %, free float, any state/strategic anchor, index membership.
- Private: cap table as far as it's visible, lead investors by round, board composition, founder holdings, any golden shares or veto rights.
- Consortium/JV: the member list, funding commitments, and the governance body. Note that shareholder-customers behave very differently from financial investors — they optimise for the parent's interest, not the vehicle's valuation. Say so if it applies.

Then the "so what": ownership predicts behaviour. A PE owner three years into a five-year hold wants EBITDA, not R&D. A consortium of banks wants a defensive utility, not a unicorn. Write that line.

## Step 4 — Executive organigram, and *who owns digital*

Map the exec committee: name, title, tenure, prior employer, remit. Tenure and prior employer often matter more than the title — a CTO hired six months ago from a hyperscaler tells you exactly what the board asked for.

Then, deliberately, **find the executive who owns digital.** This is the whole reason a brief like this gets read before a meeting. Depending on the company it could be:

- Chief Digital Officer, Chief Transformation Officer, Chief Innovation Officer
- CTO / CIO / CDIO (know the difference: CIO usually runs internal IT, CTO runs the product/platform)
- The head of a digital business unit sitting outside the exec committee — check divisional leadership, not just the top table
- In a pure digital player: there is no separate "digital exec" — the CEO/CPO/CTO *is* the digital leadership. Say that explicitly rather than forcing a match, and instead identify who owns the core platform.

Give this person a dedicated row/box in the memo: name, exact title, reporting line (do they report to the CEO or are they buried under the COO? that's a signal about how seriously digital is taken), tenure, background, and what they've publicly said or shipped. If you genuinely can't find them, say "not publicly identifiable" — never invent a name.

## Step 5 — SWOT, weighted to Strengths and Weaknesses

Most SWOTs are worthless because they're symmetric and generic. This one isn't. **Strengths and Weaknesses get the depth** — they're internal, evidenced, and specific to this company. Opportunities and Threats are shorter and framed as external conditions, not wishes.

Rules that keep it honest:

- Every Strength and Weakness carries **evidence** — a number, a filing, a hire, a product fact. "Strong brand" is not a strength; "38% unaided brand awareness in France vs 12% for the nearest challenger [B]" is.
- Aim for **4–6 Strengths and 4–6 Weaknesses**, ranked with the most material first, and keep O/T to 3 each.
- If a Strength has no evidence, cut it. An empty SWOT quadrant is more honest than a padded one.
- A weakness that's just the inverse of a strength ("dependent on its main product") is filler unless you can size the dependency.
- Look hard for weaknesses the company would not put in its own deck. That is the value you are adding.

## Step 6 — Render the document

Only now open the builder.

1. Write your findings to `memo.json` (schema: `references/memo-schema.md` — read it before writing the file).
2. Render: `python3 scripts/build_memo.py memo.json --out <path>/COMPANY_NAME_duedil.docx`

The script handles all styling, tables, the SWOT grid, charts (matplotlib → embedded PNG), the org box, and the exhibits appendix. Don't hand-roll python-docx — the script exists so every memo looks the same and you spend your tokens on research instead of formatting.

### What the document must contain

**Page 1–2 (the memo — a hard limit, and the constraint is the point: it forces you to decide what actually matters).**

Two pages is easy to breach without noticing, because every fact feels worth keeping. It isn't. Budget before you write:

| Block | Ceiling |
|---|---|
| The read | 5 bullets, **≤ 2 lines each** — long bullets are where the page budget dies |
| Conversation hook | 2 lines |
| Snapshot | 6 rows |
| Strategy prose | 4 sentences |
| Comparison table | 4 rows incl. the company itself |
| Ownership | 6 rows + 1 "so what" line |
| Leadership | 6 rows — exec committee only; everyone else goes in the org exhibit |
| Digital-owner box | 4 lines |
| SWOT | 5 per quadrant for S/W, 3 for O/T; evidence ≤ 1 line |
| Open questions | 4 |

If it doesn't fit, the answer is never to shrink the font — it's to move detail into an exhibit. Anything cut from the memo should land in an exhibit, not the bin.

After rendering, **check the result**: convert to PDF (`libreoffice --headless --convert-to pdf`) and confirm the exhibits start on page 3. If they start on page 4, you overran — cut, don't shrug, and re-render.

1. **Header band** — company, legal entity/ticker, HQ, founded, employees, latest revenue, date
2. **The read** — 4–5 bullets. The single most important block. What a smart colleague would tell you in the lift. Not a summary of the sections below; a *judgement*.
3. **The conversation hook** — closes The Read block. See below; this is mandatory.
4. **Snapshot table** — 3 years of the metrics that matter, confidence-tagged
5. **Strategy & positioning** — short prose + competitor comparison table
6. **Ownership** — table + the one-line "so what"
7. **Leadership & digital** — exec table + highlighted digital-owner box
8. **SWOT** — 2x2 grid, S/W dense, O/T light
9. **Open questions** — 3–5 things you could not resolve, phrased as questions to ask the company. This is a feature, not an admission of failure.

### The conversation hook (mandatory)

The Read must end with **the latest noteworthy digital development at the company** — the thing you could open a meeting with.

This exists because a brief is usually read twenty minutes before someone walks into a room. Facts win arguments; a well-chosen recent event wins the first two minutes. It signals you've been paying attention, and it gives the other side something they *want* to talk about.

It has to be **meaty enough to sustain a conversation**, which rules out most of what you'll find:

- ✅ A digital/tech acquisition, disposal or investment; a new platform or product shipped; a senior digital hire or departure; an AI/data partnership; a public target the digital exec has committed to; a migration, outage or security incident; a regulatory ruling that hits their tech; a strategy statement made on the record at a conference or results call.
- ❌ A generic press release, an award, a rebrand, a sponsorship, a "we are excited to announce our commitment to innovation". If your hook could apply to any company in the sector, it's not a hook.

Four things, always:

1. **What happened** — concrete, specific, named.
2. **When** — dated. Prefer the last 3–6 months; if the freshest real thing is older, say so honestly rather than dressing up something stale as news.
3. **Why it matters** — the link to their strategy, their weakness, or your reason for meeting. This is the part that makes it a conversation rather than a fact.
4. **Source** — so it can be checked before it gets repeated in a room.

Search for this deliberately and late in the process, once you know the company well enough to judge what's actually significant. A relevance judgement made before you understand the business will pick the wrong story. If you truly cannot find anything meaty, say so plainly — an honest "nothing material in the last six months, which is itself telling" beats a manufactured hook.

**Exhibits (appendix, same file):** go deep wherever the memo had to compress. Typical set — include what's relevant, skip what isn't:

- Exhibit A — Financial detail / proxy reconstruction, with the workings shown
- Exhibit B — Competitor benchmark (fuller table + chart)
- Exhibit C — Ownership & funding history (chart if there are rounds)
- Exhibit D — Full org chart
- Exhibit E — Product / pricing / regulatory footprint
- Exhibit F — Source log: every claim's source with date and confidence tag

The source log is non-negotiable. A brief that can't be audited can't be trusted with a decision.

## Tone

Write like a sharp analyst briefing a principal who is short on time and allergic to being sold to. Declarative sentences. No hedging clouds ("it appears that the company may potentially be positioned to..."). If you're unsure, say you're unsure and say why, then move on.

## Reference files

- `references/memo-schema.md` — the exact JSON structure `build_memo.py` expects. Read before writing `memo.json`.
- `references/sources.md` — where to find filings, registries, and proxy data by jurisdiction and company type. Check it when a data trail goes cold.
- `/marketdd` (separate skill) — the market deep dive run in Step 0b.
