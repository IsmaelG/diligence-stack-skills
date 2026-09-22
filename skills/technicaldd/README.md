# technicaldd — technical due diligence, explained simply

This folder contains a Claude skill and a handful of scripts to verify, rather than assume, what a
software company (the "Target") claims about its technology — before an acquisition, an investment,
or a product consolidation.

## The principle

Every line this skill produces should be readable and checkable by a CTO or a CPO, even a junior
one — no unexplained jargon, no score without visible evidence behind it. Readability isn't a
nice-to-have, it's the product.

And a harder rule than the one above: **the verdict has to be able to say no.** If the brief is
"confirm this is a good company", that's not an instruction to follow — it's the first thing to
push back on. A score that was never at risk of turning out badly is worth nothing.

## The 6 axes

Deduplicated against `/productdd` and `/duediligence`, which already cover ICP, value proposition,
revenue estimates, public product velocity and customer reviews — technicaldd only goes where those
two don't:

1. **APIs & integrations** — REST/GraphQL/EDI, documented or not, self-serve or bespoke
2. **Agent readiness** — an MCP server, an OpenAPI spec, an `llms.txt`, or none of the above
3. **Integration time** — days (self-serve) or months (bespoke project) for a new customer
4. **Architecture & dependencies** — genuinely decoupled modules or a monolith in disguise;
   proprietary or assembled on top of third-party open-source
5. **SLA, latency, uptime** — what's published vs. what's independently measurable
6. **Security & compliance** — GDPR, MFA, CVE exposure, license risk (GPL/AGPL vs. MIT/BSD)

## From findings to verdict

Each axis gets a score from 0 to 5 and a confidence tag:

- **Strong** — direct measurement on real data (≈ [A])
- **Indicative** — a useful signal, but dependent on vantage point, sample size, or the honesty of
  whoever answered (≈ [B])
- **No data** — stays a gap in the file, never a disguised estimate

**Ceiling rule**: if 4 or more of the 6 axes have no solid evidence, the verdict caps at
`Conditional`, regardless of how well the documented axes score.

**The verdict** uses the same scale as `/productdd` (`Invest` / `Conditional` / `Pass`), so the two
memos read together without translation — and it's almost never the final decision: it enters as one
piece of evidence in the memo that called this skill.

## Zero-install first, dedicated kit second

By default, try what the Target already has before asking them to run anything of ours.

| Need | Zero-install (try first) | Dedicated kit | Does the Target have to act? |
|---|---|---|:---:|
| SBOM, licenses, secrets | Native Dependabot/Dependency Scanning + reading `package.json`/`requirements.txt` + native GitHub secret scanning | `scripts/sbom_selfrun.sh` | Yes, either way |
| Architecture & velocity | `git ls-files \| wc -l` + signature files + GitHub Insights | A third-party code-audit skill, if the Target agrees to run one | Yes, either way |
| MFA + declared compliance | Screenshot of Settings > Security | `scripts/compliance_selfrun.sh` + `references/gdpr_questionnaire.md` | Yes, either way |
| APIs, agent readiness, latency | `scripts/external_probe.py` | — already the zero-install | No — we run it ourselves |
| Real integration time | — no zero-install version, this needs people | structured reference calls | Target provides contacts |
| Real SLA/uptime | — no zero-install version | internal monitoring export, 90 days | Yes |

## Folder contents

```
SKILL.md                                  — instructions for Claude
README.md                                 — this file
scripts/
  external_probe.py                       — built, tested
  sbom_selfrun.sh                         — draft, not yet tested
  compliance_selfrun.sh                   — draft, not yet tested
references/
  gdpr_questionnaire.md                   — the GDPR questionnaire, ready to send
```

## How to run an example

```bash
python3 scripts/external_probe.py example.com
```

This runs entirely from outside — no login, no access needed — and checks API/agent discoverability,
a same-session latency sample, and baseline security headers. See `SKILL.md` for what each result
does and doesn't tell you, and the TLS-issuer caveat before trusting any certificate reading.

## Status

`external_probe.py`: built and tested. `sbom_selfrun.sh` and `compliance_selfrun.sh`: drafts, not
yet run against a real target — review before the first send.
