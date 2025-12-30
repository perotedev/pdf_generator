import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime
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
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Arquivos PDF") # Defina uma altura inicial
        self.list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Button to open directory
        self.open_dir_button = ctk.CTkButton(self, text="Abrir Pasta de PDFs", command=self._open_pdf_directory)
        self.open_dir_button.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="e")

        self._load_pdfs()

    def _load_pdfs(self):
        # Atualiza os menus de filtro
        years = ["Todos"] + data_manager.get_available_years()
        self.year_menu.configure(values=years)
        
        year = self.year_var.get()
        if year != "Todos":
            months = ["Todos"] + data_manager.get_available_months(year)
            self.month_menu.configure(values=months)
        else:
            self.month_menu.configure(values=["Todos"])
            self.month_var.set("Todos")

        # Carrega os PDFs baseados nos filtros de diretório
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
            wrap = max(event.width - 520, 550)

        for label in self.file_labels:
            label.configure(wraplength=wrap)
            
    def _update_list_display(self):
        # Clear existing widgets
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.filtered_pdfs:
            ctk.CTkLabel(self.list_frame, text="Nenhum PDF encontrado.").grid(row=0, column=0, padx=20, pady=20)
            return

        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(4, weight=0)
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.left_wraper = ctk.CTkFrame(self.list_frame)
        self.left_wraper.grid(row=0, column=0, columnspan=3, padx=0, pady=0, sticky="nsew")
        self.right_wraper = ctk.CTkFrame(self.list_frame, width=280)
        self.right_wraper.grid(row=0, column=4, padx=0, pady=0, sticky="nsew")
        self.right_wraper.grid_propagate(False)

        # Header Row
        ctk.CTkLabel(self.left_wraper, text="Nome do Arquivo", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="sw")
        ctk.CTkLabel(self.right_wraper, text="Data de Criação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(self.right_wraper, text="Ação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=(10,0), pady=5, sticky="ew")
        self.file_labels: List[ctk.CTkLabel] = []

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

            file_label = ctk.CTkLabel(self.left_wraper, text=filename, justify="left")
            file_label.grid(row=row, column=0, padx=10, pady=5, sticky="sw")
            self.file_labels.append(file_label)
            ctk.CTkLabel(self.right_wraper, text=creation_date).grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            open_button = ctk.CTkButton(self.right_wraper, text="Abrir arquivo", width=120, command=lambda p=pdf_path: self._open_file(p))
            open_button.grid(row=row, column=1, padx=(10,0), pady=5, sticky="ew")

        self.list_frame.update_idletasks()
        # self.list_frame.bind("<Configure>", lambda event: self.after(100, self.update_wrap(event)))
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
