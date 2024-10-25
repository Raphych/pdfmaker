from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

def draw_contact_details(contact: dict, label = None, colWidths=None):
    content = []

    if label == "Ship To":
        print(contact)

    if contact is None or contact.get('company', None) is None:
        return Table([''], colWidths=colWidths)

    if (colWidths == None):
        width = A4[0] / 2 - 50*2
        colWidths = [ width ]

    # Create a custom bold style
    # Get the default style sheet
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = ParagraphStyle(
        name="Bold",  # Name of the style
        parent=styles["Normal"],  # Inherit from 'Normal' style
        fontName="Helvetica-Bold",  # Set the font to bold
        fontSize=10,  # Optional: Set font size
    )

    if label != None:
        content.append([Paragraph(label, bold_style)])

    # Format the label and return the rendered paragraph
    if contact['company'] != None:
        content.append([
            Paragraph(
                f"{contact.get('company', '')} {get_tax_id(contact.get('taxId', None))}",
                bold_style if label is None else normal_style
            )
        ])

    coordinates = get_coordinates(contact)
    # print(*coordinates)
    for el in coordinates:
        content.append([Paragraph(el, normal_style)])

    table = Table(content, colWidths=colWidths)
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.3),  # Remove bottom padding
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent),  # No borders
        ('FONTNAME', (0,0), (-1,0), "Helvetica-Bold" )
    ]

    table.setStyle(TableStyle(style))
    return table

def get_coordinates(contact: dict) -> str:
    infos = []

    def get_value(key: str, contact: dict):
        return contact.get(key, None)

    infos.append(", ".join(
        filter(None, [
            get_value("address", contact),
            get_value("city", contact),
            get_value("province", contact),
            get_value("country", contact),
            get_value("zip", contact)
        ])
    ))
    infos.append(get_value("email", contact))
    infos.append(get_value("phone", contact))

    if infos is None:
        return ''
    return infos


def get_tax_id(tax_id: dict) -> str:
    label = ''
    value = None
    if tax_id:
        label = tax_id.get('label', 'Tax')
        value = tax_id.get('value', None)
    
    if value is None:
        return ''
    else:
        return f"({label}: {value})"