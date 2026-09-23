# Company Diligence Stack

Everything you need to walk into a meeting, a board seat or a first call knowing more about a company than the person across the table.

```
/duediligence (runs /marketdd automatically)  ->  /companypeople  ->  /targetpeople        (/interviewlog feeds the evidence in, /onbrand restyles the result)
```

## Skills in this pack

| Skill | What it does |
|---|---|
| [`duediligence`](../skills/duediligence) | Give it a company name, get back a short report you could take into a meeting: the money (or the best signals available when there are no accounts), the strategy, who owns the company, an honest list of strengths and weaknesses, and an org chart with the person who really runs digital. Automatically runs a market deep-dive on the target's sector first (via the bundled `marketdd` skill) if one doesn't already exist, and folds it in. |
| [`companypeople`](../skills/companypeople) | Who really decides, mapped out: an org chart, a page on each person — what they have actually done, who backs them, what they say in public — plus a likely work email and a short opening message. |
| [`targetpeople`](../skills/targetpeople) | How to get in front of named people: every realistic route ranked by the chance it works, with the exact message written for each step and when to send it. |
| [`interviewlog`](../skills/interviewlog) | Turns messy call notes, voice memos and transcripts into a tidy list of sources — one entry per conversation, with clean quotes you can cite in a report. |
| [`onbrand`](../skills/onbrand) | Takes a finished report and puts it in another company's colours and fonts, read from their own website, so it lands looking like it came from inside their offices. |

## Is it a good company? — what `/duediligence` checks

- **The money** — revenue, margins, cash, debt. From filed accounts, or from proxy signals where there are none.
- **The people** — who runs it, who they hired, who left and when.
- **The key events** — funding, acquisitions, big customer wins and losses, restructurings, sites opened or closed.
- **Who owns it** — who controls the company, and what they want from it.
- **Where it stands** — who it competes with, where it wins, and where it is losing.

## How to install

### Option A — the Claude app (claude.ai, desktop or web)
Tools are added one at a time, each as its own small zip. Download each zip you need from the [site](https://the-diligence-stack.vercel.app/#downloads) (or grab all five from the pack zip), then in Claude open **Settings -> Skills** (some accounts say **Customize -> Skills**) and choose **Upload skill**. Add each zip — the tools are built to work together.

### Option B — on your own computer (Claude Code or Cowork)
Copy the folders inside `skills/` into your personal skills folder, `~/.claude/skills/`, so you end up with `~/.claude/skills/duediligence/SKILL.md`. Restart Claude — type `/` and they appear in the list. (For one project only, use `.claude/skills/` inside that project.)

### Check it worked
Ask Claude: **"which diligence skills do you have?"** — it should list them by name. Then try one: **`/duediligence Acme Corp`**.

## The rules these tools follow
- **Every number carries a mark** — `[A]` official accounts, invoices, or figures worked out from raw data · `[B]` what someone told us · `[C]` an estimate or a single source. Mixing marks in one sentence counts as a mistake.
- **Every claim points to a source** (`S-01` a document, `I-01` an interview, `P-01` something published) that must appear on the source list. A check refuses to print a report where one does not.
- **Research first, write last.** Roughly 70% finding things out, 20% building the argument, 10% making the document.
- **What is missing is part of the job.** Anything that could not be checked becomes a line in the appendix: what is needed, why, who has it, how to get it, how urgent.

## Notes
- `interviewlog` and `onbrand` are shared with the [Product Diligence Stack](./product-diligence-stack.md) — install both packs and they simply reuse the same files.
- `marketdd` ships bundled inside `duediligence`'s zip rather than as its own separate download — `/duediligence` calls it automatically for market context. It's a complete skill in its own right, so `/marketdd` also works directly once installed, if you want a standalone sector study.
- The worked examples inside are invented, not real clients.
- Nothing is hard-wired to one folder. The tools save to the Claude app's output folder when there is one, otherwise to a folder you name once, otherwise to wherever you are working.
