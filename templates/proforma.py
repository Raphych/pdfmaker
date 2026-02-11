from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from templates.parts.itemsTable import draw_items_table
from templates.parts.shippingDetails import draw_shipping_details
from templates.parts.contactDetails import draw_contact_details
from templates.parts.layout import draw_simple_table
from reportlab.lib import colors
from babel.numbers import format_currency
import datetime
from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns

styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

def generate_proforma(buffer, data):
    margins = layout()
    title = data.get("filename", "proforma.pdf")
    header="PROFORMA INVOICE"

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
    details = draw_proforma_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(400, 20))

    # Bill To and Ship To
    billTo = draw_contact_details(data.get("customer", None), "Bill To")
    shipTo = draw_contact_details(data.get("shipTo", None), "Ship To")
    elements.append(draw_independent_columns([billTo, shipTo]))
    elements.append(Spacer(400, 20))

    # Items Table
    elements.append(draw_items_table(items=data.get("items", None), discount=data.get("discount", None), tax=data.get("tax", None), subTotal=data.get("subTotal", None), discountTotal=data.get("discountTotal", None), total=data.get("total", None), totalQuantity=data.get("totalQuantity", None), currency=currency))
    elements.append(Spacer(400, 20))

    # Shipping details and Payment Terms
    shipping = draw_shipping_details(data.get("shipping", None))

    # Cargo Values Table with precalculated values
    cargoValues_data = data.get("cargoValues", {})
    cargoValuesData = [
        ["FOB Value", format_currency(cargoValues_data.get('fobValue', 0), currency, '#,##0.00 ¤', locale='en_US')],
        ["Freight Value", format_currency(cargoValues_data.get('freightValue', 0), currency, '#,##0.00 ¤', locale='en_US')],
        ["Insurance Value", format_currency(cargoValues_data.get('insuranceValue', 0), currency, '#,##0.00 ¤', locale='en_US')],
        ["Cargo Value", format_currency(cargoValues_data.get('cargoValue', 0), currency, '#,##0.00 ¤', locale='en_US')],
    ]

    # Remove Insurance Value row if it's zero
    if not cargoValues_data.get('insuranceValue'):
        cargoValuesData.pop(2)
    cargoValues = draw_simple_table(cargoValuesData, [A4[0] / 5, A4[0] / 5 ], bold_cols=[0])

    # Insert line break after title
    raw_terms = data.get("termsAndConditions", "") or ""
    html_terms = raw_terms.replace("\n", "<br/>")
    terms_text = f"<b>Terms and Conditions</b><br/>{html_terms}"
    terms_paragraph = Paragraph(terms_text, styles['Normal'])

    left_section = [ shipping, Spacer(0, 12), cargoValues ]

    elements.append(draw_independent_columns([left_section, terms_paragraph], innerVerticalColumns=True))

    # Bank Account Details in small font at the bottom
    elements.append(Spacer(400, 20))

    bank_text = (data.get("bankDetails") or "").replace("---", "<br/>")

    bankDetails = Paragraph(bank_text, ParagraphStyle(name='Small', parent=styles['Normal'], fontSize=8))
    elements.append(bankDetails)    

    # Build the PDF
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, header=header, **kwargs))


def draw_title(title):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24)
    return Paragraph(title, title_style)

def draw_proforma_details(data, currency):
    issuedDate = datetime.datetime.fromisoformat(data['issuedDate'][:-1]).strftime('%Y-%m-%d')
    rows = []
    rows.append([ Paragraph("Proforma #", bold_style), Paragraph(f"{data['proformaNumber']}", styles['Normal']) ])
    rows.append([ Paragraph("Issued Date", bold_style), Paragraph(issuedDate, styles['Normal']) ])
    rows.append([ Paragraph("Currency", bold_style), Paragraph(currency, styles['Normal']) ])
    rows.append([ Paragraph("Payment Terms", bold_style), Paragraph(data.get('paymentTerms', {}).get('code', {}).get('definition', ''), styles['Normal']) ])
    rows.append([ Paragraph("Incoterms", bold_style), Paragraph(data.get('paymentTerms', {}).get('incoterms', '') + " " + data.get('paymentTerms', {}).get('incotermsDestination', ''), styles['Normal']) ])
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
