from asyncio import subprocess
import os
from tkinter import messagebox
from core.data_manager import data_manager

def open_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.startfile(os.path.abspath(file_path))
        else:
            messagebox.showerror("Erro", "Arquivo não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")
    
def open_folder(path: str):
    try:
        if os.path.exists(path):
            path = os.path.abspath(path)
            
            if os.path.isfile(path):
                subprocess.run(['explorer', '/select,', path])
            else:
                os.startfile(path)
        else:
            messagebox.showerror("Erro", "Caminho não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir a pasta: {e}")

def open_file_directory(path: str):
    try:
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                import subprocess
                subprocess.call(['xdg-open', path])
        else:
            messagebox.showerror("Erro", "Diretório não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o diretório: {e}")