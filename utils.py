import pandas as pd
import os
from tkinter import filedialog
from typing import List, Optional, Tuple

def select_file(file_types: List[Tuple[str, str]]) -> Optional[str]:
    """Opens a file dialog and returns the selected file path."""
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo",
        filetypes=file_types
    )
    return file_path if file_path else None

def read_spreadsheet_headers(file_path: str) -> List[str]:
    """
    Lê um Excel ignorando a primeira linha e pegando o primeiro header válido
    a partir da segunda linha (linha real sem células mescladas),
    utilizando apenas pandas.
    """
    try:
        df = pd.read_excel(file_path, header=None)

        def is_merged_row(row) -> bool:
            """
            Detecta linhas com células mescladas baseando-se no comportamento do pandas:
            valores mesclados são repetidos em sequência, geralmente com 1 único valor.
            """
            unique_vals = set(row.dropna())
            return len(unique_vals) <= 1

        header_row = None

        # Começar da segunda linha (índice 1)
        for i in range(1, len(df)):
            row = df.iloc[i]
            if not is_merged_row(row):
                header_row = i
                break

        if header_row is None:
            raise Exception("Nenhuma linha válida encontrada para header.")

        row = df.iloc[header_row]

        # Converte para strings e substitui NaN
        headers = [
            str(col) if pd.notna(col) else f"Coluna {i+1}"
            for i, col in enumerate(row)
        ]

        return headers

    except Exception as e:
        raise Exception(f"Erro ao ler a planilha: {e}")

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
