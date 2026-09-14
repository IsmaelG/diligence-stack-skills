# Product Diligence Stack

Everything you need to tell an investment committee whether a product will keep growing, and what breaks if it gets ten times bigger.

```
/cohortlab + /interviewlog  ->  /productdd  ->  /valuecreation        (/onbrand restyles the result)
```

## Skills in this pack

| Skill | What it does |
|---|---|
| [`productdd`](../skills/productdd) | Will this product keep growing, and what breaks if it gets ten times bigger? The answer sits on page one with a score out of 5, then eight areas of evidence, a picture of the market, a map of the rivals, the things that worry it, and a list of what still needs checking. |
| [`cohortlab`](../skills/cohortlab) | Feed it a sales export and it works out whether customers actually stay: how each year's intake behaves over time, whether the drop-off flattens out, how much revenue is renewed, and how much sits with a handful of accounts. |
| [`interviewlog`](../skills/interviewlog) | Turns messy call notes, voice memos and transcripts into a tidy list of sources — one entry per conversation, with clean quotes you can cite in a report. |
| [`valuecreation`](../skills/valuecreation) | Turns the findings into a plan: what to fix first and what it is worth, what to do in the first 100 days, how you will know it worked, and what to ask the board for. |
| [`onbrand`](../skills/onbrand) | Takes a finished report and puts it in another company's colours and fonts, read from their own website, so it lands looking like it came from inside their offices. |

## Will the product keep growing? — the eight `/productdd` checks, each scored out of five

1. **What problem does it solve?** Ask five customers, without prompting. If they describe the value the same way, the positioning is real. Then: does the person who *pays* feel the pain, or only the person who uses it? If only the user, sales drag on for months.
2. **Who is the right customer?** One group often loves the product while the rest leave. The average hides it. The most common finding.
3. **Do customers stay?** A leaky bucket. If the drop-off levels out there is a loyal core. If it keeps falling, sales are refilling a bucket with no bottom. Built from raw customer data, not management's chart.
4. **How big is the market, really?** Count real buyers from the bottom up. Ignore "the market is EUR 7bn, we'll take 1%". A few big accounts, or thousands of small ones? Different rivals, different prices.
5. **What stops a competitor copying it?** Features get copied. The cost of switching, data that improves with use, and access to customers do not. And could the customer build it in-house?
6. **Does the price grow with the value?** If a customer gets three times more value and pays the same, income from existing customers is capped. Sales effort will not fix it.
7. **Does the sales approach fit the price?** An 80k contract needs a salesperson. A 500 product cannot afford one. Does it sell without the founder in the room?
8. **Can the team deliver the plan?** Shipping pace, whether they talk to users, how much old code is in the way. Tells you if the plan after investment is realistic, or just nice on paper.

## How to install

### Option A — the Claude app (claude.ai, desktop or web)
Tools are added one at a time, each as its own small zip. Download each zip you need from the [site](https://the-diligence-stack.vercel.app/#downloads) (or grab all five from the pack zip), then in Claude open **Settings -> Skills** (some accounts say **Customize -> Skills**) and choose **Upload skill**. Add each zip — the tools are built to work together.

### Option B — on your own computer (Claude Code or Cowork)
Copy the folders inside `skills/` into your personal skills folder, `~/.claude/skills/`, so you end up with `~/.claude/skills/productdd/SKILL.md`. Restart Claude — type `/` and they appear in the list. (For one project only, use `.claude/skills/` inside that project.)

### Check it worked
Ask Claude: **"which diligence skills do you have?"** — it should list them by name. Then try one: **`/productdd Acme Corp`**.

## The rules these tools follow
- **Every number carries a mark** — `[A]` official accounts, invoices, or figures worked out from raw data · `[B]` what someone told us · `[C]` an estimate or a single source. Mixing marks in one sentence counts as a mistake.
- **Every claim points to a source** (`S-01` a document, `I-01` an interview, `P-01` something published) that must appear on the source list. A check refuses to print a report where one does not.
- **Research first, write last.** Roughly 70% finding things out, 20% building the argument, 10% making the document.
- **What is missing is part of the job.** Anything that could not be checked becomes a line in the appendix: what is needed, why, who has it, how to get it, how urgent.

## Notes
- `interviewlog` and `onbrand` are shared with the [Company Diligence Stack](./company-diligence-stack.md) — install both packs and they simply reuse the same files.
- The worked examples inside are invented, not real clients.
- Nothing is hard-wired to one folder. The tools save to the Claude app's output folder when there is one, otherwise to a folder you name once, otherwise to wherever you are working.
