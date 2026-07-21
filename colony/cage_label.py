"""
colony/cage_label.py

Generates a 4x6" cage label PDF for the KNAON Y41BT (or any 4x6" printer).
Matches the actual musculus models:
    Cage.cage_id, Cage.cage_location, Cage.mating_pair
    Mouse.tag, Mouse.alt_id, Mouse.dob, Mouse.mouse_line (FK -> MouseLine.name),
    Mouse.sex, Mouse.protocol (FK -> Protocol.name), Mouse.status
    Cage.mice  -> related_name on Mouse.cage
"""

import io
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

LABEL_WIDTH = 4 * inch
LABEL_HEIGHT = 6 * inch
MARGIN_X = 3 * cm
MARGIN_Y = 2 * cm


def _p(text, style):
    """Paragraph() treats its input as markup, so any '&', '<', '>' in real
    lab data (e.g. cage_location = "Rack A & B") would otherwise crash
    doc.build() with a parser error. Escape everything before wrapping."""
    return Paragraph(xml_escape(str(text)), style)


def _genotype_summary(mouse):
    """'Cre:HOM, fl/fl:HET' style summary from the MouseGenotype through model."""
    parts = [
        f"{mg.tag.label}:{mg.zygosity}"
        for mg in mouse.genotype_entries.select_related("tag").all()
    ]
    return ", ".join(parts)


COLUMNS = [
    ("ID", lambda m: m.tag, 0.5 * inch),
    ("Alt", lambda m: m.alt_id, 0.42 * inch),
    ("DOB", lambda m: m.dob.strftime("%m/%d/%y") if m.dob else "", 0.42 * inch),
    ("Line", lambda m: m.mouse_line.name if m.mouse_line_id else "", 0.42 * inch),
    ("Geno", _genotype_summary, 0.62 * inch),
    ("Sex", lambda m: m.sex, 0.22 * inch),
    ("Proto", lambda m: m.protocol.name if m.protocol_id else "", 0.42 * inch),
    ("Stat", lambda m: m.get_status_display(), 0.42 * inch),
]


def render_cage_label_pdf(cage):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=(LABEL_WIDTH, LABEL_HEIGHT),
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_Y, bottomMargin=MARGIN_Y,
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        "CageHeader", parent=styles["Heading2"], fontSize=14,
        alignment=TA_CENTER, spaceAfter=2, leading=16,
    )
    sub_style = ParagraphStyle(
        "CageSub", parent=styles["Normal"], fontSize=9.5,
        alignment=TA_CENTER, spaceAfter=4,
    )
    pair_style = ParagraphStyle(
        "CagePair", parent=styles["Normal"], fontSize=8.5,
        alignment=TA_CENTER, spaceAfter=8, textColor=colors.HexColor("#555555"),
    )
    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=4.2, leading=4.8)
    header_cell_style = ParagraphStyle(
        "HeaderCell", parent=cell_style, fontName="Helvetica-Bold", textColor=colors.white,
    )

    story = [
        _p(f"Cage {cage.cage_id}", header_style),
        _p(f"Location: {cage.cage_location}", sub_style),
    ]
    if cage.mating_pair_id:
        mp = cage.mating_pair
        started = mp.start_date.strftime("%m/%d/%y") if mp.start_date else "?"
        story.append(_p(
            f"Mating pair: {mp.male.tag if mp.male_id else '?'} × "
            f"{mp.female.tag if mp.female_id else '?'} (started {started})",
            pair_style,
        ))
    else:
        story.append(_p(" ", pair_style))

    header_row = [_p(label, header_cell_style) for label, _, _ in COLUMNS]
    data = [header_row]
    for mouse in cage.mice.all():
        data.append([
            _p(getter(mouse) or "", cell_style)
            for _, getter, _ in COLUMNS
        ])

    col_widths = [w for _, _, w in COLUMNS]
    usable_width = LABEL_WIDTH - 2 * MARGIN_X
    total_width = sum(col_widths)
    if total_width > usable_width:
        scale = usable_width / total_width
        col_widths = [w * scale for w in col_widths]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ]))
    story.append(table)

    doc.build(story)
    buf.seek(0)
    return buf
