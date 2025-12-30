import customtkinter as ctk
from tkinter import messagebox
from typing import List, Optional
from datetime import datetime, date
import calendar
import locale
import os

from models import DocumentProfile, SpreadsheetProfile
from core.data_manager import data_manager
from utils import select_file
from core.pdf_generator import batch_generate_pdfs

class BatchGenerationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.document_profiles: List[DocumentProfile] = []
        self.selected_document_profile: Optional[DocumentProfile] = None
        self.spreadsheet_profile: Optional[SpreadsheetProfile] = None
        self.spreadsheet_path: Optional[str] = None
        self.status_var = ctk.StringVar(value="Pronto para gerar.")

        # --- Widgets ---
        ctk.CTkLabel(self, text="Geração de Documentos em Lote", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # 1. Document Profile Selection
        self.profile_select_frame = ctk.CTkFrame(self)
        self.profile_select_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.profile_select_frame.grid_columnconfigure(0, weight=1)
        
        self.document_profile_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                         values=["Selecione um Perfil de Documento"],
                                                         command=self._on_profile_select)
        self.document_profile_menu.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.associated_profile_label = ctk.CTkLabel(self.profile_select_frame, text="Perfil de Planilha Associado: Nenhum")
        self.associated_profile_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        # 2. Spreadsheet File Selection
        self.file_select_frame = ctk.CTkFrame(self)
        self.file_select_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.file_select_frame.grid_columnconfigure(0, weight=1)
        
        self.select_file_button = ctk.CTkButton(self.file_select_frame, text="Selecionar Planilha de Dados", command=self._select_spreadsheet)
        self.select_file_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.file_path_label = ctk.CTkLabel(self.file_select_frame, text="Arquivo Selecionado: Nenhum")
        self.file_path_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        # 3. Date Selection (Month and Year)
        self.date_select_frame = ctk.CTkFrame(self)
        self.date_select_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.date_select_frame.grid_columnconfigure(0, weight=1)
        self.date_select_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.date_select_frame, text="Mês Base:").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.date_select_frame, text="Ano Base:").grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")

        # Month Select
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'pt_BR')
            except locale.Error:
                pass # Fallback to default locale (English)

        month_names = [calendar.month_name[i].capitalize() for i in range(1, 13)]
        current_month_name = calendar.month_name[datetime.now().month].capitalize()
        self.month_select = ctk.CTkOptionMenu(self.date_select_frame, values=month_names)
        self.month_select.set(current_month_name)
        self.month_select.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Year Select
        current_year = datetime.now().year
        year_options = [str(y) for y in range(current_year - 5, current_year + 6)] # 5 years before and after
        self.year_select = ctk.CTkOptionMenu(self.date_select_frame, values=year_options)
        self.year_select.set(str(current_year))
        self.year_select.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        # 4. Generate Button
        self.generate_button = ctk.CTkButton(self, text="GERAR DOCUMENTOS EM LOTE", command=self._generate, state="disabled")
        self.generate_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # 5. Status
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.status_frame, text="Status:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        ctk.CTkLabel(self.status_frame, textvariable=self.status_var, wraplength=1200).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self._load_profiles()

    def _load_profiles(self):
        self.document_profiles = data_manager.load_profiles(DocumentProfile)
        profile_names = [p.name for p in self.document_profiles]
        
        if not profile_names:
            self.document_profile_menu.configure(values=["Nenhum Perfil de Documento Encontrado"], state="disabled")
            self.document_profile_menu.set("Nenhum Perfil de Documento Encontrado")
            self.generate_button.configure(state="disabled")
        else:
            self.document_profile_menu.configure(values=profile_names, state="normal")
            self.document_profile_menu.set(profile_names[0])
            self._on_profile_select(profile_names[0])

    def _on_profile_select(self, profile_name: str):
        self.selected_document_profile = next((p for p in self.document_profiles if p.name == profile_name), None)
        self.spreadsheet_profile = None
        
        if self.selected_document_profile:
            # Find the associated SpreadsheetProfile
            spreadsheet_profiles = data_manager.load_profiles(SpreadsheetProfile)
            self.spreadsheet_profile = next((p for p in spreadsheet_profiles if p.name == self.selected_document_profile.spreadsheet_profile_name), None)
            
            if self.spreadsheet_profile:
                self.associated_profile_label.configure(text=f"Perfil de Planilha Associado: {self.spreadsheet_profile.name}")
            else:
                self.associated_profile_label.configure(text="Perfil de Planilha Associado: NÃO ENCONTRADO", text_color="red")
        
            self._update_generate_button_state()

    def _select_spreadsheet(self):
        file_path = select_file([("Arquivos Excel", "*.xlsx *.xls")])
        if file_path:
            self.spreadsheet_path = file_path
            self.file_path_label.configure(text=f"Arquivo Selecionado: {os.path.basename(file_path)}")
        self._update_generate_button_state()

    def _update_generate_button_state(self):
        if self.selected_document_profile and self.spreadsheet_profile and self.spreadsheet_path:
            self.generate_button.configure(state="normal")
        else:
            self.generate_button.configure(state="disabled")

    def _update_status(self, message: str):
        self.status_var.set(message)
        self.update_idletasks() # Force GUI update

    def _generate(self):
        if not self.selected_document_profile or not self.spreadsheet_profile or not self.spreadsheet_path:
            messagebox.showerror("Erro", "Selecione o perfil de documento e a planilha de dados.")
            return

        # 1. Get selected month and year
        selected_month_name = self.month_select.get()
        selected_year_str = self.year_select.get()

        # 2. Convert month name to number
        month_num = -1
        # Tenta encontrar o número do mês (1-12) a partir do nome
        for i, name in enumerate(calendar.month_name):
            if name.lower() == selected_month_name.lower():
                month_num = i
                break
        
        if month_num == -1:
            messagebox.showerror("Erro de Data", f"Mês selecionado inválido: {selected_month_name}")
            return

        # 3. Determine the base date
        current_date = datetime.now()
        
        # Verifica se a seleção é a data de hoje (default)
        is_default_date = (month_num == current_date.month and int(selected_year_str) == current_date.year)
        
        if is_default_date:
            # Se for a data de hoje, usa o dia de hoje
            base_date = current_date
        else:
            # Caso contrário, usa o dia 1º do mês/ano selecionado
            try:
                base_date = datetime(year=int(selected_year_str), month=month_num, day=1)
            except ValueError as e:
                messagebox.showerror("Erro de Data", f"Combinação de Mês/Ano inválida: {e}")
                return

        self.generate_button.configure(state="disabled", text="GERANDO...")
        self._update_status("Iniciando geração...")

        try:
            generated_count = batch_generate_pdfs(
                spreadsheet_path=self.spreadsheet_path,
                document_profile=self.selected_document_profile,
                spreadsheet_profile=self.spreadsheet_profile,
                status_callback=self._update_status,
                base_date=base_date # Passa a data base para a função de geração
            )
            messagebox.showinfo("Sucesso", f"Geração concluída! {generated_count} PDFs criados.")
            
            # Notify main app to refresh PDF list
            if hasattr(self.master, 'refresh_data'):
                self.master.refresh_data()

        except Exception as e:
            messagebox.showerror("Erro de Geração", str(e))
            self._update_status(f"Erro: {e}")
        finally:
            self.generate_button.configure(state="normal", text="GERAR DOCUMENTOS EM LOTE")
            self._update_generate_button_state()
    
    def load_profiles(self):
        self._load_profiles()