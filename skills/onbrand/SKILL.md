---
name: onbrand
description: Re-skins a finished deliverable — a /productdd or /duediligence memo, a value-creation plan, any Word document — into a target company's own brand system, so it can be sent to that company as a work sample that already looks like it came from inside their house. Extracts the target's real design tokens from their website (palette, type, system colours), maps them onto document roles under contrast rules, re-renders the document, and adds a co-branded attribution block. Use this skill whenever the user says "onbrand", or asks to rebrand / re-skin / re-colour / re-format a document, put a deck or memo "in their colours", "make it look like this company's brand", prepare a work sample or leave-behind for a specific company, or white-label an existing output. Also use it when the user names a company website and a document in the same breath.
---

# On-brand

Turn a finished document into **their** document. The reader should open it and feel it was made
inside their walls — then notice, in one line at the top, that it was not.

This is a sales instrument, not a formatting pass. Three things make it work: the brand has to be
their *real* one (extracted, not guessed), the palette has to be re-mapped for paper rather than
copied off a screen, and the attribution has to be unmissable and honest.

## The two rules that matter

**1. A web palette is not a document palette.** Websites are dark-ground with a loud accent.
Documents are white-ground and get printed. Dropping the brand's banana yellow (`#FFAE19`) onto white as
a heading colour gives 1.9:1 contrast — invisible. Dropping it as a *fill* with black text on top
gives 12:1 — and it looks exactly like their site.

So never map colour-to-colour. Map **colour to role**, and let contrast decide which brand colour
gets which role. `references/role-mapping.md` is the doctrine; `scripts/make_theme.py` applies it.

**2. Colour alone never makes a document look like a brand.** A brand is recognised by its display
face, its case, its tracking, and *where* it puts its signature colour — long before anyone parses
a hex value. A memo with the brand's exact palette set entirely in Calibri sentence case reads as a Word
document that happens to be black and cream. The same memo with the company name set in the
brand's display face, uppercase, at its own negative tracking, with the signature colour on the
section rules, reads as the brand.

So the extractor captures the **heading ladder** as well as the palette, and `apply_theme.py`
runs a **brand pass** over the rendered document that sets four things: the title as a wordmark,
the signature colour as text on the dark band, the signature colour on every section rule, and
one rule separating the two dark bands. Those four moves carry more brand recognition than the
whole palette does.

## Pipeline

```
1. EXTRACT   their site  ──▶ tokens.json     (browser + scripts/extract_tokens.js)
2. MAP       tokens.json ──▶ theme.json      (scripts/make_theme.py, then you review it)
3. RENDER    theme.json  ──▶ branded .docx   (scripts/apply_theme.py  — path A, preferred)
                                             (scripts/retheme_docx.py — path B, fallback)
4. PROVE     render pages to PNG and look at them. Do not ship unseen.
```

### 1. Extract

Open the target's site in a browser tool and run `scripts/extract_tokens.js` via the browser's
JavaScript tool. Save the returned JSON to `tokens.json`.

It returns four things, in descending order of value:

- **CSS custom properties** — if the site is Webflow, Tailwind-with-tokens, or any modern design
  system, `:root` carries the brand's *named* tokens (`--base-color-brand--banana-yellow`).
  These are the brand, straight from their designer. Trust them over everything else.
- **Computed colours weighted by painted area** (backgrounds) and by text length (foreground).
  This tells you what they actually use, not what the style guide says.
- **The heading ladder** — for every `h1`–`h6`: family, size, weight, `text-transform`, tracking
  in em, and leading. The largest heading defines the `display` role. Do not skip this: it is the
  difference between a document that shares a brand's colours and one that looks like the brand.
- **Font families weighted by text length**, plus logo/asset URLs.

While you are on the site, note in one line *how* they use the signature colour, because the
classifier cannot see it: the brand put yellow on pill buttons **and as coloured words inside black
display headlines** (`text-color-brand`). That second habit is what the brand pass reproduces on
the header band. A brand that only ever uses its colour as a background gets a different treatment.

Also read what the company actually does while you are there. Their portfolio page is where you
find out that the subject of your memo is one of their holdings — which changes the pitch, and
occasionally the whole point of sending it.

If the site yields nothing (heavy canvas, an image-only page), fall back to: their press kit,
their LinkedIn banner, an investor deck they published. Screenshot it, read the hexes off the
image, and hand-write `tokens.json`. Never invent a palette — a *nearly* right brand colour is
worse than an obviously neutral one, because it reads as sloppy rather than as unbranded.

Named system colours (`--...success-green-dark`, `--...error-red`) are gold. Use them for verdict
and severity bands: their own semantic scale, not yours.

### 2. Map

```bash
python3 scripts/make_theme.py tokens.json --brand "Meridian Partners" --short the brand \
    --out assets/themes/example-brand.json
```

It classifies every colour by lightness and saturation, assigns document roles under the contrast
rules, and prints a report. **Read the report.** The classifier is good at neutrals and bad at
judgement — it cannot know that a company's teal is a legacy colour they are quietly retiring.
Open the theme, fix what is wrong, re-check:

```bash
python3 scripts/make_theme.py --check assets/themes/example-brand.json
```

Anything the check flags in red would be illegible in print. Fix it; don't ship it.

### 3. Render

**Path A — re-render from source (always prefer this).** If the document came from `/productdd`,
`/duediligence` or `/valuecreation`, its `*_doc.json` sits next to the `.docx`. Re-render it:

```bash
python3 scripts/apply_theme.py \
    --doc-json  Output/ACME_productdd_doc.json \
    --builder   SKILLS_DIR/productdd/scripts/build_product_doc.py \
    --theme     assets/themes/example-brand.json \
    --prepared-for "Meridian Partners" \
    --by "Your Name" \
    --out /mnt/user-data/outputs/ACME_productdd_MERIDIAN.docx
```

This patches the builder's palette constants in a temporary copy and runs it, so **charts, bands,
score ramps and table shading are all regenerated in-brand** — not recoloured after the fact. It
never edits the original skill.

Add `--anonymise` to scrub the subject (`Acme` → `Company A`) and `--alias "Northgate=a national
apparel retailer"` for any other name that should not travel. Ask which the user wants; default is
named.

**Path B — post-process (only when there is no source JSON).** Remaps colours inside an existing
`.docx` by walking the OOXML:

```bash
python3 scripts/retheme_docx.py in.docx --theme assets/themes/example-brand.json --out out.docx
```

Honest about its limits: it maps each colour in the file to the nearest role colour by perceptual
distance and swaps fonts. Embedded chart *images* keep their old colours — say so, and offer to
rebuild those charts if the data is recoverable.

### 4. Prove

```bash
soffice --headless --convert-to pdf out.docx --outdir /tmp/proof
pdftoppm -png -r 110 /tmp/proof/out.pdf /tmp/proof/p
```

Read the PNGs. You are checking four things and nothing else:

0. Count the pages against the unbranded original. Every point of leading you add is multiplied
   by the number of headings; a brand pass that quietly adds a page has cost more than it gained.
1. Is any text sitting on a fill it cannot be read on?
2. Do the verdict / severity bands still read as good–caution–bad to someone who does not know the
   brand? If the brand colour has eaten the semantics, the semantics win — revert them.
3. Do adjacent chart series separate in greyscale? Executives print things.
4. Does the attribution line survive on page 1?

## Attribution — co-branded, not counterfeit

Default and recommended: **their palette, your name.** The document carries a single line above the
header band:

> `PREPARED FOR MERIDIAN PARTNERS · YOUR NAME · MONTH YEAR · UNSOLICITED WORK SAMPLE`

and the same in the footer with page numbers. `apply_theme.py --prepared-for X --by Y` writes it.

Do **not** place the target's logo in the document unless the user explicitly asks and has a right
to use it. Their palette is homage; their logo on your analysis is a trademark problem and, worse,
it reads as someone pretending to already work there. The line above says *I built this for you,
before you asked* — which is the actual message and a stronger one.

Never produce a version that presents the analysis as the target company's own output, or that
removes the author. If the user asks for that, say why it backfires and offer the co-branded line.

## Judgement calls, decided in advance

**Fonts.** Default `--fonts safe`: the theme's `type.body_fallback` / `type.display_fallback` —
installed system faces chosen to match the brand's character (a condensed heavy display like Anton
falls back to Arial Black, a serif to Georgia). The recipient almost certainly does not have Anton
or Plus Jakarta Sans, and Word's own substitution is ugly and out of your control. Use
`--fonts brand` only when the deliverable is a PDF you render yourself, or the user confirms the
fonts are installed on the receiving side.

Note the case and tracking survive either way — they are set as `w:caps` and `w:spacing`, not baked
into the text — so even in `safe` mode the display line keeps the brand's typographic *behaviour*.

**Proof renders substitute fonts they do not have.** If the machine doing the PDF conversion lacks
Arial Black, the proof shows a stand-in and the display line will look wrong there and right on the
recipient's machine. Check the page count and the layout in the proof; check the display face on a
machine that actually has the fallback installed.

**Semantics beat brand.** A "Pass" verdict band stays in the red family. If the brand publishes its
own system colours, use theirs (`#3B0B0B` error-dark rather than your `#8C2F2A`) — that is the best
of both. If it does not, keep the defaults and take the accent elsewhere.

**Separate with geometry before you separate with luminance.** Brands whose ground is near-black
often publish near-black system colours too, so the verdict band and the header band become two
indistinguishable stripes. The instinct is to lighten the semantic colour until the luminance gap
appears — but that invents a colour the company does not own. Put a rule in the signature colour
between them instead: it separates the bands, keeps both colours true, and lands the brand's
accent in the most-looked-at place on page 1. `make_theme.py` still computes a lightened
`semantic_band` as a fallback for path B, where no rule can be drawn.

**Restraint reads as expensive.** Two brand colours doing real work plus their neutrals beats six.
If the theme is using every colour they own, cut it back.

**Don't rewrite the content.** This skill changes how the document looks and who it is addressed to.
The analysis, the verdict, the evidence tags stay exactly as they were. If the content needs to
change for the audience, that is a separate pass, and say so.

## PowerPoint

Not yet built. When a `.pptx` needs re-skinning, the path is: rewrite `ppt/theme/theme1.xml`'s
`<a:clrScheme>` and `<a:fontScheme>` from the same `theme.json`, then sweep `srgbClr` values in
slide masters and layouts that were hard-coded rather than theme-referenced. `theme.json` is
already format-neutral, so nothing about steps 1–2 changes. Tell the user this is the current
boundary rather than producing a half-recoloured deck.

## Reference

- `references/role-mapping.md` — the eight document roles, the contrast thresholds, and how to
  decide which brand colour takes which role.
- `assets/themes/` — themes already built. Reuse before rebuilding; a company's brand does not
  change between two prospects.
