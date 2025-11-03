from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from templates.parts.itemsTable import draw_items_table
from templates.parts.shippingDetails import draw_shipping_details
from templates.parts.contactDetails import draw_contact_details
from templates.parts.paymentTerms import draw_payment_terms
from templates.parts.layout import draw_simple_table
from reportlab.lib import colors
import datetime
from babel.numbers import format_currency

from templates.parts.layout import layout, PageNumCanvas, draw_independent_columns

styles = getSampleStyleSheet()
bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

def generate_invoice(buffer, data):
    margins = layout()
    title = data.get("filename", "invoice.pdf")
    header="INVOICE"

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
    details = draw_invoice_details(data, currency)
    elements.append(draw_independent_columns([coordinates, details]))
    elements.append(Spacer(400, 20))

    # Bill To and Ship To
    billTo = draw_contact_details(data.get("customer", None), "Bill To")
    shipTo = draw_contact_details(data.get("shipTo", None), "Ship To")
    elements.append(draw_independent_columns([billTo, shipTo]))
    elements.append(Spacer(400, 20))

    # Items Table
    elements.append(draw_items_table(items=data.get("items", None), discount=data.get("discount", None), tax=data.get("tax", None), subTotal=data.get("subTotal", None), discountTotal=data.get("discountTotal", None), grandTotal=data.get("grandTotal", None), totalQty=data.get("totalQty", None), currency=currency))
    elements.append(Spacer(400, 20))

    # Shipping details and Payment Terms
    shipping = draw_shipping_details(data.get("shipping", None))
    # Add cargo values to the shipping details
    insuredValue = get_insured_value(float(data.get("subTotal", 0)), data.get("paymentTerms", {}).get("incoterms", ""))

    # Cargo Values Table with formatted currency
    cargoValuesData = [
        [f"FOB Value", f"{format_currency(data.get('subTotal', 0) - (data.get('shipping', {}).get('cost', 0) or 0) - insuredValue, currency)}"],
        [f"Freight Value", f"{format_currency(data.get('shipping', {}).get('cost', 0) or 0, currency)}"],
        [f"Insured Value", f"{format_currency(insuredValue, currency)}"],
        [f"Cargo Value", f"{format_currency(data.get('subTotal', 0), currency)}"],
    ]
    # Remove Insured Value row if it's zero
    if insuredValue == 0:
        cargoValuesData.pop(2)
    cargoValues = draw_simple_table(cargoValuesData, [A4[0] / 5, A4[0] / 5 ], bold_cols=[0])

    # Insert line break after title
    terms_text = f"<b>Terms and Conditions</b><br/>{data.get('termsAndConditions', '')}"
    terms_paragraph = Paragraph(terms_text, styles['Normal'])

    left_section = [ shipping, Spacer(0, 12), cargoValues ]

    elements.append(draw_independent_columns([left_section, terms_paragraph], innerVerticalColumns=True))

    # Bank Account Details in small font at the bottom
    elements.append(Spacer(400, 20))
    bankDetails = Paragraph(data.get("bankDetails", None), ParagraphStyle(name='Small', parent=styles['Normal'], fontSize=8))
    elements.append(bankDetails)    

    # Build the PDF
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, title=title, header=header, **kwargs))


def draw_title(title):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24)
    return Paragraph(title, title_style)

def draw_invoice_details(data, currency):
    issuedDate = datetime.datetime.fromisoformat(data['issuedDate'][:-1]).strftime('%Y-%m-%d')
    rows = []
    rows.append([ Paragraph("Invoice #", bold_style), Paragraph(f"{data['invoiceNumber']}", styles['Normal']) ])
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

# Compute cargo value translating the logic from TypeScript to Python
def get_insured_value(sub_total: float, incoterms: str) -> float:
    insured_value = 0
    if incoterms in ['CIF', 'CPT', 'CIP', 'DPU', 'DAP', 'DDP', 'DDU']:
        insured_value = round(sub_total * 0.0018)
    
    while insured_value % 5 != 0:
        insured_value += 1

    return insured_value