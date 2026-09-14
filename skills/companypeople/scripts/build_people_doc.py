#!/usr/bin/env python3
"""Render people.json into a Word people-map: org chart + one card per person.

Usage:
    python3 build_people_doc.py people.json --out /path/to/COMPANY_people.docx

Every section is optional. See references/people-schema.md.
"""

import argparse
import hashlib
import json
import os
import tempfile

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ---------------------------------------------------------------- palette
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x6B, 0x6B, 0x6B)
ACCENT = RGBColor(0x0F, 0x3D, 0x5C)
RUST = RGBColor(0xB5, 0x56, 0x3F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT_HEX = "0F3D5C"
BAND_HEX = "0F3D5C"
CALLOUT_HEX = "EEF3F7"
HEADER_HEX = "DCE5EC"
ZEBRA_HEX = "F6F8FA"
MSG_HEX = "FBF3E9"        # the opening-message box — warm, stands out
CARD_HEX = "F9FAFB"
BODY_FONT = "Calibri"

AVATAR_COLORS = ["#0F3D5C", "#4E8FB5", "#B5563F", "#C9A227", "#5C7A5E", "#6E5A7B"]


# ---------------------------------------------------------------- docx helpers
def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def no_borders(table):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        borders.append(el)
    table._tbl.tblPr.append(borders)


def hairlines(table, color="C7CFD6"):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), color)
        borders.append(el)
    table._tbl.tblPr.append(borders)


def run(p, text, size=8.5, bold=False, italic=False, color=INK):
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = BODY_FONT
    return r


def para(container, space_after=3, space_before=0, indent=None, first=False):
    if first and container.paragraphs:
        p = container.paragraphs[0]
        p.text = ""
    else:
        p = container.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if indent is not None:
        pf.left_indent = Inches(indent)
    return p


def hyperlink(p, url, text, size=7.5):
    """Real clickable hyperlink."""
    part = p.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "4E8FB5")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size * 2)))
    rPr.append(color)
    rPr.append(u)
    rPr.append(sz)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    new_run.append(t)
    link.append(new_run)
    p._p.append(link)


def section_label(container, text, color=ACCENT, size=7.5, space_before=3):
    p = para(container, space_after=0, space_before=space_before)
    run(p, text.upper(), size=size, bold=True, color=color)
    return p


def bullets(container, items, size=7.8, indent=0.08):
    """items: str, or {point, evidence}."""
    for it in items:
        p = para(container, space_after=1, indent=indent)
        if isinstance(it, dict):
            run(p, "▪ " + it.get("point", ""), size=size, bold=True)
            if it.get("evidence"):
                run(p, "  " + it["evidence"], size=size, color=MUTED)
        else:
            run(p, "▪ " + str(it), size=size)


# ---------------------------------------------------------------- graphics
def avatar_png(person, outdir, idx):
    """Embed a real photo if a local path is given; else draw an initials disc."""
    photo = person.get("photo_path")
    if photo and os.path.exists(photo):
        return photo

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    name = person.get("name", "?")
    initials = person.get("initials") or "".join(
        w[0] for w in name.split()[:2] if w and w[0].isalpha()
    ).upper() or "?"
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    color = AVATAR_COLORS[h % len(AVATAR_COLORS)]

    fig, ax = plt.subplots(figsize=(1.2, 1.2), dpi=200)
    ax.add_patch(plt.Circle((0.5, 0.5), 0.46, color=color))
    ax.text(0.5, 0.5, initials, ha="center", va="center",
            fontsize=26, color="white", fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    path = os.path.join(outdir, f"avatar_{idx}.png")
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return path


def org_chart_png(spec, outdir):
    """nodes: [{id, name, title, parent, highlight}] — draws a top-down tree."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    nodes = spec.get("nodes", [])
    if not nodes:
        return None
    by_id = {n["id"]: n for n in nodes}

    # depth of each node
    def depth(n, seen=None):
        seen = seen or set()
        p = n.get("parent")
        if not p or p not in by_id or n["id"] in seen:
            return 0
        seen.add(n["id"])
        return 1 + depth(by_id[p], seen)

    levels = {}
    for n in nodes:
        levels.setdefault(depth(n), []).append(n)

    maxw = max(len(v) for v in levels.values())
    nlev = max(levels) + 1
    # Keep the chart shallow: it is a reference strip at the top of the doc, not the doc.
    fig_w = max(7.0, maxw * 1.75)
    fig_h = 0.55 + nlev * 0.62
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)

    pos = {}
    for lvl, group in sorted(levels.items()):
        # keep children near their parent by sorting on parent x where known
        group.sort(key=lambda n: (n.get("parent") or "", n["name"]))
        n_in = len(group)
        for i, n in enumerate(group):
            x = (i + 0.5) / n_in
            y = 1 - (lvl / max(nlev - 1, 1)) if nlev > 1 else 0.5
            pos[n["id"]] = (x, y)

    # edges first, so boxes sit on top
    for n in nodes:
        p = n.get("parent")
        if p in pos and n["id"] in pos:
            x1, y1 = pos[p]
            x2, y2 = pos[n["id"]]
            ymid = (y1 + y2) / 2
            ax.plot([x1, x1, x2, x2], [y1 - 0.055, ymid, ymid, y2 + 0.055],
                    color="#B7C3CC", linewidth=1.1, zorder=1, solid_capstyle="round")

    bw, bh = 0.86 / max(maxw, 1), 0.11
    for n in nodes:
        x, y = pos[n["id"]]
        hi = n.get("highlight")
        face = "#0F3D5C" if hi else "#EEF3F7"
        edge = "#0F3D5C" if hi else "#C7CFD6"
        txt = "white" if hi else "#1A1A1A"
        sub = "#B8D0E0" if hi else "#6B6B6B"
        ax.add_patch(FancyBboxPatch(
            (x - bw / 2, y - bh / 2), bw, bh,
            boxstyle="round,pad=0.008,rounding_size=0.012",
            facecolor=face, edgecolor=edge, linewidth=1.2, zorder=2))
        ax.text(x, y + 0.021, n.get("name", ""), ha="center", va="center",
                fontsize=7.6, fontweight="bold", color=txt, zorder=3)
        ax.text(x, y - 0.028, n.get("title", ""), ha="center", va="center",
                fontsize=6.3, color=sub, zorder=3, wrap=True)

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.12, 1.12)
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    path = os.path.join(outdir, "orgchart.png")
    fig.savefig(path, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return path


# ---------------------------------------------------------------- sections
def build_header(doc, m):
    t = doc.add_table(rows=1, cols=1)
    no_borders(t)
    c = t.rows[0].cells[0]
    shade(c, BAND_HEX)
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = para(c, space_before=4, space_after=1, first=True)
    run(p, m.get("company", "Company"), size=17, bold=True, color=WHITE)
    run(p, "   people map", size=9, color=RGBColor(0xB8, 0xD0, 0xE0))
    if m.get("subtitle"):
        p2 = para(c, space_after=5)
        run(p2, m["subtitle"], size=8, color=RGBColor(0xD4, 0xE2, 0xEB))
    d = para(doc, space_after=6)
    d.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run(d, f"Who to talk to, and what to say · {m.get('date', '')}",
        size=7, italic=True, color=MUTED)


def build_power_read(doc, m):
    items = m.get("power_read", [])
    if not items:
        return
    t = doc.add_table(rows=1, cols=1)
    no_borders(t)
    c = t.rows[0].cells[0]
    shade(c, CALLOUT_HEX)
    p = para(c, space_before=3, space_after=2, first=True)
    run(p, "THE POWER READ", size=9, bold=True, color=ACCENT)
    for it in items:
        bp = para(c, space_after=2, indent=0.08)
        run(bp, "▪ " + it, size=8.5)
    para(doc, space_after=0)


def page_break_before(doc):
    """Start a new page WITHOUT leaving a blank one behind.

    An empty paragraph carrying an explicit break (add_break) is itself laid out on the
    current page; if that page is already full the paragraph lands on a fresh page and the
    break then pushes content on again — producing a blank page. Setting page_break_before
    on a zero-height paragraph avoids this: the paragraph *is* the first thing on the new
    page, and at 1pt it is invisible.
    """
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.page_break_before = True
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    r = p.add_run("")
    r.font.size = Pt(1)
    return p


def build_person_card(doc, person, outdir, idx, page_break=True):
    if page_break:
        page_break_before(doc)

    # --- top: avatar | identity
    t = doc.add_table(rows=1, cols=2)
    no_borders(t)
    t.columns[0].width = Inches(1.15)
    t.columns[1].width = Inches(5.85)

    left = t.cell(0, 0)
    left.width = Inches(1.15)
    left.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    ap = left.paragraphs[0]
    ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ap.paragraph_format.space_after = Pt(2)
    try:
        ap.add_run().add_picture(avatar_png(person, outdir, idx), width=Inches(0.95))
    except Exception:
        run(ap, person.get("initials", "?"), size=20, bold=True, color=ACCENT)

    if person.get("photo_path") and os.path.exists(person["photo_path"]):
        pass  # real photo embedded, no link needed
    elif person.get("photo_url"):
        lp = para(left, space_after=1)
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hyperlink(lp, person["photo_url"], "photo", size=7)
    if person.get("linkedin"):
        lp = para(left, space_after=1)
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hyperlink(lp, person["linkedin"], "LinkedIn", size=7)

    right = t.cell(0, 1)
    right.width = Inches(5.85)
    right.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    hp = para(right, space_after=0, first=True)
    run(hp, person.get("name", ""), size=14, bold=True, color=ACCENT)
    if person.get("location"):
        run(hp, "    " + person["location"], size=7.5, color=MUTED)
    tp = para(right, space_after=2)
    run(tp, person.get("title", ""), size=9.5, bold=True)

    meta = []
    if person.get("reports_to"):
        meta.append("Reports to: " + person["reports_to"])
    if person.get("tenure"):
        meta.append("In role: " + person["tenure"])
    if person.get("prior"):
        meta.append("Prior: " + person["prior"])
    if meta:
        mp = para(right, space_after=3)
        run(mp, "  ·  ".join(meta), size=7.5, color=MUTED)

    if person.get("why_they_matter"):
        wp = para(right, space_after=2)
        run(wp, "WHY THEY MATTER  ", size=7.5, bold=True, color=RUST)
        run(wp, person["why_they_matter"], size=8.5, bold=True)

    # --- body sections, in the order a reader actually needs them:
    # who → what they've done → where that puts them → what they believe → who's with/against them
    if person.get("who_they_are"):
        section_label(doc, "Who they are")
        bullets(doc, person["who_they_are"])

    if person.get("track_record"):
        section_label(doc, "Track record")
        bullets(doc, person["track_record"])

    if person.get("hierarchy"):
        section_label(doc, "Position in the hierarchy")
        p = para(doc, space_after=2, indent=0.08)
        run(p, person["hierarchy"], size=8)

    if person.get("convictions"):
        section_label(doc, "Public convictions")
        bullets(doc, person["convictions"])

    # Allies and counterweights sit side by side: they are the two halves of one question,
    # they read better in opposition, and the card has to fit on one page.
    allies = person.get("allies")
    counter = person.get("counterweights")
    if allies or counter:
        at = doc.add_table(rows=2, cols=2)
        no_borders(at)
        for col, (label, items, col_color) in enumerate([
            ("Allies", allies or [], RGBColor(0x2E, 0x6B, 0x3E)),
            ("Counterweights & tension", counter or [], RUST),
        ]):
            hc = at.cell(0, col)
            hp = para(hc, space_after=1, space_before=3, first=True)
            run(hp, label.upper(), size=7.5, bold=True, color=col_color)
            bc = at.cell(1, col)
            bc.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            firstb = True
            for it in items:
                p = para(bc, space_after=2, indent=0.04, first=firstb)
                firstb = False
                if isinstance(it, dict):
                    run(p, "▪ " + it.get("point", ""), size=7.5, bold=True)
                    if it.get("evidence"):
                        run(p, "  " + it["evidence"], size=7.5, color=MUTED)
                else:
                    run(p, "▪ " + str(it), size=7.5)

    # --- emails
    emails = person.get("emails", [])
    if emails:
        section_label(doc, "Contact — inferred, not verified")
        tb = doc.add_table(rows=0, cols=3)
        hairlines(tb)
        hdr = tb.add_row().cells
        for i, h in enumerate(["Address", "Confidence", "Basis"]):
            shade(hdr[i], HEADER_HEX)
            hp2 = para(hdr[i], space_after=1, first=True)
            run(hp2, h, size=7.5, bold=True)
        for ri, e in enumerate(emails):
            cells = tb.add_row().cells
            conf = e.get("confidence", 0)
            for i in range(3):
                if ri % 2 == 1:
                    shade(cells[i], ZEBRA_HEX)
            p1 = para(cells[0], space_after=1, first=True)
            run(p1, e.get("address", ""), size=8, bold=(ri == 0))
            p2 = para(cells[1], space_after=1, first=True)
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            col = RGBColor(0x2E, 0x6B, 0x3E) if conf >= 75 else (
                RUST if conf < 55 else RGBColor(0x8A, 0x6D, 0x1F))
            run(p2, f"{conf}%", size=8, bold=True, color=col)
            p3 = para(cells[2], space_after=1, first=True)
            run(p3, e.get("basis", ""), size=7.5, color=MUTED)

    # --- the message
    msg = person.get("hook_message")
    if msg:
        mt = doc.add_table(rows=1, cols=1)
        hairlines(mt, color="D9C4A8")
        c = mt.rows[0].cells[0]
        shade(c, MSG_HEX)
        p = para(c, space_before=3, space_after=2, first=True)
        run(p, "THE MESSAGE THAT LANDS", size=7.5, bold=True, color=RUST)
        if msg.get("subject"):
            sp = para(c, space_after=2)
            run(sp, "Subject: ", size=8, bold=True, color=MUTED)
            run(sp, msg["subject"], size=8.5, bold=True)
        bp = para(c, space_after=3)
        run(bp, msg.get("body", ""), size=8.5)
        if msg.get("why_it_works"):
            wp = para(c, space_after=3)
            run(wp, "Why it works: ", size=7.5, bold=True, color=MUTED)
            run(wp, msg["why_it_works"], size=7.5, italic=True, color=MUTED)


def data_table(doc, spec, font=7.5):
    cols = spec.get("columns", [])
    rows = spec.get("rows", [])
    if not rows:
        return
    tb = doc.add_table(rows=0, cols=len(cols))
    hairlines(tb)
    hdr = tb.add_row().cells
    for i, ccol in enumerate(cols):
        shade(hdr[i], HEADER_HEX)
        p = para(hdr[i], space_after=1, first=True)
        run(p, ccol, size=font, bold=True)
    for ri, r in enumerate(rows):
        cells = tb.add_row().cells
        for i in range(len(cols)):
            if ri % 2 == 1:
                shade(cells[i], ZEBRA_HEX)
            p = para(cells[i], space_after=1, first=True)
            run(p, r[i] if i < len(r) else "", size=font, bold=(i == 0))


# ---------------------------------------------------------------- main
def build(m, out_path):
    doc = Document()
    s = doc.sections[0]
    s.top_margin = Inches(0.5)
    s.bottom_margin = Inches(0.5)
    s.left_margin = Inches(0.6)
    s.right_margin = Inches(0.6)
    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = Pt(8.5)
    st.paragraph_format.space_after = Pt(3)

    tmpdir = tempfile.mkdtemp(prefix="people_")

    build_header(doc, m)

    org = m.get("org_chart")
    if org:
        section_label(doc, org.get("title", "Org chart — highlighted = carded below"),
                      size=9, space_before=2)
        path = org_chart_png(org, tmpdir)
        if path:
            doc.add_picture(path, width=Inches(7.0))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if org.get("caption"):
            p = para(doc, space_after=4)
            run(p, org["caption"], size=7, italic=True, color=MUTED)

    build_power_read(doc, m)

    for i, person in enumerate(m.get("people", [])):
        build_person_card(doc, person, tmpdir, i, page_break=True)

    ep = m.get("email_pattern")
    if ep:
        page_break_before(doc)
        section_label(doc, "How the email addresses were derived", size=9)
        p = para(doc, space_after=3)
        run(p, "Pattern: ", size=8.5, bold=True)
        run(p, ep.get("pattern", ""), size=8.5, bold=True, color=ACCENT)
        if ep.get("evidence"):
            p2 = para(doc, space_after=3)
            run(p2, ep["evidence"], size=8)
        if ep.get("caveat"):
            p3 = para(doc, space_after=3)
            run(p3, ep["caveat"], size=8, italic=True, color=MUTED)

    log = m.get("source_log")
    if log:
        section_label(doc, "Source log", size=9)
        data_table(doc, log)

    p = para(doc, space_after=0)
    run(p, m.get("footer_note",
                 "Confidence tags: [A] filed/official · [B] company-stated or credible press · "
                 "[C] inferred. Email addresses are inferred from the company's observed pattern "
                 "and are not verified. Professional contact details only."),
        size=7, italic=True, color=MUTED)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("people_json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.people_json) as f:
        m = json.load(f)
    print("Wrote " + build(m, a.out))


if __name__ == "__main__":
    main()
