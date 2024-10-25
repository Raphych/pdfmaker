from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from templates.parts.itemsTable import draw_items_table
from templates.parts.shippingDetails import draw_shipping_details
from templates.parts.contactDetails import draw_contact_details
from templates.parts.paymentTerms import draw_payment_terms
from templates.parts.layout import draw_simple_table
from reportlab.lib import colors

from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns

styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

def generate_invoice(buffer, data):
    margins = layout()
    title="INVOICE"

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=margins['right'],
        leftMargin=margins['left'],
        topMargin=margins['top'],
        bottomMargin=margins['bottom'],
    )

    elements = []

    # Bill To and Ship To
    currency = data.get("paymentTerms", {}).get("currency", "USD")
    coordinates = draw_contact_details(data.get("coordinates", None))
    details = draw_invoice_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(400, 20))

    # Bill To and Ship To
    billTo = draw_contact_details(data.get("billTo", None), "Bill To")
    shipTo = draw_contact_details(data.get("shipTo", None), "Ship To")
    elements.append(draw_independent_columns([billTo, shipTo]))
    elements.append(Spacer(400, 20))

    # Items Table
    elements.append(draw_items_table(items=data.get("items", None), discounts=data.get("discounts", None), taxes=data.get("taxes", None), currency=currency))
    elements.append(Spacer(400, 20))

    # Shipping details and Payment Terms
    shipping = draw_shipping_details(data.get("shipping", None))
    paymentTerms = draw_payment_terms(data.get("paymentTerms", None))
    elements.append(draw_independent_columns([shipping, paymentTerms], innerVerticalColumns=True ))
    # elements.append(Spacer(400, 20))

    # Cargo Values and Bank Account Details
    cargoValues = draw_simple_table(data.get("cargoValues", None), [A4[0] / 5, A4[0] / 5 ], bold_cols=[0])
    bankDetails = draw_simple_table(data.get("bankDetails", None), [A4[0] / 2.5], default_style=ParagraphStyle(name="Normal", fontName='Helvetica', fontSize=8 ))
    elements.append(draw_independent_columns([cargoValues, bankDetails], innerVerticalColumns=True ))
    elements.append(Spacer(400, 20))

    # Build the PDF
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, **kwargs))


def draw_title(title):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24)
    return Paragraph(title, title_style)

def draw_invoice_details(data, currency):
    rows = []
    rows.append([ "Invoice #", f"{data['invoice']}" ])
    rows.append([ "Issued Date", f"{data['issuedDate']}" ])
    rows.append([ "Currency", currency ] )
    if data.get('customerReference', None) != None:
        rows.append([ "Customer Reference", data['customerReference'] ])
    table = Table(rows, colWidths=[A4[0] / 6, A4[0] / 6 ])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (-1, 0), (-1, -1), 5),  # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('FONTNAME', (0,0), (0,-1), "Helvetica-Bold" ),
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent)  # No borders
    ]))

    return table