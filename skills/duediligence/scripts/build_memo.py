#!/usr/bin/env python3
"""Render a due-diligence memo.json into a styled 2-page Word memo + exhibits.

Usage:
    python3 build_memo.py memo.json --out /path/to/COMPANY_duedil.docx

Every section is optional: omit a key in memo.json and the section is skipped.
See references/memo-schema.md for the full structure.
"""

import argparse
import json
import os
import tempfile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ---------------------------------------------------------------- palette
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x6B, 0x6B, 0x6B)
ACCENT = RGBColor(0x0F, 0x3D, 0x5C)      # deep slate blue
ACCENT_HEX = "0F3D5C"
BAND_HEX = "0F3D5C"
CALLOUT_HEX = "EEF3F7"
HEADER_HEX = "DCE5EC"
ZEBRA_HEX = "F6F8FA"
POS_HEX = "E8F2EA"   # strengths
NEG_HEX = "FBEDEC"   # weaknesses
NEU_HEX = "F3F1EC"   # opps / threats
BODY_FONT = "Calibri"

CHART_COLORS = ["#0F3D5C", "#4E8FB5", "#9EC5DC", "#C9A227", "#8C8C8C", "#B5563F"]


# ---------------------------------------------------------------- helpers
def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def no_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        borders.append(el)
    tblPr.append(borders)


def hairlines(table, color="C7CFD6"):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblPr.append(borders)


def cell_text(cell, text, size=8.5, bold=False, color=INK, align=None, space_after=1):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.text = ""
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(1)
    pf.space_after = Pt(space_after)
    run = p.add_run(str(text))
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = BODY_FONT
    return p


def cell_bullets(cell, items, size=8, color=INK):
    """items: list of str, or list of {point, evidence}."""
    cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    first = True
    for item in items:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.text = ""
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(3)
        pf.left_indent = Inches(0.10)
        if isinstance(item, dict):
            r = p.add_run("▪ " + item.get("point", ""))
            r.font.size = Pt(size)
            r.font.bold = True
            r.font.color.rgb = color
            r.font.name = BODY_FONT
            ev = item.get("evidence")
            if ev:
                r2 = p.add_run("  " + ev)
                r2.font.size = Pt(size)
                r2.font.color.rgb = MUTED
                r2.font.name = BODY_FONT
        else:
            r = p.add_run("▪ " + str(item))
            r.font.size = Pt(size)
            r.font.color.rgb = color
            r.font.name = BODY_FONT


def heading(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(8)
    pf.space_after = Pt(3)
    pf.keep_with_next = True
    r = p.add_run(text.upper())
    r.font.size = Pt(9)
    r.font.bold = True
    r.font.color.rgb = ACCENT
    r.font.name = BODY_FONT
    # thin rule under the heading
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:color"), ACCENT_HEX)
    bdr.append(bottom)
    pPr.append(bdr)
    return p


def body(doc, text, size=8.5, italic=False, color=INK, space_after=4):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = BODY_FONT
    return p


def data_table(doc, spec, font=8):
    """spec: {columns: [...], rows: [[...], ...], caption: str}"""
    cols = spec.get("columns", [])
    rows = spec.get("rows", [])
    if not cols and not rows:
        return None
    ncols = len(cols) if cols else max(len(r) for r in rows)
    t = doc.add_table(rows=0, cols=ncols)
    t.autofit = True
    hairlines(t)
    if cols:
        hdr = t.add_row().cells
        for i, c in enumerate(cols):
            shade(hdr[i], HEADER_HEX)
            cell_text(hdr[i], c, size=font, bold=True,
                      align=WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i in range(ncols):
            val = row[i] if i < len(row) else ""
            if ri % 2 == 1:
                shade(cells[i], ZEBRA_HEX)
            cell_text(cells[i], val, size=font, bold=(i == 0),
                      align=WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER)
    cap = spec.get("caption")
    if cap:
        body(doc, cap, size=7, italic=True, color=MUTED, space_after=4)
    return t


# ---------------------------------------------------------------- charts
def make_chart(spec, outdir, idx):
    """spec: {type: bar|line|grouped_bar|barh|timeline, title, x, series:[{name,values}], ylabel}"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ctype = spec.get("type", "bar")
    x = spec.get("x", [])
    series = spec.get("series", [])
    title = spec.get("title", "")
    ylabel = spec.get("ylabel", "")

    fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=200)

    if ctype == "line":
        for i, s in enumerate(series):
            ax.plot(x, s.get("values", []), marker="o", linewidth=2,
                    color=CHART_COLORS[i % len(CHART_COLORS)], label=s.get("name", ""))
    elif ctype == "barh":
        s = series[0] if series else {"values": []}
        ax.barh(x, s.get("values", []), color=CHART_COLORS[0], height=0.6)
        ax.invert_yaxis()
    elif ctype in ("grouped_bar", "bar"):
        n = max(len(series), 1)
        width = 0.8 / n
        pos = range(len(x))
        for i, s in enumerate(series):
            offs = [p - 0.4 + width / 2 + i * width for p in pos]
            ax.bar(offs, s.get("values", []), width=width,
                   color=CHART_COLORS[i % len(CHART_COLORS)], label=s.get("name", ""))
        ax.set_xticks(list(pos))
        ax.set_xticklabels(x)
    elif ctype == "timeline":
        # x = labels (e.g. round names/dates), series[0].values = amounts
        s = series[0] if series else {"values": []}
        vals = s.get("values", [])
        ax.plot(range(len(x)), vals, color=CHART_COLORS[1], linewidth=1.5, zorder=1)
        ax.scatter(range(len(x)), vals, s=70, color=CHART_COLORS[0], zorder=2)
        for i, v in enumerate(vals):
            ax.annotate(f"{v:g}", (i, v), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=7)
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, fontsize=7)

    ax.set_title(title, fontsize=9, color="#0F3D5C", fontweight="bold", loc="left", pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=7.5, color="#6B6B6B")
    ax.tick_params(labelsize=7.5, colors="#4A4A4A")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#C7CFD6")
    ax.grid(axis="y", color="#E6EAEE", linewidth=0.7)
    ax.set_axisbelow(True)
    if len([s for s in series if s.get("name")]) > 1:
        ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    path = os.path.join(outdir, f"chart_{idx}.png")
    fig.savefig(path, bbox_inches="tight", transparent=False)
    plt.close(fig)
    return path


def add_chart(doc, spec, outdir, counter):
    try:
        path = make_chart(spec, outdir, counter)
    except Exception as e:  # a broken chart must never kill the memo
        body(doc, f"[chart omitted: {e}]", size=7, italic=True, color=MUTED)
        return
    doc.add_picture(path, width=Inches(6.4))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    src = spec.get("source")
    if src:
        body(doc, src, size=7, italic=True, color=MUTED, space_after=4)


# ---------------------------------------------------------------- sections
def build_header(doc, m):
    h = m.get("header", {})
    t = doc.add_table(rows=1, cols=1)
    no_borders(t)
    c = t.rows[0].cells[0]
    shade(c, BAND_HEX)
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = c.paragraphs[0]
    p.text = ""
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(m.get("company", "Company"))
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    r.font.name = BODY_FONT
    sub = p.add_run("   " + m.get("classification", ""))
    sub.font.size = Pt(9)
    sub.font.color.rgb = RGBColor(0xB8, 0xD0, 0xE0)
    sub.font.name = BODY_FONT

    line = c.add_paragraph()
    line.paragraph_format.space_after = Pt(5)
    bits = [
        h.get("legal_entity"), h.get("ticker"), h.get("hq"),
        f"Founded {h['founded']}" if h.get("founded") else None,
        f"{h['employees']} employees" if h.get("employees") else None,
        h.get("revenue"),
    ]
    txt = "  ·  ".join([b for b in bits if b])
    r2 = line.add_run(txt)
    r2.font.size = Pt(8)
    r2.font.color.rgb = RGBColor(0xD4, 0xE2, 0xEB)
    r2.font.name = BODY_FONT

    if h.get("date"):
        d = body(doc, f"Due diligence brief · {h['date']}", size=7, italic=True,
                 color=MUTED, space_after=6)
        d.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def build_read(doc, m):
    items = m.get("the_read", [])
    hook = m.get("conversation_hook")
    if not items and not hook:
        return
    t = doc.add_table(rows=1, cols=1)
    no_borders(t)
    c = t.rows[0].cells[0]
    shade(c, CALLOUT_HEX)
    p = c.paragraphs[0]
    p.text = ""
    p.paragraph_format.space_before = Pt(3)
    r = p.add_run("THE READ")
    r.font.size = Pt(9)
    r.font.bold = True
    r.font.color.rgb = ACCENT
    r.font.name = BODY_FONT
    for it in items:
        bp = c.add_paragraph()
        bp.paragraph_format.space_after = Pt(2)
        bp.paragraph_format.left_indent = Inches(0.08)
        rr = bp.add_run("▪ " + it)
        rr.font.size = Pt(8.5)
        rr.font.color.rgb = INK
        rr.font.name = BODY_FONT
    c.paragraphs[-1].paragraph_format.space_after = Pt(4)

    if hook:
        hp = c.add_paragraph()
        hp.paragraph_format.space_before = Pt(3)
        hp.paragraph_format.space_after = Pt(1)
        hp.paragraph_format.left_indent = Inches(0.08)
        # top rule to separate the hook from the judgement bullets
        pPr = hp._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        top = OxmlElement("w:top")
        top.set(qn("w:val"), "single")
        top.set(qn("w:sz"), "6")
        top.set(qn("w:color"), "9FB6C6")
        bdr.append(top)
        pPr.append(bdr)

        lbl = hp.add_run("LATEST ON DIGITAL   ")
        lbl.font.size = Pt(7.5)
        lbl.font.bold = True
        lbl.font.color.rgb = RGBColor(0xB5, 0x56, 0x3F)
        lbl.font.name = BODY_FONT
        hd = hp.add_run(hook.get("headline", ""))
        hd.font.size = Pt(8.5)
        hd.font.bold = True
        hd.font.color.rgb = INK
        hd.font.name = BODY_FONT
        if hook.get("date"):
            dt = hp.add_run("  (" + hook["date"] + ")")
            dt.font.size = Pt(7.5)
            dt.font.color.rgb = MUTED
            dt.font.name = BODY_FONT

        wp = c.add_paragraph()
        wp.paragraph_format.space_after = Pt(4)
        wp.paragraph_format.left_indent = Inches(0.08)
        wr = wp.add_run("Why it matters: " + hook.get("why_it_matters", ""))
        wr.font.size = Pt(8.5)
        wr.font.color.rgb = INK
        wr.font.name = BODY_FONT
        if hook.get("source"):
            sr = wp.add_run("  " + hook["source"])
            sr.font.size = Pt(7)
            sr.font.italic = True
            sr.font.color.rgb = MUTED
            sr.font.name = BODY_FONT

    body(doc, "", size=4, space_after=0)


def build_swot(doc, m):
    s = m.get("swot")
    if not s:
        return
    heading(doc, "SWOT — weighted to strengths & weaknesses")
    t = doc.add_table(rows=2, cols=2)
    hairlines(t)
    quads = [
        (0, 0, "STRENGTHS", s.get("strengths", []), POS_HEX),
        (0, 1, "WEAKNESSES", s.get("weaknesses", []), NEG_HEX),
        (1, 0, "OPPORTUNITIES", s.get("opportunities", []), NEU_HEX),
        (1, 1, "THREATS", s.get("threats", []), NEU_HEX),
    ]
    for r_i, c_i, label, items, fill in quads:
        cell = t.cell(r_i, c_i)
        shade(cell, fill)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        p = cell.paragraphs[0]
        p.text = ""
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(label)
        run.font.size = Pt(8)
        run.font.bold = True
        run.font.color.rgb = ACCENT
        run.font.name = BODY_FONT
        holder = cell.add_paragraph()
        holder._p.getparent().remove(holder._p)
        # write bullets directly
        for item in items:
            bp = cell.add_paragraph()
            bp.paragraph_format.space_after = Pt(3)
            bp.paragraph_format.left_indent = Inches(0.06)
            if isinstance(item, dict):
                r1 = bp.add_run("▪ " + item.get("point", ""))
                r1.font.size = Pt(7.5)
                r1.font.bold = True
                r1.font.color.rgb = INK
                r1.font.name = BODY_FONT
                if item.get("evidence"):
                    r2 = bp.add_run("  " + item["evidence"])
                    r2.font.size = Pt(7.5)
                    r2.font.color.rgb = MUTED
                    r2.font.name = BODY_FONT
            else:
                r1 = bp.add_run("▪ " + str(item))
                r1.font.size = Pt(7.5)
                r1.font.color.rgb = INK
                r1.font.name = BODY_FONT


def build_digital_box(doc, d):
    if not d:
        return
    t = doc.add_table(rows=1, cols=1)
    hairlines(t, color=ACCENT_HEX)
    c = t.rows[0].cells[0]
    shade(c, CALLOUT_HEX)
    p = c.paragraphs[0]
    p.text = ""
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("WHO OWNS DIGITAL   ")
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = ACCENT
    r.font.name = BODY_FONT
    r2 = p.add_run(f"{d.get('name', 'Not publicly identifiable')} — {d.get('title', '')}")
    r2.font.size = Pt(9)
    r2.font.bold = True
    r2.font.color.rgb = INK
    r2.font.name = BODY_FONT
    meta = []
    if d.get("reports_to"):
        meta.append("Reports to: " + d["reports_to"])
    if d.get("tenure"):
        meta.append("In role: " + d["tenure"])
    if d.get("background"):
        meta.append("Background: " + d["background"])
    if meta:
        mp = c.add_paragraph()
        mp.paragraph_format.space_after = Pt(1)
        mr = mp.add_run("  ·  ".join(meta))
        mr.font.size = Pt(7.5)
        mr.font.color.rgb = MUTED
        mr.font.name = BODY_FONT
    if d.get("note"):
        np_ = c.add_paragraph()
        np_.paragraph_format.space_after = Pt(3)
        nr = np_.add_run(d["note"])
        nr.font.size = Pt(8)
        nr.font.color.rgb = INK
        nr.font.name = BODY_FONT


# ---------------------------------------------------------------- main
def build(memo, out_path):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.5)
    sec.bottom_margin = Inches(0.5)
    sec.left_margin = Inches(0.6)
    sec.right_margin = Inches(0.6)

    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = Pt(8.5)
    style.paragraph_format.space_after = Pt(3)

    tmpdir = tempfile.mkdtemp(prefix="duedil_charts_")
    chart_i = [0]

    def chart(spec):
        chart_i[0] += 1
        add_chart(doc, spec, tmpdir, chart_i[0])

    # --- page 1-2: the memo
    build_header(doc, memo)
    build_read(doc, memo)

    snap = memo.get("snapshot")
    if snap:
        heading(doc, snap.get("title", "Snapshot"))
        data_table(doc, snap)

    strat = memo.get("strategy")
    if strat:
        heading(doc, "Strategy & positioning")
        if strat.get("prose"):
            body(doc, strat["prose"])
        if strat.get("comparison"):
            data_table(doc, strat["comparison"])

    own = memo.get("ownership")
    if own:
        heading(doc, "Ownership & investors")
        if own.get("table"):
            data_table(doc, own["table"])
        if own.get("so_what"):
            body(doc, "So what: " + own["so_what"], size=8.5, italic=True, color=ACCENT)

    lead = memo.get("leadership")
    if lead:
        heading(doc, "Leadership")
        if lead.get("table"):
            data_table(doc, lead["table"])
        build_digital_box(doc, lead.get("digital_owner"))

    build_swot(doc, memo)

    oq = memo.get("open_questions", [])
    if oq:
        heading(doc, "Open questions to put to the company")
        for q in oq:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Inches(0.1)
            r = p.add_run("? " + q)
            r.font.size = Pt(8.5)
            r.font.color.rgb = INK
            r.font.name = BODY_FONT

    # --- exhibits
    exhibits = memo.get("exhibits", [])
    if exhibits:
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run("EXHIBITS")
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = ACCENT
        r.font.name = BODY_FONT

        for i, ex in enumerate(exhibits):
            if i > 0:
                doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            heading(doc, f"Exhibit {ex.get('id', chr(65 + i))} — {ex.get('title', '')}")
            if ex.get("prose"):
                body(doc, ex["prose"])
            if ex.get("chart"):
                chart(ex["chart"])
            if ex.get("table"):
                data_table(doc, ex["table"], font=7.5)
            for extra in ex.get("tables", []):
                data_table(doc, extra, font=7.5)
            if ex.get("notes"):
                body(doc, ex["notes"], size=7.5, italic=True, color=MUTED)

    # --- footer note
    body(doc, memo.get("confidence_note",
                       "Confidence tags: [A] audited/filed  ·  [B] company-stated or credible press  "
                       "·  [C] estimated or inferred."),
         size=7, italic=True, color=MUTED, space_after=0)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("memo_json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.memo_json) as f:
        memo = json.load(f)
    path = build(memo, args.out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
