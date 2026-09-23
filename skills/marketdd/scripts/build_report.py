"""marketdd report builder — report.json -> Word (.docx) + PDF, with layout check.

    python3 build_report.py report.json --out <dir>/SECTOR_marketdd.docx [--no-pdf]

- Enforces the fixed 10-section skeleton (keys below, in order); headings are localised
  automatically from report["lang"] ("en" default, "fr").
- Renders every chart spec through charts.py, numbers exhibits in order.
- No forced page breaks except after the cover, after the executive summary and before the
  sources annex; charts are kept with their captions and table rows never split, so pages
  do not end half-empty.
- Converts to PDF with LibreOffice and prints the fill ratio of every page; any page below
  35 % (other than the cover and the last page) is reported as a layout warning.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).parent))
import charts  # noqa: E402

SKELETON = ["summary", "scope", "value_chain", "depth_growth", "demand", "players",
            "moves", "segments", "trends", "implications"]
HEADINGS = {
    "en": {"summary": "Executive summary — what to remember", "scope": "Scope, definitions and method",
           "value_chain": "The value chain: where the money goes", "depth_growth": "Market depth and growth",
           "demand": "Demand structure: who buys, and how many", "players": "The players, segment by segment",
           "moves": "Market moves: consolidation and capital", "segments": "Customer segments and who targets them",
           "trends": "The 5 customer trends for the next 5–10 years",
           "implications": "Implications and what we don't know yet", "sources": "Annex — Sources",
           "exhibit": "Exhibit", "page": "p.", "prepared": "Prepared by",
           "legend_title": "Confidence levels — ",
           "legend": "[A] published by a primary source (statistics office, regulator, annual report, filing, "
                     "recognised analyst house) and checked; [B] secondary source or explicitly derived from [A] "
                     "figures; [C] analyst judgement, to be validated through interviews or a data room."},
    "fr": {"summary": "Synthèse — ce qu'il faut retenir", "scope": "Périmètre, définitions et méthode",
           "value_chain": "La chaîne de valeur : où va l'argent", "depth_growth": "Profondeur et croissance des marchés",
           "demand": "Structure de la demande : qui achète, et combien sont-ils",
           "players": "Les acteurs, segment par segment", "moves": "Les mouvements du marché : consolidation et capital",
           "segments": "Les segments clients et qui les vise en priorité",
           "trends": "Les 5 grandes tendances clients à 5–10 ans",
           "implications": "Implications et ce que nous ne savons pas encore", "sources": "Annexe — Sources",
           "exhibit": "Exhibit", "page": "p.", "prepared": "Préparé par",
           "legend_title": "Niveaux de confiance — ",
           "legend": "[A] donnée publiée par une source primaire (institut statistique, régulateur, rapport annuel, "
                     "dépôt réglementaire, cabinet d'analyse reconnu) et vérifiée ; [B] source secondaire ou dérivée "
                     "par calcul explicite à partir de données [A] ; [C] jugement d'analyste, à valider par entretiens "
                     "ou data room."},
}

BLUE = RGBColor(0x10, 0x42, 0x81); INK = RGBColor(0x0b, 0x0b, 0x0b)
GREY = RGBColor(0x52, 0x51, 0x4e); ORANGE = RGBColor(0xeb, 0x68, 0x34); WHITE = RGBColor(0xff, 0xff, 0xff)


class Report:
    def __init__(self, data, fig_dir):
        self.d = data
        self.lang = data.get("lang", "en")
        if self.lang not in HEADINGS:
            raise ValueError("lang must be 'en' or 'fr'")
        self.H = HEADINGS[self.lang]
        self.fig_dir = fig_dir
        self.n = 0
        self.doc = Document()
        self._styles()

    # ------------------------------------------------------------ setup
    def _styles(self):
        s = self.doc.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
        st = self.doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        st.paragraph_format.space_after = Pt(5); st.paragraph_format.line_spacing = 1.12
        for lvl, size, c in [(1, 17, BLUE), (2, 13, BLUE), (3, 11.5, INK)]:
            h = self.doc.styles[f"Heading {lvl}"]; h.font.name = "Calibri"; h.font.size = Pt(size)
            h.font.bold = True; h.font.color.rgb = c; h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
            h.paragraph_format.space_before = Pt(14 if lvl == 1 else 10); h.paragraph_format.space_after = Pt(5)
            h.paragraph_format.keep_with_next = True
        m = self.d["meta"]
        p = s.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(f"{m.get('footer', m['title'])} · {self.H['page']} "); r.font.size = Pt(8); r.font.color.rgb = GREY
        for kind, txt in [("begin", None), (None, "PAGE"), ("end", None)]:
            run = p.add_run(); run.font.size = Pt(8)
            if kind:
                e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), kind)
            else:
                e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
            run._r.append(e)

    # ------------------------------------------------------------ primitives
    def para(self, text, lead=None, size=None, color=None, italic=False):
        p = self.doc.add_paragraph()
        if lead:
            r = p.add_run(lead); r.bold = True
            if size: r.font.size = Pt(size)
        r = p.add_run(text); r.italic = italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
        return p

    def bullets(self, items, numbered=False):
        for it in items:
            p = self.doc.add_paragraph(style="List Number" if numbered else "List Bullet")
            p.paragraph_format.space_after = Pt(2)
            if isinstance(it, (list, tuple)):
                r = p.add_run(it[0]); r.bold = True; p.add_run(it[1])
            else:
                p.add_run(it)

    @staticmethod
    def _shade(cell, hexcol):
        tcPr = cell._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
        s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hexcol); tcPr.append(s)

    def table(self, header, rows, widths=None, size=8.3):
        widths = widths or [17.0 / len(header)] * len(header)
        if abs(sum(widths) - 17.0) > 0.6:
            widths = [w * 17.0 / sum(widths) for w in widths]
        t = self.doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(header):
            c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(str(h)); r.bold = True
            r.font.size = Pt(size); r.font.color.rgb = WHITE; self._shade(c, "104281")
        for k, row in enumerate(rows):
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""; par = cells[i].paragraphs[0]; par.paragraph_format.space_after = Pt(0)
                r = par.add_run(str(v)); r.font.size = Pt(size); r.bold = (i == 0)
                if k % 2 == 1: self._shade(cells[i], "F4F3EF")
        for row in t.rows:
            row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        t.autofit = False
        for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(int(w * 567)))
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def callout(self, title, items):
        t = self.doc.add_table(rows=1, cols=1); c = t.rows[0].cells[0]; self._shade(c, "EAF2FC"); c.text = ""
        r = c.paragraphs[0].add_run(title); r.bold = True; r.font.color.rgb = BLUE; r.font.size = Pt(10)
        for line in items:
            q = c.add_paragraph(); q.paragraph_format.space_after = Pt(2)
            rr = q.add_run(line); rr.font.size = Pt(9.5)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def exhibit(self, chart, caption, width=17):
        path = charts.render(chart, self.fig_dir, self.lang)
        self.n += 1
        self.doc.add_picture(path, width=Cm(width))
        pic = self.doc.paragraphs[-1]; pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic.paragraph_format.keep_with_next = True
        p = self.doc.add_paragraph()
        r = p.add_run(f"{self.H['exhibit']} {self.n} — "); r.bold = True; r.font.size = Pt(8.5); r.font.color.rgb = BLUE
        r = p.add_run(caption); r.font.size = Pt(8.5); r.font.color.rgb = GREY; r.italic = True
        p.paragraph_format.space_after = Pt(10)

    def block(self, b):
        t = b["type"]
        if t == "paragraph": self.para(b["text"], lead=b.get("lead"))
        elif t == "note": self.para(b["text"], italic=True, color=GREY, size=8.5)
        elif t == "heading": self.doc.add_heading(b["text"], b.get("level", 3))
        elif t == "bullets": self.bullets(b["items"], b.get("numbered", False))
        elif t == "callout": self.callout(b["title"], b["items"])
        elif t == "table": self.table(b["header"], b["rows"], b.get("widths"), b.get("size", 8.3))
        elif t == "exhibit": self.exhibit(b["chart"], b["caption"], b.get("width", 17))
        elif t == "page_break": self.doc.add_page_break()
        else: raise ValueError(f"Unknown block type '{t}'")

    # ------------------------------------------------------------ document
    def cover(self):
        m = self.d["meta"]; doc = self.doc
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(60)
        r = p.add_run(m.get("kicker", "MARKET DEEP DIVE" if self.lang == "en" else "DEEP DIVE MARCHÉ"))
        r.font.size = Pt(10); r.bold = True; r.font.color.rgb = ORANGE
        p = doc.add_paragraph(); r = p.add_run(m["title"]); r.font.size = Pt(30); r.bold = True; r.font.color.rgb = BLUE
        if m.get("subtitle"):
            p = doc.add_paragraph(); r = p.add_run(m["subtitle"]); r.font.size = Pt(13); r.font.color.rgb = GREY
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(18)
        r = p.add_run(" · ".join(x for x in [m.get("project"), m.get("version"), m.get("date")] if x))
        r.font.size = Pt(10); r.bold = True
        if m.get("author"):
            p = doc.add_paragraph(); r = p.add_run(f"{self.H['prepared']} {m['author']}")
            r.font.size = Pt(10); r.font.color.rgb = GREY
        if self.d.get("kpis"):
            doc.add_paragraph()
            spec = {"type": "tiles", "id": "e00_kpis", "title": self.d.get("kpis_title",
                    "The market in numbers" if self.lang == "en" else "Le marché en chiffres"),
                    "items": self.d["kpis"], "source": self.d.get("kpis_source")}
            doc.add_picture(charts.render(spec, self.fig_dir, self.lang), width=Cm(17))
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(20)
        r = p.add_run(self.H["legend_title"]); r.bold = True; r.font.size = Pt(8.5)
        r = p.add_run(self.H["legend"] + (" " + m["fx_note"] if m.get("fx_note") else ""))
        r.font.size = Pt(8.5); r.font.color.rgb = GREY
        doc.add_page_break()

    def build(self):
        secs = self.d["sections"]
        missing = [k for k in SKELETON if k not in secs]
        if missing:
            raise ValueError(f"Missing skeleton sections: {missing}. All 10 are mandatory (see report-schema.md).")
        self.cover()
        for i, key in enumerate(SKELETON, 1):
            self.doc.add_heading(f"{i}. {secs[key].get('heading', self.H[key])}", 1)
            for b in secs[key]["blocks"]:
                self.block(b)
            if key == "summary":
                self.doc.add_page_break()
        self.doc.add_page_break()
        self.doc.add_heading(self.H["sources"], 1)
        for s in self.d.get("sources", []):
            p = self.doc.add_paragraph(style="List Number"); r = p.add_run(s); r.font.size = Pt(8.5)
            p.paragraph_format.space_after = Pt(1)
        return self.doc


def to_pdf(docx_path):
    out = Path(docx_path).parent
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(docx_path)],
                   check=True, capture_output=True)
    return out / (Path(docx_path).stem + ".pdf")


def check_layout(pdf_path, threshold=35):
    """Return [(page, fill%)] and print warnings for underfilled pages."""
    from PIL import Image
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-gray", "-r", "30", str(pdf_path), f"{tmp}/g"], check=True)
    pages = sorted(Path(tmp).glob("g-*.pgm"))
    res = []
    for i, f in enumerate(pages, 1):
        im = Image.open(f); w, h = im.size; px = im.load()
        top, bot = int(h * 0.06), int(h * 0.93); last = top
        for y in range(top, bot):
            if any(px[x, y] < 200 for x in range(int(w * .08), int(w * .92), 2)):
                last = y
        res.append((i, round((last - top) / (bot - top) * 100)))
    warn = [(p, f) for p, f in res if f < threshold and p not in (1, 2, len(res))]  # cover, summary page (intentional break) and annex are exempt
    print("Page fill %:", " ".join(f"p{p}={f}" for p, f in res))
    if warn:
        print("LAYOUT WARNING — underfilled pages:", warn,
              "→ remove a manual page_break, move an exhibit up, or trim the preceding table.")
    else:
        print("Layout OK — no underfilled page.")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_json"); ap.add_argument("--out", required=True)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    data = json.load(open(a.report_json, encoding="utf-8"))
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    fig_dir = Path(tempfile.mkdtemp(prefix="marketdd_fig_"))  # exhibits stay out of the deliverable folder
    Report(data, fig_dir).build().save(out)
    print("DOCX:", out)
    if not a.no_pdf:
        pdf = to_pdf(out); print("PDF:", pdf)
        check_layout(pdf)


if __name__ == "__main__":
    main()
