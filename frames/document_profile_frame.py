# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import messagebox
import os
from typing import List, Optional
from models import DocumentProfile, SpreadsheetProfile, PdfFieldMapping, TextStyle, PageFormat, PageOrientation
from core.data_manager import data_manager
from utils import select_file, render_pdf_to_image, get_pdf_page_count, get_page_size_mm
from PIL import Image, ImageTk
import threading
from dialogs import ProgressDialog, TextStyleDialog
from resources.strings import strings
from resources.icons import icons

class DocumentProfileFrame(ctk.CTkFrame):
    left_column_width = 350
    
    # Formatos de página disponíveis
    PAGE_FORMATS = ["A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal"]
    PAGE_ORIENTATIONS = [
        (strings.DOC_ORIENTATION_PORTRAIT, "portrait"),
        (strings.DOC_ORIENTATION_LANDSCAPE, "landscape")
    ]

    def _set_text_wrap(self, text: str, max_len=30):
        if len(text) > max_len:
            text = text[:max_len-3] + "..."
        return text

    def _set_pdf_button_text(self, path: str):
        name = os.path.basename(path)
        name = self._set_text_wrap(name, 24)
        self.select_pdf_button.configure(text=strings.DOC_PDF_SELECTED.format(name))

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Configuração do grid principal
        self.grid_columnconfigure(0, weight=0) # Coluna esquerda fixa
        self.grid_columnconfigure(1, weight=1) # Coluna direita expande
        self.grid_rowconfigure(1, weight=1)

        self.pdf_path: Optional[str] = None
        self.pdf_image: Optional[Image.Image] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None
        self.image_width_mm: float = 210  # A4 padrão
        self.image_height_mm: float = 297  # A4 padrão
        self.current_page_index = 0
        self.total_pages = 0
        self.page_format: PageFormat = "A4"
        self.page_orientation: PageOrientation = "portrait"
        
        self.document_profile_name_var = ctk.StringVar()
        self.available_spreadsheet_profiles: List[SpreadsheetProfile] = []
        self.field_mappings: List[PdfFieldMapping] = []
        
        self.real_values: dict[str, str] = {"to_map": "", "to_title": "", "to_spreadsheed": ""}
        self.label_values: dict[str, ctk.StringVar] = {"to_map": ctk.StringVar(), "to_title": ctk.StringVar(), "to_spreadsheed": ctk.StringVar()}
        self.spreadsheet_profile_name_var = ctk.StringVar()
        self.selected_column_to_map_var = ""
        self.x_coord_var = ctk.StringVar(value="0.0")
        self.y_coord_var = ctk.StringVar(value="0.0")

        # --- Título ---
        ctk.CTkLabel(self, text=strings.DOC_PROFILE_TITLE, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # --- Coluna Esquerda (Configurações) ---
        self.wrapper = ctk.CTkFrame(self, width=self.left_column_width, fg_color="transparent")
        self.wrapper.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.wrapper.grid_columnconfigure(0, weight=1)
        self.wrapper.grid_rowconfigure(4, weight=1)
        self.wrapper.grid_propagate(False)

        # Top Frame (PDF e Nome)
        self.top_frame = ctk.CTkFrame(self.wrapper)
        self.top_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.select_pdf_button = ctk.CTkButton(self.top_frame, text=strings.DOC_SELECT_PDF, command=self._select_pdf)
        self.select_pdf_button.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="we")

        self.profile_name_entry = ctk.CTkEntry(self.top_frame, placeholder_text=strings.DOC_PROFILE_NAME_PLACEHOLDER, textvariable=self.document_profile_name_var)
        self.profile_name_entry.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="we")

        # Spreadsheet Profile Selection
        self.profile_select_frame = ctk.CTkFrame(self.wrapper)
        self.profile_select_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.profile_select_frame.grid_columnconfigure(0, weight=1)
        
        self.spreadsheet_profile_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                         variable=self.label_values["to_spreadsheed"],
                                                         values=[strings.DOC_SELECT_SPREADSHEET_PROFILE],
                                                         command=self._on_profile_select)
        self.spreadsheet_profile_menu.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        ctk.CTkLabel(self.profile_select_frame, text=strings.DOC_TITLE_COLUMN).grid(row=2, column=0, padx=10, pady=0, sticky="w")
        self.title_column_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                   variable=self.label_values["to_title"],
                                                   values=[strings.DOC_SELECT_COLUMN],
                                                   command=self._on_select_to_title)
        self.title_column_menu.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Page Format Frame
        self.format_frame = ctk.CTkFrame(self.wrapper)
        self.format_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.format_frame.grid_columnconfigure(0, weight=1)
        self.format_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.format_frame, text=strings.DOC_PAGE_FORMAT).grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        self.page_format_var = ctk.StringVar(value="A4")
        self.page_format_menu = ctk.CTkOptionMenu(
            self.format_frame,
            variable=self.page_format_var,
            values=self.PAGE_FORMATS,
            command=self._on_page_format_change
        )
        self.page_format_menu.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(self.format_frame, text=strings.DOC_PAGE_ORIENTATION).grid(row=0, column=1, padx=10, pady=(5,0), sticky="w")
        self.page_orientation_var = ctk.StringVar(value=strings.DOC_ORIENTATION_PORTRAIT)
        self.page_orientation_menu = ctk.CTkOptionMenu(
            self.format_frame,
            variable=self.page_orientation_var,
            values=[label for label, _ in self.PAGE_ORIENTATIONS],
            command=self._on_page_orientation_change
        )
        self.page_orientation_menu.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
              
        # Mapping Area Frame
        self.mapping_area_frame = ctk.CTkFrame(self.wrapper)
        self.mapping_area_frame.grid(row=4, column=0, padx=20, pady=0, sticky="nsew")
        self.mapping_area_frame.grid_columnconfigure(0, weight=1)
        self.mapping_area_frame.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self.mapping_area_frame, text=strings.DOC_STEP_1, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        
        self.column_menu = ctk.CTkOptionMenu(
                self.mapping_area_frame,
                variable=self.label_values["to_map"],
                values=[strings.DOC_SELECT_COLUMN],
                command=self._on_select_to_map
            )
        self.column_menu.grid(row=1, column=0, padx=10, pady=0, sticky="ew")

        # Mapping Display Area
        self.mapping_display_frame = ctk.CTkScrollableFrame(self.mapping_area_frame, label_text=strings.DOC_CURRENT_MAPPINGS, fg_color="transparent")
        self.mapping_display_frame.grid(row=3, column=0, padx=3, pady=(10, 0), sticky="nsew")
        self.mapping_display_frame.grid_columnconfigure(0, weight=1)

        # Save Button
        self.save_button_frame = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        self.save_button_frame.grid(row=5, column=0, padx=0, pady=0, sticky="ew")
        self.save_button_frame.grid_columnconfigure(0, weight=1)
        self.save_button = ctk.CTkButton(self.save_button_frame, text=strings.DOC_SAVE_PROFILE, command=self._save_profile)
        self.save_button.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="ew")

        # --- Coluna Direita (PDF Viewer) ---
        self.pdf_viewer_container = ctk.CTkFrame(self, fg_color="transparent")
        self.pdf_viewer_container.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.pdf_viewer_container.grid_columnconfigure(0, weight=1)
        self.pdf_viewer_container.grid_rowconfigure(1, weight=1)

        # Controles de Página
        self.page_controls = ctk.CTkFrame(self.pdf_viewer_container, fg_color="transparent")
        self.page_controls.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        
        self.prev_page_button = ctk.CTkButton(self.page_controls, text=strings.DOC_PREVIOUS_PAGE, width=80, command=self._prev_page, state="disabled")
        self.prev_page_button.pack(side="left", padx=10)
        
        self.page_label = ctk.CTkLabel(self.page_controls, text=strings.DOC_PAGE_LABEL.format(0, 0))
        self.page_label.pack(side="left", expand=True)
        
        self.next_page_button = ctk.CTkButton(self.page_controls, text=strings.DOC_NEXT_PAGE, width=80, command=self._next_page, state="disabled")
        self.next_page_button.pack(side="right", padx=10)

        # Canvas com Scroll
        self.canvas_frame = ctk.CTkFrame(self.pdf_viewer_container)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew")
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.pdf_canvas = ctk.CTkCanvas(self.canvas_frame, bg="gray80", highlightthickness=0)
        self.pdf_canvas.grid(row=0, column=0, sticky="nsew")
        
        self.v_scrollbar = ctk.CTkScrollbar(self.canvas_frame, orientation="vertical", command=self.pdf_canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.h_scrollbar = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal", command=self.pdf_canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.pdf_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.pdf_canvas.bind("<Button-1>", self._on_pdf_click)
        self.pdf_canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Suporte ao scroll com a roda do mouse
        self.pdf_canvas.bind_all("<MouseWheel>", self._on_mousewheel) # Windows/macOS
        self.pdf_canvas.bind_all("<Button-4>", self._on_mousewheel)   # Linux scroll up
        self.pdf_canvas.bind_all("<Button-5>", self._on_mousewheel)   # Linux scroll down

        self.pdf_canvas_label = ctk.CTkLabel(self.pdf_canvas, text=strings.DOC_SELECT_PDF_VIEWER)
        self.pdf_canvas_label.place(relx=0.5, rely=0.5, anchor="center")

        self._load_profiles()
        self._update_mapping_display()
    
    def _on_page_format_change(self, value):
        """Callback quando o formato da página é alterado"""
        if self.field_mappings:
            # Avisa que os mapeamentos serão perdidos
            result = messagebox.askyesno(
                strings.CONFIRM_FORMAT_CHANGE_TITLE,
                strings.CONFIRM_FORMAT_CHANGE_MESSAGE
            )
            if not result:
                # Restaura o valor anterior
                self.page_format_var.set(self.page_format)
                return
            # Limpa os mapeamentos
            self.field_mappings = []
            self._update_mapping_display()
            self._on_canvas_resize()
        
        self.page_format = value
        self._update_page_dimensions()
    
    def _on_page_orientation_change(self, value):
        """Callback quando a orientação da página é alterada"""
        if self.field_mappings:
            # Avisa que os mapeamentos serão perdidos
            result = messagebox.askyesno(
                strings.CONFIRM_FORMAT_CHANGE_TITLE,
                strings.CONFIRM_FORMAT_CHANGE_MESSAGE
            )
            if not result:
                # Restaura o valor anterior
                for label, orientation in self.PAGE_ORIENTATIONS:
                    if orientation == self.page_orientation:
                        self.page_orientation_var.set(label)
                        return
            # Limpa os mapeamentos
            self.field_mappings = []
            self._update_mapping_display()
            self._on_canvas_resize()
        
        # Converte o label para o valor interno
        for label, orientation in self.PAGE_ORIENTATIONS:
            if label == value:
                self.page_orientation = orientation
                break
        
        self._update_page_dimensions()
    
    def _update_page_dimensions(self):
        """Atualiza as dimensões da página baseado no formato e orientação"""
        width_mm, height_mm = get_page_size_mm(self.page_format, self.page_orientation)
        self.image_width_mm = width_mm
        self.image_height_mm = height_mm
        
        # Re-renderiza o PDF se já houver um carregado
        if self.pdf_path:
            self._on_canvas_resize()

    def _prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._render_pdf_image()

    def _next_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self._render_pdf_image()

    def _update_page_controls(self):
        self.page_label.configure(text=strings.DOC_PAGE_LABEL.format(self.current_page_index + 1, self.total_pages))
        self.prev_page_button.configure(state="normal" if self.current_page_index > 0 else "disabled")
        self.next_page_button.configure(state="normal" if self.current_page_index < self.total_pages - 1 else "disabled")

    def _on_mousewheel(self, event):
        if not self.pdf_image:
            return
            
        # Windows/macOS usam event.delta, Linux usa event.num
        if event.num == 4 or event.delta > 0:
            self.pdf_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.pdf_canvas.yview_scroll(1, "units")

    def load_profile_for_editing(self, profile: DocumentProfile):
        self.document_profile_name_var.set(profile.name)
        self.pdf_path = profile.pdf_path
        self.field_mappings = profile.field_mappings
        self.page_format = profile.page_format
        self.page_orientation = profile.page_orientation
        
        # Atualiza os controles de formato
        self.page_format_var.set(self.page_format)
        for label, orientation in self.PAGE_ORIENTATIONS:
            if orientation == self.page_orientation:
                self.page_orientation_var.set(label)
                break
        
        self._update_page_dimensions()
        self._on_select_to_spreadsheed(profile.spreadsheet_profile_name)
        self._on_select_to_title(profile.title_column)
        
        self.profile_name_entry.configure(state="disabled")
        self._set_pdf_button_text(self.pdf_path)
        self.save_button.configure(text=strings.DOC_SAVE_CHANGES, command=lambda: self._save_profile(is_editing=True))
        
        self.total_pages = get_pdf_page_count(self.pdf_path)
        self.current_page_index = 0
        self._render_pdf_image()
        
        self._on_profile_select(profile.spreadsheet_profile_name)
        self._on_select_to_title(profile.title_column)
        self._update_mapping_display()

    def clear_form(self):
        self.pdf_path = None
        self.document_profile_name_var.set("")
        self.field_mappings = []
        self.current_page_index = 0
        self.total_pages = 0
        self.page_format = "A4"
        self.page_orientation = "portrait"
        self.page_format_var.set("A4")
        self.page_orientation_var.set(strings.DOC_ORIENTATION_PORTRAIT)
        self._update_page_dimensions()
        self.profile_name_entry.configure(state="normal")
        self.select_pdf_button.configure(state="normal", text=strings.DOC_SELECT_PDF)
        self.save_button.configure(text=strings.DOC_SAVE_PROFILE, command=self._save_profile)
        self.pdf_image = None
        self.tk_image = None
        self.pdf_canvas.delete("all")
        self.pdf_canvas_label.place(relx=0.5, rely=0.5, anchor="center")
        self._update_page_controls()
        self._load_profiles()
        self._update_mapping_display()

    def _load_profiles(self):
        self.available_spreadsheet_profiles = data_manager.load_profiles(SpreadsheetProfile)
        profile_names = [p.name for p in self.available_spreadsheet_profiles]
        if not profile_names:
            profile_names = [strings.NO_PROFILES_FOUND]
            self._on_select_to_spreadsheed(profile_names[0])
        else:
            self.spreadsheet_profile_menu.configure(values=profile_names, state="normal")
            self._on_select_to_spreadsheed(profile_names[0])
            self._on_profile_select(profile_names[0])

    def _on_profile_select(self, profile_name: str):
        self._on_select_to_spreadsheed(profile_name)
        selected_profile = next((p for p in self.available_spreadsheet_profiles if p.name == profile_name), None)
        
        if selected_profile:
            column_names = [c.custom_name for c in selected_profile.columns]
            self.column_menu.configure(values=column_names)
            self.title_column_menu.configure(values=column_names)
            self._on_select_to_map(column_names[0] if column_names else strings.DOC_SELECT_COLUMN)
            self._on_select_to_title(column_names[0] if column_names else strings.DOC_SELECT_COLUMN)
        else:
            self.title_column_menu.configure(values=[strings.DOC_SELECT_COLUMN])
            self.column_menu.configure(values=[strings.DOC_SELECT_COLUMN])
            self._on_select_to_map(strings.DOC_SELECT_COLUMN)
            self._on_select_to_title(strings.DOC_SELECT_COLUMN)

        self._update_mapping_display()

    def _on_select(self, value: str, input_name: str, max_len=30):
        self.real_values[input_name] = value
        self.label_values[input_name].set(self._set_text_wrap(value, max_len))

    def _on_select_to_map(self, value: str):
        self._on_select(value, 'to_map', 38)
        self.selected_column_to_map_var = value
    
    def _on_select_to_title(self, value: str):
        self._on_select(value, 'to_title', 38)

    def _on_select_to_spreadsheed(self, value: str):
        self._on_select(value, 'to_spreadsheed', 38)

    def _select_pdf(self):
        pdf_path = select_file([(strings.FILE_FILTERS_PDF, "*.pdf")])
        if pdf_path:
            self.pdf_path = pdf_path
            self.total_pages = get_pdf_page_count(pdf_path)
            self.current_page_index = 0
            self.document_profile_name_var.set(os.path.basename(pdf_path).split('.')[0] + "_DocProfile")
            self.select_pdf_button.configure(text=strings.DOC_PDF_SELECTED.format(os.path.basename(pdf_path)))
            self._render_pdf_image()

    def _handle_render_pdf_result(self, progress_dialog):
        if progress_dialog.winfo_exists():
            try: progress_dialog.grab_release()
            except: pass
            progress_dialog.withdraw()
            progress_dialog.after(200, lambda: progress_dialog.destroy())
        
        if self.pdf_image:
            self.pdf_canvas_label.place_forget()
            self._update_page_controls()
            self._on_canvas_resize()
            return True
        else:
            messagebox.showerror(strings.ERROR_RENDER_PDF_TITLE, strings.ERROR_RENDER_PDF_MESSAGE)
            self.pdf_canvas_label.place(relx=0.5, rely=0.5, anchor="center")
            return False

    def _render_pdf_to_image_thread(self, pdf_path, page_index, progress_dialog):
        self.pdf_image = render_pdf_to_image(pdf_path, page_index, dpi=150)
        self.after(50, lambda: self._handle_render_pdf_result(progress_dialog))

    def _render_pdf_image(self):
        if not self.pdf_path: return False
        progress_dialog = ProgressDialog(self, title=strings.PROGRESS_LOADING_PDF, message=strings.PROGRESS_RENDERING_PAGE.format(self.current_page_index + 1))
        threading.Thread(target=self._render_pdf_to_image_thread, args=(self.pdf_path, self.current_page_index, progress_dialog)).start()

    def _on_canvas_resize(self, event=None):
        if not self.pdf_image: return

        canvas_width = self.pdf_canvas.winfo_width()
        if canvas_width <= 1: return

        img_width, img_height = self.pdf_image.size
        
        # O PDF deve ocupar a largura total do canvas (menos um pequeno padding)
        padding = 40
        new_width = canvas_width - padding
        ratio = new_width / img_width
        new_height = int(img_height * ratio)

        resized_image = self.pdf_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)

        self.pdf_canvas.delete("all")
        # Centraliza horizontalmente, mas começa do topo (y=20)
        x_offset = padding // 2
        y_offset = 20
        self.pdf_canvas.create_image(x_offset, y_offset, anchor="nw", image=self.tk_image)
        
        # Atualiza a região de scroll do canvas
        self.pdf_canvas.configure(scrollregion=(0, 0, canvas_width, new_height + 40))
        
        self._draw_mappings(new_width, new_height, x_offset, y_offset)

    def _draw_mappings(self, img_width, img_height, x_offset, y_offset):
        if not self.pdf_image: return
        scale_x = img_width / self.image_width_mm
        scale_y = img_height / self.image_height_mm

        for mapping in self.field_mappings:
            # Só desenha se for da página atual
            if getattr(mapping, 'page_index', 0) != self.current_page_index:
                continue
                
            x_pixel = int(mapping.x * scale_x) + x_offset
            y_pixel = int(mapping.y * scale_y) + y_offset

            radius = 5
            self.pdf_canvas.create_oval(x_pixel - radius, y_pixel - radius, x_pixel + radius, y_pixel + radius, fill="red", outline="white", tags="mapping_marker")
            self.pdf_canvas.create_text(x_pixel + radius + 2, y_pixel, anchor="w", text=mapping.column_name, fill="red", font=("Arial", 10, "bold"), tags="mapping_text")

    def _on_pdf_click(self, event):
        if not self.pdf_image or not self.tk_image: return

        column_name = self.selected_column_to_map_var
        if column_name == strings.DOC_SELECT_COLUMN:
            messagebox.showerror(strings.ERROR_TITLE, strings.ERROR_SELECT_COLUMN)
            return

        # Coordenadas reais no canvas considerando o scroll
        canvas_x = self.pdf_canvas.canvasx(event.x)
        canvas_y = self.pdf_canvas.canvasy(event.y)

        canvas_width = self.pdf_canvas.winfo_width()
        img_width, img_height = self.pdf_image.size
        padding = 40
        new_width = canvas_width - padding
        ratio = new_width / img_width
        new_height = int(img_height * ratio)
        x_offset = padding // 2
        y_offset = 20

        if not (x_offset <= canvas_x <= x_offset + new_width and y_offset <= canvas_y <= y_offset + new_height):
            return 

        x_img_pixel = canvas_x - x_offset
        y_img_pixel = canvas_y - y_offset

        scale_x = self.image_width_mm / new_width
        scale_y = self.image_height_mm / new_height

        x_mm = x_img_pixel * scale_x
        y_mm = y_img_pixel * scale_y

        self.x_coord_var.set(f"{x_mm:.1f}")
        self.y_coord_var.set(f"{y_mm:.1f}")
        self._add_mapping()

    def _add_mapping(self):
        column_name = self.selected_column_to_map_var
        if column_name == strings.DOC_SELECT_COLUMN: return

        try:
            x = float(self.x_coord_var.get())
            y = float(self.y_coord_var.get())
        except ValueError: return

        # Remove mapeamento existente da mesma coluna (independente da página)
        self.field_mappings = [m for m in self.field_mappings if m.column_name != column_name]
        
        # Adiciona o novo mapeamento com o índice da página atual e estilo padrão
        new_mapping = PdfFieldMapping(
            column_name=column_name,
            x=x,
            y=y,
            page_index=self.current_page_index,
            style=TextStyle()  # Estilo padrão
        )
        self.field_mappings.append(new_mapping)
            
        self._update_mapping_display()
        self._on_canvas_resize()
    
    def _edit_mapping_style(self, mapping: PdfFieldMapping):
        """Abre o diálogo para editar o estilo do mapeamento"""
        def on_style_saved(new_style: TextStyle):
            mapping.style = new_style
            self._update_mapping_display()
        
        TextStyleDialog(self, initial_style=mapping.style, callback=on_style_saved)

    def _update_mapping_display(self):
        for widget in self.mapping_display_frame.winfo_children():
            widget.destroy()

        if not self.field_mappings:
            ctk.CTkLabel(self.mapping_display_frame, text=strings.DOC_NO_MAPPINGS).grid(row=3, column=0, padx=20, pady=0)
            return

        for i, mapping in enumerate(sorted(self.field_mappings, key=lambda x: (getattr(x, 'page_index', 0), x.column_name))):
            row = i + 1
            pg = getattr(mapping, 'page_index', 0) + 1
            col_name = self._set_text_wrap(mapping.column_name, max_len=21)
            
            row_frame = ctk.CTkFrame(self.mapping_display_frame, fg_color="transparent", corner_radius=4, cursor="hand2")
            row_frame.grid(row=row, column=0, columnspan=3, padx=0, pady=0, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)

            name_label = ctk.CTkLabel(row_frame, text=col_name)
            name_label.grid(row=0, column=0, padx=5, pady=4, sticky="w")
            
            page_label = ctk.CTkLabel(row_frame, text=f"{strings.DOC_PAGE_PREFIX} {pg}")
            page_label.grid(row=0, column=1, padx=5, pady=4)
            
            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, padx=5, pady=2)
            
            style_btn = ctk.CTkButton(
                btn_frame, 
                text=icons.ICON_PAINT,
                width=28,
                command=lambda m=mapping: self._edit_mapping_style(m), 
                fg_color="blue",
                font=("Arial", 14)
            )
            style_btn.pack(side="left", padx=2)
            
            del_btn = ctk.CTkButton(
                btn_frame, 
                text=icons.ICON_DELETE,
                width=28, 
                command=lambda m=mapping: self._remove_mapping(m), 
                fg_color="red",
                font=("Arial", 10)
            )
            del_btn.pack(side="left", padx=(2,0))

            def on_enter(event, f=row_frame):
                f.configure(fg_color=("gray85", "gray25")) # Cor para modo claro e escuro

            def on_leave(event, f=row_frame):
                f.configure(fg_color="transparent")

            # go_action = lambda event, p=pg-1: self._go_to_page(p)

            go_action = lambda event, p=pg-1, col=mapping.column_name: self.handle_event(p, col)

            
            for widget in [row_frame, name_label, page_label]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                
                if widget != page_label: 
                    widget.bind("<Button-1>", go_action)

    def handle_event(self, p, column_name):
        self._go_to_page(p)
        self._on_select_to_map(column_name)
        
    def _go_to_page(self, page_index):
        if self.current_page_index != page_index:
            self.current_page_index = page_index
            self._render_pdf_image()

    def _remove_mapping(self, mapping: PdfFieldMapping):
        self.field_mappings.remove(mapping)
        self._update_mapping_display()
        self._on_canvas_resize()

    def clear_form(self):
        self.pdf_path = None
        self.pdf_image = None
        self.tk_image = None
        self.current_page_index = 0
        self.total_pages = 0
        self.field_mappings = []
        self.document_profile_name_var.set("")
        self.label_values["to_spreadsheed"].set(strings.DOC_SELECT_SPREADSHEET_PROFILE)
        self.label_values["to_title"].set(strings.DOC_SELECT_COLUMN)
        self.label_values["to_map"].set(strings.DOC_SELECT_COLUMN)
        self.page_format_var.set("A4")
        self.page_orientation_var.set(strings.DOC_ORIENTATION_PORTRAIT)
        self.select_pdf_button.configure(text=strings.DOC_SELECT_PDF)
        self.profile_name_entry.configure(state="normal")
        self.save_button.configure(text=strings.DOC_SAVE_PROFILE, command=self._save_profile)
        
        # Limpa o canvas
        self.pdf_canvas.delete("all")
        self.pdf_canvas_label.grid(row=0, column=0, sticky="nsew")
        self.page_label.configure(text=strings.DOC_PAGE_LABEL.format(0, 0))
        self.prev_page_button.configure(state="disabled")
        self.next_page_button.configure(state="disabled")
        
        self._update_mapping_display()
        self._load_profiles()

    def _save_profile(self, is_editing=False):
        profile_name = self.document_profile_name_var.get().strip()
        spreadsheet_profile_name = self.real_values["to_spreadsheed"]

        if not profile_name:
            messagebox.showerror(strings.ERROR_TITLE, strings.ERROR_NO_PROFILE_NAME)
            return
        
        if not self.pdf_path:
            messagebox.showerror(strings.ERROR_TITLE, strings.ERROR_NO_PDF_SELECTED)
            return
        
        if spreadsheet_profile_name == strings.NO_PROFILES_FOUND:
            messagebox.showerror(strings.ERROR_TITLE, strings.ERROR_NO_SPREADSHEET_PROFILE)
            return
        
        if not self.field_mappings:
            messagebox.showerror(strings.ERROR_TITLE, strings.ERROR_NO_MAPPINGS)
            return

        if not is_editing:
            existing_profiles = data_manager.load_profiles(DocumentProfile)
            if any(p.name == profile_name for p in existing_profiles):
                messagebox.showerror(strings.ERROR_TITLE, strings.ERROR_PROFILE_EXISTS)
                return

        profile = DocumentProfile(
            name=profile_name,
            pdf_path=self.pdf_path,
            spreadsheet_profile_name=self.real_values["to_spreadsheed"],
            title_column=self.real_values["to_title"],
            field_mappings=self.field_mappings,
            page_format=self.page_format,
            page_orientation=self.page_orientation
        )
        data_manager.save_profile(profile)
        
        if is_editing:
            messagebox.showinfo(strings.SUCCESS_TITLE, strings.SUCCESS_PROFILE_UPDATED)
        else:
            messagebox.showinfo(strings.SUCCESS_TITLE, strings.SUCCESS_PROFILE_SAVED)
        
        self.clear_form()
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("document_list")
        
        if hasattr(self.master, 'refresh_data'):
            self.master.refresh_data()
