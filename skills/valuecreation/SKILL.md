---
name: valuecreation
description: Turns product due-diligence findings into an investor value-creation plan — prioritised levers with sized impact and effort, the 100-day plan, the metrics that prove it worked, and the board asks. Use this skill whenever the user says "valuecreation", "value creation plan", "100-day plan", "post-investment plan", or asks what to do with a company after investing, how to fix a portfolio company's product or pricing, what to put in a board pack, or how to turn diligence red flags into an action plan. Chains naturally from /productdd.
---

# Value creation

Diligence ends with a judgement. This begins with a decision already made and asks: **what are the
three things that change the outcome, and who does them by when?**

Input: a `/productdd` memo (preferred), or the raw findings. If the memo exists, read it first —
the red flags and the low-scoring modules *are* the lever list. Don't re-diligence.

Output: write to `/mnt/user-data/outputs/COMPANY_NAME_valuecreation.docx`, then call `present_files`.

## The discipline

Most value-creation plans fail the same way: twenty initiatives, none owned, none sized. Three rules:

1. **Three to five levers. No more.** A plan with ten levers is a wish list; the portfolio company has
   one product team and it is already busy.
2. **Every lever is sized.** Not "improve pricing" — "reprice to a job-based metric; +8–12pt NRR on
   the mid-market base, worth €X ARR at current volumes". If you can't size it, you don't understand
   it yet, and it isn't ready to be a lever.
3. **Every lever names an owner and a date.** An unowned lever is a paragraph.

## Step 1 — Derive the levers

Read across from diligence, don't invent:

| Where it came from | What it becomes |
|---|---|
| Lowest-weighted-score module | The primary lever, almost always |
| A high-severity red flag with a stated mitigation | A lever with the mitigation as its first milestone |
| A conditional-verdict condition | A pre-close or day-1 action, not a 100-day one |
| Segment divergence in `/cohortlab` | A GTM decision: focus, harvest or sunset |
| A misaligned pricing metric | The highest-ROI lever available; it compounds through the whole base |

For each: the thesis it protects, expected impact with a range, effort (weeks of the product team),
dependencies, and confidence.

## Step 2 — Sequence into 100 days

| Phase | What belongs there |
|---|---|
| Days 0–30 | Instrument and verify. Fix the measurement before fixing the thing — you cannot prove a lever worked against a metric nobody trusts. Confirm the diligence findings from inside. |
| Days 31–60 | Land one visible win. Choose the lever with the shortest path to evidence, not the biggest number. It buys the credibility for the rest. |
| Days 61–100 | Start the structural lever — repricing, segment focus, platform work. Set the milestone that proves it by month 6. |

Put pre-close conditions in their own block, before day 0. They are leverage; they disappear at close.

## Step 3 — Metrics and governance

The measurement plan is the part that survives contact with reality. For each lever: the leading
indicator (weekly), the lagging one (quarterly), the current baseline, and the target with a date.
Baseline from `/cohortlab` where possible so the starting point isn't contested later.

Then the board asks: 3–5 things you need from management or the board to make the plan executable —
a hire, a decision, a budget, a deprioritisation. Be explicit about what gets *stopped*; a plan that
only adds is a plan that won't run.

## Step 4 — Render

Same renderer as `/productdd` — the documents differ in content, not in typography. Read
`../productdd/references/product-schema.md`, then:

```bash
python3 ../productdd/scripts/build_product_doc.py plan.json \
    --out /mnt/user-data/outputs/COMPANY_valuecreation.docx
```

Mapping into the schema:

| Plan element | Schema key |
|---|---|
| Doc label | `doc_label: "Value-creation plan"` |
| The thesis in one line | `verdict` → `call: "Invest"`, `one_liner` = the thesis being protected |
| What we're doing and why | `the_read` |
| Lever summary | `scorecard` — reuse it: `module` = lever, `score` = expected impact 0–5, `weight` = effort, `finding` = sized outcome |
| Each lever in detail | `sections` — one per lever, with the milestone table |
| The 100-day plan | a `section` with a phase/workstream/owner/milestone table |
| Execution risks | `red_flags` — `mitigation` becomes the contingency |
| Board asks | `open_questions` with `questions_heading: "Board asks"` |
| Baselines, workings | `exhibits` |

Verify pagination as in `/productdd`: convert to PDF and confirm the plan body ends before the
exhibits. Two pages is the target — a plan nobody rereads has failed.

## Tone

Write for the operating partner who will be held to this in six months, and for the founder who has
to run it. Specific, owned, dated. No initiative that can't be told apart from doing nothing.
