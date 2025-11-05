from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from templates.parts.itemsTable import draw_items_table
from templates.parts.contactDetails import draw_contact_details
from templates.parts.layout import draw_simple_table
from reportlab.lib import colors
import datetime
from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns
from babel.numbers import format_currency

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
    currency = data.get("paymentTerms", {}).get("currency", "USD")
    coordinates = draw_contact_details(data.get("coordinates", None))
    details = draw_credit_note_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(400, 20))

    # Bill To and Ship To
    billTo = draw_contact_details(data.get("supplier", None), "Order To")
    shipTo = draw_contact_details(data.get("shipTo", None), "Ship To")
    elements.append(draw_independent_columns([billTo, shipTo]))
    elements.append(Spacer(400, 20))

    # Items Table
    elements.append(draw_items_table(items=data.get("items", None), discount=data.get("discount", None), tax=data.get("tax", None), subTotal=data.get("subTotal", None), discountTotal=data.get("discountTotal", None), grandTotal=data.get("grandTotal", None), totalQty=data.get("totalQty", None), currency=currency))
    elements.append(Spacer(400, 20))

    # Insert line break after title
    terms_text = f"<b>Terms and Conditions</b><br/>{data.get('termsAndConditions', '')}"
    terms_paragraph = Paragraph(terms_text, styles['Normal'])

    left_rows = []
    if data.get("relatedInvoice"):
        left_rows.append([Paragraph("Related Invoice", bold_style), Paragraph(data.get("relatedInvoice", {}).get("invoiceNumber", ""), styles['Normal'])])
        related_invoice_date = data.get("relatedInvoice", {}).get('issuedDate', None)
        if related_invoice_date:
            left_rows.append([Paragraph("Invoice Date", bold_style), Paragraph(datetime.datetime.fromisoformat(related_invoice_date[:-1]).strftime('%Y-%m-%d'), styles['Normal'])])
        if data.get("relatedInvoice", {}).get("customerReference", None):
            left_rows.append([Paragraph("Customer Reference", bold_style), Paragraph(data.get("relatedInvoice", {}).get("customerReference", ""), styles['Normal'])])
        if data.get("relatedInvoice", {}).get("grandTotal", None) and data.get("relatedInvoice", {}).get("paymentTerms", {}).get("currency", None):
            left_rows.append([Paragraph("Invoice Total", bold_style), Paragraph(format_currency(data.get("relatedInvoice", {}).get("grandTotal", 0), data.get("relatedInvoice", {}).get("paymentTerms", {}).get("currency", "USD")), styles['Normal'])])

    left_section = draw_simple_table(left_rows)

    elements.append(draw_independent_columns([left_section, terms_paragraph], innerVerticalColumns=True))

    # Build the PDF
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, header=header, **kwargs))


def draw_title(title):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24)
    return Paragraph(title, title_style)

def draw_credit_note_details(data, currency):
    issuedDate = datetime.datetime.fromisoformat(data['issuedDate'][:-1]).strftime('%Y-%m-%d')
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