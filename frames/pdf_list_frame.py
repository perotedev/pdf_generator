import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime
from typing import List

from core.data_manager import data_manager
from utils import open_file_in_explorer

class PdfListFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.all_pdfs: List[str] = []
        self.filtered_pdfs: List[str] = []
        self.search_var = ctk.StringVar()
        self.year_var = ctk.StringVar(value="Todos")
        self.month_var = ctk.StringVar(value="Todos")

        # --- Widgets ---
        ctk.CTkLabel(self, text="PDFs Gerados", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Search Bar
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.search_frame, text="Ano:").grid(row=0, column=2, padx=(10, 5), pady=10)
        self.year_menu = ctk.CTkOptionMenu(self.search_frame, variable=self.year_var, values=["Todos"], command=lambda _: self._on_filter_change())
        self.year_menu.grid(row=0, column=3, padx=(0, 10), pady=10, sticky="w")

        ctk.CTkLabel(self.search_frame, text="Mês:").grid(row=0, column=4, padx=(10, 5), pady=10)
        self.month_menu = ctk.CTkOptionMenu(self.search_frame, variable=self.month_var, values=["Todos"], command=lambda _: self._on_filter_change())
        self.month_menu.grid(row=0, column=5, padx=(0, 10), pady=10, sticky="w")

        ctk.CTkLabel(self.search_frame, text="Buscar:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Digite o nome do arquivo...")
        self.search_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(5, weight=1)
        self.search_var.trace_add("write", lambda name, index, mode: self._filter_pdfs())

        # PDF List Display
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Arquivos PDF")
        self.list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        # Configura a coluna interna do scrollable frame para expandir
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Button to open directory
        self.open_dir_button = ctk.CTkButton(self, text="Abrir Pasta de PDFs", command=self._open_pdf_directory)
        self.open_dir_button.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="e")
        
        # Ajuste do wrap quando o frame é redimensionado
        self.list_frame.bind("<Configure>", lambda event: self.after(100, lambda: self.update_wrap(event)) if event.width else None)

        self._load_pdfs()

    def _load_pdfs(self):
        years = ["Todos"] + data_manager.get_available_years()
        self.year_menu.configure(values=years)
        
        year = self.year_var.get()
        if year != "Todos":
            months = ["Todos"] + data_manager.get_available_months(year)
            self.month_menu.configure(values=months)
        else:
            self.month_menu.configure(values=["Todos"])
            self.month_var.set("Todos")

        y = None if self.year_var.get() == "Todos" else self.year_var.get()
        m = None if self.month_var.get() == "Todos" else self.month_var.get()
        
        self.all_pdfs = data_manager.get_generated_pdfs(year=y, month=m)
        self._filter_pdfs()

    def _on_filter_change(self):
        self._load_pdfs()

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

    def update_wrap(self, event):
        if event is None:
            wrap = 550
        else:
            # Ajuste dinâmico do wrap baseado na largura do frame
            wrap = max(event.width - 600, 300)

        for label in self.file_labels:
            label.configure(wraplength=wrap)
            
    def _update_list_display(self):
        # Limpa widgets existentes
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.filtered_pdfs:
            ctk.CTkLabel(self.list_frame, text="Nenhum PDF encontrado.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Criamos o container principal diretamente no list_frame
        # Importante: Não definir largura fixa aqui para não quebrar o scroll
        self.main_container = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="ew")
        self.main_container.grid_columnconfigure(0, weight=1) # Nome (Expansível)
        self.main_container.grid_columnconfigure(1, weight=0) # Ano
        self.main_container.grid_columnconfigure(2, weight=0) # Mês
        self.main_container.grid_columnconfigure(3, weight=0) # Data
        self.main_container.grid_columnconfigure(4, weight=0) # Ação

        # Header Row
        ctk.CTkLabel(self.main_container, text="Nome do Arquivo", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.main_container, text="Ano", font=ctk.CTkFont(weight="bold"), width=60).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.main_container, text="Mês", font=ctk.CTkFont(weight="bold"), width=40).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.main_container, text="Data Criação", font=ctk.CTkFont(weight="bold"), width=120).grid(row=0, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.main_container, text="Ação", font=ctk.CTkFont(weight="bold"), width=140).grid(row=0, column=4, padx=10, pady=5, sticky="e")
        
        self.file_labels: List[ctk.CTkLabel] = []

        # Data Rows
        for i, pdf_path in enumerate(self.filtered_pdfs):
            row = i + 1
            filename = os.path.basename(pdf_path)
            
            path_parts = os.path.normpath(pdf_path).split(os.sep)
            try:
                file_year = path_parts[-3]
                file_month = path_parts[-2]
            except IndexError:
                file_year = "-"
                file_month = "-"

            try:
                timestamp = os.path.getctime(pdf_path)
                creation_date = datetime.fromtimestamp(timestamp).strftime("%d/%m/%y %H:%M")
            except:
                creation_date = "-"

            file_label = ctk.CTkLabel(self.main_container, text=filename, justify="left")
            file_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            self.file_labels.append(file_label)
            
            ctk.CTkLabel(self.main_container, text=file_year, width=60).grid(row=row, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.main_container, text=file_month, width=40).grid(row=row, column=2, padx=10, pady=5)
            ctk.CTkLabel(self.main_container, text=creation_date, width=120).grid(row=row, column=3, padx=10, pady=5)
            
            open_button = ctk.CTkButton(self.main_container, text="Abrir arquivo", width=120, command=lambda p=pdf_path: self._open_file(p))
            open_button.grid(row=row, column=4, padx=10, pady=5, sticky="e")

        # Força a atualização do layout para calcular o tamanho correto
        self.list_frame.update_idletasks()
        
        # O segredo para o scroll funcionar com grid é garantir que o canvas interno saiba o tamanho do conteúdo
        # No CTkScrollableFrame, isso geralmente é automático, mas em layouts complexos podemos ajudar:
        self.list_frame._parent_canvas.configure(scrollregion=self.list_frame._parent_canvas.bbox("all"))

    def _open_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                messagebox.showerror("Erro", "Arquivo não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")

    def _open_pdf_directory(self):
        try:
            pdf_dir = data_manager.pdf_base_dir
            if os.path.exists(pdf_dir):
                os.startfile(pdf_dir)
            else:
                messagebox.showerror("Erro", "Diretório não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o diretório: {e}")

    def refresh_data(self):
        self._load_pdfs()