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
import threading


class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Processando...", message="Por favor, aguarde..."):
        super().__init__(master)
        self.title(title)
        self.geometry("400x100")
        self.transient(master)  # Make it modal
        self.grab_set()         # Modal behavior
        self.resizable(False, False)
        
        # Center the dialog
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        
        x = master_x + (master_width // 2) - 150
        y = master_y + (master_height // 2) - 50
        self.geometry(f"+{x}+{y}")

        self.label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14))
        self.label.pack(pady=10, padx=20)

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate")
        self.progressbar.pack(pady=10, padx=20, fill="x")
        self.progressbar.start()

        self.protocol("WM_DELETE_WINDOW", self.disable_close) # Prevent closing with X button

    def disable_close(self):
        pass # Do nothing to prevent closing

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

        self.title("PDF Generator")
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
            text="Adicionar Logo",
            width=140,
            height=140,
            command=self.change_logo,
            border_spacing=0,
        )
        self.logo_button.grid(row=0, column=0, sticky="n")
        self.original_logo_fg = self.logo_button.cget("fg_color")

        self.remove_logo_button = ctk.CTkButton(
            self.logo_container,
            text="Remover Logo",
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
            text="PDF Generator",
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
            self.navigation_frame, text="Perfis de Planilha",
            command=lambda: self.select_frame_by_name("spreadsheet_list")
        )
        self.spreadsheet_profile_button.grid(row=2, column=0, padx=20, pady=(10, 5))

        self.document_profile_button = ctk.CTkButton(
            self.navigation_frame, text="Perfis de Documento",
            command=lambda: self.select_frame_by_name("document_list")
        )
        self.document_profile_button.grid(row=3, column=0, padx=20, pady=5)

        self.batch_generate_button = ctk.CTkButton(
            self.navigation_frame, text="Gerar em Lote",
            command=lambda: self.select_frame_by_name("batch")
        )
        self.batch_generate_button.grid(row=4, column=0, padx=20, pady=5)

        self.pdf_list_button = ctk.CTkButton(
            self.navigation_frame, text="PDFs Gerados",
            command=lambda: self.select_frame_by_name("list")
        )
        self.pdf_list_button.grid(row=5, column=0, padx=20, pady=5)

        self.export_button = ctk.CTkButton(
            self.navigation_frame, text="Exportar Perfis (ZIP)",
            command=self.export_profiles,
            fg_color="gray30",
        )
        self.export_button.grid(row=6, column=0, padx=20, pady=(10, 5))

        self.import_button = ctk.CTkButton(
            self.navigation_frame, text="Importar Perfis (ZIP)",
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
            text="Gerenciar Licença",
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
                self.after(0, lambda: messagebox.showwarning("Licença Inválida", "Sua licença foi invalidada ou expirou. Por favor, verifique sua assinatura."))

    def update_license_status(self):
        licensed = license_manager.is_licensed
        self.license_status_label.configure(
            text="Licença: Ativa" if licensed else "Licença: Inativa",
            text_color="green" if licensed else "red"
        )

        state = "normal" if licensed else "disabled"
        self.document_profile_button.configure(state=state)
        self.batch_generate_button.configure(state=state)
        self.spreadsheet_profile_button.configure(state=state)
        self.export_button.configure(state=state)
        self.import_button.configure(state=state)

        if licensed:
            self.license_expiration.configure(text=f"Válido até {license_manager.get_expiration_date()}")
            company = getattr(license_manager.license_info, "company", "")
            self.logo_button.configure(state="normal")
            self.remove_logo_button.configure(state="normal")
            if company:
                self.navigation_frame_label.grid_forget()
                self.company_label.configure(text=company)
                self.company_label.grid(row=1, column=0, padx=20, pady=(5, 10))
        else:
            self.company_label.grid_forget()
            self.navigation_frame_label.grid(row=1, column=0, padx=20, pady=10)
            self.license_expiration.configure(text="--/--/--")
            self.logo_button.configure(state="disabled")
            self.remove_logo_button.configure(state="disabled")

    # ---------- LOGO ----------
    def change_logo(self):
        if path := filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]):
            data_manager.save_logo(path)
            self.load_logo()

    def remove_logo(self):
        data_manager.delete_logo()
        self.load_logo()

    def export_profiles(self):
        path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if path:
            try:
                data_manager.export_profiles_to_zip(path)
                messagebox.showinfo("Sucesso", "Perfis exportados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar perfis: {e}")

    def import_profiles(self):
        path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if path:
            try:
                data_manager.import_profiles_from_zip(path)
                messagebox.showinfo("Sucesso", "Perfis importados com sucesso! (Perfis existentes foram ignorados)")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar perfis: {e}")

    def load_logo(self):
        logo_path = data_manager.get_logo_path()
        if not logo_path:
            self.logo_button.configure(image=None, text="Adicionar Logo", fg_color=self.original_logo_fg, width=140, height=140)
            self.remove_logo_button.grid_forget()
            return

        try:
            img = Image.open(logo_path)
            # Get original dimensions
            width, height = img.size
            # Calculate new dimensions maintaining aspect ratio within 140x140
            ratio = min(120 / width, 120 / height)
            new_size = (int(width * ratio), int(height * ratio))
            
            self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=new_size)
            self.logo_button.configure(image=self.logo_img, text="", fg_color="transparent", width=140, height=140)
            
            self.remove_logo_button.grid(row=1, column=0, pady=(0, 5), sticky="n")
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            self.logo_button.configure(image=None, text="Adicionar Logo", fg_color=self.original_logo_fg, width=140, height=140)
            self.remove_logo_button.grid_forget()

    # ---------- LICENSE DIALOG ----------
    def show_license_dialog(self):
        dialog = ctk.CTkInputDialog(
            text="Insira seu código de licença de 25 dígitos:",
            title="Ativação de Licença",
        )
        if (code := dialog.get_input()):
            # 1. Show progress dialog
            progress_dialog = ProgressDialog(
                self,
                title="Ativando Licença",
                message="Conectando ao servidor e validando licença..."
            )
            
            # 2. Run activation in a separate thread
            activation_thread = threading.Thread(
                target=self._run_activation,
                args=(code, progress_dialog)
            )
            activation_thread.start()

    def _run_activation(self, code, progress_dialog):
        # This runs in a separate thread
        result_message = license_manager.activate_license(code)
        
        # 3. Use after() to safely update the GUI from the main thread
        self.after(0, lambda: self._handle_activation_result(result_message, progress_dialog))

    def _handle_activation_result(self, result_message, progress_dialog):
        # This runs in the main thread
        progress_dialog.destroy()
        messagebox.showinfo("Ativação de Licença", result_message)
        self.update_license_status()


if __name__ == "__main__":
    app = App()
    app.mainloop()
