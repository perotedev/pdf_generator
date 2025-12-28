from datetime import datetime
import pandas as pd
import os
from tkinter import filedialog
from typing import Any, List, Optional, Tuple
from pdf2image import convert_from_path
from PIL import Image

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
    Converte datas para formato brasileiro:
    - data -> DD/MM/YYYY
    - data e hora -> DD/MM/YYYY HH:MM
    """
    if pd.isna(value) or str(value).strip() == "":
        return ""
    
    dt = None

    if isinstance(value, (pd.Timestamp, datetime)):
        dt = value
    else:
        date_str = str(value).strip()
        dt = pd.to_datetime(date_str, dayfirst=True, errors="coerce")

        if pd.isna(dt):
            try:
                from dateutil import parser
                dt = parser.parse(date_str, dayfirst=True)
            except:
                try:
                    just_date = date_str.split(" ")[0]
                    dt = pd.to_datetime(just_date, dayfirst=False)
                except:
                    return date_str

    if pd.isna(dt):
        return ""

    output_type = (output_type or "").strip().lower()

    # ---- FORMATAÇÃO DEFINITIVA ----
    if output_type in ("data", "date"):
        return dt.strftime("%d/%m/%Y")

    if output_type in ("data e hora", "data_hora", "datetime", "datahora"):
        return dt.strftime("%d/%m/%Y às %H:%M")

    # default: retorna data completa BR
    return dt.strftime("%d/%m/%Y %H:%M")

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

def get_poppler__path() -> str:
    """Retorna o caminho para os binários do Poppler."""
    # Se estiver rodando como executável (PyInstaller), o Poppler pode estar no _MEIPASS
    import sys
    if getattr(sys, 'frozen', False):
        # No executável, incluiremos o poppler na raiz do pacote
        base_path = sys._MEIPASS
        return os.path.join(base_path, "poppler", "Library", "bin")
    
    # Em desenvolvimento, usa o caminho na pasta de dados
    return os.path.join(os.getcwd(), "poppler", "Library", "bin")

# Constantes para conversão de coordenadas (A4 em mm)
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297

def render_pdf_to_image(pdf_path: str, dpi: int = 150) -> Optional[Image.Image]:
    """
    Converte a primeira página de um PDF para um objeto PIL Image.
    """
    try:
        # Converte a primeira página do PDF para uma imagem PIL
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1, poppler_path=get_poppler__path())
        if images:
            return images[0]
        return None
    except Exception as e:
        print(f"Erro ao renderizar PDF: {e}")
        return None
