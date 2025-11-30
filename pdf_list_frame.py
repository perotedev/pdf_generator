import customtkinter as ctk
from tkinter import messagebox
import os
from typing import List

from data_manager import data_manager
from utils import open_file_in_explorer

class PdfListFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.all_pdfs: List[str] = []
        self.filtered_pdfs: List[str] = []
        self.search_var = ctk.StringVar()

        # --- Widgets ---
        ctk.CTkLabel(self, text="PDFs Gerados", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Search Bar
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.search_frame, text="Buscar:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Digite o nome do arquivo...")
        self.search_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.search_var.trace_add("write", lambda name, index, mode: self._filter_pdfs())

        # PDF List Display
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Arquivos PDF")
        self.list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Button to open directory
        self.open_dir_button = ctk.CTkButton(self, text="Abrir Pasta de PDFs", command=self._open_pdf_directory)
        self.open_dir_button.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="e")

        self._load_pdfs()

    def _load_pdfs(self):
        self.all_pdfs = data_manager.get_generated_pdfs()
        self._filter_pdfs()

    def _filter_pdfs(self):
        search_term = self.search_var.get().lower()
        if search_term:
            self.filtered_pdfs = [
                pdf for pdf in self.all_pdfs 
                if os.path.basename(pdf).lower().find(search_term) != -1
            ]
        else:
            self.filtered_pdfs = self.all_pdfs
        
        self._update_list_display()

    def _update_list_display(self):
        # Clear existing widgets
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.filtered_pdfs:
            ctk.CTkLabel(self.list_frame, text="Nenhum PDF encontrado.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Header Row
        ctk.CTkLabel(self.list_frame, text="Nome do Arquivo", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.list_frame, text="Data de Criação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.list_frame, text="Ação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Data Rows
        for i, pdf_path in enumerate(self.filtered_pdfs):
            row = i + 1
            filename = os.path.basename(pdf_path)
            
            try:
                # Get creation time and format it
                timestamp = os.path.getctime(pdf_path)
                creation_date = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
            except:
                creation_date = "N/A"

            ctk.CTkLabel(self.list_frame, text=filename, wraplength=400).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.list_frame, text=creation_date).grid(row=row, column=1, padx=10, pady=5, sticky="w")

            open_button = ctk.CTkButton(self.list_frame, text="Abrir no Explorer", width=120, command=lambda p=pdf_path: self._open_file(p))
            open_button.grid(row=row, column=2, padx=10, pady=5, sticky="w")

    def _open_file(self, file_path: str):
        try:
            open_file_in_explorer(file_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo no Explorer: {e}")

    def _open_pdf_directory(self):
        try:
            pdf_dir = data_manager.get_generated_pdfs_dir()
            open_file_in_explorer(pdf_dir)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o diretório: {e}")

    def refresh_data(self):
        self._load_pdfs()

# Import datetime for formatting
from datetime import datetime
