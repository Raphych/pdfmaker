from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from templates.parts.contactDetails import draw_contact_details
from templates.parts.layout import draw_simple_table
from reportlab.lib import colors
import datetime
from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns
from babel.numbers import format_currency

from reportlab.lib.units import inch


styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

def generate_credit_note(buffer, data):
    margins = layout()
    title = data.get("filename", "credit_note.pdf")
    header="CREDIT NOTE"

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=margins['right'],
        leftMargin=margins['left'],
        topMargin=margins['top'],
        bottomMargin=margins['bottom'],
        title=title
    )

    elements = []

    # Bill To and Ship To
    currency = data.get("currency", "USD")
    coordinates = draw_contact_details(data.get("coordinates", None))
    details = draw_credit_note_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(400, 20))

    # Bill To and Ship To
    billTo = draw_contact_details(data.get("customer", None), "Customer")
    shipTo = draw_contact_details(data.get("customer", None), "Ship To")
    elements.append(draw_independent_columns([billTo, shipTo]))
    elements.append(Spacer(400, 20))

    # Items Table
    elements.append(draw_credit_note_items_table(items=data.get("items", None), total=data.get("total", None), currency=currency))
    elements.append(Spacer(400, 20))

    # Insert line break after title
    raw_terms = data.get("termsAndConditions", "") or ""
    html_terms = raw_terms.replace("\n", "<br/>")
    terms_text = f"<b>Terms and Conditions</b><br/>{html_terms}"
    terms_paragraph = Paragraph(terms_text, styles['Normal'])

    left_rows = []
    if data.get("relatedInvoice"):
        left_rows.append(["Related Invoice #", data.get("relatedInvoice", {}).get("invoiceNumber", "")])

        related_invoice_date_str = data.get("relatedInvoice", {}).get('issuedDate', '')
        related_invoice_date = datetime.datetime.fromisoformat(related_invoice_date_str.rstrip('Z')).strftime('%Y-%m-%d')
        if related_invoice_date:
            left_rows.append(["Related Invoice Date", related_invoice_date])

        if data.get("relatedInvoice", {}).get("customerReference", None):
            left_rows.append(["Customer Reference", data.get("relatedInvoice", {}).get("customerReference", "")])
            
        if data.get("relatedInvoice", {}).get("total", None) and data.get("relatedInvoice", {}).get("paymentTerms", {}).get("currency", None):
            left_rows.append(["Related Invoice Total", format_currency(data.get("relatedInvoice", {}).get("total", 0), data.get("relatedInvoice", {}).get("paymentTerms", {}).get("currency", "USD"), locale='en_US')])

    left_section = draw_simple_table(left_rows, colWidths=[A4[0] / 5, A4[0] / 5], bold_cols=[0]) if left_rows else Spacer(1, 1)

    elements.append(draw_independent_columns([left_section, terms_paragraph], innerVerticalColumns=True))

    # Build the PDF
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, header=header, **kwargs))


def draw_title(title):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24)
    return Paragraph(title, title_style)

def draw_credit_note_details(data, currency):

    issued_date_str = data.get('issuedDate')
    if issued_date_str:
        issuedDate = datetime.datetime.fromisoformat(issued_date_str.rstrip('Z')).strftime('%Y-%m-%d')
    else:
        issuedDate = ''

    rows = []
    rows.append([ Paragraph("Credit Note #", bold_style), Paragraph(f"{data['creditNoteNumber']}", styles['Normal']) ])
    rows.append([ Paragraph("Issued Date", bold_style), Paragraph(issuedDate, styles['Normal']) ])
    rows.append([ Paragraph("Currency", bold_style), Paragraph(currency, styles['Normal']) ])
    rows.append([ Paragraph("Customer Reference", bold_style), Paragraph(data.get('customerReference', ''), styles['Normal']) ])
    table = Table(rows, colWidths=[105, 180])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('FONTNAME', (0,0), (0,-1), "Helvetica-Bold" ),
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent),  # No borders
        ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),  # Enable wrapping on text column
    ]))

    return table




def draw_credit_note_items_table(items=None, total=None, currency='USD'):
    data = [['DESCRIPTION', 'QTY', 'PRICE', 'TOTAL']]

    styles = getSampleStyleSheet()
    right_align_style = ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=2)
    bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
    bold_right_align_style = ParagraphStyle(name='BoldRightAlign', parent=bold_style, alignment=2)

    # --- Items Rows ---
    if items is not None:
        for item in items:
            data.append([
                Paragraph(f"{item['description']}", styles['Normal']),
                Paragraph(f"{item['quantity']}", styles['Normal']),
                Paragraph(format_currency(item['unitPrice'], currency, '#,##0.00 ¤', locale='en_US'), right_align_style),
                Paragraph(format_currency(item['total'], currency, '#,##0.00 ¤', locale='en_US'), right_align_style),
            ])

    # --- Total ---
    data.append([
        '', Paragraph('TOTAL', bold_style),
        Paragraph(format_currency(f"{total}", currency, '#,##0.00 ¤', locale='en_US'), bold_right_align_style),''
    ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[4.2 * inch, 1 * inch, 1 * inch, 1.2* inch]
    )

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#272b29')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('TOPPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8), # Header padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 8), # Header padding

        ('BOTTOMPADDING', (0, 1), (-1, len(items)), 5), # Items rows padding
        ('TOPPADDING', (0, 1), (-1, len(items)), 5), # Items rows padding
        # ('SPAN', (0, len(items)), (1, len(items))) ,  # Span Total Weight row

        # Grid for items rows only
        # ('GRID', (0, 0), (-1, items_count), 0.1, colors.black),
        ('BOX', (0, 0), (-1, len(items)), 0.8, colors.black),
        # Bold text for totals area
        ('FONTNAME', (2, len(items) + 1), (-1, -1), 'Helvetica-Bold'),
    ])

    # --- Outer border for Total Weight row only (no internal grid) ---
    # style.add('BOX', (0, items_count + 1), (-1, items_count + 1), 0.8, colors.black)

    # --- Grids for the totals area below Total Weight ---
    # style.add('GRID', (1, len(items) + 1), (-1, -1), 0.4, colors.black)
    style.add('BOX', (1, len(items) + 1), (-1, -1), 1.2, colors.black)
    style.add('LINEABOVE', (0, len(items) + 1), (-1, len(items) + 1), 1.2, colors.black)
    style.add('BOTTOMPADDING', (0, len(items) + 1), (-1, -1), 8 )
    style.add('TOPPADDING', (0, len(items) + 1), (-1, -1), 8)

    # Merge cells for total-related rows (subtotal, taxes, total)
    style.add('SPAN', (2, -1), (3, -1))

    table.setStyle(style)
    return table
