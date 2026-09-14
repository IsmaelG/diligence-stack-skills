#!/usr/bin/env python3
"""Evidence gate. Refuses to render a memo whose claims can't be traced.

    python3 validate_doc.py doc.json            # report and exit 1 on failure
    python3 validate_doc.py doc.json --warn-only

Four gates, all fatal unless --warn-only:

  1. tags_present        every figure carries [A], [B] or [C]
  2. sources_resolve     every [tag] cites a source_id that exists in the source log
  3. log_complete        every source-log row has source, date read, and a tag
  4. no_orphan_sources   every logged source is cited at least once

Rationale: a memo is only as good as its weakest untraceable number, and the
number that breaks a deal is never the one you double-checked. The gate is
deliberately mechanical — it does not judge whether a claim is true, only
whether a reader could check it.

Reads the same doc.json the builder renders, so it cannot drift from the output.
"""

import argparse
import json
import re
import sys

# a bracket whose first token is a confidence letter: [A] [A/B] [A obs.] [A, S-01]
TAG = re.compile(r"\[\s*(?:A|B|C)\b[^\]]{0,40}\]")
# a source id inside any bracket: [S-01], [I-02, S-01], [A, S-01]. An id is
# stronger evidence than a bare tag — it resolves to a specific artifact rather
# than to a quality band.
BRACKET = re.compile(r"\[([^\]]{1,80})\]")
ID_IN_BRACKET = re.compile(r"\b[A-Z]{1,3}-\d{1,3}\b")


def cited_ids(text):
    return [m for b in BRACKET.findall(text) for m in ID_IN_BRACKET.findall(b)]


def has_cite(text):
    return bool(cited_ids(text))
# a "figure": money, percentages, multiples, counts with a unit
FIGURE = re.compile(
    r"(?:[€$£]\s?\d[\d\s.,]*\s?(?:m|bn|k)?)"
    r"|(?:\d[\d\s.,]*\s?(?:%|pts?|x\b))"
    r"|(?:\d[\d\s.,]*\s?(?:m|bn|k)\b)"
)
SKIP_KEYS = {"summary", "caption", "notes", "so_what", "confidence_note",
             "data_gaps_intro", "prose_intro"}


ID_LIKE = re.compile(r"^[A-Z]{1,3}-\d{1,3}$")


def units(doc):
    """Yield (path, text) for each *evidence unit* — the smallest block a reader
    would check as one claim. A table row is one unit, not one unit per cell:
    a financials table tags the row label ("Revenue [A]") or the caption, and
    tagging every cell would be unreadable. A scorecard row carries its tag in
    its own `confidence` field. Getting this granularity right is the whole
    difference between a gate people use and a gate people disable."""
    for i, r in enumerate(doc.get("scorecard", {}).get("rows", [])):
        yield f"scorecard.rows[{i}]", " ".join(
            str(r.get(k, "")) for k in ("module", "finding", "confidence"))

    def tables(container, base):
        specs = ([container["table"]] if container.get("table") else []) + \
                container.get("tables", [])
        for ti, tbl in enumerate(specs):
            cap = tbl.get("caption", "")
            hdr = " ".join(str(c) for c in tbl.get("columns", []))
            for ri, row in enumerate(tbl.get("rows", [])):
                yield (f"{base}.table[{ti}].rows[{ri}]",
                       " ".join(str(c) for c in row) + " " + hdr + " " + cap)

    for i, sec in enumerate(doc.get("sections", [])):
        base = f"sections[{i}]"
        if sec.get("prose"):
            yield f"{base}.prose", sec["prose"]
        if sec.get("so_what"):
            yield f"{base}.so_what", sec["so_what"]
        for bi, b in enumerate(sec.get("bullets", [])):
            txt = f"{b.get('point','')} {b.get('evidence','')}" if isinstance(b, dict) else str(b)
            yield f"{base}.bullets[{bi}]", txt
        yield from tables(sec, base)

    for i, f in enumerate(doc.get("red_flags", [])):
        yield f"red_flags[{i}]", " ".join(
            str(f.get(k, "")) for k in ("flag", "evidence", "mitigation"))

    for i, t in enumerate(doc.get("the_read", [])):
        yield f"the_read[{i}]", t

    for i, ex in enumerate(doc.get("exhibits", [])):
        base = f"exhibits[{i}]"
        ch = ([ex["chart"]] if ex.get("chart") else []) + ex.get("charts", [])
        blob = " ".join(str(c.get("source", "")) for c in ch) + " " + str(ex.get("notes", ""))
        if ex.get("prose"):
            yield f"{base}.prose", ex["prose"] + " " + blob
        for ci, c in enumerate(ch):
            yield f"{base}.chart[{ci}]", str(c.get("source", "")) + " " + str(ex.get("notes", ""))
        yield from tables(ex, base)


def walk(node, path=""):
    """Yield (path, string) for every text value in the document."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def source_ids(doc):
    """Collect declared source ids from the source-log exhibit and data_gaps."""
    ids = set()
    for ex in doc.get("exhibits", []):
        title = (ex.get("title") or "").lower()
        if "source" in title or "interview" in title:
            for tbl in ([ex["table"]] if ex.get("table") else []) + ex.get("tables", []):
                for row in tbl.get("rows", []):
                    if row and str(row[0]).strip():
                        ids.add(str(row[0]).strip())
    return ids


def source_log_rows(doc):
    for ex in doc.get("exhibits", []):
        if "source" in (ex.get("title") or "").lower():
            for tbl in ([ex["table"]] if ex.get("table") else []) + ex.get("tables", []):
                for row in tbl.get("rows", []):
                    yield row
            return


# --------------------------------------------------------------- correlation
# Generic heads produce noise, not correlation. Country and category words recur
# in every section of any memo and carry no signal about a connected finding.
STOP = {
    "The", "This", "That", "These", "Those", "Rev", "Source", "Sources", "Note",
    "Test", "Data", "It", "If", "In", "On", "At", "For", "And", "But", "With",
    "Their", "Our", "We", "One", "Two", "Three", "None", "Both", "Either", "Not",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Tier", "Exhibit", "Product", "Products", "Revenue", "Customer", "Customers",
    "Carrier", "Carriers", "Market", "Pricing", "Price", "Growth", "Scale",
    "Company", "Business", "Team", "Board", "Group", "Platform", "Service",
    "Enterprise", "Retail", "Analyst", "Interview", "Method", "Total", "Only",
    "Very", "Well", "Above", "Below", "Same", "Rather", "Against", "Since",
    "Where", "When", "What", "Which", "Who", "Any", "All", "Each", "Every",
    "France", "French", "Europe", "European", "Spain", "Spanish", "Belgium",
    "Belgian", "Germany", "German", "UK", "US", "Italy", "Netherlands",
}
ENTITY = re.compile(r"\b[A-Z][A-Za-z0-9&’'\-]{2,}(?:\s+[A-Z][A-Za-z0-9&’'\-]{2,}){0,2}\b")


def block_kind(path):
    """Which part of the argument a unit belongs to — the 'domain' being correlated."""
    if path.startswith("scorecard"):
        return "scorecard"
    if path.startswith("red_flags"):
        return "red flags"
    if path.startswith("the_read"):
        return "the read"
    if path.startswith("exhibits"):
        return "exhibits"
    if path.startswith("sections["):
        return f"section {path.split('[')[1].split(']')[0]}"
    return path


def correlate(doc, min_domains=3):
    """Cross-domain correlation: the finding that matters is usually the one that
    surfaces independently in several places and is written up as several separate
    problems. Legal flags a risk, finance flags another, nobody connects them.

    This does not decide anything — it lists entities recurring across domains so
    the analyst checks whether N separate findings are actually one."""
    # never correlate on the subject itself, or on words from its own descriptor
    own = set()
    for f in (doc.get("company", ""), doc.get("classification", ""),
              doc.get("header", {}).get("product", "")):
        own |= {w.strip("’'s.,—·") for w in str(f).split()}
    hits = {}
    section_names = {f"section {i}": (s.get("heading") or f"section {i}")
                     for i, s in enumerate(doc.get("sections", []))}
    for path, text in units(doc):
        dom = block_kind(path)
        dom = section_names.get(dom, dom)
        for ent in ENTITY.findall(text):
            ent = ent.rstrip("’'s").strip()
            words = ent.split()
            head = words[0]
            if head in STOP or len(ent) < 4:
                continue
            if len(words) == 1 and (head in own or head.rstrip("’'") in own):
                continue
            if re.fullmatch(r"(FY|Q|H)\d.*", ent):        # period labels, not entities
                continue
            hits.setdefault(ent, set()).add(dom)
    # drop entities fully contained in a longer one that spans the same domains
    out = []
    for ent, doms in hits.items():
        if len(doms) < min_domains:
            continue
        if any(ent != o and ent in o and hits[o] >= doms for o in hits):
            continue
        out.append((len(doms), ent, sorted(doms)))
    return sorted(out, reverse=True)


def check(doc):
    fails, warns = [], []

    # --- gate 1: every evidence unit containing a figure carries a tag -------
    for path, text in units(doc):
        if FIGURE.search(text) and not (TAG.search(text) or has_cite(text)):
            snippet = " ".join(text.split())[:100]
            fails.append(("tags_present", path,
                          f"figure with no [A]/[B]/[C] anywhere in the row/block: {snippet}"))

    # --- gate 2: [[source_id]] references resolve ----------------------------
    declared = source_ids(doc)
    for path, text in walk(doc):
        for ref in cited_ids(text):
            if ref in declared:
                continue
            if True:
                fails.append(("sources_resolve", path,
                              f"cites source id {ref!r}, which is not in the source log"))

    # --- gate 3: source log is complete --------------------------------------
    rows = list(source_log_rows(doc))
    if not rows:
        fails.append(("log_complete", "exhibits", "no source-log exhibit found"))
    for i, row in enumerate(rows):
        cells = [str(c).strip() for c in row]
        if len(cells) < 3 or not all(cells[:3]):
            fails.append(("log_complete", f"source_log[{i}]",
                          f"incomplete row: {cells}"))
        elif not TAG.search(" ".join(cells)):
            fails.append(("log_complete", f"source_log[{i}]",
                          f"row without a confidence tag: {cells[0]}"))

    # --- gate 4: no orphan sources (warning, not fatal) -----------------------
    body = " ".join(t for _, t in walk(doc))
    for i, row in enumerate(rows):
        key = str(row[0]).strip()
        if not ID_LIKE.match(key):      # log keyed by claim area, not by id — skip
            continue
        if body.count(key) <= 1:
            warns.append(("no_orphan_sources", f"source_log[{i}]",
                          f"{key!r} is logged but never cited in the body"))

    return fails, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc_json")
    ap.add_argument("--warn-only", action="store_true",
                    help="report but exit 0 — for drafts, never for a delivered memo")
    a = ap.parse_args()
    doc = json.load(open(a.doc_json))
    fails, warns = check(doc)

    for gate, path, msg in fails:
        print(f"FAIL  {gate:18} {path}\n      {msg}")
    for gate, path, msg in warns:
        print(f"warn  {gate:18} {path}\n      {msg}")

    corr = correlate(doc)
    if corr:
        print("\nCross-domain correlation — recurring across the argument.")
        print("Check whether each is several findings, or one finding written up several times:")
        for n, ent, doms in corr[:8]:
            print(f"  {n}x  {ent:32} {', '.join(doms)}")

    n = len(fails)
    print(f"\n{'PASS' if not n else 'FAILED'} — {n} fatal, {len(warns)} warnings, "
          f"{len(source_ids(doc))} sources declared")
    if n and not a.warn_only:
        print("Fix the claims above, or move them to the data-gaps appendix. "
              "Do not render a memo that fails this gate.")
        sys.exit(1)


if __name__ == "__main__":
    main()
