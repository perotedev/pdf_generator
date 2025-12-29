import customtkinter as ctk
from tkinter import messagebox
import os
from typing import List, Optional

from models import DocumentProfile, SpreadsheetProfile, PdfFieldMapping
from data_manager import data_manager
from utils import select_file, render_pdf_to_image, A4_WIDTH_MM, A4_HEIGHT_MM
from PIL import Image, ImageDraw, ImageTk

class DocumentProfileFrame(ctk.CTkFrame):
    def _set_pdf_button_text(self, path: str):
        name = os.path.basename(path)

        max_len = 30  # ajuste o limite
        if len(name) > max_len:
            name = name[:max_len-3] + "..."

        self.select_pdf_button.configure(text=f"PDF Selecionado: {name}")

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1) # Adicionar coluna para o visualizador de PDF

        self.pdf_path: Optional[str] = None
        self.pdf_image: Optional[Image.Image] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None
        self.image_width_mm: float = A4_WIDTH_MM
        self.image_height_mm: float = A4_HEIGHT_MM
        self.document_profile_name_var = ctk.StringVar()
        self.spreadsheet_profile_name_var = ctk.StringVar()
        self.available_spreadsheet_profiles: List[SpreadsheetProfile] = []
        self.field_mappings: List[PdfFieldMapping] = []
        
        self.selected_column_to_map_var = ctk.StringVar()
        self.title_column_var = ctk.StringVar()
        self.x_coord_var = ctk.StringVar(value="0.0")
        self.y_coord_var = ctk.StringVar(value="0.0")

        # --- Widgets ---
        ctk.CTkLabel(self, text="Gerenciamento de Perfis de Documento", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Top Frame for selection and name
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1, uniform="top")
        self.top_frame.grid_columnconfigure(1, weight=1, uniform="top")

        self.select_pdf_button = ctk.CTkButton(self.top_frame, text="Selecionar Template PDF", command=self._select_pdf)
        self.select_pdf_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.profile_name_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Nome do Perfil de Documento", textvariable=self.document_profile_name_var)
        self.profile_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Spreadsheet Profile Selection
        self.profile_select_frame = ctk.CTkFrame(self)
        self.profile_select_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.profile_select_frame.grid_columnconfigure(0, weight=1)
        
        self.spreadsheet_profile_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                         variable=self.spreadsheet_profile_name_var,
                                                         values=["Selecione um Perfil de Planilha"],
                                                         command=self._on_profile_select)
        self.spreadsheet_profile_menu.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.profile_select_frame, text="Coluna para Título do PDF:").grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        self.title_column_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                   variable=self.title_column_var,
                                                   values=["Selecione a Coluna"])
        self.title_column_menu.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Mapping Input
        self.mapping_input_frame = ctk.CTkFrame(self)
        self.mapping_input_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.mapping_input_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.mapping_input_frame, text="1. Selecione a Coluna:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.column_menu = ctk.CTkOptionMenu(self.mapping_input_frame, 
                                             variable=self.selected_column_to_map_var,
                                             values=["Selecione a Coluna"],
                                             width=200)
        self.column_menu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.mapping_input_frame, text="2. Clique no PDF ao lado para mapear a posição.", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")
        
        # Display X and Y for confirmation (optional, but good for debugging/confirmation)
        ctk.CTkLabel(self.mapping_input_frame, text="X (mm):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_input_frame, textvariable=self.x_coord_var).grid(row=3, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_input_frame, text="Y (mm):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_input_frame, textvariable=self.y_coord_var).grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Mapping Display Area
        self.mapping_display_frame = ctk.CTkScrollableFrame(self, label_text="Mapeamentos Atuais")
        self.mapping_display_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.mapping_display_frame.grid_columnconfigure(0, weight=1)

        # Save Button
        self.save_button = ctk.CTkButton(self, text="Salvar Perfil de Documento", command=self._save_profile)
        self.save_button.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="e")

        # PDF Viewer Frame
        self.pdf_viewer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pdf_viewer_frame.grid(row=1, column=1, rowspan=5, padx=20, pady=20, sticky="nsew")
        self.pdf_viewer_frame.grid_columnconfigure(0, weight=1)
        self.pdf_viewer_frame.grid_rowconfigure(0, weight=1)

        self.pdf_canvas = ctk.CTkCanvas(self.pdf_viewer_frame, bg="white", highlightthickness=0)
        self.pdf_canvas.grid(row=0, column=0, sticky="nsew")
        self.pdf_canvas.bind("<Button-1>", self._on_pdf_click)
        self.pdf_canvas.bind("<Configure>", self._on_canvas_resize)

        self.pdf_canvas_label = ctk.CTkLabel(self.pdf_viewer_frame, text="Selecione um PDF para visualizar o template.")
        self.pdf_canvas_label.grid(row=0, column=0, sticky="nsew")

        self._load_profiles()
        self._update_mapping_display()

    def load_profile_for_editing(self, profile: DocumentProfile):
        self.document_profile_name_var.set(profile.name)
        self.pdf_path = profile.pdf_path
        self.field_mappings = profile.field_mappings
        self.spreadsheet_profile_name_var.set(profile.spreadsheet_profile_name)
        self.title_column_var.set(profile.title_column)
        
        self.profile_name_entry.configure(state="disabled") # Prevent name change during edit
        self._set_pdf_button_text(self.pdf_path)
        self.save_button.configure(text="Salvar Alterações", command=lambda: self._save_profile(is_editing=True))
        self._render_pdf_image() # Render the PDF for visual editing
        self._on_profile_select(profile.spreadsheet_profile_name) # Load columns for menus
        self.title_column_var.set(profile.title_column) # Restore title column after menu load
        self._update_mapping_display()

    def clear_form(self):
        self.pdf_path = None
        self.document_profile_name_var.set("")
        self.field_mappings = []
        self.profile_name_entry.configure(state="normal")
        self.select_pdf_button.configure(state="normal", text="Selecionar Template PDF")
        self.save_button.configure(text="Salvar Perfil de Documento", command=self._save_profile)
        self.pdf_image = None
        self.tk_image = None
        self.pdf_canvas.delete("all")
        self.pdf_canvas_label.grid(row=0, column=0, sticky="nsew")
        self._load_profiles() # Reload profiles to ensure the dropdown is up-to-date
        self._update_mapping_display()

    def _load_profiles(self):
        self.available_spreadsheet_profiles = data_manager.load_profiles(SpreadsheetProfile)
        profile_names = [p.name for p in self.available_spreadsheet_profiles]
        if not profile_names:
            profile_names = ["Nenhum Perfil de Planilha Encontrado"]
            self.spreadsheet_profile_name_var.set(profile_names[0])
            self.spreadsheet_profile_menu.configure(state="disabled")
        else:
            self.spreadsheet_profile_menu.configure(values=profile_names, state="normal")
            self.spreadsheet_profile_name_var.set(profile_names[0])
            self._on_profile_select(profile_names[0])

    def _on_profile_select(self, profile_name: str):
        selected_profile = next((p for p in self.available_spreadsheet_profiles if p.name == profile_name), None)
        if selected_profile:
            column_names = [c.custom_name for c in selected_profile.columns]
            self.column_menu.configure(values=column_names)
            self.selected_column_to_map_var.set(column_names[0] if column_names else "Selecione a Coluna")
            self.title_column_menu.configure(values=column_names)
            self.title_column_var.set(column_names[0] if column_names else "Selecione a Coluna")
        else:
            self.column_menu.configure(values=["Selecione a Coluna"])
            self.selected_column_to_map_var.set("Selecione a Coluna")
            self.title_column_menu.configure(values=["Selecione a Coluna"])
            self.title_column_var.set("Selecione a Coluna")
        
        # Do NOT clear existing mappings here, as it might be an edit operation.
        # The clear is handled by clear_form or load_profile_for_editing.
        # self.field_mappings = []
        self._update_mapping_display()

    def _select_pdf(self):
        pdf_path = select_file([("Arquivos PDF", "*.pdf")])
        if pdf_path:
            self.pdf_path = pdf_path
            self.document_profile_name_var.set(os.path.basename(pdf_path).split('.')[0] + "_DocProfile")
            self.select_pdf_button.configure(text=f"PDF Selecionado: {os.path.basename(pdf_path)}")
            self._render_pdf_image()

    def _render_pdf_image(self):
        if not self.pdf_path:
            return

        # Renderiza o PDF para uma imagem PIL
        self.pdf_image = render_pdf_to_image(self.pdf_path)
        
        if self.pdf_image:
            # Assume que o PDF tem o tamanho A4 (210x297mm)
            self.image_width_mm = A4_WIDTH_MM
            self.image_height_mm = A4_HEIGHT_MM
            self.pdf_canvas_label.grid_forget()
            self._on_canvas_resize()
        else:
            messagebox.showerror("Erro de Renderização", "Não foi possível renderizar o PDF. Verifique o arquivo.")
            self.pdf_canvas_label.grid(row=0, column=0, sticky="nsew")

    def _on_canvas_resize(self, event=None):
        if not self.pdf_image:
            return

        # Calcula a proporção para caber no canvas
        canvas_width = self.pdf_canvas.winfo_width()
        canvas_height = self.pdf_canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        img_width, img_height = self.pdf_image.size
        
        # Mantém a proporção
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        # Redimensiona a imagem
        resized_image = self.pdf_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)

        # Centraliza a imagem no canvas
        x_center = (canvas_width - new_width) // 2
        y_center = (canvas_height - new_height) // 2

        # Limpa o canvas e desenha a imagem
        self.pdf_canvas.delete("all")
        self.pdf_canvas.create_image(x_center, y_center, anchor="nw", image=self.tk_image)
        
        # Desenha os marcadores de mapeamento
        self._draw_mappings(new_width, new_height, x_center, y_center)

    def _draw_mappings(self, img_width, img_height, x_offset, y_offset):
        if not self.pdf_image:
            return

        # Fatores de conversão de mm para pixel na imagem redimensionada
        scale_x = img_width / self.image_width_mm
        scale_y = img_height / self.image_height_mm

        for mapping in self.field_mappings:
            # Converte mm (topo-esquerda) para pixel (topo-esquerda da imagem)
            x_mm = mapping.x
            y_mm = mapping.y
            
            x_pixel = int(x_mm * scale_x) + x_offset
            y_pixel = int(y_mm * scale_y) + y_offset

            # Desenha um círculo (marcador)
            radius = 5
            self.pdf_canvas.create_oval(
                x_pixel - radius, y_pixel - radius,
                x_pixel + radius, y_pixel + radius,
                fill="red", outline="white", tags="mapping_marker"
            )
            # Desenha o nome da coluna
            self.pdf_canvas.create_text(
                x_pixel + radius + 2, y_pixel,
                anchor="w", text=mapping.column_name, fill="red", tags="mapping_text"
            )

    def _on_pdf_click(self, event):
        if not self.pdf_image or not self.tk_image:
            return

        column_name = self.selected_column_to_map_var.get()
        if column_name == "Selecione a Coluna":
            messagebox.showerror("Erro", "Selecione uma coluna para mapear antes de clicar no PDF.")
            return

        # 1. Obter as dimensões da imagem redimensionada e o offset
        canvas_width = self.pdf_canvas.winfo_width()
        canvas_height = self.pdf_canvas.winfo_height()
        img_width, img_height = self.pdf_image.size
        
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2

        # 2. Verificar se o clique está dentro da imagem
        if not (x_offset <= event.x <= x_offset + new_width and
                y_offset <= event.y <= y_offset + new_height):
            return # Clique fora da imagem

        # 3. Converter coordenadas do canvas (pixel) para coordenadas da imagem (pixel)
        x_img_pixel = event.x - x_offset
        y_img_pixel = event.y - y_offset

        # 4. Converter coordenadas da imagem (pixel) para coordenadas em mm (topo-esquerda)
        scale_x = self.image_width_mm / new_width
        scale_y = self.image_height_mm / new_height

        x_mm = x_img_pixel * scale_x
        y_mm = y_img_pixel * scale_y

        # 5. Atualizar os campos X e Y
        self.x_coord_var.set(f"{x_mm:.1f}")
        self.y_coord_var.set(f"{y_mm:.1f}")

        # 6. Adicionar o mapeamento automaticamente
        self._add_mapping()

    def _add_mapping(self):
        column_name = self.selected_column_to_map_var.get()
        
        if column_name == "Selecione a Coluna":
            # This should be caught by _on_pdf_click, but as a safeguard
            messagebox.showerror("Erro", "Selecione uma coluna para mapear.")
            return

        try:
            x = float(self.x_coord_var.get())
            y = float(self.y_coord_var.get())
        except ValueError:
            # This should not happen if _on_pdf_click is called first
            messagebox.showerror("Erro", "As coordenadas X e Y não foram definidas corretamente.")
            return

        # Check if mapping already exists and update it instead of adding a new one
        existing_mapping = next((m for m in self.field_mappings if m.column_name == column_name), None)

        if existing_mapping:
            existing_mapping.x = x
            existing_mapping.y = y
        else:
            self.field_mappings.append(PdfFieldMapping(column_name=column_name, x=x, y=y))
            
        self._update_mapping_display()
        self._on_canvas_resize() # Redraw markers

    def _update_mapping_display(self):
        # Clear existing widgets
        for widget in self.mapping_display_frame.winfo_children():
            widget.destroy()

        if not self.field_mappings:
            ctk.CTkLabel(self.mapping_display_frame, text="Nenhum mapeamento adicionado.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Header Row
        ctk.CTkLabel(self.mapping_display_frame, text="Coluna", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="X (mm)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="Y (mm)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="Ação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Data Rows
        for i, mapping in enumerate(self.field_mappings):
            row = i + 1
            
            ctk.CTkLabel(self.mapping_display_frame, text=mapping.column_name).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.mapping_display_frame, text=f"{mapping.x:.1f}").grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.mapping_display_frame, text=f"{mapping.y:.1f}").grid(row=row, column=2, padx=10, pady=5, sticky="w")

            delete_button = ctk.CTkButton(self.mapping_display_frame, text="Remover", width=80, command=lambda m=mapping: self._remove_mapping(m))
            delete_button.grid(row=row, column=3, padx=10, pady=5, sticky="w")

    def _remove_mapping(self, mapping: PdfFieldMapping):
        self.field_mappings.remove(mapping)
        self._update_mapping_display()
        self._on_canvas_resize()

    def _save_profile(self, is_editing=False):
        profile_name = self.document_profile_name_var.get().strip()
        spreadsheet_profile_name = self.spreadsheet_profile_name_var.get()

        if not profile_name or not self.pdf_path or spreadsheet_profile_name == "Nenhum Perfil de Planilha Encontrado" or not self.field_mappings:
            messagebox.showerror("Erro", "Preencha todos os campos e adicione pelo menos um mapeamento.")
            return

        # Check for duplicate name only if not editing
        if not is_editing:
            existing_profiles = data_manager.load_profiles(DocumentProfile)
            if any(p.name == profile_name for p in existing_profiles):
                messagebox.showerror("Erro", f"Já existe um perfil de documento com o nome '{profile_name}'.")
                return

        profile = DocumentProfile(
            name=profile_name,
            pdf_path=self.pdf_path,
            spreadsheet_profile_name=self.spreadsheet_profile_name_var.get(),
            title_column=self.title_column_var.get(),
            field_mappings=self.field_mappings
        )
        data_manager.save_profile(profile)
        messagebox.showinfo("Sucesso", f"Perfil de documento '{profile_name}' salvo com sucesso!")
        
        # Clear the form and return to the list view
        self.clear_form()
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("document_list")
        
        # Notify main app to refresh lists if necessary
        if hasattr(self.master, 'refresh_data'):
            self.master.refresh_data()

