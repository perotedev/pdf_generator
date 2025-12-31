# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import colorchooser
from models import TextStyle
from resources.strings import strings

class TextStyleDialog(ctk.CTkToplevel):
    """Diálogo para configurar estilo de texto"""
    
    # Fontes padrão disponíveis no Windows
    AVAILABLE_FONTS = [
        "Arial",
        "Calibri",
        "Cambria",
        "Comic Sans MS",
        "Courier New",
        "Georgia",
        "Helvetica",
        "Impact",
        "Lucida Console",
        "Palatino",
        "Tahoma",
        "Times New Roman",
        "Trebuchet MS",
        "Verdana"
    ]
    
    def __init__(self, master, initial_style: TextStyle = None, callback=None):
        super().__init__(master)
        
        self.callback = callback
        self.result_style = None
        
        self.title(strings.STYLE_DIALOG_TITLE)
        self.geometry("400x350")
        self.resizable(False, False)
        
        # Centraliza na tela
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - 200
        y = (screen_height // 2) - 175
        self.geometry(f"400x350+{x}+{y}")
        
        self.transient(master)
        self.grab_set()
        
        # Inicializa com estilo existente ou padrão
        if initial_style:
            self.style = TextStyle(
                font_family=initial_style.font_family,
                font_size=initial_style.font_size,
                bold=initial_style.bold,
                italic=initial_style.italic,
                underline=initial_style.underline,
                color=initial_style.color
            )
        else:
            self.style = TextStyle()
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Container principal
        main_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Fonte
        font_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        font_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(font_frame, text=strings.STYLE_FONT_LABEL, width=100, anchor="w").pack(side="left", padx=5)
        self.font_var = ctk.StringVar(value=self.style.font_family)
        font_menu = ctk.CTkOptionMenu(
            font_frame,
            variable=self.font_var,
            values=self.AVAILABLE_FONTS,
            width=200
        )
        font_menu.pack(side="left", padx=5)
        
        # Tamanho
        size_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(size_frame, text=strings.STYLE_SIZE_LABEL, width=100, anchor="w").pack(side="left", padx=5)
        self.size_var = ctk.StringVar(value=str(self.style.font_size))
        size_spinbox = ctk.CTkEntry(size_frame, textvariable=self.size_var, width=80)
        size_spinbox.pack(side="left", padx=5)
        
        # Slider para tamanho
        self.size_slider = ctk.CTkSlider(
            size_frame,
            from_=8,
            to=58,
            number_of_steps=50,
            command=self._on_size_slider_change,
            width=100
        )
        self.size_slider.set(self.style.font_size)
        self.size_slider.pack(side="left", padx=5)
        
        # Estilos (negrito, itálico, sublinhado)
        style_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        style_frame.pack(fill="x", pady=10)
        
        self.bold_var = ctk.BooleanVar(value=self.style.bold)
        bold_check = ctk.CTkCheckBox(style_frame, text=strings.STYLE_BOLD, variable=self.bold_var)
        bold_check.pack(side="left", padx=10)
        
        self.italic_var = ctk.BooleanVar(value=self.style.italic)
        italic_check = ctk.CTkCheckBox(style_frame, text=strings.STYLE_ITALIC, variable=self.italic_var)
        italic_check.pack(side="left", padx=10)
        
        self.underline_var = ctk.BooleanVar(value=self.style.underline)
        underline_check = ctk.CTkCheckBox(style_frame, text=strings.STYLE_UNDERLINE, variable=self.underline_var)
        underline_check.pack(side="left", padx=10)
        
        # Cor
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(color_frame, text=strings.STYLE_COLOR_LABEL, width=100, anchor="w").pack(side="left", padx=5)
        
        self.color_display = ctk.CTkFrame(color_frame, width=50, height=30, fg_color=self.style.color)
        self.color_display.pack(side="left", padx=5)
        
        color_button = ctk.CTkButton(
            color_frame,
            text=strings.STYLE_CHOOSE_COLOR,
            command=self._choose_color,
            width=120
        )
        color_button.pack(side="left", padx=5)
        
        # Preview
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(preview_frame, text="Preview:", anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Texto de Exemplo",
            font=self._get_preview_font(),
            text_color=self.style.color
        )
        self.preview_label.pack(pady=20)
        
        # Botões
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text=strings.STYLE_CANCEL,
            command=self._on_cancel,
            fg_color="gray40",
            width=120
        )
        cancel_button.pack(side="left", padx=10)
        
        save_button = ctk.CTkButton(
            button_frame,
            text=strings.STYLE_SAVE,
            command=self._on_save,
            width=120
        )
        save_button.pack(side="right", padx=10)
        
        # Bind para atualizar preview
        self.font_var.trace_add("write", lambda *args: self._update_preview())
        self.size_var.trace_add("write", lambda *args: self._update_preview())
        self.bold_var.trace_add("write", lambda *args: self._update_preview())
        self.italic_var.trace_add("write", lambda *args: self._update_preview())
        self.underline_var.trace_add("write", lambda *args: self._update_preview())
    
    def _on_size_slider_change(self, value):
        """Atualiza o campo de tamanho quando o slider muda"""
        self.size_var.set(str(int(value)))
    
    def _get_preview_font(self):
        """Retorna a fonte para o preview"""
        try:
            size = int(self.size_var.get())
        except:
            size = 10
        
        weight = "bold" if self.bold_var.get() else "normal"
        slant = "italic" if self.italic_var.get() else "roman"
        underline = 1 if self.underline_var.get() else 0
        
        return ctk.CTkFont(
            family=self.font_var.get(),
            size=size,
            weight=weight,
            slant=slant,
            underline=underline
        )
    
    def _update_preview(self):
        """Atualiza o preview do texto"""
        try:
            self.preview_label.configure(
                font=self._get_preview_font(),
                text_color=self.style.color
            )
        except:
            pass
    
    def _choose_color(self):
        """Abre o seletor de cor"""
        color = colorchooser.askcolor(
            initialcolor=self.style.color,
            title=strings.STYLE_CHOOSE_COLOR,
            parent=self.winfo_toplevel()
        )
        if color[1]:  # color[1] é o valor hexadecimal
            self.style.color = color[1]
            self.color_display.configure(fg_color=color[1])
            self._update_preview()
    
    def _on_save(self):
        """Salva o estilo e fecha o diálogo"""
        try:
            size = int(self.size_var.get())
            if size < 8:
                size = 8
            elif size > 58:
                size = 58
        except:
            size = 10
        
        self.result_style = TextStyle(
            font_family=self.font_var.get(),
            font_size=size,
            bold=self.bold_var.get(),
            italic=self.italic_var.get(),
            underline=self.underline_var.get(),
            color=self.style.color
        )
        
        if self.callback:
            self.callback(self.result_style)
        
        self.grab_release()
        self.destroy()
    
    def _on_cancel(self):
        """Cancela e fecha o diálogo"""
        self.result_style = None
        self.grab_release()
        self.destroy()
