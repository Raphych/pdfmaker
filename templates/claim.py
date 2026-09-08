from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from babel.numbers import format_currency
import datetime

from templates.parts.contactDetails import draw_contact_details
from templates.parts.htmlFlowables import html_to_flowables
from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns, draw_simple_table


styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

STATUS_LABELS = {
    "open": "Open",
    "in_progress": "In Progress",
    "resolved": "Resolved",
    "rejected": "Rejected",
}


def _parse_date(value):
    if not value:
        return ""
    try:
        return datetime.datetime.fromisoformat(value.rstrip('Z')).strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        return ""


def generate_claim(buffer, data):
    margins = layout()
    title = data.get("filename", "claim.pdf")
    header = "SUPPLIER CLAIM"

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=margins['right'],
        leftMargin=margins['left'],
        topMargin=margins['top'],
        bottomMargin=margins['bottom'],
        title=title,
    )

    elements = []
    currency = data.get("currency", "USD")

    # Row 1: Company coordinates + claim meta
    coordinates = draw_contact_details(data.get("coordinates", None))
    details = _draw_claim_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(400, 20))

    # Row 2: Supplier
    supplier_block = draw_contact_details(data.get("supplier", None), "Claim Against")
    elements.append(draw_independent_columns([supplier_block, Spacer(1, 1)]))
    elements.append(Spacer(400, 20))

    # Row 3: Related documents + amount
    elements.append(_draw_related_and_amount(data, currency))
    elements.append(Spacer(400, 20))

    # Row 4: Description (rich text — HTML from Quill, or legacy plain text)
    description = data.get("description", "") or ""
    elements.append(Paragraph("<b>Description</b>", styles['Normal']))
    elements.append(Spacer(1, 4))
    description_flowables = html_to_flowables(description)
    if description_flowables:
        elements.extend(description_flowables)
    else:
        elements.append(Paragraph("&nbsp;", styles['Normal']))
    elements.append(Spacer(400, 16))

    # Row 5: Resolution notes (only if present)
    resolution = data.get("resolutionNotes", "") or ""
    if resolution.strip():
        resolution_html = resolution.replace("\n", "<br/>")
        elements.append(Paragraph("<b>Resolution Notes</b>", styles['Normal']))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(resolution_html, styles['Normal']))

    pdf.build(
        elements,
        canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, header=header, **kwargs),
    )


def _draw_claim_details(data, currency):
    issued_date = _parse_date(data.get('issuedDate'))
    resolved_date = _parse_date(data.get('resolvedDate'))
    status_key = data.get('status', 'open')
    status_label = STATUS_LABELS.get(status_key, status_key)

    rows = [
        [Paragraph("Claim #", bold_style), Paragraph(f"{data.get('claimNumber', '')}", styles['Normal'])],
        [Paragraph("Issued Date", bold_style), Paragraph(issued_date, styles['Normal'])],
        [Paragraph("Status", bold_style), Paragraph(status_label, styles['Normal'])],
        [Paragraph("Currency", bold_style), Paragraph(currency, styles['Normal'])],
    ]
    if resolved_date:
        rows.append([Paragraph("Resolved Date", bold_style), Paragraph(resolved_date, styles['Normal'])])

    table = Table(rows, colWidths=[105, 180])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('FONTNAME', (0, 0), (0, -1), "Helvetica-Bold"),
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent),
        ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
    ]))

    return table


def _draw_related_and_amount(data, currency):
    right_align_style = ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=2)
    bold_right_align_style = ParagraphStyle(name='BoldRightAlign', parent=bold_style, alignment=2)

    related_bill = data.get("relatedBill") or {}
    related_order = data.get("relatedOrder") or {}

    rows = [['DETAIL', 'REFERENCE', 'AMOUNT']]

    if related_bill.get("invoiceNumber"):
        bill_currency = related_bill.get("currency") or currency
        bill_total = related_bill.get("total")
        bill_amount = (
            format_currency(float(bill_total), bill_currency, '#,##0.00 ¤', locale='en_US')
            if bill_total is not None else ''
        )
        rows.append([
            Paragraph("Related Bill", styles['Normal']),
            Paragraph(related_bill['invoiceNumber'], styles['Normal']),
            Paragraph(bill_amount, right_align_style),
        ])

    if related_order.get("orderNumber"):
        rows.append([
            Paragraph("Related Order", styles['Normal']),
            Paragraph(related_order['orderNumber'], styles['Normal']),
            Paragraph('', right_align_style),
        ])

    if len(rows) == 1:
        rows.append([
            Paragraph("—", styles['Normal']),
            Paragraph("No related documents", styles['Normal']),
            Paragraph('', right_align_style),
        ])

    amount = float(data.get("amount") or 0)
    rows.append([
        '',
        Paragraph('CLAIMED AMOUNT', bold_style),
        Paragraph(format_currency(amount, currency, '#,##0.00 ¤', locale='en_US'), bold_right_align_style),
    ])

    body_rows = len(rows) - 2  # excluding header and total

    table = Table(
        rows,
        repeatRows=1,
        colWidths=[2.2 * inch, 3 * inch, 2.2 * inch],
    )

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#272b29')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),

        ('BOTTOMPADDING', (0, 1), (-1, body_rows), 5),
        ('TOPPADDING', (0, 1), (-1, body_rows), 5),

        ('BOX', (0, 0), (-1, body_rows), 0.8, colors.black),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
    ])

    style.add('BOX', (1, body_rows + 1), (-1, -1), 1.2, colors.black)
    style.add('LINEABOVE', (0, body_rows + 1), (-1, body_rows + 1), 1.2, colors.black)
    style.add('BOTTOMPADDING', (0, body_rows + 1), (-1, -1), 8)
    style.add('TOPPADDING', (0, body_rows + 1), (-1, -1), 8)

    table.setStyle(style)
    return table
