# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

from dialogs.license_dialog import LicenseDialog

# Ajuste para PyInstaller --onefile
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável, o diretório base é o sys._MEIPASS
    base_path = sys._MEIPASS
else:
    # Se estiver rodando como script, o diretório base é o diretório do arquivo
    base_path = os.path.dirname(os.path.abspath(__file__))

if base_path not in sys.path:
    sys.path.insert(0, base_path)

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional
from PIL import Image

from core.data_manager import data_manager
from core.license_manager import license_manager
from frames import (
    SpreadsheetProfileFrame,
    SpreadsheetProfileListFrame,
    DocumentProfileFrame,
    DocumentProfileListFrame,
    BatchGenerationFrame,
    PdfListFrame
)
from models import SpreadsheetProfile
from dialogs import ProgressDialog
from resources.strings import strings
import threading


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Ícone ---
        assets_dir = Path(__file__).resolve().parent / "assets"
        try:
            if (ico := assets_dir / "pdf_generator.ico").exists():
                self.iconbitmap(str(ico))
            elif (png := assets_dir / "pdf_generator.png").exists():
                self._icon_image = tk.PhotoImage(file=str(png))
                self.iconphoto(True, self._icon_image)
        except Exception as e:
            print(f"Não foi possível carregar ícone: {e}")

        self.title(strings.APP_TITLE)
        self.geometry("1100x700")
        self.minsize(1100, 700)

        # --- Appearance ---
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Navigation ---
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, width=180)
        self.navigation_frame.grid(row=0, column=0, sticky="ns")
        self.navigation_frame.grid_propagate(False) # Prevent frame from resizing to fit content
        self.navigation_frame.grid_rowconfigure(8, weight=1)

        # Logo
        self.logo_container = ctk.CTkFrame(self.navigation_frame, fg_color="transparent", width=140, height=170)
        self.logo_container.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.logo_container.grid_propagate(False) # Maintain fixed size for logo area

        self.logo_button = ctk.CTkButton(
            self.logo_container,
            text=strings.LOGO_ADD,
            width=140,
            height=140,
            command=self.change_logo,
            border_spacing=0,
        )
        self.logo_button.grid(row=0, column=0, sticky="n")
        self.original_logo_fg = self.logo_button.cget("fg_color")

        self.remove_logo_button = ctk.CTkButton(
            self.logo_container,
            text=strings.LOGO_REMOVE,
            width=140,
            height=20,
            font=ctk.CTkFont(size=10),
            command=self.remove_logo,
            fg_color="transparent",
            text_color="gray"
        )

        # Labels
        self.navigation_frame_label = ctk.CTkLabel(
            self.navigation_frame,
            text=strings.APP_TITLE,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.navigation_frame_label.grid(row=1, column=0, padx=20, pady=10)

        self.company_label = ctk.CTkLabel(
            self.navigation_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold")
        )

        # Buttons
        self.spreadsheet_profile_button = ctk.CTkButton(
            self.navigation_frame, text=strings.NAV_SPREADSHEET_PROFILES,
            command=lambda: self.select_frame_by_name("spreadsheet_list")
        )
        self.spreadsheet_profile_button.grid(row=2, column=0, padx=20, pady=(10, 5))

        self.document_profile_button = ctk.CTkButton(
            self.navigation_frame, text=strings.NAV_DOCUMENT_PROFILES,
            command=lambda: self.select_frame_by_name("document_list")
        )
        self.document_profile_button.grid(row=3, column=0, padx=20, pady=5)

        self.batch_generate_button = ctk.CTkButton(
            self.navigation_frame, text=strings.NAV_BATCH_GENERATE,
            command=lambda: self.select_frame_by_name("batch")
        )
        self.batch_generate_button.grid(row=4, column=0, padx=20, pady=5)

        self.pdf_list_button = ctk.CTkButton(
            self.navigation_frame, text=strings.NAV_GENERATED_PDFS,
            command=lambda: self.select_frame_by_name("list")
        )
        self.pdf_list_button.grid(row=5, column=0, padx=20, pady=5)

        self.export_button = ctk.CTkButton(
            self.navigation_frame, text=strings.NAV_EXPORT_PROFILES,
            command=self.export_profiles,
            fg_color="gray30",
        )
        self.export_button.grid(row=6, column=0, padx=20, pady=(10, 5))

        self.import_button = ctk.CTkButton(
            self.navigation_frame, text=strings.NAV_IMPORT_PROFILES,
            command=self.import_profiles,
            fg_color="gray30"
        )
        self.import_button.grid(row=7, column=0, padx=20, pady=5)

        # --- License ---
        self.license_status_label = ctk.CTkLabel(self.navigation_frame, text="", font=ctk.CTkFont(size=14))
        self.license_status_label.grid(row=9, column=0, padx=20, pady=0, sticky="s")

        self.license_expiration = ctk.CTkLabel(self.navigation_frame, text="", font=ctk.CTkFont(size=12))
        self.license_expiration.grid(row=10, column=0, padx=20, pady=0, sticky="s")

        self.license_button = ctk.CTkButton(
            self.navigation_frame,
            text=strings.NAV_MANAGE_LICENSE,
            command=self.show_license_dialog
        )
        self.license_button.grid(row=11, column=0, padx=20, pady=20, sticky="s")

        # --- Frames ---
        self.spreadsheet_list_frame = SpreadsheetProfileListFrame(self, fg_color="transparent")
        self.spreadsheet_create_frame = SpreadsheetProfileFrame(self, fg_color="transparent")
        self.document_list_frame = DocumentProfileListFrame(self, fg_color="transparent")
        self.document_create_frame = DocumentProfileFrame(self, fg_color="transparent")
        self.batch_frame = BatchGenerationFrame(self, fg_color="transparent")
        self.list_frame = PdfListFrame(self, fg_color="transparent")

        self.load_logo()
        self.select_frame_by_name("list")
        self.update_license_status()
        
        # Start background license validation
        threading.Thread(target=self.validate_license_startup, daemon=True).start()

    # ---------- REFRESH ----------
    def refresh_data(self):
        self.list_frame.refresh_data()
        self.spreadsheet_list_frame.refresh_data()
        self.document_list_frame.refresh_data()
        self.document_create_frame._load_profiles()

    # ---------- FRAME SWITCH ----------
    def select_frame_by_name(self, name, profile_to_edit: Optional[SpreadsheetProfile] = None):
        for frame in (
            self.spreadsheet_list_frame,
            self.spreadsheet_create_frame,
            self.document_list_frame,
            self.document_create_frame,
            self.batch_frame,
            self.list_frame
        ):
            frame.grid_forget()

        if name == "spreadsheet_list":
            self.spreadsheet_list_frame.refresh_data()
            self.spreadsheet_list_frame.grid(row=0, column=1, sticky="nsew")

        elif name in ("spreadsheet_create", "spreadsheet_edit"):
            if profile_to_edit and name == "spreadsheet_edit":
                self.spreadsheet_create_frame.load_profile_for_editing(profile_to_edit)
            else:
                self.spreadsheet_create_frame.clear_form()
            self.spreadsheet_create_frame.grid(row=0, column=1, sticky="nsew")

        elif name == "document_list":
            self.document_list_frame.refresh_data()
            self.document_list_frame.grid(row=0, column=1, sticky="nsew")

        elif name in ("document_create", "document_edit"):
            if profile_to_edit and name == "document_edit":
                self.document_create_frame.load_profile_for_editing(profile_to_edit)
            else:
                self.document_create_frame.clear_form()
            self.document_create_frame.grid(row=0, column=1, sticky="nsew")

        elif name == "batch":
            self.batch_frame.load_profiles()
            self.batch_frame.grid(row=0, column=1, sticky="nsew")

        elif name == "list":
            self.list_frame.refresh_data()
            self.list_frame.grid(row=0, column=1, sticky="nsew")

    # ---------- LICENSE ----------
    def validate_license_startup(self):
        """
        Checks internet and validates license via API in the background.
        """
        if license_manager.check_internet():
            is_valid = license_manager.validate_license_online()
            
            # Update UI on main thread
            self.after(0, self.update_license_status)
            
            if not is_valid:
                # If license became invalid, redirect to list screen (only accessible screen)
                self.after(0, lambda: self.select_frame_by_name("list"))
                self.after(0, lambda: messagebox.showwarning(strings.LICENSE_INVALID_TITLE, strings.LICENSE_INVALID_MESSAGE))

    def update_license_status(self):
        licensed = license_manager.is_licensed
        self.license_status_label.configure(
            text=strings.LICENSE_ACTIVE if licensed else strings.LICENSE_INACTIVE,
            text_color="green" if licensed else "red"
        )

        state = "normal" if licensed else "disabled"
        self.document_profile_button.configure(state=state)
        self.batch_generate_button.configure(state=state)
        self.spreadsheet_profile_button.configure(state=state)
        self.export_button.configure(state=state)
        self.import_button.configure(state=state)

        if licensed:
            self.license_expiration.configure(text=strings.LICENSE_VALID_UNTIL.format(license_manager.get_expiration_date()))
            company = getattr(license_manager.license_info, "company", "")
            self.logo_button.configure(state="normal")
            self.remove_logo_button.configure(state="normal")
            if company:
                self.navigation_frame_label.grid_forget()
                self.company_label.configure(text=company)
                self.company_label.grid(row=1, column=0, padx=20, pady=10)
            else:
                self.company_label.grid_forget()
                self.navigation_frame_label.configure(text=strings.APP_TITLE)
                self.navigation_frame_label.grid(row=1, column=0, padx=20, pady=10)
        else:
            self.license_expiration.configure(text="")
            self.company_label.grid_forget()
            self.logo_button.configure(state="disabled")
            self.remove_logo_button.configure(state="disabled")

    def show_license_dialog(self):
        dialog = LicenseDialog(self)
        code = dialog.get_input()
        if code:
            # 1. Show progress dialog
            progress_dialog = ProgressDialog(
                self,
                title="Ativando Licença",
                message="Conectando ao servidor e validando licença...",
            )
            
            # 2. Run activation in a separate thread
            activation_thread = threading.Thread(
                target=self._run_activation,
                args=(code, progress_dialog)
            )
            activation_thread.start()

    def _run_activation(self, code, progress_dialog):
        try:
            result_message = license_manager.activate_license(code)
            
            # Update UI on main thread
            self.after(0, lambda: self._handle_activation_result(result_message, progress_dialog))
        except Exception as e:
            self.after(0, lambda: self._handle_activation_result(f"Erro: {str(e)}", progress_dialog))

    def _handle_activation_result(self, message, progress_dialog):
        # Close progress dialog
        if progress_dialog.winfo_exists():
            progress_dialog.destroy()
            
        # Show result
        if "sucesso" in message.lower():
            messagebox.showinfo("Sucesso", message)
        else:
            messagebox.showerror("Erro", message)
            
        # Refresh UI
        self.update_license_status()

    # ---------- LOGO ----------
    def load_logo(self):
        logo_path = data_manager.get_logo_path()
        if logo_path and Path(logo_path).exists():
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((123, 123), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(123, 123))
                self.logo_button.configure(image=logo_photo, text="", fg_color="transparent")
                self.logo_button._image = logo_photo
                self.remove_logo_button.grid(row=1, column=0, pady=(5, 0))
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
        else:
            self.logo_button.configure(image=None, text=strings.LOGO_ADD, fg_color=self.original_logo_fg)
            self.remove_logo_button.grid_forget()

    def change_logo(self):
        file_path = filedialog.askopenfilename(
            title="Selecione a Logo da Empresa",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            data_manager.save_logo(file_path)
            self.load_logo()

    def remove_logo(self):
        data_manager.delete_logo()
        self.load_logo()

    # ---------- EXPORT/IMPORT ----------
    def export_profiles(self):
        file_path = filedialog.asksaveasfilename(
            title="Salvar Perfis",
            defaultextension=".zip",
            filetypes=[(strings.FILE_FILTERS_ZIP, "*.zip")]
        )
        if file_path:
            try:
                data_manager.export_profiles_to_zip(file_path)
                messagebox.showinfo(strings.SUCCESS_TITLE, "Perfis exportados com sucesso!")
            except Exception as e:
                messagebox.showerror(strings.ERROR_TITLE, f"Erro ao exportar perfis: {e}")

    def import_profiles(self):
        file_path = filedialog.askopenfilename(
            title="Importar Perfis",
            filetypes=[(strings.FILE_FILTERS_ZIP, "*.zip")]
        )
        if file_path:
            try:
                data_manager.import_profiles_from_zip(file_path)
                messagebox.showinfo(strings.SUCCESS_TITLE, "Perfis importados com sucesso!")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror(strings.ERROR_TITLE, f"Erro ao importar perfis: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
