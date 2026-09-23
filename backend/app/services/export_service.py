import csv
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
)


def generate_csv(verdicts):
    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        newline="",
        encoding="utf-8",
    )

    writer = csv.writer(temp)

    writer.writerow([
        "ID",
        "Rule ID",
        "Rule Name",
        "Verdict",
        "Verdict Hash",
        "Created At",
    ])

    for verdict in verdicts:
        writer.writerow([
            verdict.id,
            verdict.rule_id,
            verdict.rule_name,
            verdict.verdict,
            verdict.verdict_hash,
            verdict.created_at,
        ])

    temp.close()
    return temp.name


def generate_pdf(verdicts):
    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    )

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        temp.name,
        pagesize=landscape(A4),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
    )

    header_style = styles["Normal"]
    header_style.fontName = "Helvetica-Bold"
    header_style.fontSize = 8
    header_style.leading = 10

    body_style = styles["Normal"]
    body_style.fontSize = 7
    body_style.leading = 9

    data = [[
        Paragraph("ID", header_style),
        Paragraph("Rule", header_style),
        Paragraph("Verdict", header_style),
        Paragraph("Hash", header_style),
        Paragraph("Created At", header_style),
    ]]

    for verdict in verdicts:
        data.append([
            Paragraph(str(verdict.id), body_style),
            Paragraph(str(verdict.rule_name), body_style),
            Paragraph(str(verdict.verdict), body_style),
            Paragraph(str(verdict.verdict_hash), body_style),
            Paragraph(str(verdict.created_at), body_style),
        ])

    table = Table(
        data,
        colWidths=[35, 150, 65, 190, 135],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    document.build([table])

    return temp.name