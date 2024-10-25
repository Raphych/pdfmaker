from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime

def draw_shipping_details(shipping):
    content = []
    
    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

    if shipping.get('ets', None) != None:
        content.append([
            Paragraph("Early Time Shipping", bold_style ),
            Paragraph(datetime.datetime.fromisoformat(shipping['ets'][:-1]).strftime('%Y-%m-%d'), styles['Normal'] )
        ])
    
    if shipping.get('eta', None) != None:
        content.append([
            Paragraph("Early Time Arrival", bold_style ),
            Paragraph(datetime.datetime.fromisoformat(shipping['eta'][:-1]).strftime('%Y-%m-%d'), styles['Normal'] )
        ])
    
    if shipping.get('portOfOrigin', None) != None:
        content.append([
            Paragraph("Port of Origin", bold_style ),
            Paragraph(shipping['portOfOrigin'], styles['Normal'] )
        ])
    
    if shipping.get('portOfDischarge', None) != None:
        content.append([
            Paragraph("Port of Discharge", bold_style ),
            Paragraph(shipping['portOfDischarge'], styles['Normal'] )
        ])
    
    if shipping.get('finalDestination', None) != None:
        content.append([
            Paragraph("Final Destination", bold_style ),
            Paragraph(shipping['finalDestination'], styles['Normal'] )
        ])
    
    if shipping.get('carrier', None) != None:
        content.append([
            Paragraph("Carrier", bold_style ),
            Paragraph(shipping['carrier'], styles['Normal'] )
        ])
    
    if shipping.get('vessel', None) != None:
        content.append([
            Paragraph("Vessel", bold_style ),
            Paragraph(f"{shipping['vessel']} {shipping.get('voyageNumber', '')}", styles['Normal'] )
        ])
    
    if shipping.get('others', None) != None:
        content.append(['',''])
        for other in shipping['others']:
            content.append([
                Paragraph(other, styles['Normal']),
                ''
            ])
    
    table = Table(content, colWidths=[A4[0] / 5, A4[0] / 5 ])
    style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent)  # No borders
    ])

    if shipping['others'] != None:
        for i in range(1, len(shipping['others']) + 1):
            style.add("SPAN", (0, -i ), (-1, -i) )
            style.add("FONTNAME", (0, -i ), (-1, -i), "Helvetica")
        
    table.setStyle(style)
    return table