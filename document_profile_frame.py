import customtkinter as ctk
from tkinter import messagebox
from typing import List, Optional

from models import DocumentProfile, SpreadsheetProfile, PdfFieldMapping
from data_manager import data_manager
from utils import select_file

class DocumentProfileFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.pdf_path: Optional[str] = None
        self.document_profile_name_var = ctk.StringVar()
        self.spreadsheet_profile_name_var = ctk.StringVar()
        self.available_spreadsheet_profiles: List[SpreadsheetProfile] = []
        self.field_mappings: List[PdfFieldMapping] = []
        
        self.selected_column_to_map_var = ctk.StringVar()
        self.x_coord_var = ctk.StringVar(value="0.0")
        self.y_coord_var = ctk.StringVar(value="0.0")

        # --- Widgets ---
        ctk.CTkLabel(self, text="Gerenciamento de Perfis de Documento", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Top Frame for selection and name
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.select_pdf_button = ctk.CTkButton(self.top_frame, text="Selecionar Template PDF", command=self._select_pdf)
        self.select_pdf_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.profile_name_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Nome do Perfil de Documento", textvariable=self.document_profile_name_var)
        self.profile_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Spreadsheet Profile Selection
        self.profile_select_frame = ctk.CTkFrame(self)
        self.profile_select_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.profile_select_frame.grid_columnconfigure(0, weight=1)
        
        self.spreadsheet_profile_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                         variable=self.spreadsheet_profile_name_var,
                                                         values=["Selecione um Perfil de Planilha"],
                                                         command=self._on_profile_select)
        self.spreadsheet_profile_menu.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Mapping Input
        self.mapping_input_frame = ctk.CTkFrame(self)
        self.mapping_input_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.mapping_input_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.mapping_input_frame, text="Mapeamento de Campos (Coordenadas em mm):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=5, padx=10, pady=(10, 5), sticky="w")
        
        self.column_menu = ctk.CTkOptionMenu(self.mapping_input_frame, 
                                             variable=self.selected_column_to_map_var,
                                             values=["Selecione a Coluna"],
                                             width=200)
        self.column_menu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.mapping_input_frame, text="X:").grid(row=1, column=1, padx=(10, 0), pady=10)
        ctk.CTkEntry(self.mapping_input_frame, textvariable=self.x_coord_var, width=80).grid(row=1, column=2, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(self.mapping_input_frame, text="Y:").grid(row=1, column=3, padx=(10, 0), pady=10)
        ctk.CTkEntry(self.mapping_input_frame, textvariable=self.y_coord_var, width=80).grid(row=1, column=4, padx=(0, 10), pady=10)
        
        ctk.CTkButton(self.mapping_input_frame, text="Adicionar Mapeamento", command=self._add_mapping).grid(row=1, column=5, padx=10, pady=10)

        # Mapping Display Area
        self.mapping_display_frame = ctk.CTkScrollableFrame(self, label_text="Mapeamentos Atuais")
        self.mapping_display_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.mapping_display_frame.grid_columnconfigure(0, weight=1)

        # Save Button
        self.save_button = ctk.CTkButton(self, text="Salvar Perfil de Documento", command=self._save_profile)
        self.save_button.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="e")

        self._load_profiles()
        self._update_mapping_display()

    def load_profile_for_editing(self, profile: DocumentProfile):
        self.document_profile_name_var.set(profile.name)
        self.pdf_path = profile.pdf_path
        self.field_mappings = profile.field_mappings
        self.spreadsheet_profile_name_var.set(profile.spreadsheet_profile_name)
        
        self.profile_name_entry.configure(state="disabled") # Prevent name change during edit
        self.select_pdf_button.configure(state="disabled", text=f"PDF Selecionado: {os.path.basename(self.pdf_path)}") # Prevent PDF change during edit
        self.save_button.configure(text="Salvar Alterações", command=lambda: self._save_profile(is_editing=True))
        self._update_mapping_display()

    def clear_form(self):
        self.pdf_path = None
        self.document_profile_name_var.set("")
        self.field_mappings = []
        self.profile_name_entry.configure(state="normal")
        self.select_pdf_button.configure(state="normal", text="Selecionar Template PDF")
        self.save_button.configure(text="Salvar Perfil de Documento", command=self._save_profile)
        self._load_profiles() # Reload profiles to ensure the dropdown is up-to-date
        self._update_mapping_display()

    def _load_profiles(self):
        self.available_spreadsheet_profiles = data_manager.load_profiles(SpreadsheetProfile)
        profile_names = [p.name for p in self.available_spreadsheet_profiles]
        if not profile_names:
            profile_names = ["Nenhum Perfil de Planilha Encontrado"]
            self.spreadsheet_profile_name_var.set(profile_names[0])
            self.spreadsheet_profile_menu.configure(state="disabled")
        else:
            self.spreadsheet_profile_menu.configure(values=profile_names, state="normal")
            self.spreadsheet_profile_name_var.set(profile_names[0])
            self._on_profile_select(profile_names[0])

    def _on_profile_select(self, profile_name: str):
        selected_profile = next((p for p in self.available_spreadsheet_profiles if p.name == profile_name), None)
        if selected_profile:
            column_names = [c.custom_name for c in selected_profile.columns]
            self.column_menu.configure(values=column_names)
            self.selected_column_to_map_var.set(column_names[0] if column_names else "Selecione a Coluna")
        else:
            self.column_menu.configure(values=["Selecione a Coluna"])
            self.selected_column_to_map_var.set("Selecione a Coluna")
        
        # Do NOT clear existing mappings here, as it might be an edit operation.
        # The clear is handled by clear_form or load_profile_for_editing.
        # self.field_mappings = []
        self._update_mapping_display()

    def _select_pdf(self):
        pdf_path = select_file([("Arquivos PDF", "*.pdf")])
        if pdf_path:
            self.pdf_path = pdf_path
            self.document_profile_name_var.set(os.path.basename(pdf_path).split('.')[0] + "_DocProfile")
            self.select_pdf_button.configure(text=f"PDF Selecionado: {os.path.basename(pdf_path)}")

    def _add_mapping(self):
        column_name = self.selected_column_to_map_var.get()
        try:
            x = float(self.x_coord_var.get())
            y = float(self.y_coord_var.get())
        except ValueError:
            messagebox.showerror("Erro", "As coordenadas X e Y devem ser números.")
            return

        if column_name == "Selecione a Coluna":
            messagebox.showerror("Erro", "Selecione uma coluna para mapear.")
            return

        if any(m.column_name == column_name for m in self.field_mappings):
            messagebox.showerror("Erro", f"A coluna '{column_name}' já foi mapeada.")
            return

        self.field_mappings.append(PdfFieldMapping(column_name=column_name, x=x, y=y))
        self._update_mapping_display()

    def _update_mapping_display(self):
        # Clear existing widgets
        for widget in self.mapping_display_frame.winfo_children():
            widget.destroy()

        if not self.field_mappings:
            ctk.CTkLabel(self.mapping_display_frame, text="Nenhum mapeamento adicionado.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Header Row
        ctk.CTkLabel(self.mapping_display_frame, text="Coluna", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="X (mm)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="Y (mm)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="Ação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Data Rows
        for i, mapping in enumerate(self.field_mappings):
            row = i + 1
            
            ctk.CTkLabel(self.mapping_display_frame, text=mapping.column_name).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.mapping_display_frame, text=f"{mapping.x:.1f}").grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.mapping_display_frame, text=f"{mapping.y:.1f}").grid(row=row, column=2, padx=10, pady=5, sticky="w")

            delete_button = ctk.CTkButton(self.mapping_display_frame, text="Remover", width=80, command=lambda m=mapping: self._remove_mapping(m))
            delete_button.grid(row=row, column=3, padx=10, pady=5, sticky="w")

    def _remove_mapping(self, mapping: PdfFieldMapping):
        self.field_mappings.remove(mapping)
        self._update_mapping_display()

    def _save_profile(self, is_editing=False):
        profile_name = self.document_profile_name_var.get().replace(" ", "_")
        spreadsheet_profile_name = self.spreadsheet_profile_name_var.get()

        if not profile_name or not self.pdf_path or spreadsheet_profile_name == "Nenhum Perfil de Planilha Encontrado" or not self.field_mappings:
            messagebox.showerror("Erro", "Preencha todos os campos e adicione pelo menos um mapeamento.")
            return

        # Check for duplicate name only if not editing
        if not is_editing:
            existing_profiles = data_manager.load_profiles(DocumentProfile)
            if any(p.name == profile_name for p in existing_profiles):
                messagebox.showerror("Erro", f"Já existe um perfil de documento com o nome '{profile_name}'.")
                return

        profile = DocumentProfile(
            name=profile_name,
            pdf_path=self.pdf_path,
            spreadsheet_profile_name=spreadsheet_profile_name,
            field_mappings=self.field_mappings
        )
        data_manager.save_profile(profile)
        messagebox.showinfo("Sucesso", f"Perfil de documento '{profile_name}' salvo com sucesso!")
        
        # Clear the form and return to the list view
        self.clear_form()
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("document_list")
        
        # Notify main app to refresh lists if necessary
        if hasattr(self.master, 'refresh_data'):
            self.master.refresh_data()

# Import os for basename
import os
