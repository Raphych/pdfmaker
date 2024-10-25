from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_credit_note(filename, data):
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Credit Note", styles['Title']))
    credit_note_meta = [
        ['Credit Note Number:', data['credit_note_number']],
        ['Date:', data['date']],
        ['Customer:', data['customer_name']],
    ]
    elements.append(Table(credit_note_meta))

    table_data = [['Description', 'Quantity', 'Unit Price', 'Total']] + [
        [item['description'], item['quantity'], f"${item['unit_price']}", f"${item['total']}"]
        for item in data['items']
    ]
    elements.append(Table(table_data))

    elements.append(Paragraph(f"Total Amount: ${data['total_amount']}", styles['Heading2']))
    pdf.build(elements)
