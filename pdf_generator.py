import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
from pdf2image import convert_from_path
import platform
import getpass
from typing import Dict, Any

from models import DocumentProfile, SpreadsheetProfile, ColumnType
from data_manager import data_manager

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
    Generates a single PDF document based on a template and a row of data.
    """
    
    # 1. Setup Canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # 2. Draw Template (Assuming template is a single image for simplicity, 
    # but since the user provided a PDF, we'll assume the template is a PDF 
    # that ReportLab cannot directly modify. We will overlay text on a blank page 
    # based on the coordinates, which is the most common approach when the template 
    # is a fixed background image or a pre-printed form).
    
    # NOTE: To truly use a PDF as a template, a library like PyPDF2/pypdf 
    # would be needed to overlay content. Since ReportLab is for *creating* PDFs, 
    # we'll proceed by drawing on a blank page, relying on the user to know 
    # the coordinates relative to an A4 page.
    
    # If the user wants to use the PDF as a background, they would need to convert 
    # it to an image first and load it here:
    pages = convert_from_path(document_profile.pdf_path, dpi=200, poppler_path="C:/Users/rodri/Poppler/poppler-25.11.0/Library/bin")
    temp_dir = os.path.join(os.path.dirname(__file__), ".temp")
    os.makedirs(temp_dir, exist_ok=True)
    bg_image_path = os.path.join(temp_dir, "background_temp.png")
    pages[0].save(bg_image_path, "PNG")

    try:
        c.drawImage(ImageReader(bg_image_path), 0, 0, width=width, height=height)
    except Exception:
        pass # Ignore if not an image

    # 3. Add Mapped Data
    c.setFont("Helvetica", 10)
    for mapping in document_profile.field_mappings:
        column_name = mapping.column_name
        
        # Find the corresponding value in the data row
        value = data_row.get(column_name, "")
        
        # Find the column type for formatting
        col_mapping = next((c for c in spreadsheet_profile.columns if c.custom_name == column_name), None)
        
        if col_mapping and col_mapping.column_type == "monetario":
            try:
                value = f"R$ {float(value):.2f}".replace('.', ',')
            except:
                pass # Keep original value if conversion fails
        
        # Convert mm coordinates (from top-left) to ReportLab points (from bottom-left)
        # Assuming X is from left, Y is from top. A4 height is 297mm.
        x_point = mapping.x * MM_TO_POINTS
        y_point = (A4[1] - (mapping.y * MM_TO_POINTS))
        
        c.drawString(x_point, y_point, str(value))

    # 4. Add Metadata (as requested)
    c.setAuthor(getpass.getuser())
    c.setTitle(os.path.basename(output_path))
    
    # Custom metadata (not standard PDF fields, but can be added to the Info dictionary)
    metadata = {
        "CreationDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ComputerID": platform.node(),
    }
    
    # ReportLab's info dictionary
    c.setSubject(metadata["CreationDate"])
    c.setCreator(metadata["ComputerID"])
    
    # 5. Save PDF
    c.save()
    os.remove(bg_image_path)

def batch_generate_pdfs(
    spreadsheet_path: str,
    document_profile: DocumentProfile,
    spreadsheet_profile: SpreadsheetProfile,
    status_callback: callable
) -> int:
    """
    Reads a spreadsheet and generates multiple PDFs.
    Returns the number of PDFs generated.
    """
    
    status_callback("Lendo planilha...")
    
    # 1. Read Spreadsheet Data
    try:
        df = pd.read_excel(spreadsheet_path)
    except Exception as e:
        raise Exception(f"Erro ao ler a planilha: {e}")

    # 2. Prepare Output Directory
    output_dir = data_manager.get_generated_pdfs_dir()
    
    generated_count = 0
    
    # 3. Map custom column names to DataFrame columns
    custom_to_original = {c.custom_name: c.original_header for c in spreadsheet_profile.columns}
    
    # 4. Iterate over data rows
    for index, row in df.iterrows():
        if index == 0:
            continue  # Skip header row if present
        
        status_callback(f"Processando linha {index + 1} de {len(df)}...")
        
        data_row = {}
        for column in spreadsheet_profile.columns:
            # Use .get() to safely access the column, handling case where original_header might not exist
            # due to user error or data change.
            if column.original_header in row:
                continue
            else:
                data_row[column.custom_name] = row[column.index]
        
        # Determine output filename (using the first column's value)
        first_column_value = str(data_row.get(spreadsheet_profile.columns[0].custom_name, "Document"))
        safe_filename = "".join(c for c in first_column_value if c.isalnum() or c in (' ', '_', '-')).rstrip()
        output_filename = f"{document_profile.name}_{safe_filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Generate the PDF
        generate_pdf_with_template(data_row, document_profile, spreadsheet_profile, output_path)
        generated_count += 1
        
    status_callback(f"Geração concluída. {generated_count} PDFs criados.")
    return generated_count
