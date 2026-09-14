---
name: targetpeople
description: Builds an outreach plan to actually reach specific people. Takes a name or list of names plus the angle you're pursuing, then works out every viable route to them — public events where they'll physically be, warm introductions, direct email, LinkedIn, public commentary, inbound content — ranks those routes by real probability of landing, and writes the message body for each touch in a timed sequence. Every entry gives the name, objective, channel, the exact message, the destination (email address or venue), and the tip that raises conversion, explained. Use this skill whenever the user says "TargetPeople", or asks how to get in front of someone, how to reach or approach an executive, how to get a meeting, what to say to a prospect, how to open a door, or hands over a list of names and a goal. Chains naturally from a CompanyPeople document.
---

# TargetPeople

`companypeople` tells you who matters. This tells you **how to get in front of them and what to say when you do.**

Output: one Word document at
`{output folder}/<EXPLICIT_NAME>_outreach.docx`

(`{output folder}` is `/mnt/user-data/outputs/` in the Claude app — write there and call `present_files` — or a folder the user has named; failing both, the working folder.)

Name it so the user knows what's inside without opening it: `ACME_CPO_AND_CTO_outreach.docx`, or `PAYMENTS_MIGRATION_ANGLE_outreach.docx` if the angle is the organising idea. Explicit beats short. Ship the .docx alone; keep scratch files in a temp directory.

## Two things you need before you start

**The names.** One person or several. If given a `_people.docx` from `companypeople`, read it — the convictions, the counterweights and the reporting lines in there are the raw material for the angle. Don't redo that research.

**The angle.** What the user actually wants out of this person: a meeting, a pilot, a partnership, a job, an introduction onwards, a piece of information. If the user hasn't said, **ask before doing anything else.** An outreach plan without a stated objective is a set of pleasantries, and pleasantries have a zero percent conversion rate. The angle determines the channel, the message and the ask — all three change completely between "I want to sell you something" and "I want your advice".

## The rule that makes the rest work

Outreach fails for one reason above all others: it is about the sender. Every element below exists to force the plan to be about **the recipient** — what they're publicly worried about, what they've committed to, what would make their next quarter easier.

Two hard constraints, which are ethical *and* practical:

- **Public professional settings only.** Conferences, panels, industry events, trade bodies, public talks. Never a home, never a private location, never a family context. Beyond the obvious: someone approached outside a professional frame doesn't become a client, they become an enemy.
- **No fabricated pretext.** Never invent a mutual connection, a shared alma mater, a prior meeting, or a credential the user doesn't have. Where the user's own experience is needed to make a claim land, leave an explicit `[bracket]` for them to fill and say so. A pretext that unravels in the room destroys the relationship permanently, and it will unravel.

## Step 1 — Rank the routes honestly

For each person, work through every channel and rank them by *actual* probability of landing, not by how easy they are for the user. Say why. The ranking is the intelligence; the messages are just execution.

| Route | Works when | Typical reality |
|---|---|---|
| **Warm introduction** | A real, identifiable person can vouch. Name them. | Highest conversion by a distance. Always look for this first, and only discard it when you've genuinely failed to find a path. |
| **Physical encounter at a public event** | They speak, chair, judge, or exhibit somewhere in the next 3–6 months | Very high — a face and a voice outrank an email forever. Requires planning and a reason to be there. |
| **Direct email** | The message is unmistakably about them | Low base rate, but high when the message is genuinely specific. Cheap to try. |
| **LinkedIn message / connection with a note** | They post; they're reachable; the note is short | Middling. Better than email for people who don't run their own inbox. |
| **Public commentary on their post/talk** | They publish and engage | Slow but disarming: you become a familiar name *before* you ask for anything. |
| **Inbound content** | The user can publish something they'd want to read | Slowest, strongest. They come to you, which inverts the power of the whole conversation. |
| **Their gatekeeper / chief of staff / EA** | The person is senior enough to have one | Underrated. A well-framed request to an EA beats a cold email to a CEO. |

Discard routes that don't apply and say why in one line. A ranked list with an honest "not viable, because…" is more useful than six channels of false hope.

## Step 2 — Find where they will physically be

This is the part everyone skips and it's the highest-value research in the document.

Search deliberately: `"<name>" conference OR keynote OR panel OR speaker 2026`, the agendas of the sector's main events, their own LinkedIn (they announce their appearances), their employer's events page, trade-body working groups, awards juries, university guest lectures.

For each opportunity, give the user what they actually need to act:

- **Event, date, city** — dated and specific, or it's useless
- **Their role there** — keynote, panel, chairing, attending. A panellist is approachable after the session; a keynote is mobbed. This changes the plan.
- **Access** — is it open, ticketed (roughly what price), invitation-only, or industry-restricted? If there's a cheaper route in (side event, sponsor pass, a session anyone can attend), say so.
- **The approach** — precisely where and when. After their panel, not during the coffee scrum. With a question that references what they just said, not a business card.

If nothing is scheduled, say so plainly, and pivot the plan to the routes that don't depend on it. "No public appearances found in the next six months" is a finding that redirects the whole strategy.

## Step 3 — Build a sequence, not a message

One email is a coin toss. A sequence is a campaign, and it works because familiarity does most of the persuading before the ask arrives.

Three or four touches, each dated relative to day zero, each with a **distinct purpose** and its own message body:

1. **Signal** (D+0) — become visible without asking for anything. A thoughtful comment on their post; a share of their talk with an added observation. Cost to them: zero. You are now a name they've seen.
2. **Approach** (D+5 to D+10) — the real message. Specific, short, about them, with a small concrete ask.
3. **The room** (whenever the event is) — the face-to-face, prepared. If an event exists, this is the anchor and everything else is built to make it land.
4. **Re-entry** (D+15 after silence) — not a "just bumping this up". A new piece of value: something you saw, something relevant that happened, one line. Never guilt, never a fourth attempt.

Stop after the re-entry. A fourth chase converts nobody and costs the user their standing.

## Step 4 — Write the message bodies

For each touch, write the message the user could send today. Not a template with `[insert value prop]` — the actual words.

**Structure that works, in four beats:**

1. **The proof you paid attention** — a dated, specific reference to something they said, shipped, or are visibly struggling with. One sentence. This buys you the next three.
2. **The relevance** — why *you* specifically are worth their time on *that* thing. This is where you need the user's own experience; if you don't have it, leave a `[bracket]` and flag it.
3. **The offer, not the ask** — give something. A lesson, an introduction, a piece of data. Value first inverts the dynamic.
4. **The small ask** — twenty minutes, one question, a coffee at the event. Small asks get said yes to. Large asks get deferred, and deferred means dead.

Hard rules learned from what actually gets replies:

- **Short.** Under 120 words for a cold email. Every added line lowers the reply rate.
- **No flattery.** "I've long admired your work" reads as a prelude to a sales pitch, because it is one.
- **No jargon a human wouldn't say aloud.** Synergies, ecosystems, journeys, leveraging.
- **One idea per message.** Two asks is zero asks.
- **The subject line is half the email.** Make it a concrete thing, not a category: "the merchant side of the iDEAL migration" beats "partnership opportunity".

Apply the sector's own language, which you'll have picked up in the research. Writing to a payments exec about "interchange" and "reconciliation" proves more than any adjective.

## Step 5 — The conversion tip, explained

Every entry carries one tip that raises the odds — and the *reason it works*, because a rule the user understands is a rule they can adapt, and one they don't is a rule they'll misapply.

Good tips are behavioural and specific:

- *"Send Tuesday–Thursday, 07:00–08:00 their local time — senior people clear their own inbox before the day starts; after 09:00 an assistant may be triaging."*
- *"Approach after the panel, not the keynote: panellists come off stage under-consulted and slightly under-used. Lead with a question about something they said, and don't mention what you do until they ask."*
- *"He's German and the company is remote-first — write in English but keep it formal on first contact; the cultural cost of over-familiarity is higher than the cost of being slightly stiff."*
- *"Ask for her opinion, not her time. People who decline meetings will answer a sharp question, and an answered question is a relationship."*

Bad tips are horoscopes: "be authentic", "personalise your message", "follow up persistently".

## Step 6 — Build the document

Research fully, then render.

1. Write findings to `outreach.json` — schema in `references/outreach-schema.md`, read it first.
2. Render: `python3 scripts/build_outreach_doc.py outreach.json --out <path>/<NAME>_outreach.docx`

**Structure:**

1. **Header** — the angle, stated in one line, so the document can't drift from it
2. **The plan at a glance** — a table: person / objective / best route / when. The whole strategy on one screen.
3. **One section per person**: objective · ranked routes with reasons · where they'll be (dated, with access) · the sequence timeline · every message body in full with its destination · the conversion tip and why it works
4. **Source log** — where the event dates, addresses and quotes came from

Every message block must show its **destination** — the exact email address (with the confidence score if inferred), the LinkedIn URL, or the venue and moment. A message with nowhere to go is not a plan.

Check the pagination in a temp directory afterwards; trim if a person's section sprawls past two pages.

## Tone

Write like someone who has actually done this and has no interest in wasting the user's credibility. Where the odds are poor, say the odds are poor. A plan that admits "this one is a long shot, here's the only realistic path" is worth more than four pages of confident nonsense — because the user will spend real social capital on what you write.

## Reference files

- `references/outreach-schema.md` — the JSON the renderer expects. Read before writing `outreach.json`.
- `references/channels.md` — how each channel actually behaves, where to find events, and the message patterns that work per channel. Read when planning the sequence.
