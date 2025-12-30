from datetime import datetime
import pandas as pd
import os
from tkinter import filedialog
from typing import Any, List, Optional, Tuple
from PIL import Image
import re
import fitz 

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

# método antigo com pdf2image e poppler
# def render_pdf_to_image(pdf_path: str, dpi: int = 150) -> Optional[Image.Image]:
#     """
#     Converte a primeira página de um PDF para um objeto PIL Image.
#     """
#     try:
#         # Converte a primeira página do PDF para uma imagem PIL
#         images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1, poppler_path=get_poppler__path())
#         if images:
#             return images[0]
#         return None
#     except Exception as e:
#         print(f"Erro ao renderizar PDF: {e}")
#         return None

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