from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def draw_payment_terms(payment_terms):
    content = []

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

    if payment_terms.get('definition', None) != None:
        content.append([
            Paragraph("Payment Terms", bold_style ),
            Paragraph(payment_terms['definition'], styles['Normal'] )
        ])

    if payment_terms.get('currency', None) != None:
        content.append([
            Paragraph("Currency", bold_style ),
            Paragraph(payment_terms['currency'], styles['Normal'] )
        ])

    if payment_terms.get('incoterms', None) != None and payment_terms.get('incotermsDestination', None) != None:
        content.append([
            Paragraph("Incoterms", bold_style ),
            Paragraph(f"{payment_terms['incoterms']} {payment_terms['incotermsDestination']}", styles['Normal'] )
        ])

    if len(content) == 0:
        content.append([''])

    table = Table(content, colWidths=[A4[0] / 6, A4[0] / 4 ])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('FONTNAME', (0,0), (0,-1), "Helvetica-Bold" ),
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent)  # No borders
    ]))
    return table