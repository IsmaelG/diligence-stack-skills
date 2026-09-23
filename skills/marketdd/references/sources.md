# Where market numbers live — and how much to trust them

## Source hierarchy (use in this order)

| Tier | Source type | Examples | Default tag |
|---|---|---|---|
| 1 | Official statistics | Eurostat (SBS business demography, ICT usage), national statistics offices (INSEE, Destatis, ONS), OECD, World Bank, US Census / BLS | [A] |
| 1 | Regulators & legislation | EU Official Journal, European Commission DGs, national regulators, central banks | [A] |
| 1 | Company filings | Annual reports, SEC 10-K/10-Q, ASX/LSE/AIM releases, national company registries (Pappers/Infogreffe FR, Companies House UK, Handelsregister DE) | [A] |
| 2 | Specialist analyst houses with a stable, published definition | Gartner (Magic Quadrants, Market Guides, press-release forecasts), IDC, Forrester, Berg Insight, ARC Advisory, sector-specific research houses | [A] when the figure is quoted by the publisher; [B] when second-hand |
| 2 | Industry associations | Trade federations, European sector associations, national unions | [A]/[B] |
| 3 | Consultancies & banks | McKinsey, BCG, Bain, Roland Berger, Capgemini Research Institute, PwC, ING Think, deal advisers' sector updates (multiples) | [B] |
| 4 | Generalist market-research sites | MarketsandMarkets, Grand View, Mordor, Fortune BI, IMARC, Technavio | [B] — **upper bound only** |
| 5 | Press, vendor blogs, SEO pages | — | [C] unless they cite a tier 1–3 source you then open |

## Rules that make the numbers defensible

1. **Anchor on one source per segment** — the one with a stable, published definition and a geographic split for the geography under study. Say why in the scope section.
2. **Show the dispersion.** Tier-4 estimates routinely differ 3–10× from the specialist's figure for the same market because they fold in services, hardware and adjacent suites. Put all estimates on a `dotplot` exhibit and name the one you keep.
3. **Global ≠ regional.** Never present a global figure as a regional one. If only a global number exists, say so and derive the regional share explicitly (e.g. "Europe ≈ 30 % per publisher X") and tag [B].
4. **Derived numbers show their formula** in the table's basis column: "units × €15–20/month ARPU (our assumption) [B]". An assumption you made is [C] until validated.
5. **Extrapolation is [B]**: applying a publisher's CAGR to move its base year to the report's year is fine, but label it "extrapolated".
6. **Forecast track record.** When a publisher has older editions, compare its past forecast with today's actual and report the gap — it calibrates the reader's trust.
7. **Absence is a finding.** When no credible public figure exists (a frequent case for adoption rates, niche segments, private-company revenue), write it in the "what we don't know" table with the paid source or interview that would close it. Never fill the gap with a plausible-looking number.
8. **Currency & date.** State base year, currency and FX rate once on the cover (`meta.fx_note`).

## Checklist per section

| Section | Minimum evidence |
|---|---|
| Value chain | Total spend of the physical/underlying activity; turnover per link (statistics office); operating margin per link; software margin benchmark from a listed peer or a deal |
| Depth & growth | Size + CAGR per software segment from the anchor source; dispersion exhibit; installed-base or penetration series if the segment is unit-driven |
| Demand | Number of buying entities by size class and their share of turnover (business statistics); digital adoption vs all-sector benchmark |
| Players | Named vendors per segment with HQ, owner, scale (revenue, ARR, units, customers) and priority customer segment; analyst-house positioning (e.g. Magic Quadrant) where it exists |
| Moves | M&A 2019→today with value, date and multiple where computable; capital pattern (strategic roll-ups, PE platforms, non-software entrants, customers verticalising) |
| Segments | Size of each customer segment, what it buys, buying criterion #1, sales cycle and ticket (usually [C]) and who targets it |
| Trends | For each trend: a dated regulatory or market fact, a number, and "what it changes for the customer" |
| Implications | Link back to the mandate; list of unknowns with the source that would close each |

## Parallel research passes (when sub-agents are available)

Split the research into four independent passes and run them at the same time; each returns a table of `figure | value | geography | year | CAGR | source | URL` and flags anything unverified:

1. **Sizing** — each software segment, global and regional, all tiers, plus structure statistics (number of firms by size, adoption rates).
2. **Players A** — the core software category (e.g. the management-system layer): vendors, owners, scale, analyst positioning, M&A.
3. **Players B** — the adjacent/operational categories (e.g. hardware-linked, field or last-mile tools): same fields.
4. **Value chain, trends, customers** — underlying activity size, margins per link, regulation calendar, technology adoption, customer segmentation, deal multiples and funding.

Search budgets run out: give each pass a clear list of must-have figures first, nice-to-have second.
