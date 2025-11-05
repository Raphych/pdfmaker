from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime 

def draw_shipping_details(shipping):
    content = []
    
    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

    
# if shipping.get('bookingNumber', None) != None:
    content.append([
        Paragraph("Booking #", bold_style ),
        Paragraph(shipping.get('bookingNumber', ''), styles['Normal'] )
    ])

# if shipping.get('billOfLadingNumber', None) != None:
    content.append([
        Paragraph("Bill of Lading #", bold_style ),
        Paragraph(shipping.get('billOfLadingNumber', ''), styles['Normal'] )
    ])

# if shipping.get('billOfLadingType', None) != None:
#     content.append([
#         Paragraph("Bill of Lading Type", bold_style ),
#         Paragraph(shipping['billOfLadingType'], styles['Normal'] )
#     ])

# if shipping.get('ets', None) != None:
    ets_text = (
        datetime.datetime.fromisoformat(shipping.get('ets', '')[:-1]).strftime('%Y-%m-%d')
        if shipping.get('ets') else ''
    )
    content.append([
        Paragraph("ETS", bold_style ),
        Paragraph(ets_text, styles['Normal'] )
    ])

# if shipping.get('eta', None) != None:
    eta_text = (
        datetime.datetime.fromisoformat(shipping.get('eta', '')[:-1]).strftime('%Y-%m-%d')
        if shipping.get('eta') else ''
    )
    content.append([
        Paragraph("ETA", bold_style ),
        Paragraph(eta_text, styles['Normal'] )
    ])

# if shipping.get('portOfLoading', None) != None:
    content.append([
        Paragraph("Port of Loading", bold_style ),
        Paragraph(shipping.get('portOfLoading', ''), styles['Normal'] )
    ])

# if shipping.get('portOfDischarge', None) != None:
    content.append([
        Paragraph("Port of Discharge", bold_style ),
        Paragraph(shipping.get('portOfDischarge', ''), styles['Normal'] )
    ])

# if shipping.get('finalDestination', None) != None:
    content.append([
        Paragraph("Final Destination", bold_style ),
        Paragraph(shipping.get('finalDestination', ''), styles['Normal'] )
    ])

# if shipping.get('carrier', None) != None:
    content.append([
        Paragraph("Carrier", bold_style ),
        Paragraph(shipping.get('carrier', ''), styles['Normal'] )
    ])

# if shipping.get('vessel', None) != None:
    content.append([
        Paragraph("Vessel", bold_style ),
        Paragraph(f"{shipping.get('vessel', '')} {shipping.get('voyageNumber', '')}", styles['Normal'] )
    ])

    if len(content) == 0:
        content.append([''])
    
    table = Table(content, colWidths=[A4[0] / 5, A4[0] / 5 ])
    style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent)  # No borders
    ])
        
    table.setStyle(style)
    return table