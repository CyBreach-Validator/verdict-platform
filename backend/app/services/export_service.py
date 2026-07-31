import csv
import tempfile

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


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
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    document = SimpleDocTemplate(temp.name)

    data = [[
        "ID",
        "Rule",
        "Verdict",
        "Hash",
        "Created At",
    ]]

    for verdict in verdicts:
        data.append([
            verdict.id,
            verdict.rule_name,
            verdict.verdict,
            verdict.verdict_hash,
            str(verdict.created_at),
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ]))

    document.build([table])

    return temp.name