from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional
from PIL import Image

from data_manager import data_manager
from license_manager import license_manager
from spreadsheet_profile_frame import SpreadsheetProfileFrame
from spreadsheet_profile_list_frame import SpreadsheetProfileListFrame
from models import SpreadsheetProfile
from document_profile_frame import DocumentProfileFrame
from document_profile_list_frame import DocumentProfileListFrame
from batch_generation_frame import BatchGenerationFrame
from pdf_list_frame import PdfListFrame


# --- Main Application Window ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Ícone da aplicação (janela + barra de tarefas) ---
        assets_dir = Path(__file__).resolve().parent / "assets"
        ico_path = assets_dir / "pdf_generator.ico"
        png_path = assets_dir / "pdf_generator.png"
        try:
            if ico_path.exists():
                # ícone .ico funciona bem no Windows (barra de tarefas)
                self.iconbitmap(str(ico_path))
            elif png_path.exists():
                # fallback usando PhotoImage (útil em outros SOs)
                self._icon_image = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._icon_image)
        except Exception as e:
            print(f"Não foi possível carregar ícone: {e}")

        self.title("PDF Generator")
        self.geometry("1100x700")

        # --- Appearance ---
        ctk.set_appearance_mode("System")  # or "Dark", "Light"
        ctk.set_default_color_theme("blue")

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Navigation Frame ---
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")
        self.navigation_frame.grid_rowconfigure(6, weight=1)

        # --- Logo / Avatar ---
        self.logo_container = ctk.CTkFrame(self.navigation_frame, fg_color="transparent")
        self.logo_container.grid(row=0, column=0, padx=20, pady=(20, 0))
        
        self.logo_button = ctk.CTkButton(self.logo_container, text="Adicionar Logo", 
                                        width=140, height=140, 
                                        command=self.change_logo,
                                        fg_color="gray70" if ctk.get_appearance_mode() == "Light" else "gray30")
        self.logo_button.grid(row=0, column=0)
        
        self.remove_logo_button = ctk.CTkButton(self.logo_container, text="Remover Logo", 
                                               width=100, height=20, font=ctk.CTkFont(size=10),
                                               command=self.remove_logo, fg_color="transparent", text_color="gray")
        
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="PDF Generator",
                                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.navigation_frame_label.grid(row=1, column=0, padx=20, pady=10)

        self.company_label = ctk.CTkLabel(self.navigation_frame, text="",
                                            font=ctk.CTkFont(size=16, weight="bold"))
        # company_label will be gridded in update_license_status if needed

        self.spreadsheet_profile_button = ctk.CTkButton(self.navigation_frame, text="Perfis de Planilha",
                                                                command=lambda: self.select_frame_by_name("spreadsheet_list"))
        self.spreadsheet_profile_button.grid(row=2, column=0, padx=20, pady=10)

        self.document_profile_button = ctk.CTkButton(self.navigation_frame, text="Perfis de Documento",
                                                       command=lambda: self.select_frame_by_name("document_list"))
        self.document_profile_button.grid(row=3, column=0, padx=20, pady=10)

        self.batch_generate_button = ctk.CTkButton(self.navigation_frame, text="Gerar em Lote",
                                                     command=lambda: self.select_frame_by_name("batch"))
        self.batch_generate_button.grid(row=4, column=0, padx=20, pady=10)

        self.pdf_list_button = ctk.CTkButton(self.navigation_frame, text="PDFs Gerados",
                                               command=lambda: self.select_frame_by_name("list"))
        self.pdf_list_button.grid(row=5, column=0, padx=20, pady=10)

        # --- License Status ---
        self.license_status_label = ctk.CTkLabel(self.navigation_frame, text="", font=ctk.CTkFont(size=14))
        self.license_status_label.grid(row=7, column=0, padx=20, pady=0, sticky="s")
        self.license_expiration = ctk.CTkLabel(self.navigation_frame, text="", font=ctk.CTkFont(size=12))
        self.license_expiration.grid(row=8, column=0, padx=20, pady=0, sticky="s")
        self.license_button = ctk.CTkButton(self.navigation_frame, text="Gerenciar Licença", command=self.show_license_dialog)
        self.license_button.grid(row=9, column=0, padx=20, pady=20, sticky="s")

        # --- Initial Load ---
        self.load_logo()

        # --- Main Frames ---
        self.spreadsheet_list_frame = SpreadsheetProfileListFrame(self, corner_radius=0, fg_color="transparent")
        self.spreadsheet_create_frame = SpreadsheetProfileFrame(self, corner_radius=0, fg_color="transparent")
        self.document_list_frame = DocumentProfileListFrame(self, corner_radius=0, fg_color="transparent") # New list frame
        self.document_create_frame = DocumentProfileFrame(self, corner_radius=0, fg_color="transparent") # Renamed
        self.batch_frame = BatchGenerationFrame(self, corner_radius=0, fg_color="transparent")
        self.list_frame = PdfListFrame(self, corner_radius=0, fg_color="transparent")

        # --- Initial State ---
        if license_manager.is_licensed:
            self.select_frame_by_name("spreadsheet_list")
        else:
            self.select_frame_by_name("list")
        self.update_license_status()

    def refresh_data(self):
        """Called by sub-frames to notify the main app to refresh data."""
        self.list_frame.refresh_data()
        self.spreadsheet_list_frame.refresh_data()
        self.document_list_frame.refresh_data() # Refresh document list
        self.document_create_frame._load_profiles() # Refresh profiles for document frame
        # Other refresh logic can go here


    def select_frame_by_name(self, name, profile_to_edit: Optional[SpreadsheetProfile] = None):
        # Hide all frames
        self.spreadsheet_list_frame.grid_forget()
        self.spreadsheet_create_frame.grid_forget()
        self.document_list_frame.grid_forget() # New list frame
        self.document_create_frame.grid_forget() # Rename document_frame to document_create_frame
        self.batch_frame.grid_forget()
        self.batch_frame.grid_forget()
        self.list_frame.grid_forget()

        # Show the selected frame
        if name == "spreadsheet_list":
            self.spreadsheet_list_frame.refresh_data()
            self.spreadsheet_list_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "spreadsheet_create" or name == "spreadsheet_edit":
            if name == "spreadsheet_edit" and profile_to_edit:
                self.spreadsheet_create_frame.load_profile_for_editing(profile_to_edit)
            elif name == "spreadsheet_create":
                self.spreadsheet_create_frame.clear_form()
            self.spreadsheet_create_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "document_list":
            self.document_list_frame.refresh_data()
            self.document_list_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "document_create" or name == "document_edit":
            if name == "document_edit" and profile_to_edit:
                self.document_create_frame.load_profile_for_editing(profile_to_edit)
            elif name == "document_create":
                self.document_create_frame.clear_form()
            self.document_create_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "batch":
            self.batch_frame.load_profiles()
            self.batch_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "list":
            self.list_frame.refresh_data() # Refresh data when navigating to the list
            self.list_frame.grid(row=0, column=1, sticky="nsew")

    def update_license_status(self):
        if license_manager.is_licensed:
            self.license_status_label.configure(text="Licença: Ativa", text_color="green")
            self.document_profile_button.configure(state="normal")
            self.batch_generate_button.configure(state="normal")
            self.spreadsheet_profile_button.configure(state="normal")
            self.license_expiration.configure(text=f"Válido até {license_manager.get_expiration_date()}")
            self.logo_container = ctk.CTkFrame(self.navigation_frame, fg_color="transparent")
            self.logo_container.grid(row=0, column=0, padx=20, pady=(20, 0))
            
            self.logo_button = ctk.CTkButton(self.logo_container, text="Adicionar Logo", 
                                            width=140, height=140, 
                                            command=self.change_logo,
                                            fg_color="gray70" if ctk.get_appearance_mode() == "Light" else "gray30")
            self.logo_button.grid(row=0, column=0)
            
            self.remove_logo_button = ctk.CTkButton(self.logo_container, text="Remover Logo", 
                                                width=100, height=20, font=ctk.CTkFont(size=10),
                                                command=self.remove_logo, fg_color="transparent", text_color="gray")
            self.load_logo()
            
            # Show company name if available
            company_name = license_manager.license_info.company if license_manager.license_info else ""
            if company_name:
                self.navigation_frame_label.grid_forget()
                self.company_label.configure(text=company_name)
                self.company_label.grid(row=1, column=0, padx=20, pady=(0, 10))
            else:
                self.company_label.grid_forget()
                self.navigation_frame_label.grid(row=1, column=0, padx=20, pady=10)
        else:
            self.license_status_label.configure(text="Licença: Inativa", text_color="red")
            self.document_profile_button.configure(state="disabled")
            self.batch_generate_button.configure(state="disabled")
            self.spreadsheet_profile_button.configure(state="disabled")
            self.license_expiration.configure(text=f"--/--/--")
            self.company_label.grid_forget()
            self.navigation_frame_label.grid(row=1, column=0, padx=20, pady=10)
            self.logo_container.destroy()
            self.logo_button.destroy()
            self.remove_logo_button.destroy()

    def change_logo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            data_manager.save_logo(file_path)
            self.load_logo()

    def remove_logo(self):
        data_manager.delete_logo()
        self.load_logo()

    def load_logo(self):
        logo_path = data_manager.get_logo_path()
        if logo_path:
            try:
                img = Image.open(logo_path)
                # Resize maintaining aspect ratio, max 140x140
                img.thumbnail((140, 140))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self.logo_button.configure(image=ctk_img, text="")
                self.remove_logo_button.grid(row=1, column=0, pady=(0, 5))
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
                self.logo_button.configure(image=None, text="Adicionar Logo")
                self.remove_logo_button.grid_forget()
        else:
            self.logo_button.configure(image=None, text="Adicionar Logo")
            self.remove_logo_button.grid_forget()

    def show_license_dialog(self):
        dialog = ctk.CTkInputDialog(text="Insira seu código de licença de 25 dígitos:", title="Ativação de Licença")
        code = dialog.get_input()
        if code:
            status_message = license_manager.activate_license(code)
            messagebox.showinfo("Ativação de Licença", status_message)
            self.update_license_status()

if __name__ == "__main__":
    app = App()
    app.mainloop()
