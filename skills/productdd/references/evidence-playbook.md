# Evidence playbook

Where product evidence actually lives, and how to get it when the data room is thin.

## The data room request list

Ask for raw, not rendered. One row per customer per period beats any dashboard export, because
you can recompute it and they can't shade it.

| Ask for | Feeds | Why raw matters |
|---|---|---|
| Customer × month revenue (csv), from first billing month | `/cohortlab` → modules 2, 3, 6 | Their "active user" definition is the whole argument |
| Same file with a segment/plan column | Segment economics | Blended metrics are where problems hide |
| Signups → activation → paid funnel by month and channel | Modules 3, 7 | Reveals whether growth is paid or pulled |
| CAC by channel and segment, with cost inputs | Module 7 | Blended CAC hides a broken channel |
| Price list history + top-20 realised prices | Module 6 | Discount discipline is invisible in the price list |
| Churn reasons, verbatim, last 24 months | Modules 1, 2 | The honest version of the ICP |
| Product usage events by account (or top-50 sample) | Module 3 | Revenue retention without usage retention is a lagging indicator |
| Roadmap, last 4 quarters planned vs shipped | Module 8 | Velocity and honesty in one artifact |
| Support ticket volume by theme | Modules 1, 8 | Product debt shows up here first |

If they won't give the raw file, that is a finding — write it in the memo and tag the affected
modules `[B]` at best.

## Customer reference calls

Six to eight calls beats any survey. Insist on picking some yourself from the customer list —
a curated reference list tells you about the CS team, not the product.

Compose the set deliberately: 2 champions, 2 average accounts, **2 churned**, 1 evaluated-and-declined.
The churned and the declined carry most of the information.

Questions that work:
1. What were you doing before? (If the answer is "nothing", the market may not exist.)
2. Walk me through the last time you used it. (Recalled specifics beat stated satisfaction.)
3. Who else uses it, and who decided to buy? (Buyer/user split, expansion path.)
4. What would you use if it disappeared tomorrow? (The real competitive set — usually a spreadsheet.)
5. How would you feel if it disappeared? Very disappointed / somewhat / not. (The Sean Ellis question;
   >40% "very" among the ICP is the conventional PMF marker — treat as a signal, not a verdict.)
6. What did you expect that it doesn't do? (Roadmap validity.)
7. How did the price land, and would you pay 30% more? (Pricing headroom, honestly.)
8. *For churned:* what actually happened, and what would have kept you?

Log every call in an exhibit: role, segment, tenure, and the one sentence that mattered. Anonymise
if you agreed to.

## External proxies when access is limited

| Signal | Reads on | Source |
|---|---|---|
| Release notes, changelog, app-store cadence | Velocity (module 8) | Product site, stores |
| Job postings by function and level | Revealed strategy; a VP Sales hire before PMF is a tell | Careers page |
| Review sites, sorted by lowest rating | The weaknesses the deck omits | G2, Capterra, app stores |
| Public API/docs depth | Extensibility, integration moat | Developer docs |
| Pricing page history | Repricing attempts, packaging changes | Wayback Machine |
| Integration/partner directories | Distribution and entrenchment | Partner marketplaces |
| Community, forum, subreddit tone | Pull vs push demand | Public communities |
| Downloads, traffic, app rank trend | Demand-side proxy for consumer plays | Public estimators |

Everything from this table is `[C]` unless corroborated. Say so.

## Traps that produce flattering numbers

- **Survivor cohorts** — retention computed on customers still present. Anchor on the acquisition
  cohort, always.
- **Reset on downgrade** — a customer who drops to the free tier counted as retained.
- **Annual-plan illusion** — 12-month contracts look like retention until the first renewal cliff.
  Check renewal rate separately from logo retention.
- **Blended NRR** — one enterprise expansion masking broad SMB contraction. Always decompose.
- **Pilot revenue as ARR** — non-recurring counted as recurring. Ask what fraction is contracted.
- **Design partners** — heavily discounted early accounts with unrepresentative behaviour. Exclude
  them and recompute; if the picture changes, that's the finding.
