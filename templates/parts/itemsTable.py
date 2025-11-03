from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from babel.numbers import format_currency
from decimal import Decimal, ROUND_HALF_UP


def draw_items_table(items=None, discount=None, tax=None, totalQty=None, subTotal=None, discountTotal=None,  grandTotal=None, currency='USD'):
    data = [['Description', 'Qty', 'Unit', 'Price', 'Total']]

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
                Paragraph(f"{item['description']}", styles['Normal']),
                Paragraph(f"{item['quantity']}", styles['Normal']),
                Paragraph(f"{item['uom']}", styles['Normal']),
                Paragraph(format_currency(item['unitPrice'], currency, '#,##0.00 ¤'), right_align_style),
                Paragraph(format_currency(itemTotal, currency, '#,##0.00 ¤'), right_align_style),
            ])


    # --- Add total quantity line before discounts/taxes ---
    data.append([
        Paragraph(f"Total Weight", bold_left_align_style),
        Paragraph(f"{totalQty:.3f}", bold_left_align_style), '', '', ''
    ])

    # --- Subtotal if taxes or discount exist ---
    if tax and len(tax) > 0:
        data.append(['', '', Paragraph('Subtotal', bold_style), '', format_currency(f"{subTotal}", currency, '#,##0.00 ¤')])


    # --- Discounts ---
    discount_count = 0
    if discount is not None:
        discount_count = 1
        operator = discount.get('operator', None)
        if operator == 'fixed':
            discount_label = f"Discount {format_currency(discount['amount'], currency, '#,##0.00 ¤')}"
        elif operator == 'unit':
            discount_label = f"Discount {str(round(discount['amount'], 2)).rstrip('.0')} per unit"
        else:  # percentage
            discount_label = f"Discount {str(round(discount['amount'] * 100, 2)).rstrip('.0')}%"

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
            '', '', Paragraph(discount_label, green_bold_left),
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
        '', '', Paragraph('Total', bold_style),
        '', Paragraph(format_currency(f"{grandTotal}", currency, '#,##0.00 ¤'), bold_right_align_style)
    ])

    # --- Table Setup ---
    items_count = len(items) if items else 0
    total_rows_count = 1  # base total row
    total_rows_count += discount_count
    if isinstance(tax, list) and len(tax) > 0:
        total_rows_count += len(tax) + 1  # subtotal + each tax

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
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('TOPPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('LEFTPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('RIGHTPADDING', (0, 0), (-1, 0), 8), # Header padding
        ('BOTTOMPADDING', (1, 1), (-1, -1), 6), # Items rows padding
        ('TOPPADDING', (1, 1), (-1, -1), 6), # Items rows padding
        ('LEFTPADDING', (0, 1), (-1, -1), 8), # Items rows padding
        ('RIGHTPADDING', (0, 1), (-1, -1), 8), # Items rows padding

        # Grid for items rows only
        ('GRID', (0, 0), (-1, items_count), 0.1, colors.black),

        # Bold text for totals area
        ('FONTNAME', (2, items_count + 1), (-1, -1), 'Helvetica-Bold'),
    ])

    # --- Outer border for Total Weight row only (no internal grid) ---
    style.add('BOX', (0, items_count + 1), (-1, items_count + 1), 0.8, colors.black)

    # --- Grids for the totals area below Total Weight ---
    style.add('GRID', (2, items_count + 2), (-1, -1), 0.4, colors.black)
    style.add('BOX', (2, items_count + 2), (-1, -1), 1.2, colors.black)

    # Merge cells for total-related rows (subtotal, taxes, total)
    for i in range(1, total_rows_count + 1):
        style.add('SPAN', (0, -i), (1, -i))
        style.add('SPAN', (2, -i), (3, -i))

    table.setStyle(style)
    return table
