# Role mapping — from a brand's screen palette to a document palette

## Why a straight swap fails

A brand palette is authored for a screen: dark ground, one loud accent, generous whitespace, and a
guarantee that the viewer sees it backlit at 100% opacity. A document is authored for white paper
at 8.5pt, often printed on a mono office laser, often read on a phone in a mail client.

Three failures follow from copying colour-to-colour:

1. **The signature colour becomes invisible.** Bright yellows, limes, cyans and oranges sit at
   1.5–3:1 against white. They are perfect as *fills* and unusable as *ink*.
2. **The dark ground disappears.** A brand whose site is near-black loses its identity entirely
   once the ground is white, unless the darkness is put back deliberately as bands.
3. **Semantics get overwritten.** If the brand accent is green and it lands on the verdict band, a
   "Pass" reads as a "Proceed". Colour carries meaning in a diligence memo before it carries brand.

## The eight roles

Every document the `/duediligence` / `/productdd` / `/valuecreation` renderers produce is built
from these. A theme fills all eight.

| Role | Where it lands | Rule |
|---|---|---|
| `ink` | body text | Darkest brand neutral. **≥ 12:1 on white.** Prefer a brand near-black over pure `#000` — it is the cheapest signal that a palette was chosen, not defaulted. |
| `muted` | captions, sources, confidence notes | Mid brand neutral. **≥ 4.5:1 on white.** |
| `accent` | headings, heading rules, "so what" lines, exhibit titles | The brand colour that *passes* **≥ 4.5:1 on white**. If the signature colour fails, it does not get this role — the darkest brand chromatic or near-black does, and the signature colour moves to `accent_fill`. |
| `band_fill` + `band_text` | the header band, page-1 identity | The brand's dominant dark ground and its on-dark text colour. **≥ 7:1 between them.** This is where a dark-site brand gets its identity back. |
| `accent_fill` | the signature colour, used as a block with dark text on it | The loud one. Needs **≥ 4.5:1 against `ink`**, not against white. Use it once or twice per page — a rule under the band, a callout label, one chart series. |
| `header_fill` + `zebra` | table header row, alternating rows | The brand's two lightest neutrals or tints of the accent. `zebra` must stay **≤ 6% darker than white** or tables look dirty when printed. |
| `callout` | callout box grounds | An 8–12% tint of `accent_fill` or `accent` over white. Computed, not picked. |
| `verdict` / `severity` / `score` | semantic bands and the 0–5 score ramp | **Semantics win.** Use the brand's own published system colours when the site declares them; otherwise keep the defaults. Never let the brand accent take a semantic slot. |

Plus two roles that exist only because a signature colour that failed the text test still has work
to do:

| Role | Where it lands | Rule |
|---|---|---|
| `rule` | heading rules, the line above a semantic band, the line under the attribution | A hairline carries no text, so the 4.5:1 bar does not apply. This is how a brand whose accent failed on white still gets its colour onto **every page** rather than only page one. Needs only ≥ 1.5:1 against white — enough to be seen. |
| `on_band_accent` / `on_band_muted` | the signature colour as *text* on the dark band; secondary text below it | Many brands use their loud colour as coloured words inside a dark headline, not as a block. `on_band_accent` needs ≥ 4.5:1 against `band_fill`; `on_band_muted` is the same, dimmed, so the headline still wins. |

Plus `chart[]`: an ordered series list, and the `type` block below.

## Typography — the half of a brand that is not colour

Someone recognises a brand from its display face and how it is set before they have consciously
registered a single colour. A memo in a brand's exact palette, entirely in Calibri sentence case,
reads as a Word document that happens to be black and cream.

The extractor captures the heading ladder, and the largest heading defines the `display` role:

| Field | From | Used for |
|---|---|---|
| `display` / `display_fallback` | family of the largest heading | company name in the header band, the verdict call word, section headings, exhibit dividers |
| `display_case` | its `text-transform` | applied as `w:caps`, so copy-paste still yields the original casing |
| `display_tracking` | its `letter-spacing ÷ font-size`, in em | Word stores spacing as an absolute value in twentieths of a point, so it must be resolved against each run's own size |
| `body` / `body_fallback` | the smallest heading in a *different* family | running text |

**Fallbacks are chosen for character, not for name.** A condensed heavy display (Anton, Oswald,
Bebas) falls back to Arial Black; a serif to Georgia; a mono to Consolas. Case and tracking survive
the fallback, because they are set as attributes rather than baked into the text — so even in safe
mode the display line keeps the brand's typographic behaviour, which is most of the recognition.

## Separate with geometry before luminance

A brand whose ground is near-black usually publishes near-black system colours too. Put its error
dark under its header band and page 1 shows two indistinguishable stripes, with the verdict lost.

The tempting fix is to lighten the semantic colour until a luminance gap appears. Resist it: the
result is a colour the company does not own, sitting in the most-looked-at place in the document.
Put a rule in the signature colour between the two bands instead. It separates them, keeps both
colours true, and places the brand accent exactly where the eye already is.

## Contrast thresholds, and why these numbers

Measured as WCAG 2.1 relative-luminance ratio.

| Pair | Minimum | Reason |
|---|---|---|
| `ink` on white | 12:1 | 8.5pt body text, printed |
| `muted` on white | 4.5:1 | 7pt captions — the smallest type in the document |
| `accent` on white | 4.5:1 | headings are large but often thin-weight |
| `band_text` on `band_fill` | 7:1 | reversed-out type loses apparent weight |
| any text on `accent_fill` | 4.5:1 | |
| `zebra` / `header_fill` vs white | ≤ 1.06:1 / ≤ 1.25:1 | banding should be felt, not seen |

`make_theme.py --check` enforces these and names the failing pair.

## Choosing chart series

Order matters more than count. Series 1 gets `accent`, series 2 `accent_fill`, series 3 the
brand's secondary chromatic, then neutrals from dark to light. Two constraints:

- **Adjacent pairs must differ in lightness by ≥ 15 L\*.** Hue alone does not survive a mono
  printer or a red–green colour-vision deficiency.
- **Never use a semantic colour as a neutral series.** A red bar in a chart about headcount reads
  as bad news.

## Worked example — Meridian Partners (meridian.example)

Extracted tokens: rich black `#010506`, jet black `#18191B`, banana yellow `#FFAE19`, gunmetal
`#00818C`, cream `#F4EEE6`, neutral-100 `#FFFCF6`, slate gray `#3F4246`, manatee `#9FA3A9`, light
silver `#D4D5D8`; system colours error-dark `#3B0B0B`, success-dark `#114E0B`, warning-dark
`#5E5515`; heading font Anton, body Plus Jakarta Sans.

The naive read is "yellow brand". The correct read is "near-black brand *with* a yellow signal",
because yellow appears on the site only as a fill behind black text.

| Role | Value | Why |
|---|---|---|
| `ink` | `#18191B` jet black | 16.7:1. Their own black, not `#000`. |
| `muted` | `#3F4246` slate gray | 9.5:1 — comfortably legible at 7pt. |
| `accent` | `#010506` rich black | Yellow fails at 1.9:1, so the darkest brand colour takes headings; the identity arrives through bands instead. |
| `band_fill` / `band_text` | `#010506` / `#FFFCF6` | 20:1. Their site's exact ground. |
| `accent_fill` | `#FFAE19` banana yellow | 12:1 against ink. The rule under the header band and the callout label — used twice, not everywhere. |
| `header_fill` / `zebra` | `#F4EEE6` cream / `#FFFCF6` | Their two cream neutrals, already designed as a pair. |
| `callout` | `#FFF6E6` | 10% yellow over white, computed. |
| verdict / severity | their system darks | `#3B0B0B` / `#5E5515` / `#114E0B` — brand-true *and* semantically correct. Best possible outcome. |
| `chart` | `#010506`, `#FFAE19`, `#00818C`, `#3F4246`, `#9FA3A9`, `#D4D5D8` | Black → yellow → teal, then a neutral ramp descending in lightness. |
| `rule` | `#FFAE19` | The colour that could not be ink becomes every heading rule and the line above the verdict band. |
| `on_band_accent` | `#FFAE19` | 11:1 on their black. Mirrors `text-color-brand`, the way they highlight words inside black headlines. |
| display type | Anton, uppercase, −1.7% tracking → Arial Black in safe mode | Their H1–H3 are all Anton uppercase at −2%. This carries more recognition than the palette does. |
| fonts | Anton / Plus Jakarta Sans, fallback Arial Black / Calibri | Neither brand face is installed on a normal machine — ship `safe`. |

The result reads as Meridian to anyone who knows Meridian, and as a clean executive memo to anyone who does
not. That is the target.
