# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd
import os
from tkinter import filedialog
from typing import Any, List, Optional, Tuple, Dict
from PIL import Image
import re
import fitz 
from reportlab.lib.pagesizes import A1, A2, A3, A4, A5, A6, LETTER, LEGAL, landscape

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

def format_date_value(value: Any, output_type: Optional[str] = None) -> str:
    """
    Converte datas para formato brasileiro com maior robustez.
    """
    if pd.isna(value) or str(value).strip() == "":
        return ""
    
    dt = None

    # 1. Se já for objeto de data
    if isinstance(value, (pd.Timestamp, datetime)):
        dt = value
    else:
        date_str = str(value).strip()
        
        # 2. Tenta converter com dayfirst=True (Padrão BR)
        # O pandas é inteligente para ISO (YYYY-MM-DD) mesmo com dayfirst=True
        dt = pd.to_datetime(date_str, dayfirst=True, errors="coerce")

        # 3. Se falhou, tenta dateutil parser (mais flexível para formatos exóticos)
        if pd.isna(dt):
            try:
                from dateutil import parser
                dt = parser.parse(date_str, dayfirst=True)
            except:
                # 4. Fallback manual para casos onde o separador ou formato é estranho
                try:
                    # Tenta extrair apenas a parte da data se houver lixo
                    match = re.search(r'(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})', date_str)
                    if match:
                        dt = pd.to_datetime(match.group(1), dayfirst=True, errors="coerce")
                except:
                    pass

    # Se ainda assim não conseguiu converter, retorna o original ou vazio
    if pd.isna(dt) or dt is None:
        # Se for uma string que não parece data, talvez seja melhor retornar vazio ou a string
        return str(value).strip()

    output_type = (output_type or "").strip().lower()

    # ---- FORMATAÇÃO ----
    try:
        if output_type in ("data", "date"):
            return dt.strftime("%d/%m/%Y")
        elif output_type in ("data e hora", "data_hora", "datetime", "datahora"):
            return dt.strftime("%d/%m/%Y às %H:%M")
        else:
            # Default: DD/MM/YYYY HH:MM (sem o "às" para ser mais padrão)
            return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return str(value).strip()

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

def get_pdf_page_count(pdf_path: str) -> int:
    try:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except:
        return 0

def render_pdf_to_image(pdf_path: str, page_index: int = 0, dpi: int = 150) -> Optional[Image.Image]:
    try:
        doc = fitz.open(pdf_path)
        if page_index >= len(doc):
            doc.close()
            return None
            
        page = doc[page_index]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        mode = "RGB"
        
        if pix.alpha:   # se tiver alpha, converte corretamente
            mode = "RGBA"

        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        doc.close()
        return img
    except Exception as e:
        print(f"Erro ao renderizar PDF: {e}")
        return None

def format_cpf(value: str):
    digits = re.sub(r'\D', '', str(value))
    if len(digits) == 11:
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
    return value  # Mantém original se não bater

def format_cnpj(value: str):
    digits = re.sub(r'\D', '', str(value))
    if len(digits) == 14:
        return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
    return value

def format_phone(value: str):
    digits = re.sub(r'\D', '', str(value))
    
    # (99) 99999-9999 → 11 dígitos
    if len(digits) == 11:
        return f"({digits[0:2]}) {digits[2:7]}-{digits[7:]}"
    
    # (99) 9999-9999 → 10 dígitos
    if len(digits) == 10:
        return f"({digits[0:2]}) {digits[2:6]}-{digits[6:]}"
    
    return value  # não formata caso não bata

# Mapeamento de formatos de página
PAGE_SIZES: Dict[str, Tuple[float, float]] = {
    "A1": A1,
    "A2": A2,
    "A3": A3,
    "A4": A4,
    "A5": A5,
    "A6": A6,
    "Letter": LETTER,
    "Legal": LEGAL
}

def get_page_size(format_name: str, orientation: str = "portrait") -> Tuple[float, float]:
    """
    Retorna o tamanho da página em pontos (width, height) baseado no formato e orientação.
    
    Args:
        format_name: Nome do formato (A1, A2, A3, A4, A5, A6, Letter, Legal)
        orientation: "portrait" ou "landscape"
    
    Returns:
        Tupla (width, height) em pontos
    """
    size = PAGE_SIZES.get(format_name, A4)
    
    if orientation == "landscape":
        return landscape(size)
    
    return size

def get_page_size_mm(format_name: str, orientation: str = "portrait") -> Tuple[float, float]:
    """
    Retorna o tamanho da página em milímetros baseado no formato e orientação.
    
    Args:
        format_name: Nome do formato (A1, A2, A3, A4, A5, A6, Letter, Legal)
        orientation: "portrait" ou "landscape"
    
    Returns:
        Tupla (width_mm, height_mm) em milímetros
    """
    size_points = get_page_size(format_name, orientation)
    # Converte pontos para mm (1 ponto = 0.352778 mm)
    POINTS_TO_MM = 0.352778
    width_mm = size_points[0] * POINTS_TO_MM
    height_mm = size_points[1] * POINTS_TO_MM
    return (width_mm, height_mm)

# Constantes para conversão de coordenadas (A4 em mm) - mantidas para compatibilidade
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
