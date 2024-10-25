from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

def draw_contact_details(contact: dict, label = None, colWidths=None):
    content = []

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

    tax_id = contact.get('taxId', '')
    tax_id_string = get_tax_id(tax_id) if tax_id is not None else ''
    # Format the label and return the rendered paragraph
    if contact.get('company', None) != None:
        content.append([
            Paragraph(
                f"{contact['company']} {tax_id_string}",
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
    
    # Create a function to fetch values from the contact
    def get_value(key: str) -> str:
        return contact.get(key, '')  # Return '' instead of None for cleaner output

    # Gather address components
    address_parts = [
        get_value("address"),
        get_value("city"),
        get_value("province"),
        get_value("country"),
        get_value("zip")
    ]
    
    # Join non-empty address components with a comma
    address_string = ", ".join(filter(None, address_parts))
    if address_string:  # Only append if address_string is not empty
        infos.append(address_string)

    # Append email and phone, if they exist
    email = get_value("email")
    phone = get_value("phone")

    if email:  # Only append if email is not an empty string
        infos.append(email)
    if phone:  # Only append if phone is not an empty string
        infos.append(phone)

    # Join all info components into a single string
    return ", ".join(infos) if infos else ''  # Return empty string if infos is empty


def get_tax_id(tax_id: dict) -> str:
    if not isinstance(tax_id, dict):
        return ''
    
    label = tax_id.get('label', 'Tax')
    value = tax_id.get('value', None)

    if value is None:
        return ''
    else:
        return f"({label}: {value})"