---
name: interviewlog
description: Turns raw interview material — call notes, voice-memo transcripts, VTT/SRT files, emails, scribbles — into a clean, citable source log with one entry per interview (name, company, role, date, relationship, edited transcript, verbatim quotes, what it changes) and emits source-log rows for a due-diligence memo. Use this skill whenever the user says "interviewlog", hands over interview notes or transcripts, asks to clean up or structure customer/expert calls, or wants interviews organised as sources for a diligence document. Chains into /productdd and /duediligence.
---

# Interview log

Raw interviews are evidence only once someone else can check them. This turns a pile of notes
into entries a partner can cite: **who said it, in what capacity, when** — then the cleaned text.

Output: write to `/mnt/user-data/outputs/COMPANY_NAME_interviews.docx`, then call `present_files`.
Also emit `sources.json` for the memo's source log.

## Input

Anything: `.txt`, `.md`, `.docx`, `.vtt`/`.srt`, pasted text, or several files in a folder. If a
file is a transcript with timestamps or speaker tags, keep the speaker attribution and drop the
rest. If it's notes, reconstruct Q/A structure from the questions the interviewer evidently asked.

For each interview establish, and ask if missing: **name (or anonymisation label), company, role,
date, relationship to the target** (current customer / churned / prospect / ex-employee / expert /
partner / competitor). Relationship is what determines how much weight the memo gives it.

## Editing rules

- **Edited means readable, not improved.** Remove fillers, false starts, cross-talk, off-topic.
  Never sharpen a claim, never add a number the speaker didn't give, never resolve an ambiguity
  the speaker left open.
- **Verbatim is sacred.** Anything in `key_quotes` is word-for-word. Everything in
  `edited_transcript` is faithful paraphrase at sentence level. If you're unsure whether the
  speaker said it, it's paraphrase, not quote.
- **Anonymise on request, keep capacity.** "Anonymised — Head of Logistics, French DIY retailer"
  is a fine `name`; "Anonymised" alone is not, because the reader can't weigh it.
- **Takeaways are the memo's, not the speaker's.** One to four lines: what this interview
  confirms, contradicts, or opens. Tag which productdd modules it feeds.
- **Confidence.** `[B]` for a first-hand account from someone in a position to know; `[C]` for
  secondhand, hearsay, or a source with an obvious axe to grind (competitor, disgruntled ex-employee).
  Say which and why in the takeaways.

## Render

1. Write `interviews.json` (schema in the script header).
2. `python3 scripts/build_interview_log.py interviews.json --out /mnt/user-data/outputs/COMPANY_interviews.docx --sources sources.json`
3. Paste the `sources.json` rows into the productdd source-log exhibit, and reference interviews
   by ID (`I-03`) in memo findings.

## Composition check

Before closing, count the set. A good product-DD interview set has champions, average accounts,
**churned** accounts, and at least one evaluated-and-declined. If it's all champions, say so at
the top of the log — a curated reference list is evidence about the CS team, not about the product.
