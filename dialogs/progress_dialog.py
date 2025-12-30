# -*- coding: utf-8 -*-
import customtkinter as ctk
from resources.strings import strings

class ProgressDialog(ctk.CTkToplevel):
    """Diálogo de progresso reutilizável"""
    
    def __init__(self, master, title=None, message=None):
        super().__init__(master)
        
        if title is None:
            title = strings.PROGRESS_PROCESSING
        if message is None:
            message = strings.PROGRESS_WAIT
            
        self.title(title)
        self.resizable(False, False)

        dialog_width = 400
        dialog_height = 100
        self.geometry(f"{dialog_width}x{dialog_height}")

        # Centraliza na tela do computador
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        self.transient(master)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14))
        self.label.pack(pady=10, padx=20)

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate")
        self.progressbar.pack(pady=10, padx=20, fill="x")
        self.progressbar.start()

        self.protocol("WM_DELETE_WINDOW", self.disable_close)

    def disable_close(self):
        """Impede o fechamento do diálogo"""
        pass
    
    def update_message(self, message: str):
        """Atualiza a mensagem do diálogo"""
        self.label.configure(text=message)
        self.update_idletasks()
