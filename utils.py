from datetime import datetime
import pandas as pd
import os
from tkinter import filedialog
from typing import Any, List, Optional, Tuple
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import io

def select_file(file_types: List[Tuple[str, str]]) -> Optional[str]:
    """Opens a file dialog and returns the selected file path."""
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo",
        filetypes=file_types
    )
    return file_path if file_path else None

def read_spreadsheet_headers(file_path: str, header_row_index: int = 0) -> List[str]:
    """
    Lê os cabeçalhos de uma planilha Excel baseando-se no índice da linha fornecido (0-indexed).
    """
    try:
        # Lê a planilha sem cabeçalho para pegar a linha específica
        df = pd.read_excel(file_path, header=None)
        
        if header_row_index >= len(df):
            raise Exception(f"A linha {header_row_index + 1} não existe na planilha.")
            
        row = df.iloc[header_row_index]

        # Converte para strings e substitui NaN
        headers = [
            str(col) if pd.notna(col) else f"Coluna {i+1}"
            for i, col in enumerate(row)
        ]

        return headers

    except Exception as e:
        raise Exception(f"Erro ao ler a planilha: {e}")

def format_date_value(value: Any, output_type: str) -> str:
    """
    Trata campos de data e data/hora suportando múltiplos formatos de entrada.
    output_type: 'data' -> 'dd/mm/yyyy', 'data e hora' -> 'dd/mm/yy às hh:mm'
    """
    if pd.isna(value) or value == "":
        return ""
    
    try:
        # Se já for um objeto datetime do pandas/python
        if isinstance(value, (pd.Timestamp, datetime)):
            dt = value
        else:
            # Tenta converter string para datetime
            # O pandas.to_datetime é excelente para lidar com múltiplos formatos automaticamente
            dt = pd.to_datetime(str(value))
        
        if output_type == "data":
            return dt.strftime("%d/%m/%Y")
        elif output_type == "data e hora":
            return dt.strftime("%d/%m/%y às %H:%M")
        return str(value)
    except:
        return str(value)

# def read_spreadsheet_headers(file_path: str) -> List[str]:
#     """Reads the first row of a spreadsheet as headers."""
#     try:
#         # Read only the first row (header)
#         df = pd.read_excel(file_path, nrows=1, header=None)
        
#         # Extract headers, converting to string and handling potential NaN/None
#         headers = [str(col) if pd.notna(col) else f"Coluna {i+1}" 
#                    for i, col in enumerate(df.iloc[0])]
        
#         return headers
#     except Exception as e:
#         raise Exception(f"Erro ao ler a planilha: {e}")

def open_file_in_explorer(file_path: str):
    """Opens the file or directory in the default file explorer (Windows specific)."""
    if os.path.exists(file_path):
        # On Windows, 'explorer /select,path' opens the folder and selects the file
        # For a directory, just 'explorer path'
        if os.path.isdir(file_path):
            os.startfile(file_path)
        else:
            # This is a Windows-specific command
            os.system(f'explorer /select,"{file_path}"')
    else:
        # Fallback for directory if file doesn't exist
        dir_path = os.path.dirname(file_path)
        if os.path.exists(dir_path):
            os.startfile(dir_path)

# Constantes para conversão de coordenadas (A4 em mm)
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297

def render_pdf_to_image(pdf_path: str, dpi: int = 150) -> Optional[Image.Image]:
    """
    Converte a primeira página de um PDF para um objeto PIL Image.
    """
    try:
        # Converte a primeira página do PDF para uma imagem PIL
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1, poppler_path="C:/Users/rodri/Poppler/poppler-25.11.0/Library/bin")
        if images:
            return images[0]
        return None
    except Exception as e:
        print(f"Erro ao renderizar PDF: {e}")
        return None
