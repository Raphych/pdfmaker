from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import datetime
from babel.numbers import format_currency

from templates.parts.contactDetails import draw_contact_details
from templates.parts.htmlFlowables import html_to_flowables
from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns


styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
section_heading_style = ParagraphStyle(
    name='SectionHeading',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    spaceAfter=4,
)
regarding_label_style = ParagraphStyle(
    name='RegardingLabel',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
)
regarding_value_style = ParagraphStyle(
    name='RegardingValue',
    parent=styles['Normal'],
    fontSize=10,
)
amount_label_style = ParagraphStyle(
    name='AmountLabel',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    alignment=2,  # right
)
amount_value_style = ParagraphStyle(
    name='AmountValue',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=16,
    alignment=2,
)

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

    # ── Row 1: Company coordinates (left) + claim meta (right) ──
    coordinates = draw_contact_details(data.get("coordinates", None))
    details = _draw_claim_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(1, 20))

    # ── Row 2: Supplier ──
    supplier_block = draw_contact_details(data.get("supplier", None), "Claim Against")
    elements.append(draw_independent_columns([supplier_block, Spacer(1, 1)]))
    elements.append(Spacer(1, 18))

    # ── Row 3: Regarding (related docs as compact key-value lines) ──
    regarding = _draw_regarding(data)
    if regarding is not None:
        elements.append(regarding)
        elements.append(Spacer(1, 18))

    # ── Row 4: Description (rich text — the substance of the claim) ──
    elements.append(Paragraph("Description", section_heading_style))
    description = data.get("description", "") or ""
    description_flowables = html_to_flowables(description)
    if description_flowables:
        elements.extend(description_flowables)
    else:
        elements.append(Paragraph("&nbsp;", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ── Row 5: Claimed amount — prominent, right-aligned, ruled ──
    elements.append(_draw_amount_line(data, currency))

    # ── Row 6: Resolution notes (only if present) ──
    resolution = (data.get("resolutionNotes") or "").strip()
    if resolution:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Resolution Notes", section_heading_style))
        resolution_html = resolution.replace("\n", "<br/>")
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


def _draw_regarding(data):
    """Compact 'Regarding:' block showing linked bill/order as key-value lines.

    Returns None if there are no related documents so the caller can skip
    the section entirely rather than emit an empty header.
    """
    related_bill = data.get("relatedBill") or {}
    related_order = data.get("relatedOrder") or {}

    rows = []
    if related_bill.get("invoiceNumber"):
        rows.append([
            Paragraph("Related Bill:", regarding_label_style),
            Paragraph(related_bill['invoiceNumber'], regarding_value_style),
        ])
    if related_order.get("orderNumber"):
        rows.append([
            Paragraph("Related Order:", regarding_label_style),
            Paragraph(related_order['orderNumber'], regarding_value_style),
        ])

    if not rows:
        return None

    table = Table(rows, colWidths=[110, 380])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent),
    ]))
    return table


def _draw_amount_line(data, currency):
    """Prominent 'Claimed Amount' line with a top rule, right-aligned."""
    amount = float(data.get("amount") or 0)
    formatted = format_currency(amount, currency, '#,##0.00 ¤', locale='en_US')

    rows = [
        [Paragraph("CLAIMED AMOUNT", amount_label_style)],
        [Paragraph(formatted, amount_value_style)],
    ]
    table = Table(rows, colWidths=[A4[0] - 80])
    table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1.2, colors.black),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('TOPPADDING', (0, 1), (-1, 1), 0),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table
