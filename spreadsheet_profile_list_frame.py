import customtkinter as ctk
from tkinter import messagebox
from typing import List, Optional

from models import SpreadsheetProfile
from data_manager import data_manager

class SpreadsheetProfileListFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.profiles: List[SpreadsheetProfile] = []

        ctk.CTkLabel(self, text="Perfis de Planilha Cadastrados", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Scrollable frame for the list
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Perfis")
        self.add_button = ctk.CTkButton(self, text="Adicionar Novo Perfil de Planilha", command=self._add_profile)
        self.add_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.refresh_data()

    def _add_profile(self):
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("spreadsheet_create")

    def refresh_data(self):
        # Clear existing widgets
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.profiles = data_manager.load_profiles(SpreadsheetProfile)

        if not self.profiles:
            ctk.CTkLabel(self.list_frame, text="Nenhum perfil de planilha cadastrado.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Header Row
        ctk.CTkLabel(self.list_frame, text="Nome do Perfil", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.list_frame, text="Colunas Mapeadas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.list_frame, text="Ações", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Data Rows
        for i, profile in enumerate(self.profiles):
            row = i + 1
            
            ctk.CTkLabel(self.list_frame, text=profile.name).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.list_frame, text=f"{len(profile.columns)}").grid(row=row, column=1, padx=10, pady=5, sticky="w")

            # Action Buttons Frame
            action_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            action_frame.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            edit_button = ctk.CTkButton(action_frame, text="Editar", width=80, command=lambda p=profile: self._edit_profile(p))
            edit_button.grid(row=0, column=0, padx=(0, 5))
            
            delete_button = ctk.CTkButton(action_frame, text="Excluir", width=80, fg_color="red", hover_color="darkred", command=lambda p=profile: self._delete_profile(p))
            delete_button.grid(row=0, column=1)

    def _edit_profile(self, profile: SpreadsheetProfile):
        # Navigate to the SpreadsheetProfileFrame and load the profile for editing
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("spreadsheet_edit", profile)
        else:
            messagebox.showerror("Erro", "Funcionalidade de edição não disponível.")

    def _delete_profile(self, profile: SpreadsheetProfile):
        # Check if spreadsheet profile is linked to any document profile
        from models import DocumentProfile
        doc_profiles = data_manager.load_profiles(DocumentProfile)
        linked_docs = [dp.name for dp in doc_profiles if dp.spreadsheet_profile_name == profile.name]
        
        if linked_docs:
            messagebox.showerror("Erro de Exclusão", 
                                 f"Não é possível excluir o perfil '{profile.name}' porque ele está vinculado aos seguintes perfis de documento:\n\n" + 
                                 "\n".join(f"- {name}" for name in linked_docs) + 
                                 "\n\nRemova o vínculo ou exclua os perfis de documento primeiro.")
            return

        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o perfil '{profile.name}'?"):
            try:
                data_manager.delete_profile(profile)
                messagebox.showinfo("Sucesso", f"Perfil '{profile.name}' excluído com sucesso.")
                self.refresh_data()
                # Notify main app to refresh other lists
                if hasattr(self.master, 'refresh_data'):
                    self.master.refresh_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir perfil: {e}")
