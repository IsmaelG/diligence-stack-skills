# The Diligence Stack

Claude skills for investors, operators and product people — company diligence, product diligence, technical diligence, people mapping, outreach, cohort analysis, and value-creation planning.

**Site:** https://the-diligence-stack.vercel.app

## The three packs

- **[Company Diligence Stack](./packs/company-diligence-stack.md)** — `duediligence`, `companypeople`, `targetpeople`, `interviewlog`, `onbrand`. Is this a good company, and who do I need to talk to? `duediligence` automatically runs `marketdd` (bundled with it, not a separate download) for market context.
- **[Product Diligence Stack](./packs/product-diligence-stack.md)** — `productdd`, `cohortlab`, `valuecreation`, `interviewlog`, `onbrand`. Will the product keep growing, and what do we do about it?
- **[Technical Diligence Stack](./packs/technical-diligence-stack.md)** — `technicaldd`, `interviewlog`, `onbrand`. Does the technology hold up under the hood? Chains after either of the packs above once a target is identified.

`interviewlog` and `onbrand` are shared by all three packs. All 10 skills live under [`/skills`](./skills), one folder each, and are the single source of truth for this project — the downloadable zips on the site are built straight from this repo. (`marketdd` is the 10th — it isn't listed as its own pack item since it ships bundled inside `duediligence`, but it's a complete skill and works standalone too.)

## Install

**Claude app (claude.ai, desktop, web):** download the zip for each skill you want (or a whole pack) from the site, then in Claude go to **Settings -> Skills -> Upload skill** and add each one.

**Claude Code / Cowork:** copy the folder(s) you want from [`/skills`](./skills) into `~/.claude/skills/`, so you end up with e.g. `~/.claude/skills/duediligence/SKILL.md`. Restart Claude and type `/` to see them. For a single project only, use `.claude/skills/` inside that project instead.

Check it worked by asking Claude: *"which diligence skills do you have?"*

## Repo layout

```
skills/    one folder per skill — SKILL.md + scripts/references/assets
packs/     pack-level docs (which skills, in what order, how to install)
```

## License

[CC BY-NC 4.0](./LICENSE) — free to use and share, no commercial resale. See [LICENSE](./LICENSE) for the full terms and a contact for commercial licensing.
