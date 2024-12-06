from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


logo_path = 'assets/img/apt_logotype_couleur.svg'

def layout():
    margins = {
        "left": 40,
        "right": 40,
        "top": 60,
        "bottom": 20
    }
    return margins


class PageNumCanvas(canvas.Canvas):
    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        self.title = kwargs.pop('title', 'Untitled')
        self.header= kwargs.pop('header', 'Document')
        super().__init__(*args, **kwargs)
        self.pages = []
        
    #----------------------------------------------------------------------
    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    #----------------------------------------------------------------------
    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)
        
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            self.draw_logo()
            self.draw_file_name(self.header)
            super().showPage()

        canvas.Canvas.save(self)
        
    #----------------------------------------------------------------------
    def draw_page_number(self, page_count):
        """
        Add the page number
        """
        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 9)
        self.drawRightString(205*mm, 5*mm, page)

    def draw_logo(self):
        """
        Draw the SVG logo on the page.
        """
        logo_x = 10 * mm
        margins = layout()
        logo_y = (A4[1] - margins["top"] / 1.7 *mm)

        # Load and convert the SVG to a Drawing object
        drawing = svg2rlg(logo_path)

        # Adjust the size by scaling (optional)
        drawing.scale(0.7, 0.7)
        # Render the Drawing object to the canvas
        renderPDF.draw(drawing, self, logo_x, logo_y)

    def draw_file_name(self, filename):
    # #     """
    # #     Draw the dynamic title on each page.
    # #     """
        margins = layout()
        title_y = (A4[1] - margins["top"]/2*mm)  # Adjust title position (below the logo or top of the page)
        self.setFont("Helvetica-Bold", 28)
        self.drawRightString(A4[0] - margins["right"], title_y, filename)



def draw_independent_columns(nested_tables_array, page_width=A4[0], left_margin=30, right_margin=30, gap=5, innerVerticalColumns=False):

    # Calculate the available width after accounting for the margins
    num_columns = len(nested_tables_array)
    available_width = page_width - (left_margin + right_margin) - (gap * (num_columns - 1))

    column_width = available_width / num_columns

    # Create the outer table with the calculated column widths
    outer_table = Table([nested_tables_array], colWidths=[column_width] * num_columns)

    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content at the top
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Remove left padding
        ('RIGHTPADDING', (0,0), (-2, -1), gap ),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0), # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent)  # No borders
    ]

    if innerVerticalColumns and num_columns > 1:
        for i in range(num_columns - 1) :
            style.append(('LINEAFTER', (i, 0), (i, -1), 0.3, colors.black))

    outer_table.setStyle(TableStyle(style))

    # Return the outer table
    return outer_table


styles = getSampleStyleSheet()

def draw_simple_table(rows, colWidths, default_style=None, cell_styles=None, row_styles=None, col_styles=None, bold_rows=None, bold_cols=None, font_size_rows=None, font_size_cols=None):
    content = []
    for r, row in enumerate(rows):
        row_data = []
        for c, col in enumerate(row):
            style = ParagraphStyle(name='Normal', parent=styles['Normal'])
            if default_style:
                style = default_style

            # Apply bold style for specific rows or columns
            if (bold_rows and r in bold_rows) or (bold_cols and c in bold_cols):
                style.fontName = 'Helvetica-Bold'
            
            # Apply font size for specific rows
            if font_size_rows and r in font_size_rows:
                style.fontSize = font_size_rows[r]
            
            # Apply font size for specific columns
            if font_size_cols and c in font_size_cols:
                style.fontSize = font_size_cols[c]
            
            row_data.append(Paragraph(col, style))
        content.append(row_data)

    table = Table(content, colWidths=colWidths)
    # Default styles
    table_styles = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),       # Align content at the top
        ('LEFTPADDING', (0, 0), (-1, -1), 0),      # Remove left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),     # Adjust right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),       # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),    # Remove bottom padding
        ('LINEBELOW', (0, 0), (-1, -1), 0, colors.transparent)  # No borders
    ]
    
    # Add row-specific styles if provided
    if row_styles:
        for r, style in row_styles.items():
            table_styles.append((style[0], (0, r), (-1, r), style[1]))
    
    # Add column-specific styles if provided
    if col_styles:
        for c, style in col_styles.items():
            table_styles.append((style[0], (c, 0), (c, -1), style[1]))

    # Apply styles to the table
    table.setStyle(TableStyle(table_styles))

    return table