---
name: technicaldd
description: Technical due diligence on a SaaS/software target ("the Target") across 6 axes — APIs & integrations, agent readiness (MCP), real integration time, architecture & dependencies, SLA/latency/uptime, security & compliance. Produces a weighted scorecard and an Invest/Conditional/Pass verdict, same scale as /productdd. Use whenever the user wants to verify a vendor's technical claims, compare software targets for an M&A or investment decision, or run a technical bake-off. Chains after /productdd or /duediligence once a target is identified.
---

# Technical Due Diligence (technicaldd)

Turns vendor claims ("proprietary", "enterprise-grade", "API-first") into evidence with a confidence
tag, across 6 axes. "The Target" = the entity being diligenced.

## The 6 axes

| # | Axis | What it checks |
|---|------|------|
| 1 | APIs & integrations | REST/GraphQL/EDI, documented or not, self-serve or bespoke |
| 2 | Agent readiness | MCP server, OpenAPI spec, `llms.txt`, or none of the above — discoverable or not |
| 3 | Integration time | Self-serve (days) vs. sales-led project (weeks/months) for a new customer |
| 4 | Architecture & dependencies | Real decoupling vs. a monolith marketed as "modules"; proprietary vs. assembled from open-source/third-party components |
| 5 | SLA, latency, uptime | Published commitments vs. what's independently measurable |
| 6 | Security & compliance | GDPR posture, MFA, CVE exposure, license risk (GPL/AGPL vs. MIT/BSD) |

## Tools per axis

Default to zero-install (what the Target already has) before asking for a dedicated kit:

| Need | Zero-install (try first) | Dedicated kit | Target must act? |
|---|---|---|:---:|
| APIs, agent readiness, latency | `scripts/external_probe.py <domain>` | — already the zero-install | No — run it yourself |
| SBOM, licenses, secrets | Dependabot/Dependency Scanning + reading `package.json`/`requirements.txt` + native secret scanning | `scripts/sbom_selfrun.sh` | Yes, either way |
| Architecture & velocity | `git ls-files \| wc -l` + signature files + GitHub Insights | A third-party code-audit skill, if the Target will run one | Yes, either way |
| MFA + declared compliance | Screenshot of Settings > Security | `scripts/compliance_selfrun.sh` + `references/gdpr_questionnaire.md` | Yes, either way |
| Real integration time | — no zero-install version | Structured reference calls, 5-8 per target | Target provides contacts |
| Real SLA/uptime | — no zero-install version | Internal monitoring export, 90 days | Yes |

Before trusting `external_probe.py`'s TLS reading, check the `issuer` field — if it names the sandbox
rather than a real CA, the network is intercepted and that field is worthless.

## Scoring

Each axis gets a score (0-5) and a confidence tag:
- **Strong** — measured directly (≈ [A])
- **Indicative** — real signal but vantage-point/sample/honesty-dependent (≈ [B])
- **No data** — stays a gap in the write-up, never a guess

Weight axes by what the decision depends on (architecture and SLA/compliance are usually high
weight; integration time is usually medium).

**Ceiling rule**: 4+ axes with no Strong/Indicative evidence caps the verdict at Conditional, no
exception. A high-weight axis (e.g. architecture) with zero evidence is reason enough on its own to
cap at Conditional even when the numeric trigger doesn't fire — say so explicitly rather than let a
few strong axes carry a verdict the evidence doesn't support.

**Verdict**: same scale as `/productdd` — **Invest** / **Conditional** / **Pass** — so the two memos
read together. Almost never the final decision on its own; it's one piece of evidence inside the
calling `/productdd` or `/duediligence` memo.

## Architecture exhibit

For axis 4, the highest-value exhibit is a graph of business capabilities (not code files) with
their dependencies, third-party/open-source components visually flagged. Requires internal access
(a code-audit skill the Target runs, or the zero-install equivalent) — never buildable from outside.
If only public module names are known (marketing site, pricing tiers), label the exhibit as
commercial packaging, not a verified architecture, and leave the axis scored as a data gap.

## Limitations to disclose every time

- Sandboxed network egress may be proxied (check the TLS `issuer`).
- Latency numbers are single-run, single-vantage-point — relative comparison only.
- A marketing domain is not the product; the real app/API is usually elsewhere.
- No G2/Capterra reviews found is not evidence of a bad product (that axis lives in `/productdd`).
