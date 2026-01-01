import customtkinter as ctk
from resources.strings import strings

class LicenseDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.title(strings.LICENSE_DIALOG_TITLE)
        self.geometry("350x150")
        self.resizable(False, False)
        
        # Faz a janela ser modal (bloqueia a janela principal)
        self.transient(master)
        self.grab_set()
        
        self.result = None

        # Centralização
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 100
        self.geometry(f"350x150+{x}+{y}")

        # Widgets
        self.label = ctk.CTkLabel(self, text=strings.LICENSE_DIALOG_ENTER_CODE, wraplength=350)
        self.label.pack(pady=(10,0), padx=20)

        self.entry = ctk.CTkEntry(self, placeholder_text=strings.LICENSE_DIALOG_CODE_PLACEHOLDER, width=300)
        self.entry.pack(pady=10, padx=20)
        self.entry.focus_set()
        # Centralizar o texto
        self.entry.configure(justify="center")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill="x")

        self.ok_button = ctk.CTkButton(self.button_frame, text=strings.LICENSE_DIALOG_CONFIRM, width=0, command=self._on_ok)
        self.ok_button.pack(side="right", padx=(10,5), expand=True, fill="x")

        self.cancel_button = ctk.CTkButton(self.button_frame, text=strings.LICENSE_DIALOG_CANCEL, text_color=("black", "white"), fg_color="transparent", border_width=2, width=0, command=self._on_cancel)
        self.cancel_button.pack(side="left", padx=(5,10), expand=True, fill="x")

        # Bind da tecla Enter
        self.bind("<Return>", lambda e: self._on_ok())

        # Espera a janela ser fechada
        self.master.wait_window(self)

    def _on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def get_input(self):
        return self.result
