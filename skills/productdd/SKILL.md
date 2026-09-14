---
name: productdd
description: Runs product due diligence on a company for an investor — assesses whether the product compounds and what breaks at 10x, then delivers a decision-grade Word memo with a verdict, weighted scorecard, market pyramid, competitive positioning map, evidence sections, red flags, and an appendix listing the raw data still needed and from whom. Uses what the company shares plus external feedback (reviews, customers, partners) and expert/trade press, and navigates the product where access exists. Use this skill whenever the user says "productdd", "product due diligence", "product DD", or asks you to assess a product for an investment decision, evaluate product-market fit, review a startup's product before an IC, or judge whether a product thesis holds — even phrased as "is this product actually working" or "help me diligence Acme before Thursday".
---

# Product due diligence

Company due diligence asks *is this a good company?* This asks: **does the product compound, and
what breaks at 10x?** The reader is an investment committee. Open with the call; everything after
is the evidence that would change it.

Output: write the .docx to `{output folder}/COMPANY_NAME_productdd.docx` — `/mnt/user-data/outputs/`
in the Claude app, otherwise a folder the user has named, otherwise the working folder — then call
`present_files` on it so it appears as a download. A file written and not delivered is unreachable.

Length: as long as the evidence needs. The verdict and scorecard must sit on page 1; the rest is
read by whoever wants the detail. Move nothing to an exhibit merely to hit a page count.

## Where this sits

| Skill | Answers | Feeds this one with |
|---|---|---|
| `/duediligence` | Is it a good company? | Financials, ownership, org — read it first if it exists, don't redo it |
| `/cohortlab` | What do the numbers say? | Retention triangles, NRR bridge, segment splits |
| `/interviewlog` | Who said what, in what capacity? | Citable interview entries + source-log rows |
| `/valuecreation` | What do we do in 100 days? | (consumes this memo) |

## Sources — three layers, all three every time

1. **What the company shares.** Data room, decks, product access, management calls. Tag `[A]` only
   for raw data you recomputed or filed accounts; management-stated numbers are `[B]`.
2. **External feedback.** Review sites (G2, Capterra, app stores — sort by lowest rating first),
   customer and partner references, churned accounts, ex-employees, LinkedIn signals, community
   forums. Run `/interviewlog` on any calls. Note review count: three five-star reviews dated the
   same week are a CS campaign, not a signal.
3. **Expert and trade press.** Sector analysts (Gartner/IDC guides — note *inclusion* is not
   *ranking*), specialist trade press with named journalists, filed accounts (Pappers, Companies
   House, registries), regulator registers. Press releases republished by trade sites are `[B]`
   at best — check the site's own disclaimer.

**Keep only what's high quality.** Generic market-research reports with round-number TAMs, SEO
listicles, vendor blogs about themselves, AI-generated company profiles (Latka, LeadIQ, "Top 10"
sites): don't cite them. If a figure exists only there, mark it `[C]` and put the real source in
the data-gaps appendix. Every number in the memo carries `[A]`/`[B]`/`[C]` inline.

**Navigate the product.** If there is a demo, sandbox, trial, or public API docs, use them. Note:
time-to-first-value, what's documented vs what's promised, release-note cadence, SLA terms,
whether the pricing metric is visible. If access is refused, that is a finding and a data-gap row.

## The eight modules

Each is a claim to test, not a topic to describe. `references/modules-explained.md` explains each
module in full, spells out every acronym, and shows a worked reading (an anonymised composite, "Northwind") — read it if the
summaries below are too terse.

1. **Problem & value proposition** — what job is this hired for; do 5+ customers describe it the
   same way? Painkiller or vitamin; does the *buyer* feel the pain or only the user?
2. **Segmentation & ICP** — segment by behaviour and willingness to pay; is the best-retaining
   segment the one sales targets? Blended metrics hiding one good segment is the most common finding.
3. **PMF evidence** — does the retention curve flatten? Usage frequency vs natural frequency of the
   job; organic vs paid mix; NRR and its decomposition. Run `/cohortlab` on raw rows; never accept
   the management chart.
4. **Market — build the pyramid.** Bottom-up, tiered by customer value: at each tier, how many
   actors and what share of value. The apex (few actors, most value) is where enterprise SaaS
   lives; the base (thousands of actors, little value each) is a different business with different
   competitors. Place the target and its competitors on the pyramid. Use national-federation or
   registry data for actor counts (FEVAD, INSEE, ONS…), not analyst round numbers.
5. **Differentiation & moat — map the competitors.** Name them, place each on a two-axis
   positioning map (e.g. breadth of orchestration vs depth of execution; enterprise vs long tail),
   and state which pyramid tier each addresses. Then the hard question: what is defensible in
   24 months? Features aren't a moat; data that improves the product, switching costs, distribution
   lock, network effects are.
6. **Monetization** — is the pricing metric aligned to the value metric? If customers can triple
   value at flat cost, NRR is structurally capped.
7. **GTM–product fit** — does the motion match ACV and complexity? CAC payback by segment and
   channel; can it be sold without a founder in the room?
8. **Product org & velocity** — discovery practice, roadmap-to-strategy coherence, release cadence,
   tech debt as a product constraint. This predicts whether a value-creation plan is executable.

## Correlate before you score

Diligence fails the same way advisory work fails: legal flags a risk, finance flags another, and
nobody connects them. A termination clause in one workstream and a revenue-concentration risk in
another are one finding about one customer, written up twice as two smaller problems.

Before scoring, read your own findings across the eight modules and ask of each recurring subject —
a customer, a competitor, a person, a product line, a country — **is this several findings, or one
finding surfacing in several places?** When it is one, say so once, in the module where it does the
most damage, and cross-reference from the others. A connected finding is almost always more severe
than the sum of its parts, because it means the cause is structural.

`scripts/validate_doc.py` prints a correlation report listing subjects that recur across modules.
It decides nothing — it tells you where to look. The judgement is yours.

Worked example (Northwind, the anonymised composite in `references/modules-explained.md`):
"the reference account churned", "the carrier network was never activated",
"per-order pricing was too expensive", and "in-house build won" appeared as four findings across
four modules. They are one: *where the customer brings its own carrier, the product is a label
printer, and a label printer gets rebuilt in-house.* Stated that way it moves from four scores of
2 to a structural conclusion that changes the verdict.

## Score, verdict, red flags

- Score each module 0–5 against `references/scoring-rubric.md`; weight by stage and fund thesis.
  A score without a finding and a tag is not a score. Unverifiable → `n/a` with the reason.
- Verdict band: `Invest` / `Conditional` / `Pass`, conviction, one line. Conditions must be
  testable ("repricing pilot on 10 accounts before close", not "improve monetization").
- Red flags: 3–6, each with severity, evidence, and **what would change our mind**.

## The data-gaps appendix (mandatory)

Every `[B]` or `[C]` that matters, and every module marked `n/a`, becomes a row: what we need,
why (which module it unlocks), **from whom** (named role or body), **how to obtain** (data-room
request, registry pull, reference call, demo access, paid report), priority 1–3, status. This is
the work plan for the next diligence phase and it is often what the fund values most.

## Render

1. Write `doc.json` — schema in `references/product-schema.md`. Read it first.
2. **Run the evidence gate before rendering:** `python3 scripts/validate_doc.py doc.json`
   It exits non-zero if any block containing a figure lacks a confidence tag or a resolvable
   source id, if a cited source id is missing from the source log, or if a source-log row is
   incomplete. Fix the claims it names, or move them to the data-gaps appendix — do not render a
   memo that fails the gate, and do not reach for `--warn-only` on anything you intend to deliver.
3. `python3 scripts/build_product_doc.py doc.json --out /mnt/user-data/outputs/COMPANY_productdd.docx`
4. Convert to PDF and check that the verdict and full scorecard are on page 1.
5. Present `doc.json` alongside the .docx. It is the reproducible artifact — the session filesystem
   is wiped afterwards, and the user re-uploads the JSON to produce a rev. 2 rather than starting
   over. Keep the revision visible in `header.date` and say in the read what changed and why.

### Citing so the gate can check you

Give every source in the log a short id in its first column (`S-01` a document, `I-01` an
interview, `P-01` a published source), then cite it inline where the claim is made:
`FY24 revenue €5.14m [A, S-03]`. The confidence tag says how good the evidence is; the id says
*which artifact*, so a reader can go and look. Either satisfies the gate; both is the standard.

Exhibits, typical set: A cohort retention · B NRR bridge · C market pyramid · D competitive
positioning map and grid · E external feedback digest · F product walkthrough notes ·
G interview index · H source log. Source log is non-negotiable.

## Tone

Declarative. No hedging fog. The most valuable sentence is usually the one the founder would
argue with. If you're unsure, say so, say why, and put the fix in the appendix.
