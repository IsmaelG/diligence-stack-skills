# Technical Diligence Stack

Everything you need to turn a vendor's technical claims — "API-first", "enterprise-grade", "proprietary" — into evidence, once a target is on the table.

```
/duediligence or /productdd  ->  /technicaldd        (/interviewlog feeds the evidence in, /onbrand restyles the result)
```

## Skills in this pack

| Skill | What it does |
|---|---|
| [`technicaldd`](../skills/technicaldd) | Technical due diligence across 6 axes — APIs & integrations, agent readiness, real integration time, architecture & dependencies, SLA/latency/uptime, and security & compliance. A weighted scorecard and an Invest/Conditional/Pass verdict, on the same scale as `/productdd`. |
| [`interviewlog`](../skills/interviewlog) | Turns messy call notes, voice memos and transcripts into a tidy list of sources — one entry per conversation, with clean quotes you can cite in a report. |
| [`onbrand`](../skills/onbrand) | Takes a finished report and puts it in another company's colours and fonts, read from their own website, so it lands looking like it came from inside their offices. |

## Does the technology hold up under the hood? — the 6 `/technicaldd` axes

1. **APIs & integrations** — REST/GraphQL/EDI, documented or not, self-serve or bespoke.
2. **Agent readiness** — an MCP server, an OpenAPI spec, an `llms.txt`, or none of the above.
3. **Integration time** — days (self-serve) or months (a sales-led project) for a new customer.
4. **Architecture & dependencies** — real decoupling vs. a monolith marketed as "modules"; proprietary vs. assembled on top of open-source.
5. **SLA, latency, uptime** — published commitments vs. what's independently measurable.
6. **Security & compliance** — GDPR posture, MFA, CVE exposure, license risk (GPL/AGPL vs. MIT/BSD).

Each axis gets a score out of 5 and a confidence tag — Strong, Indicative, or No data, never a disguised guess. Four or more axes with no real evidence caps the verdict at Conditional, no exception.

## How to install

### Option A — the Claude app (claude.ai, desktop or web)
Tools are added one at a time, each as its own small zip. Download each zip you need from the [site](https://the-diligence-stack.vercel.app/#downloads) (or grab all three from the pack zip), then in Claude open **Settings -> Skills** (some accounts say **Customize -> Skills**) and choose **Upload skill**. Add each zip — the tools are built to work together.

### Option B — on your own computer (Claude Code or Cowork)
Copy the folders inside `skills/` into your personal skills folder, `~/.claude/skills/`, so you end up with `~/.claude/skills/technicaldd/SKILL.md`. Restart Claude — type `/` and they appear in the list. (For one project only, use `.claude/skills/` inside that project.)

### Check it worked
Ask Claude: **"which diligence skills do you have?"** — it should list them by name. Then try one: **`/technicaldd example.com`**.

## The rules these tools follow
- **Every number carries a mark** — `[A]` official accounts, invoices, or figures worked out from raw data · `[B]` what someone told us · `[C]` an estimate or a single source. Mixing marks in one sentence counts as a mistake.
- **Every claim points to a source** (`S-01` a document, `I-01` an interview, `P-01` something published) that must appear on the source list. A check refuses to print a report where one does not.
- **Research first, write last.** Roughly 70% finding things out, 20% building the argument, 10% making the document.
- **What is missing is part of the job.** Anything that could not be checked becomes a line in the appendix: what is needed, why, who has it, how to get it, how urgent.

## Notes
- `interviewlog` and `onbrand` are shared with the [Company Diligence Stack](./company-diligence-stack.md) and [Product Diligence Stack](./product-diligence-stack.md) — install any of the three and they simply reuse the same files.
- `technicaldd` is designed to chain after `/duediligence` or `/productdd` once a target is identified, not to stand alone — it's almost never the final word on its own, just one piece of evidence in the calling memo.
- `scripts/external_probe.py` is built and tested. `scripts/sbom_selfrun.sh` and `scripts/compliance_selfrun.sh` are drafts, not yet run against a real target — review before the first send.
- Nothing is hard-wired to one folder. The tool saves to the Claude app's output folder when there is one, otherwise to a folder you name once, otherwise to wherever you are working.
