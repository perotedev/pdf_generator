# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import os
from typing import List, Optional

from models import SpreadsheetProfile, ColumnMapping, ColumnType
from core.data_manager import data_manager
from utils import select_file, read_spreadsheet_headers
from utils.scroll_helper import bind_mousewheel_to_scrollable_frame
from resources.strings import strings

class SpreadsheetProfileFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.file_path: Optional[str] = None
        self.column_mappings: List[ColumnMapping] = []
        self.profile_name_var = ctk.StringVar()
        self.header_row_var = ctk.StringVar(value="1")

        # --- Widgets ---
        ctk.CTkLabel(self, text=strings.SHEET_PROFILE_TITLE, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # File Selection and Profile Name
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.select_file_button = ctk.CTkButton(self.top_frame, text=strings.SHEET_SELECT_FILE, command=self._select_file)
        self.select_file_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.profile_name_entry = ctk.CTkEntry(self.top_frame, placeholder_text=strings.SHEET_PROFILE_NAME_PLACEHOLDER, textvariable=self.profile_name_var)
        self.profile_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Header Row Selection
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkLabel(self.header_frame, text=strings.SHEET_HEADER_ROW).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.header_row_menu = ctk.CTkOptionMenu(self.header_frame, values=[str(i) for i in range(1, 11)], variable=self.header_row_var, command=self._on_header_row_change)
        self.header_row_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Mapping Display Area
        self.mapping_frame = ctk.CTkScrollableFrame(self, label_text="Mapeamento de Colunas")
        self.mapping_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.mapping_frame.grid_columnconfigure(0, weight=1)
        self.mapping_frame.grid_columnconfigure(1, weight=1)
        self.mapping_frame.grid_columnconfigure(2, weight=1)
        
        # Adiciona suporte a scroll com mouse
        bind_mousewheel_to_scrollable_frame(self.mapping_frame)

        # Save Button
        self.save_button = ctk.CTkButton(self, text=strings.SHEET_SAVE_PROFILE, command=self._save_profile)
        self.save_button.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="e")

        self._update_mapping_display()

    def load_profile_for_editing(self, profile: SpreadsheetProfile):
        self.profile_name_var.set(profile.name)
        self.header_row_var.set(str(profile.header_row))
        self.column_mappings = profile.columns
        self.file_path = None # Editing doesn't require a file selection
        self.profile_name_entry.configure(state="disabled") # Prevent name change during edit
        self.select_file_button.configure(state="disabled") # Prevent file change during edit
        self.header_row_menu.configure(state="disabled")
        self.save_button.configure(text=strings.SHEET_SAVE_CHANGES, command=lambda: self._save_profile(is_editing=True))
        self._update_mapping_display()

    def clear_form(self):
        self.file_path = None
        self.column_mappings = []
        self.profile_name_var.set("")
        self.header_row_var.set("1")
        self.profile_name_entry.configure(state="normal")
        self.select_file_button.configure(state="normal")
        self.header_row_menu.configure(state="normal")
        self.save_button.configure(text=strings.SHEET_SAVE_PROFILE, command=self._save_profile)
        self._update_mapping_display()

    def _select_file(self):
        file_path = select_file([(strings.FILE_FILTERS_EXCEL, "*.xlsx *.xls")])
        if file_path:
            self.file_path = file_path
            self._load_columns_from_file()

    def _on_header_row_change(self, _):
        if self.file_path:
            self._load_columns_from_file()

    def _load_columns_from_file(self):
        if not self.file_path:
            return
        try:
            header_row_idx = int(self.header_row_var.get()) - 1
            headers = read_spreadsheet_headers(self.file_path, header_row_idx)
            self.column_mappings = [
                ColumnMapping(
                    original_header=h,
                    custom_name=h,
                    column_type="texto",
                    index=i
                ) for i, h in enumerate(headers)
            ]
            if not self.profile_name_var.get():
                self.profile_name_var.set(os.path.basename(self.file_path).split('.')[0])
            self._update_mapping_display()
        except Exception as e:
            messagebox.showerror(strings.ERROR_TITLE, str(e))
            self.column_mappings = []
            self._update_mapping_display()

    def _update_mapping_display(self):
        # Clear existing widgets
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()

        if not self.column_mappings:
            ctk.CTkLabel(self.mapping_frame, text="Selecione um arquivo para ver as colunas.").grid(row=0, column=0, columnspan=3, padx=20, pady=20)
            return

        # Header Row
        ctk.CTkLabel(self.mapping_frame, text="Header Original", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_frame, text="Nome Personalizado", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_frame, text="Tipo de Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Data Rows
        for i, mapping in enumerate(self.column_mappings):
            row = i + 1
            
            # Original Header
            ctk.CTkLabel(self.mapping_frame, text=mapping.original_header).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Custom Name Entry
            name_var = ctk.StringVar(value=mapping.custom_name)
            def update_name(var, mapping_obj):
                mapping_obj.custom_name = var.get()
            name_var.trace_add("write", lambda name, index, mode, var=name_var, mapping_obj=mapping: update_name(var, mapping_obj))
            ctk.CTkEntry(self.mapping_frame, textvariable=name_var).grid(row=row, column=1, padx=10, pady=5, sticky="ew")

            # Column Type Dropdown
            type_var = ctk.StringVar(value=mapping.column_type)
            def update_type(var, mapping_obj):
                mapping_obj.column_type = var.get()
            type_var.trace_add("write", lambda name, index, mode, var=type_var, mapping_obj=mapping: update_type(var, mapping_obj))
            ctk.CTkOptionMenu(self.mapping_frame, variable=type_var, values=list(ColumnType.__args__)).grid(row=row, column=2, padx=10, pady=5, sticky="ew")
        
        # Re-bind scroll após adicionar novos widgets
        bind_mousewheel_to_scrollable_frame(self.mapping_frame)

    def _save_profile(self, is_editing=False):
        profile_name = self.profile_name_var.get().strip()
        if not profile_name:
            messagebox.showerror(strings.ERROR_TITLE, "O nome do perfil não pode estar vazio.")
            return
        if not self.column_mappings:
            messagebox.showerror(strings.ERROR_TITLE, "Nenhuma coluna mapeada para salvar.")
            return

        # Check for duplicate name only if not editing
        if not is_editing:
            existing_profiles = data_manager.load_profiles(SpreadsheetProfile)
            if any(p.name == profile_name for p in existing_profiles):
                messagebox.showerror(strings.ERROR_TITLE, f"Já existe um perfil de planilha com o nome '{profile_name}'.")
                return

        profile = SpreadsheetProfile(
            name=profile_name,
            header_row=int(self.header_row_var.get()),
            columns=self.column_mappings
        )
        data_manager.save_profile(profile)
        messagebox.showinfo(strings.SUCCESS_TITLE, f"Perfil de planilha '{profile_name}' salvo com sucesso!")
        
        # Clear the form and return to the list view
        self.clear_form()
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("spreadsheet_list")
        
        # Notify main app to refresh lists if necessary
        if hasattr(self.master, 'refresh_data'):
            self.master.refresh_data()
