---
name: cohortlab
description: Computes retention, cohort and revenue-quality evidence from a raw customer revenue export — logo and revenue retention triangles, the retention-curve plateau test, NRR/GRR with an expansion-contraction-churn bridge, revenue concentration, and the same metrics split by segment. Emits chart specs that drop straight into a product due-diligence memo. Use this skill whenever the user says "cohortlab", asks for cohort analysis, retention curves, NRR or churn analysis, wants to check whether a retention curve flattens, wants to verify a company's own retention chart, or hands over a subscription/billing/MRR export and asks what it says. Called automatically by /productdd whenever raw customer data exists.
---

# Cohort lab

Management's retention chart is an argument. This produces the version you can defend in an IC.

Two things make a cohort number wrong far more often than arithmetic: the definition of *active*,
and the treatment of downgrades. Recomputing from raw rows removes both.

## Input

One row per customer per period. CSV or XLSX. Minimum three columns:

| Column | Example values |
|---|---|
| customer id | `C1041`, `acme-ltd` |
| period | `2025-03`, `2025-03-01`, any parseable date |
| revenue | MRR or recognised revenue for that customer in that period |

Optional but high-value: a **segment** column (plan, tier, size band, country). Segment splits are
where the finding usually is.

Rows are summed per customer-period, so multi-product exports need no pre-processing. Periods are
normalised to months.

## Run it

```bash
python3 scripts/cohort.py revenue.csv \
    --customer customer_id --period month --revenue mrr \
    --segment plan --out evidence.json
```

It prints the four numbers that decide the PMF module, then writes the full evidence file:

```
  window        : 2025-01 → 2026-06
  logo plateau  : NONE — curve still falling
  NRR / GRR     : 78.9% / 59.2%
  top-10 concn  : 11.8%
```

**Why pandas and not hand-rolled dicts:** the entire job is group-by, pivot and align on a
customer × period grid. Cohort bugs are almost always off-by-one periods or customers silently
dropped when they skip a month — exactly what a pivot handles and a loop doesn't.

## What comes out

`evidence.json`:

| Key | Contents |
|---|---|
| `cohorts` | Logo and revenue retention triangles (% of month 0), ragged, immature tail trimmed |
| `plateau_logo` / `plateau_revenue` | First period where the curve stops falling, or `null` — **the PMF test** |
| `nrr` | Base, expansion, contraction, churn, ending, NRR%, GRR% over a 12-month window |
| `concentration` | Top 1/5/10/20 customer share of the latest period |
| `segments` | Customers, revenue, NRR, M6 retention and plateau per segment |
| `charts` | `logo_heatmap`, `revenue_heatmap`, `retention_curve`, `nrr_bridge` — already shaped for `build_product_doc.py` |

Paste a chart block straight into a `/productdd` exhibit; no reformatting needed.

## Reading the output

- **`plateau_logo: null`** — the curve has not flattened inside the observed window. Past seed, this
  is the single most consequential finding in the memo. Say it in The Read.
- **NRR high but GRR low** — a few expanding accounts are masking broad churn. Always report both;
  quoting NRR alone is how a leaky bucket gets funded.
- **Segment divergence** — if one segment plateaus and another doesn't, the blended number is
  meaningless and the real question becomes a go-to-market decision, not a product one.
- **Rising top-10 share** — growth is coming from a handful of accounts; check whether those accounts
  are structurally different from the ICP.

## Honesty rules

- State the method in the exhibit notes: cohort = first paying month, revenue = summed per period,
  immature periods trimmed rather than shown as zero.
- If design partners or discounted early accounts are in the file, exclude them and **recompute**.
  If the picture changes materially, that difference is itself a finding.
- Annual contracts distort monthly logo retention — flag it and look at renewal rate separately.
- Everything computed from a data-room file is `[A]`. Everything inferred from it is `[C]`. Don't blur.
