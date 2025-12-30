import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
import platform
import getpass
from typing import Dict, Any, List
import fitz

from models import DocumentProfile, SpreadsheetProfile, ColumnType, PdfFieldMapping
from data_manager import data_manager
from utils import format_date_value, format_cpf, format_cnpj, format_phone

# PDF coordinates are typically measured from the bottom-left corner.
# ReportLab uses points (1 point = 1/72 inch). 1mm = 2.83465 points.
MM_TO_POINTS = 2.83465

def generate_pdf_with_template(
    data_row: Dict[str, Any],
    document_profile: DocumentProfile,
    spreadsheet_profile: SpreadsheetProfile,
    output_path: str
):
    """
    Generates a multi-page PDF document based on a template and a row of data.
    """
    
    # 1. Setup Canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
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
        c.setFont("Helvetica", 10)
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

                # Convert mm coordinates (from top-left) to ReportLab points (from bottom-left)
                x_point = mapping.x * MM_TO_POINTS
                y_point = (A4[1] - (mapping.y * MM_TO_POINTS))
                
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
