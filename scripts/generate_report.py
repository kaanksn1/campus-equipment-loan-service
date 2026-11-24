#!/usr/bin/env python3
"""Build the eight-section report from evidence using ReportLab and PyMuPDF."""
from pathlib import Path
from report_content import build_pages
from datetime import datetime
import html
import json
import re
from html.parser import HTMLParser
import pymupdf as fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, Spacer, Preformatted, KeepTogether, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"
SUMMARY = json.loads((ROOT / "evidence/summary.json").read_text())
REPORT_DATE = datetime.fromisoformat(SUMMARY["run_time_oslo"]).strftime("%d %B %Y")
CASES = json.loads((ROOT / "evidence/test-cases.json").read_text())
FAULTS = json.loads((ROOT / "evidence/fault-injection/summary.json").read_text())
STUDENT_RUN = json.loads((ROOT / "evidence/student-run.json").read_text())
BY_ID = {row["id"]: row for row in CASES}

CSS = """
body { font-family: sans-serif; font-size: 11pt; line-height: 1.10; color: #182430;
       max-width: 840px; margin: 32px auto; padding: 0 24px; }
p { margin-top: 0; margin-bottom: 6pt; }
h1 { font-size: 16pt; color: #2e74b5; margin-top: 16pt; margin-bottom: 8pt; }
h2 { font-size: 13pt; color: #2e74b5; margin-top: 12pt; margin-bottom: 6pt; }
h3 { font-size: 12pt; color: #1f4d78; margin-top: 8pt; margin-bottom: 4pt; }
.title { font-size: 22pt; color: #0b2545; line-height: 1.08; margin-bottom: 9pt; }
.subtitle { font-size: 12pt; color: #526273; margin-bottom: 10pt; }
.meta { font-size: 10pt; color: #526273; margin-bottom: 4pt; }
.lead { background-color: #f4f6f9; padding: 9pt; margin-top: 10pt; margin-bottom: 12pt; }
table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-top: 6pt; margin-bottom: 10pt; }
th, td { border: 0.5pt solid #cbd3df; padding: 5pt; vertical-align: middle; text-align: left; }
th { background-color: #f2f4f7; font-weight: bold; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
pre { font-family: monospace; font-size: 8.6pt; line-height: 1.18; background-color: #f4f6f9; padding: 7pt; }
code { font-family: monospace; font-size: 9pt; }
ul, ol { margin-top: 2pt; margin-bottom: 8pt; padding-left: 20pt; }
li { margin-bottom: 4pt; }
a { color: #1f4d78; text-decoration: none; }
.small { font-size: 9.5pt; color: #526273; }
"""


def table(headers, rows, widths=None):
    cols = ""
    if widths:
        cols = "<colgroup>" + "".join('<col style="width:' + str(w) + '%">' for w in widths) + "</colgroup>"
    head = "<thead><tr>" + "".join("<th>" + html.escape(str(h)) + "</th>" for h in headers) + "</tr></thead>"
    body = "<tbody>" + "".join("<tr>" + "".join("<td>" + html.escape(str(c)) + "</td>" for c in r) + "</tr>" for r in rows) + "</tbody>"
    return "<table>" + cols + head + body + "</table>"


def counter_ratio(counter):
    covered = counter["covered"]
    total = covered + counter["missed"]
    return f"{covered}/{total} ({100 * covered / total:.2f}%)" if total else "Not applicable"


def build_sections():
    return build_pages(ROOT, SUMMARY, CASES, FAULTS, STUDENT_RUN,
                       REPORT_DATE, table, counter_ratio)


class HtmlNode:
    def __init__(self, tag="root", attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []


class FragmentParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = HtmlNode()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in ("br", "col", "meta", "hr"):
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ("br", "col", "meta", "hr"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def inline(node, plain=False):
    if isinstance(node, str):
        return node if plain else html.escape(node)
    content = "".join(inline(child, plain) for child in node.children)
    if plain:
        return "\n" if node.tag == "br" else content
    if node.tag in ("b", "i", "u"):
        return f"<{node.tag}>" + content + f"</{node.tag}>"
    if node.tag == "br":
        return "<br/>"
    if node.tag == "code":
        return '<font name="Courier" size="9">' + content + '</font>'
    if node.tag == "a":
        return '<a href="' + html.escape(node.attrs["href"], quote=True) + '" color="#1f4d78">' + content + '</a>'
    return content


def render(sections):
    OUT.mkdir(exist_ok=True)
    html_document = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                     '<title>SWE411 Equipment Loan Report</title><style>' + CSS
                     + 'section+section{break-before:page;page-break-before:always}</style>'
                     + ''.join('<section>' + section + '</section>' for section in sections) + '</html>')
    (ROOT / "docs/report.html").write_text(html_document, encoding="utf-8")
    # PDF-specific preset: standard_business_brief, Helvetica substitution for Calibri,
    # with 1-inch margins and a compact 9.3-point repeated-data table style.
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=11, leading=12.1,
                          spaceBefore=0, spaceAfter=6, alignment=TA_LEFT, allowWidows=0, allowOrphans=0)
    styles = {"p": body}
    styles["h1"] = ParagraphStyle("H1", parent=body, fontName="Helvetica-Bold", fontSize=16,
                                  leading=18, textColor=colors.HexColor("#2e74b5"),
                                  spaceBefore=16, spaceAfter=8, keepWithNext=True)
    styles["h2"] = ParagraphStyle("H2", parent=body, fontName="Helvetica-Bold", fontSize=13,
                                  leading=15, textColor=colors.HexColor("#2e74b5"),
                                  spaceBefore=12, spaceAfter=6, keepWithNext=True)
    styles["title"] = ParagraphStyle("Title", parent=body, fontName="Helvetica-Bold", fontSize=22,
                                     leading=24, textColor=colors.HexColor("#0b2545"), spaceAfter=9)
    styles["subtitle"] = ParagraphStyle("Subtitle", parent=body, fontSize=12, leading=14,
                                        textColor=colors.HexColor("#526273"), spaceAfter=10)
    styles["meta"] = ParagraphStyle("Metadata", parent=body, fontSize=10, leading=12,
                                    textColor=colors.HexColor("#526273"), spaceAfter=4)
    styles["lead"] = ParagraphStyle("Lead", parent=body, backColor=colors.HexColor("#f4f6f9"),
                                    borderPadding=8, spaceBefore=10, spaceAfter=12)
    styles["small"] = ParagraphStyle("Small", parent=body, fontSize=9.5, leading=11.2)
    cell_style = ParagraphStyle("Cell", parent=body, fontSize=9.3, leading=11,
                                spaceBefore=0, spaceAfter=0)
    header_style = ParagraphStyle("HeaderCell", parent=cell_style, fontName="Helvetica-Bold")
    code_style = ParagraphStyle("Code", fontName="Courier", fontSize=8.5, leading=10.3,
                                backColor=colors.HexColor("#f4f6f9"), borderPadding=6,
                                spaceBefore=3, spaceAfter=10)
    flow = []
    for section_index, section in enumerate(sections):
        # The instructor limits the complete report, including references, to seven pages.
        if section_index:
            flow.append(PageBreak())
        blocks = [node for node in FragmentParser(section).root.children if isinstance(node, HtmlNode)]
        for index, node in enumerate(blocks):
            if node.tag in ("p", "h1", "h2", "h3"):
                chosen = styles.get(node.attrs.get("class", node.tag), body)
                if node.tag == "p" and index + 1 < len(blocks) and blocks[index + 1].tag == "table":
                    chosen = ParagraphStyle("TableIntro", parent=chosen, keepWithNext=True)
                flow.append(Paragraph(inline(node), chosen))
            elif node.tag == "pre":
                flow.append(Preformatted(inline(node, plain=True), code_style))
            elif node.tag == "table":
                data, widths = [], []
                for group in node.children:
                    if isinstance(group, str):
                        continue
                    if group.tag == "colgroup":
                        for col in group.children:
                            if isinstance(col, HtmlNode) and col.tag == "col":
                                widths.append(float(re.search(r"width:([0-9.]+)%", col.attrs["style"]).group(1)))
                    elif group.tag in ("thead", "tbody"):
                        for row in group.children:
                            if isinstance(row, HtmlNode) and row.tag == "tr":
                                data.append([Paragraph(inline(cell), header_style if cell.tag == "th" else cell_style)
                                             for cell in row.children if isinstance(cell, HtmlNode)])
                geometry = [468 * width / 100 for width in widths] if widths else None
                grid = Table(data, colWidths=geometry, repeatRows=1, hAlign="LEFT", splitByRow=1)
                grid.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f7")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd3df")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                # Move the table's heading/introduction with the complete table, avoiding
                # an isolated heading or a single table row at the end of a page.
                prefix = []
                if index > 0 and blocks[index - 1].tag in ("p", "h1", "h2"):
                    prefix.insert(0, flow.pop())
                    if (blocks[index - 1].tag == "p" and index > 1
                            and blocks[index - 2].tag in ("h1", "h2")):
                        prefix.insert(0, flow.pop())
                flow.append(KeepTogether(prefix + [grid, Spacer(1, 8)]))

    destination = OUT / "220911810_SerdarKaan_Kesen.pdf"
    document = BaseDocTemplate(str(destination), pagesize=(612, 792),
                                  leftMargin=72, rightMargin=72, topMargin=64, bottomMargin=64,
                                  title="Campus Equipment Loan Eligibility and Overdue Fee Service",
                                  author="Serdar Kaan Kesen",
                                  subject="SWE411 implementation and JUnit 5 testing report")
    frame = Frame(72, 64, 468, 664, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, id="body")
    document.addPageTemplates(PageTemplate(id="Report", frames=[frame]))
    document.build(flow)
    pdf = fitz.open(destination)
    if len(pdf) > 7:
        pages = len(pdf)
        pdf.close()
        raise RuntimeError(f"Report has {pages} pages; instructor maximum is 7")
    for i, page in enumerate(pdf):
        page.wrap_contents()
        shade = (0.32, 0.38, 0.45)
        page.insert_text((72, 35), "SWE411 | Campus Equipment Loan Service", fontsize=8, color=shade)
        page.insert_text((72, 755), f"Serdar Kaan Kesen | 220911810 | {REPORT_DATE}", fontsize=8, color=shade)
        label = f"{i + 1} / {len(pdf)}"
        page.insert_text((540 - fitz.get_text_length(label, fontsize=8), 755), label, fontsize=8, color=shade)
    final_pdf = destination.with_suffix(".tmp.pdf")
    pdf.save(final_pdf, garbage=4, deflate=True)
    pdf.close()
    final_pdf.replace(destination)
    pdf = fitz.open(destination)
    qa = ROOT / ".qa/report"
    qa.mkdir(parents=True, exist_ok=True)
    for old in qa.glob("page-*.png"):
        old.unlink()
    for i, page in enumerate(pdf):
        page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(qa / f"page-{i+1}.png")
    print(json.dumps({"report": str(destination), "pages": len(pdf)}, indent=2))
    pdf.close()


if __name__ == "__main__":
    render(build_sections())
