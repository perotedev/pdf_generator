# -*- coding: utf-8 -*-
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import platform
import getpass
from typing import Dict, Any, List
import fitz

from models import DocumentProfile, SpreadsheetProfile, ColumnType, PdfFieldMapping, TextStyle
from utils import format_date_value, format_cpf, format_cnpj, format_phone, get_page_size

# PDF coordinates are typically measured from the bottom-left corner.
# ReportLab uses points (1 point = 1/72 inch). 1mm = 2.83465 points.
MM_TO_POINTS = 2.83465

def hex_to_rgb(hex_color: str) -> tuple:
    """Converte cor hexadecimal para RGB (0-1)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (r/255.0, g/255.0, b/255.0)

def apply_text_style(c: canvas.Canvas, style: TextStyle):
    """Aplica o estilo de texto ao canvas"""
    # Determina o nome da fonte baseado nos estilos
    font_name = style.font_family
    
    # ReportLab tem algumas fontes padrão que suportam bold/italic
    # Para outras fontes, usamos as variantes disponíveis
    if style.bold and style.italic:
        if font_name == "Helvetica":
            font_name = "Helvetica-BoldOblique"
        elif font_name == "Times New Roman":
            font_name = "Times-BoldItalic"
        elif font_name == "Courier New":
            font_name = "Courier-BoldOblique"
        else:
            font_name = "Helvetica-BoldOblique"
    elif style.bold:
        if font_name == "Helvetica":
            font_name = "Helvetica-Bold"
        elif font_name == "Times New Roman":
            font_name = "Times-Bold"
        elif font_name == "Courier New":
            font_name = "Courier-Bold"
        else:
            font_name = "Helvetica-Bold"
    elif style.italic:
        if font_name == "Helvetica":
            font_name = "Helvetica-Oblique"
        elif font_name == "Times New Roman":
            font_name = "Times-Italic"
        elif font_name == "Courier New":
            font_name = "Courier-Oblique"
        else:
            font_name = "Helvetica-Oblique"
    else:
        # Mapeia nomes de fontes comuns para nomes do ReportLab
        font_map = {
            "Times New Roman": "Times-Roman",
            "Courier New": "Courier",
            "Helvetica": "Helvetica"
        }
        font_name = font_map.get(font_name, "Helvetica")
    
    # Define a fonte e tamanho
    c.setFont(font_name, style.font_size)
    
    # Define a cor
    r, g, b = hex_to_rgb(style.color)
    c.setFillColorRGB(r, g, b)

def generate_pdf_with_template(
    data_row: Dict[str, Any],
    document_profile: DocumentProfile,
    spreadsheet_profile: SpreadsheetProfile,
    output_path: str
):
    """
    Generates a multi-page PDF document based on a template and a row of data.
    """
    
    # 1. Setup Canvas com o formato e orientação corretos
    page_size = get_page_size(document_profile.page_format, document_profile.page_orientation)
    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size
    
    # 2. Load Template PDF
    doc = fitz.open(document_profile.pdf_path)
    total_pages = len(doc)
    
    temp_dir = os.path.join(os.path.dirname(__file__), ".temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Group mappings by page
    mappings_by_page: Dict[int, List[PdfFieldMapping]] = {}
    for mapping in document_profile.field_mappings:
        pg = getattr(mapping, 'page_index', 0)
        if pg not in mappings_by_page:
            mappings_by_page[pg] = []
        mappings_by_page[pg].append(mapping)

    # 3. Process each page
    for page_idx in range(total_pages):
        # Render template page to image for background
        page = doc[page_idx]
        dpi = 200
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)
        
        bg_image_path = os.path.join(temp_dir, f"bg_p{page_idx}_temp.png")
        pix.save(bg_image_path)
        
        # Draw background
        c.drawImage(ImageReader(bg_image_path), 0, 0, width=width, height=height)
        
        # Add Mapped Data for this page
        if page_idx in mappings_by_page:
            for mapping in mappings_by_page[page_idx]:
                column_name = mapping.column_name
                value = str(data_row.get(column_name, ""))
                
                # Find the column type for formatting
                col_mapping = next((col for col in spreadsheet_profile.columns if col.custom_name == column_name), None)
                
                if col_mapping:
                    match col_mapping.column_type:
                        case "monetario":
                            try:
                                value = str(value).replace('$', '').replace('R$', '').strip()
                                value = f"R$ {float(value):.2f}".replace('.', ',')
                            except (ValueError, TypeError): pass
                        case "data":
                            value = format_date_value(value, "data")
                        case "data e hora":
                            value = format_date_value(value, "data e hora")
                        case "cpf":
                            value = format_cpf(value)
                        case "cnpj":
                            value = format_cnpj(value)
                        case "telefone":
                            value = format_phone(value)

                if not value or value.lower() == "nan":
                    value = ""

                # Aplica o estilo do texto
                style = mapping.style if mapping.style else TextStyle()
                apply_text_style(c, style)
                
                # Convert mm coordinates (from top-left) to ReportLab points (from bottom-left)
                x_point = mapping.x * MM_TO_POINTS
                y_point = (height - (mapping.y * MM_TO_POINTS))
                
                # Desenha o texto
                if style.underline:
                    # Para sublinhado, precisamos desenhar uma linha abaixo do texto
                    text_width = c.stringWidth(str(value), c._fontname, c._fontsize)
                    c.drawString(x_point, y_point, str(value))
                    c.line(x_point, y_point - 2, x_point + text_width, y_point - 2)
                else:
                    c.drawString(x_point, y_point, str(value))
        
        # Finish current page and start next if not last
        c.showPage()
        
        # Cleanup temp image
        if os.path.exists(bg_image_path):
            os.remove(bg_image_path)

    doc.close()

    # 4. Add Metadata
    c.setAuthor(getpass.getuser())
    c.setTitle(os.path.basename(output_path))
    
    # 5. Save PDF
    c.save()

def batch_generate_pdfs(
    spreadsheet_path: str,
    document_profile: DocumentProfile,
    spreadsheet_profile: SpreadsheetProfile,
    status_callback: callable,
    base_date: datetime
) -> int:
    """
    Reads a spreadsheet and generates multiple PDFs.
    Returns the number of PDFs generated.
    """
    from core.data_manager import data_manager
    
    status_callback("Lendo planilha...")
    
    # 1. Read Spreadsheet Data
    try:
        header_idx = spreadsheet_profile.header_row
        df = pd.read_excel(spreadsheet_path, header=header_idx)
    except Exception as e:
        raise Exception(f"Erro ao ler a planilha: {e}")

    # 2. Prepare Output Directory
    output_dir = data_manager.get_generated_pdfs_dir(base_date)
    generated_count = 0
    
    # 3. Iterate over data rows
    for index, row in df.iterrows():
        status_callback(f"Processando linha {index + 1} de {len(df)}...")
        
        data_row = {}
        for column in spreadsheet_profile.columns:
            if column.original_header in df.columns:
                data_row[column.custom_name] = row[column.original_header]
            else:
                data_row[column.custom_name] = row.iloc[column.index]
        
        title_value = str(data_row.get(document_profile.title_column, "Documento"))
        safe_filename = "".join(c for c in title_value if c.isalnum() or c in (' ', '_', '-')).rstrip()
        if not safe_filename:
            safe_filename = "Documento"
            
        output_filename = f"{safe_filename}_{document_profile.name}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        counter = 1
        while os.path.exists(output_path):
            output_filename = f"{safe_filename}_{document_profile.name}_{counter}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            counter += 1
        
        generate_pdf_with_template(data_row, document_profile, spreadsheet_profile, output_path)
        generated_count += 1
        
    status_callback(f"Geração concluída. {generated_count} PDFs criados.")
    return generated_count
