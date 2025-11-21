from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from babel.numbers import format_currency, format_decimal
from decimal import Decimal, ROUND_HALF_UP


def draw_items_table(items=None, discount=None, tax=None, totalQty=None, subTotal=None, discountTotal=None,  grandTotal=None, currency='USD'):
    data = [['DESCRIPTION', 'QTY', 'UOM', 'PRICE', 'TOTAL']]

    styles = getSampleStyleSheet()
    right_align_style = ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=2)
    bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
    bold_right_align_style = ParagraphStyle(name='BoldRightAlign', parent=bold_style, alignment=2)
    bold_left_align_style = ParagraphStyle(name='BoldLeftAlign', parent=bold_style, alignment=0)

    # --- Items Rows ---
    if items is not None:
        for item in items:
            itemTotal = (Decimal(item['quantity']) * Decimal(item['unitPrice'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            data.append([
                Paragraph(f"{(item['product']['name']).upper()}<br />{item['description']}", styles['Normal']),
                Paragraph(f"{item['quantity']}", styles['Normal']),
                Paragraph(f"{item['uom']}", styles['Normal']),
                Paragraph(format_currency(item['unitPrice'], currency, '#,##0.00 ¤'), right_align_style),
                Paragraph(format_currency(itemTotal, currency, '#,##0.00 ¤'), right_align_style),
            ])


    # --- Add total quantity line before discounts/taxes ---
    data.append([
        Paragraph(f"TOTAL WEIGHT: {format_decimal(totalQty, '#,##0.000')}", bold_right_align_style),
        '', '', '', ''
    ])

    # --- Subtotal if taxes or discount exist ---
    if tax and len(tax) > 0 or discount is not None:
        data.append(['', '', Paragraph('SUBTOTAL', bold_style), '', Paragraph(format_currency(f"{subTotal}", currency, '#,##0.## ¤'), bold_right_align_style)])


    # --- Discounts ---
    discount_count = 0
    if discount is not None:
        discount_count = 1

        # Make the label green inline
        green_bold_left = ParagraphStyle(
            name='GreenBoldLeft',
            parent=bold_style,
            textColor=colors.green,
            alignment=0  # left
        )
        green_bold_right = ParagraphStyle(
            name='GreenBoldRight',
            parent=bold_style,
            textColor=colors.green,
            alignment=2  # right
        )
        data.append([
            '', '', Paragraph("Discount (" + discount.get('description', '') + ")", green_bold_left),
            '', Paragraph(format_currency(f"{-discountTotal}", currency, '#,##0.00 ¤'), green_bold_right)
        ])

    # --- Taxes ---
    if tax:
        for taxItem in tax:
            label = f"{taxItem['label']}"
            percentage = f"({str(round(taxItem['percentage'], 3)).rstrip('.0')}%)"
            summedTotal = round(subTotal * taxItem['percentage'] / 100, 2)
            data.append([
                '', '', Paragraph(f"{label} {percentage}", bold_style),
                '', format_currency(f"{summedTotal}", currency, '#,##0.00 ¤')
            ])

    # --- Grand Total ---
    data.append([
        '', '', Paragraph('TOTAL', bold_style),
        '', Paragraph(format_currency(f"{grandTotal}", currency, '#,##0.00 ¤'), bold_right_align_style)
    ])

    # --- Table Setup ---
    items_count = len(items) if items else 0
    total_rows_count = 1  # base total row
    total_rows_count += discount_count
    if isinstance(tax, list) and len(tax) > 0:
        total_rows_count += len(tax) + 1  # subtotal + each tax
    if discount is not None or (isinstance(tax, list) and len(tax) > 0):
        total_rows_count += 1  # subtotal row

    table = Table(
        data,
        repeatRows=1,
        colWidths=[4 * inch, 0.8 * inch, 0.7 * inch, 0.9 * inch, 1.1 * inch]
    )

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#272b29')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('TOPPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8), # Header padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 8), # Header padding

        ('BOTTOMPADDING', (0, 1), (-1, items_count+1), 5), # Items rows padding
        ('TOPPADDING', (0, 1), (-1, items_count+1), 5), # Items rows padding
        ('SPAN', (0, items_count + 1), (1, items_count + 1)) ,  # Span Total Weight row
        # ('ALIGN', (0, items_count + 1), (2, items_count + 1), 'RIGHT'),  # Align Total Weight right

        # Grid for items rows only
        ('GRID', (0, 0), (-1, items_count), 0.1, colors.black),
        ('BOX', (0, 0), (-1, items_count + 1), 0.8, colors.black),

        # Bold text for totals area
        ('FONTNAME', (2, items_count + 1), (-1, -1), 'Helvetica-Bold'),
    ])

    # --- Outer border for Total Weight row only (no internal grid) ---
    # style.add('BOX', (0, items_count + 1), (-1, items_count + 1), 0.8, colors.black)

    # --- Grids for the totals area below Total Weight ---
    style.add('GRID', (2, items_count + 2), (-1, -1), 0.4, colors.black)
    style.add('BOX', (2, items_count + 2), (-1, -1), 1.2, colors.black)
    style.add('LINEABOVE', (0, items_count + 2), (-1, items_count + 2), 1.2, colors.black)
    style.add('BOTTOMPADDING', (0, items_count + 2), (-1, -1), 8 )
    style.add('TOPPADDING', (0, items_count + 2), (-1, -1), 8)

    # Merge cells for total-related rows (subtotal, taxes, total)
    for i in range(1, total_rows_count + 1):
        style.add('SPAN', (0, -i), (1, -i))
        style.add('SPAN', (2, -i), (3, -i))

    table.setStyle(style)
    return table
