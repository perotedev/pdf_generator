# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import colorchooser
# Importe seus modelos e strings aqui
# from models import TextStyle
# from resources.strings import strings

class TextStyleDialog(ctk.CTkToplevel):
    """Diálogo para configurar estilo de texto corrigido"""
    
    AVAILABLE_FONTS = [
        "Arial", "Calibri", "Cambria", "Comic Sans MS", "Courier New",
        "Georgia", "Helvetica", "Impact", "Lucida Console", "Palatino",
        "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"
    ]
    
    def __init__(self, master, initial_style=None, callback=None):
        super().__init__(master)
        
        self.callback = callback
        self.result_style = None
        
        # Título e Geometria
        # Aumentei um pouco a altura para garantir que os botões não fiquem escondidos
        self.title("Configurar Estilo") 
        self.geometry("420x450") 
        self.resizable(False, False)
        
        # Centraliza na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 210
        y = (self.winfo_screenheight() // 2) - 225
        self.geometry(f"420x450+{x}+{y}")
        
        self.transient(master)
        self.grab_set()
        
        # Mock do estilo se não fornecido (para teste)
        if initial_style:
            self.style = initial_style
        else:
            # Fallback caso TextStyle não esteja definido no contexto
            class DefaultStyle:
                def __init__(self):
                    self.font_family = "Arial"
                    self.font_size = 12
                    self.bold = False
                    self.italic = False
                    self.underline = False
                    self.color = "#FFFFFF"
            self.style = DefaultStyle()
        
        self._create_widgets()
        
    def _create_widgets(self):
        # 1. Container principal com a cor de fundo da janela para "sumir" o frame
        # Usamos fg_color do self para evitar o bug do transparent
        main_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"), corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- Seção de Configurações ---
        
        # Fonte
        font_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        font_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(font_frame, text="Fonte:", width=80, anchor="w").pack(side="left")
        self.font_var = ctk.StringVar(value=self.style.font_family)
        font_menu = ctk.CTkOptionMenu(font_frame, variable=self.font_var, values=self.AVAILABLE_FONTS, width=200)
        font_menu.pack(side="left", padx=5)
        
        # Tamanho
        size_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(size_frame, text="Tamanho:", width=80, anchor="w").pack(side="left")
        self.size_var = ctk.StringVar(value=str(self.style.font_size))
        size_entry = ctk.CTkEntry(size_frame, textvariable=self.size_var, width=60)
        size_entry.pack(side="left", padx=5)
        
        self.size_slider = ctk.CTkSlider(size_frame, from_=8, to=72, number_of_steps=64, 
                                        command=lambda v: self.size_var.set(str(int(v))), width=150)
        self.size_slider.set(int(self.style.font_size))
        self.size_slider.pack(side="left", padx=5)
        
        # Estilos
        style_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        style_frame.pack(fill="x", pady=10)
        self.bold_var = ctk.BooleanVar(value=self.style.bold)
        ctk.CTkCheckBox(style_frame, text="Negrito", variable=self.bold_var).pack(side="left", padx=5)
        self.italic_var = ctk.BooleanVar(value=self.style.italic)
        ctk.CTkCheckBox(style_frame, text="Itálico", variable=self.italic_var).pack(side="left", padx=5)
        
        # Cor
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(color_frame, text="Cor:", width=80, anchor="w").pack(side="left")
        self.color_display = ctk.CTkFrame(color_frame, width=40, height=25, fg_color=self.style.color)
        self.color_display.pack(side="left", padx=5)
        ctk.CTkButton(color_frame, text="Escolher Cor", width=100, command=self._choose_color).pack(side="left", padx=5)
        
        # --- Preview ---
        preview_group = ctk.CTkFrame(main_frame, fg_color=("gray85", "gray25"), corner_radius=10)
        preview_group.pack(fill="both", expand=True, pady=15)
        
        self.preview_label = ctk.CTkLabel(preview_group, text="Texto de Exemplo", font=self._get_preview_font())
        self.preview_label.pack(expand=True, pady=20)
        
        # --- Botões de Ação (Confirmar/Cancelar) ---
        # Colocamos em um frame separado no final para garantir visibilidade
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        save_button = ctk.CTkButton(
            button_frame, 
            text="Confirmar", 
            command=self._on_save,
            fg_color="#009454", # Cor verde para destacar o confirmar
            hover_color="#106a43",
            width=140
        )
        save_button.pack(side="right", padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame, 
            text="Cancelar", 
            command=self._on_cancel,
            fg_color="transparent",
            border_width=2,
            text_color=("black", "white"),
            width=100
        )
        cancel_button.pack(side="right", padx=5)
        
        # Traces para o preview
        for var in [self.font_var, self.size_var, self.bold_var, self.italic_var]:
            var.trace_add("write", lambda *args: self._update_preview())

    def _get_preview_font(self):
        try:
            size = int(self.size_var.get())
        except:
            size = 12
        weight = "bold" if self.bold_var.get() else "normal"
        slant = "italic" if self.italic_var.get() else "roman"
        return ctk.CTkFont(family=self.font_var.get(), size=size, weight=weight, slant=slant)

    def _update_preview(self):
        self.preview_label.configure(font=self._get_preview_font(), text_color=self.style.color)

    def _choose_color(self):
        color = colorchooser.askcolor(
                initialcolor=self.style.color, 
                title="Escolher Cor",
                parent=self.winfo_toplevel()
            )
        if color[1]:
            self.style.color = color[1]
            self.color_display.configure(fg_color=color[1])
            self._update_preview()

    def _on_save(self):
        # Aqui você reconstrói seu objeto TextStyle com os novos valores
        # self.result_style = TextStyle(...) 
        if self.callback:
            self.callback(self.style)
        self.destroy()

    def _on_cancel(self):
        self.destroy()