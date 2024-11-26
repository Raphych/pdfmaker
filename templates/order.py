from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from templates.parts.itemsTable import draw_items_table
from templates.parts.contactDetails import draw_contact_details
from templates.parts.paymentTerms import draw_payment_terms
from templates.parts.layout import draw_simple_table, layout, PageNumCanvas, draw_independent_columns
import datetime

styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

def generate_order(buffer, data):
    margins = layout()
    title="PURCHASE ORDER"

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=margins['right'],
        leftMargin=margins['left'],
        topMargin=margins['top'],
        bottomMargin=margins['bottom'],
    )

    elements = []

    # Details
    currency = data.get("paymentTerms", {'currency': "USD"}).get("currency", "USD")
    coordinates = draw_contact_details(data.get("coordinates", None))
    details = draw_order_details(data, currency)
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
    additional_infos = []
    if (data.get('finalConsignee', None) is not None):
        additional_infos.append(["Final Consignee", data['finalConsignee']])

    if (data.get('countryOfDischarge', None) is not None):
        additional_infos.append(["Country of Discharge", data['countryOfDischarge']])

    if (data.get('portOfDischarge', None) is not None):
        additional_infos.append(["Port of Discharge", data['portOfDischarge']])
    
    if (data.get('deliveryDate', None) is not None):
        additional_infos.append(["Delivery Date", data['deliveryDate'][:-1]])

    if len(additional_infos) == 0:
        additional_infos.append([''])

    shipping = draw_simple_table(additional_infos, [A4[0] / 5, A4[0] / 5 ], bold_cols=[0])
    paymentTerms = draw_payment_terms(data.get("paymentTerms", None))
    elements.append(draw_independent_columns([shipping, paymentTerms], innerVerticalColumns=True ))

    # Build the PDF
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, **kwargs))


def draw_title(title):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24)
    return Paragraph(title, title_style)

def draw_order_details(data, currency):
    rows = []
    rows.append([ "Order #", f"{data.get('order', '')}" ])
    rows.append([ "Issued Date", f"{data.get('issuedDate', '')}" ])
    rows.append([ "Currency", currency ] )
    if data.get('supplierReference', None) != None:
        rows.append([ "Supplier Reference", data['supplierReference'] ])
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