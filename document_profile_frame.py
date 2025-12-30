import customtkinter as ctk
from tkinter import messagebox
import os
from typing import List, Optional
from models import DocumentProfile, SpreadsheetProfile, PdfFieldMapping
from data_manager import data_manager
from utils import select_file, render_pdf_to_image, get_pdf_page_count, A4_WIDTH_MM, A4_HEIGHT_MM
from PIL import Image, ImageTk
import threading

class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Processando...", message="Por favor, aguarde..."):
        super().__init__(master)
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
        pass # Do nothing to prevent closing

class DocumentProfileFrame(ctk.CTkFrame):
    left_column_width = 350

    def _set_text_wrap(self, text: str, max_len=30):
        if len(text) > max_len:
            text = text[:max_len-3] + "..."
        return text

    def _set_pdf_button_text(self, path: str):
        name = os.path.basename(path)
        name = self._set_text_wrap(name, 24)
        self.select_pdf_button.configure(text=f"PDF Selecionado: {name}")

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Configuração do grid principal
        self.grid_columnconfigure(0, weight=0) # Coluna esquerda fixa
        self.grid_columnconfigure(1, weight=1) # Coluna direita expande
        self.grid_rowconfigure(1, weight=1)

        self.pdf_path: Optional[str] = None
        self.pdf_image: Optional[Image.Image] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None
        self.image_width_mm: float = A4_WIDTH_MM
        self.image_height_mm: float = A4_HEIGHT_MM
        self.current_page_index = 0
        self.total_pages = 0
        
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
        ctk.CTkLabel(self, text="Gerenciamento de Perfis de Documento", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

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

        self.select_pdf_button = ctk.CTkButton(self.top_frame, text="Selecionar Template PDF", command=self._select_pdf)
        self.select_pdf_button.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="we")

        self.profile_name_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Nome do Perfil de Documento", textvariable=self.document_profile_name_var)
        self.profile_name_entry.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="we")

        # Spreadsheet Profile Selection
        self.profile_select_frame = ctk.CTkFrame(self.wrapper)
        self.profile_select_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.profile_select_frame.grid_columnconfigure(0, weight=1)
        
        self.spreadsheet_profile_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                         variable=self.label_values["to_spreadsheed"],
                                                         values=["Selecione um Perfil de Planilha"],
                                                         command=self._on_profile_select)
        self.spreadsheet_profile_menu.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        ctk.CTkLabel(self.profile_select_frame, text="Coluna para Título do PDF:").grid(row=2, column=0, padx=10, pady=0, sticky="w")
        self.title_column_menu = ctk.CTkOptionMenu(self.profile_select_frame, 
                                                   variable=self.label_values["to_title"],
                                                   values=["Selecione a Coluna"],
                                                   command=self._on_select_to_title)
        self.title_column_menu.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Mapping Input
        self.mapping_input_frame = ctk.CTkFrame(self.wrapper)
        self.mapping_input_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.mapping_input_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.mapping_input_frame, text="1. Selecione a Coluna:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.column_menu = ctk.CTkOptionMenu(self.mapping_input_frame,
                                             variable=self.label_values["to_map"],
                                             values=["Selecione a Coluna"],
                                             command=self._on_select_to_map)
        self.column_menu.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        ctk.CTkLabel(self.mapping_input_frame, text="2. Clique no PDF ao lado para mapear.", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Mapping Display Area
        self.mapping_display_frame = ctk.CTkScrollableFrame(self.wrapper, label_text="Mapeamentos Atuais")
        self.mapping_display_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.mapping_display_frame.grid_columnconfigure(0, weight=1)

        # Save Button
        self.save_button_frame = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        self.save_button_frame.grid(row=5, column=0, padx=0, pady=0, sticky="ew")
        self.save_button_frame.grid_columnconfigure(0, weight=1)
        self.save_button = ctk.CTkButton(self.save_button_frame, text="Salvar Perfil de Documento", command=self._save_profile)
        self.save_button.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="ew")

        # --- Coluna Direita (PDF Viewer) ---
        self.pdf_viewer_container = ctk.CTkFrame(self, fg_color="transparent")
        self.pdf_viewer_container.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.pdf_viewer_container.grid_columnconfigure(0, weight=1)
        self.pdf_viewer_container.grid_rowconfigure(1, weight=1)

        # Controles de Página
        self.page_controls = ctk.CTkFrame(self.pdf_viewer_container, fg_color="transparent")
        self.page_controls.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        
        self.prev_page_button = ctk.CTkButton(self.page_controls, text="Anterior", width=80, command=self._prev_page, state="disabled")
        self.prev_page_button.pack(side="left", padx=10)
        
        self.page_label = ctk.CTkLabel(self.page_controls, text="Página: 0 / 0")
        self.page_label.pack(side="left", expand=True)
        
        self.next_page_button = ctk.CTkButton(self.page_controls, text="Próxima", width=80, command=self._next_page, state="disabled")
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

        self.pdf_canvas_label = ctk.CTkLabel(self.pdf_canvas, text="Selecione um PDF para visualizar o template.")
        self.pdf_canvas_label.place(relx=0.5, rely=0.5, anchor="center")

        self._load_profiles()
        self._update_mapping_display()

    def _prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._render_pdf_image()

    def _next_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self._render_pdf_image()

    def _update_page_controls(self):
        self.page_label.configure(text=f"Página: {self.current_page_index + 1} / {self.total_pages}")
        self.prev_page_button.configure(state="normal" if self.current_page_index > 0 else "disabled")
        self.next_page_button.configure(state="normal" if self.current_page_index < self.total_pages - 1 else "disabled")

    def load_profile_for_editing(self, profile: DocumentProfile):
        self.document_profile_name_var.set(profile.name)
        self.pdf_path = profile.pdf_path
        self.field_mappings = profile.field_mappings
        self._on_select_to_spreadsheed(profile.spreadsheet_profile_name)
        self._on_select_to_title(profile.title_column)
        
        self.profile_name_entry.configure(state="disabled")
        self._set_pdf_button_text(self.pdf_path)
        self.save_button.configure(text="Salvar Alterações", command=lambda: self._save_profile(is_editing=True))
        
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
        self.profile_name_entry.configure(state="normal")
        self.select_pdf_button.configure(state="normal", text="Selecionar Template PDF")
        self.save_button.configure(text="Salvar Perfil de Documento", command=self._save_profile)
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
            profile_names = ["Nenhum Perfil de Planilha Encontrado"]
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
            self._on_select_to_map(column_names[0] if column_names else "Selecione a Coluna")
            self._on_select_to_title(column_names[0] if column_names else "Selecione a Coluna")
        else:
            self.title_column_menu.configure(values=["Selecione a Coluna"])
            self.column_menu.configure(values=["Selecione a Coluna"])
            self._on_select_to_map("Selecione a Coluna")
            self._on_select_to_title("Selecione a Coluna")

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
        pdf_path = select_file([("Arquivos PDF", "*.pdf")])
        if pdf_path:
            self.pdf_path = pdf_path
            self.total_pages = get_pdf_page_count(pdf_path)
            self.current_page_index = 0
            self.document_profile_name_var.set(os.path.basename(pdf_path).split('.')[0] + "_DocProfile")
            self.select_pdf_button.configure(text=f"PDF Selecionado: {os.path.basename(pdf_path)}")
            self._render_pdf_image()

    def _handle_render_pdf_result(self, progress_dialog):
        if progress_dialog.winfo_exists():
            try: progress_dialog.grab_release()
            except: pass
            progress_dialog.withdraw()
            progress_dialog.after(200, lambda: progress_dialog.destroy())
        
        if self.pdf_image:
            self.image_width_mm = A4_WIDTH_MM
            self.image_height_mm = A4_HEIGHT_MM
            self.pdf_canvas_label.place_forget()
            self._update_page_controls()
            self._on_canvas_resize()
            return True
        else:
            messagebox.showerror("Erro de Renderização", "Não foi possível renderizar o PDF.")
            self.pdf_canvas_label.place(relx=0.5, rely=0.5, anchor="center")
            return False

    def _render_pdf_to_image_thread(self, pdf_path, page_index, progress_dialog):
        self.pdf_image = render_pdf_to_image(pdf_path, page_index, dpi=150)
        self.after(50, lambda: self._handle_render_pdf_result(progress_dialog))

    def _render_pdf_image(self):
        if not self.pdf_path: return False
        progress_dialog = ProgressDialog(self, title="Carregando PDF...", message=f"Renderizando página {self.current_page_index + 1}...")
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
        if column_name == "Selecione a Coluna":
            messagebox.showerror("Erro", "Selecione uma coluna para mapear.")
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
        if column_name == "Selecione a Coluna": return

        try:
            x = float(self.x_coord_var.get())
            y = float(self.y_coord_var.get())
        except ValueError: return

        # Remove mapeamento existente da mesma coluna (independente da página)
        self.field_mappings = [m for m in self.field_mappings if m.column_name != column_name]
        
        # Adiciona o novo mapeamento com o índice da página atual
        self.field_mappings.append(PdfFieldMapping(column_name=column_name, x=x, y=y, page_index=self.current_page_index))
            
        self._update_mapping_display()
        self._on_canvas_resize()

    def _update_mapping_display(self):
        for widget in self.mapping_display_frame.winfo_children():
            widget.destroy()

        if not self.field_mappings:
            ctk.CTkLabel(self.mapping_display_frame, text="Nenhum mapeamento adicionado.").grid(row=0, column=0, padx=20, pady=20)
            return

        ctk.CTkLabel(self.mapping_display_frame, text="Coluna", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="Pág.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.mapping_display_frame, text="Ação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        for i, mapping in enumerate(sorted(self.field_mappings, key=lambda x: (getattr(x, 'page_index', 0), x.column_name))):
            row = i + 1
            pg = getattr(mapping, 'page_index', 0) + 1
            col_name = self._set_text_wrap(mapping.column_name, max_len=20)
            
            ctk.CTkLabel(self.mapping_display_frame, text=col_name).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.mapping_display_frame, text=str(pg)).grid(row=row, column=1, padx=5, pady=2, sticky="w")
            
            btn_frame = ctk.CTkFrame(self.mapping_display_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=2, padx=5, pady=2)
            
            # Botão para ir até a página do mapeamento
            go_btn = ctk.CTkButton(btn_frame, text="Ver", width=40, command=lambda p=pg-1: self._go_to_page(p))
            go_btn.pack(side="left", padx=2)
            
            del_btn = ctk.CTkButton(btn_frame, text="X", width=30, fg_color="red", hover_color="darkred", command=lambda m=mapping: self._remove_mapping(m))
            del_btn.pack(side="left", padx=2)

    def _go_to_page(self, page_index):
        self.current_page_index = page_index
        self._render_pdf_image()

    def _remove_mapping(self, mapping: PdfFieldMapping):
        self.field_mappings.remove(mapping)
        self._update_mapping_display()
        self._on_canvas_resize()

    def _save_profile(self, is_editing=False):
        profile_name = self.document_profile_name_var.get().strip()
        spreadsheet_profile_name = self.real_values["to_spreadsheed"]

        if not profile_name or not self.pdf_path or spreadsheet_profile_name == "Nenhum Perfil de Planilha Encontrado" or not self.field_mappings:
            messagebox.showerror("Erro", "Preencha todos os campos e adicione pelo menos um mapeamento.")
            return

        if not is_editing:
            existing_profiles = data_manager.load_profiles(DocumentProfile)
            if any(p.name == profile_name for p in existing_profiles):
                messagebox.showerror("Erro", f"Já existe um perfil de documento com o nome '{profile_name}'.")
                return

        profile = DocumentProfile(
            name=profile_name,
            pdf_path=self.pdf_path,
            spreadsheet_profile_name=self.real_values["to_spreadsheed"],
            title_column=self.real_values["to_title"],
            field_mappings=self.field_mappings
        )
        data_manager.save_profile(profile)
        messagebox.showinfo("Sucesso", f"Perfil de documento '{profile_name}' salvo com sucesso!")
        
        self.clear_form()
        if hasattr(self.master, 'select_frame_by_name'):
            self.master.select_frame_by_name("document_list")
        
        if hasattr(self.master, 'refresh_data'):
            self.master.refresh_data()
