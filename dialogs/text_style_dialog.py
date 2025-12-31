# -*- coding: utf-8 -*-
import copy 
import customtkinter as ctk
from tkinter import colorchooser
from resources.strings import strings

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
        self.title(strings.STYLE_DIALOG_TITLE) 
        self.geometry("350x365") # Aumentado de 365 para 380 para acomodar o novo checkbox
        self.resizable(False, False)
        
        # Centraliza na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 210
        y = (self.winfo_screenheight() // 2) - 225
        self.geometry(f"350x365+{x}+{y}")
        
        self.transient(master)
        self.grab_set()

        self.initial_style = initial_style

        # Mock do estilo se não fornecido (para teste)
        if initial_style:
            self.style = copy.deepcopy(initial_style)
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
        ctk.CTkLabel(font_frame, text=strings.STYLE_DIALOG_FONT_LABEL, width=80, anchor="w").pack(side="left")
        self.font_var = ctk.StringVar(value=self.style.font_family)
        font_menu = ctk.CTkOptionMenu(font_frame, variable=self.font_var, values=self.AVAILABLE_FONTS, width=200)
        font_menu.pack(side="left", padx=5)
        
        # Tamanho
        size_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(size_frame, text=strings.STYLE_DIALOG_SIZE_LABEL, width=80, anchor="w").pack(side="left")
        self.size_var = ctk.StringVar(value=str(self.style.font_size))
        size_entry = ctk.CTkEntry(size_frame, textvariable=self.size_var, width=60)
        size_entry.pack(side="left", padx=5)
        
        self.size_slider = ctk.CTkSlider(size_frame, from_=8, to=72, number_of_steps=64, 
                                        command=lambda v: self.size_var.set(str(int(v))), width=150)
        self.size_slider.set(int(self.style.font_size))
        self.size_slider.pack(side="left", padx=5)
        
        # Estilos (Negrito, Itálico, Sublinhado)
        style_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        style_frame.pack(fill="x", pady=10, padx=0)
        
        self.bold_var = ctk.BooleanVar(value=self.style.bold)
        ctk.CTkCheckBox(style_frame, text=strings.STYLE_DIALOG_BOLD, variable=self.bold_var).pack(side="left", padx=0)
        
        self.italic_var = ctk.BooleanVar(value=self.style.italic)
        ctk.CTkCheckBox(style_frame, text=strings.STYLE_DIALOG_ITALIC, variable=self.italic_var).pack(side="left", padx=5)
        
        self.underline_var = ctk.BooleanVar(value=self.style.underline)
        ctk.CTkCheckBox(style_frame, text=strings.STYLE_DIALOG_UNDERLINE, variable=self.underline_var).pack(side="left", padx=0)
        
        # Cor
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(color_frame, text=strings.STYLE_DIALOG_COLOR_LABEL, width=80, anchor="w").pack(side="left")
        self.color_display = ctk.CTkFrame(color_frame, width=40, height=25, fg_color=self.style.color)
        self.color_display.pack(side="left", padx=5)
        ctk.CTkButton(color_frame, text=strings.STYLE_DIALOG_CHOOSE_COLOR, width=100, command=self._choose_color).pack(side="left", padx=5)
        
        # --- Preview ---
        preview_group = ctk.CTkFrame(main_frame, fg_color=("gray85", "gray25"), corner_radius=10, height=115)
        preview_group.pack(fill="x", pady=(15, 5)) 
        preview_group.pack_propagate(False)  

        self.preview_label = ctk.CTkLabel(
            preview_group, 
            text=strings.STYLE_DIALOG_TEXT_EXAMPLE, 
            font=self._get_preview_font(), 
            height=100
        )
        self.preview_label.pack(pady=10, fill="x") 
        
        # --- Botões de Ação (Confirmar/Cancelar) ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=0)
        
        # Para que os botões preencham toda a largura, usamos side="left" com fill="x" e expand=True
        cancel_button = ctk.CTkButton(
            button_frame, 
            text=strings.STYLE_DIALOG_CANCEL, 
            command=self._on_cancel,
            fg_color="transparent",
            border_width=2,
            text_color=("black", "white"),
            width=0 # Removido largura fixa para permitir expansão
        )
        cancel_button.pack(side="left", padx=(0, 5), pady=(0,5), fill="x", expand=True)

        save_button = ctk.CTkButton(
            button_frame, 
            text=strings.STYLE_DIALOG_SAVE, 
            command=self._on_save,
            width=0 # Removido largura fixa para permitir expansão
        )
        save_button.pack(side="left", padx=(5, 0), pady=(0,5),fill="x", expand=True)
        
        self._update_preview()
        
        # Traces para o preview
        for var in [self.font_var, self.size_var, self.bold_var, self.italic_var, self.underline_var]:
            var.trace_add("write", lambda *args: self._update_preview())

    def _get_preview_font(self):
        try:
            size = int(self.size_var.get())
        except:
            size = 12
        weight = "bold" if self.bold_var.get() else "normal"
        slant = "italic" if self.italic_var.get() else "roman"
        underline = self.underline_var.get()
        return ctk.CTkFont(family=self.font_var.get(), size=size, weight=weight, slant=slant, underline=underline)

    def _update_preview(self):
        self.preview_label.configure(font=self._get_preview_font(), text_color=self.style.color)

    def _choose_color(self):
        color = colorchooser.askcolor(
                initialcolor=self.style.color, 
                title=strings.STYLE_DIALOG_CHOOSE_COLOR,
                parent=self.winfo_toplevel()
            )
        if color[1]:
            self.style.color = color[1]
            self.color_display.configure(fg_color=color[1])
            self._update_preview()

    def _on_save(self):
        # Atualiza o objeto style com os valores atuais antes de retornar
        self.style.font_family = self.font_var.get()
        try:
            self.style.font_size = int(self.size_var.get())
        except:
            pass
        self.style.bold = self.bold_var.get()
        self.style.italic = self.italic_var.get()
        self.style.underline = self.underline_var.get()
        
        if self.callback:
            self.callback(self.style)
        self.destroy()

    def _on_cancel(self):
        self.destroy()