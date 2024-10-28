from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from babel.numbers import format_currency

def draw_items_table(items=None, discounts=None, taxes=None, currency='USD'):
    data = [['#', 'Product', 'Description', 'Qty', 'Unit', 'Price', 'Total']]
    
    styles = getSampleStyleSheet()
    right_align_style = ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=2) 
    bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
    bold_right_align_style = ParagraphStyle(name='BoldRightAlign', parent=bold_style, alignment=2)

    if items is not None:
        for index, item in enumerate(items):
            total = item['quantity'] * item['unitPrice']
            data.append([
                Paragraph(f"{index+1}", styles['Normal']),
                Paragraph(f"{item['product']}", styles['Normal']),
                Paragraph(f"{item['description']}", styles['Normal']),
                Paragraph(f"{item['quantity']}", styles['Normal']),
                Paragraph(f"{item['unitType']}", styles['Normal']),
                Paragraph(format_currency( f"{item['unitPrice']:.2f}", currency ), right_align_style),
                Paragraph(format_currency( f"{total:.2f}", currency ), right_align_style)
            ])

    total = sum([item['quantity'] * item['unitPrice'] for item in items]) if items is not None else 0
    totalQty = sum(item['quantity'] for item in items)

    # Append discount rows (each discount on a separate line)
    if discounts is not None:
        for discount in discounts:
            description = f"{discount['description']}"
            discountInfos = get_discount(discount['operator'], discount['amount'], total)
            discountAmount = discountInfos['amount']
            discountSummedTotal = discountInfos['summedTotal']
            data.append(['', '', '', '', Paragraph(f"{description} {discountAmount}", styles['Normal']), '', format_currency(f"{-discountSummedTotal}", currency, '#,##0.00 \xa4')])
            total -= discountSummedTotal

    if (taxes is not None and len(taxes) > 0):
        data.append(['', '', '', '', Paragraph('Subtotal', bold_style), '', format_currency(f"{total}", currency, '#,##0.00 \xa4')])

    grandTotal = total
    # Append tax rows (each tax on a separate line)
    if taxes is not None:
        for tax in taxes:
            label = f"{tax['label']}"
            percentage = f"{tax['percentage']}%"
            summedTotal = (tax['percentage'] / 100) * total
            data.append(['', '', '', '', Paragraph(f"{label} {percentage}", bold_style), '', format_currency(f"{summedTotal}", currency, '#,##0.00 \xa4')])
            grandTotal += summedTotal

    # Optionally add a total row
    data.append(['', '','', '', Paragraph('Total', bold_style), '', Paragraph(format_currency(f"{grandTotal}", currency, '#,##0.00 \xa4'), bold_right_align_style)])
    data[len(items)+1][0] = Paragraph(f"Total Qty: {totalQty:.3f}" if totalQty else '', bold_right_align_style)

    items_count = len(items) if items is not None else 0
    discount_count = len(discounts) if discounts is not None else 0
    total_rows_count = 1 #default 1 for total
    if (type(taxes) == list and len(taxes) > 0):
        total_rows_count += len(taxes)
    if (type(discounts) == list and len(discounts) > 0):
        total_rows_count += len(discounts)
    if (type(taxes) == list and len(taxes) > 0):
        total_rows_count += 1 #add for subtotal

    table = Table(data, repeatRows=1, colWidths=[0.4*inch, 1.1*inch, 2.7*inch, 0.8*inch, 0.5*inch, 0.8*inch, 1.1*inch])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#272b29')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, items_count ), 0.1, colors.black), #Items grid
        ('GRID', (0, items_count+1), (4, items_count+1), 0.1, colors.black),
        # ('SPAN', (0, items_count+1), (4, items_count+1)),
        #Total Rows
        ('FONTNAME', (4, items_count + discount_count +1), (-1, -1), 'Helvetica-Bold'), #Bold
        ('GRID', (4, items_count +1), (-1, -1), 0.4, colors.black), #Total grid
        ('BOX', (4, items_count + discount_count +1), (-1, -1), 1.5, colors.black )
    ])

    for i in range(1, total_rows_count+1):
        style.add('SPAN', (0, -i), (3, -i) )
        style.add('SPAN', (4, -i), (5, -i) )

    table.setStyle(style)
    return table


def get_discount(operator, amount, total):
    # Calculate the discount based on the operator ('FIXED' or 'PERCENTAGE').
    if operator == 'fixed':
        return {'amount': '', 'summedTotal': amount}
    elif operator == 'percentage':
        discount_value = total * (amount / 100)
        return {'amount': f"{amount}%", 'summedTotal': discount_value}
    else:
        discount_value = total * (amount / 100)
        return {'amount': f"{amount}%", 'summedTotal': discount_value}