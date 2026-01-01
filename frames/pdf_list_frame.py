import customtkinter as ctk
from resources.icons import icons
from typing import List
import math
from tkinter import messagebox
from resources.strings import strings
from core.data_manager import data_manager
from utils.explorer_utils import open_file, open_file_directory, open_folder

class PdfListFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.all_pdfs: List[dict] = []
        self.filtered_pdfs: List[dict] = []
        self.current_page = 1
        self.items_per_page = 15
        
        self.search_var = ctk.StringVar()
        self.year_var = ctk.StringVar(value="Todos")
        self.month_var = ctk.StringVar(value="Todos")

        # --- Widgets ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text="PDFs Gerados", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")

        # Search Bar
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.search_frame, text="Ano:").grid(row=0, column=2, padx=(10, 5), pady=10)
        self.year_menu = ctk.CTkOptionMenu(self.search_frame, variable=self.year_var, values=["Todos"], command=lambda _: self._on_filter_change())
        self.year_menu.grid(row=0, column=3, padx=(0, 10), pady=10, sticky="w")

        ctk.CTkLabel(self.search_frame, text="Mês:").grid(row=0, column=4, padx=(10, 5), pady=10)
        self.month_menu = ctk.CTkOptionMenu(self.search_frame, variable=self.month_var, values=["Todos"], command=lambda _: self._on_filter_change())
        self.month_menu.grid(row=0, column=5, padx=(0, 10), pady=10, sticky="w")

        ctk.CTkLabel(self.search_frame, text="Buscar:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Digite o nome do arquivo...")
        self.search_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.search_var.trace_add("write", lambda name, index, mode: self._filter_pdfs())

        # PDF List Display
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Arquivos PDF")
        self.list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Footer Frame (Pagination + Open Dir)
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1) # Centralize pagination

        # Pagination Controls Container
        self.pagination_container = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.pagination_container.grid(row=0, column=0, sticky="w")
        
        # Total Items Label (now part of pagination area)
        self.total_label = ctk.CTkLabel(self.pagination_container, text="Total: 0", font=ctk.CTkFont(weight="bold"))
        self.total_label.pack(side="left", padx=(0, 20))

        # First Page Button
        self.first_button = ctk.CTkButton(self.pagination_container, text=icons.ICON_CHEVRON_LEFT_2, width=32, command=self._first_page)
        self.first_button.pack(side="left", padx=2)
        
        # Prev Button
        self.prev_button = ctk.CTkButton(self.pagination_container, text=icons.ICON_CHEVRON_LEFT_1, width=32, command=self._prev_page)
        self.prev_button.pack(side="left", padx=2)
        
        # Page Selection Menu
        self.page_var = ctk.StringVar(value="1")
        self.page_menu = ctk.CTkOptionMenu(self.pagination_container, variable=self.page_var, values=["1"], width=70, command=self._on_page_select)
        self.page_menu.pack(side="left", padx=10)
        
        self.page_info_label = ctk.CTkLabel(self.pagination_container, text="de 1")
        self.page_info_label.pack(side="left", padx=(0, 10))
        
        # Next Button
        self.next_button = ctk.CTkButton(self.pagination_container, text=icons.ICON_CHEVRON_RIGHT_1, width=32, command=self._next_page)
        self.next_button.pack(side="left", padx=2)

        # Last Page Button
        self.last_button = ctk.CTkButton(self.pagination_container, text=icons.ICON_CHEVRON_RIGHT_2, width=32, command=self._last_page)
        self.last_button.pack(side="left", padx=2)

        # Button to open directory
        self.open_dir_button = ctk.CTkButton(self.footer_frame, text="Abrir Pasta de PDFs", command=self._open_pdf_directory)
        self.open_dir_button.grid(row=0, column=1, sticky="e")
        
        # Ajuste do wrap quando o frame é redimensionado
        self.list_frame.bind("<Configure>", lambda event: self.after(100, lambda: self.update_wrap(event)) if event.width else None)

        self._load_pdfs()

    def _load_pdfs(self):
        years = ["Todos"] + data_manager.get_available_years()
        self.year_menu.configure(values=years)
        
        year = self.year_var.get()
        if year != "Todos":
            months = ["Todos"] + data_manager.get_available_months(year)
            self.month_menu.configure(values=months)
        else:
            self.month_menu.configure(values=["Todos"])
            self.month_var.set("Todos")

        y = None if self.year_var.get() == "Todos" else self.year_var.get()
        m = None if self.month_var.get() == "Todos" else self.month_var.get()
        
        self.all_pdfs = data_manager.get_generated_pdfs_info(year=y, month=m)
        self._filter_pdfs()

    def _on_filter_change(self):
        self.current_page = 1
        self._load_pdfs()

    def _filter_pdfs(self):
        search_term = self.search_var.get().lower()
        if search_term:
            self.filtered_pdfs = [
                pdf for pdf in self.all_pdfs 
                if pdf["name"].lower().find(search_term) != -1
            ]
        else:
            self.filtered_pdfs = self.all_pdfs
        
        self.current_page = 1
        self._update_list_display()

    def _first_page(self):
        if self.current_page != 1:
            self.current_page = 1
            self._update_list_display()

    def _last_page(self):
        total_pages = max(1, math.ceil(len(self.filtered_pdfs) / self.items_per_page))
        if self.current_page != total_pages:
            self.current_page = total_pages
            self._update_list_display()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._update_list_display()

    def _next_page(self):
        total_pages = math.ceil(len(self.filtered_pdfs) / self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_list_display()

    def _on_page_select(self, page_str):
        try:
            page = int(page_str)
            if page != self.current_page:
                self.current_page = page
                self._update_list_display()
        except ValueError:
            pass

    def update_wrap(self, event):
        if event is None:
            wrap = 550
        else:
            wrap = max(event.width - 670, 300)

        if hasattr(self, 'file_labels'):
            for label in self.file_labels:
                label.configure(wraplength=wrap)
            
    def _update_list_display(self):
        # Limpa widgets existentes
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        total_items = len(self.filtered_pdfs)
        self.total_label.configure(text=f"Total: {total_items}")
        
        total_pages = max(1, math.ceil(total_items / self.items_per_page))
        if self.current_page > total_pages:
            self.current_page = total_pages
            
        # Update page selection menu
        page_values = [str(i) for i in range(1, total_pages + 1)]
        self.page_menu.configure(values=page_values)
        self.page_var.set(str(self.current_page))
        self.page_info_label.configure(text=f"de {total_pages}")
        
        # Enable/Disable pagination buttons
        self.first_button.configure(state="normal" if self.current_page > 1 else "disabled")
        self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < total_pages else "disabled")
        self.last_button.configure(state="normal" if self.current_page < total_pages else "disabled")

        if not self.filtered_pdfs:
            ctk.CTkLabel(self.list_frame, text="Nenhum PDF encontrado.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Get items for current page
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = self.filtered_pdfs[start_idx:end_idx]

        # Criamos o container principal diretamente no list_frame
        self.main_container = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="ew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=0)
        self.main_container.grid_columnconfigure(2, weight=0)
        self.main_container.grid_columnconfigure(3, weight=0)
        self.main_container.grid_columnconfigure(4, weight=0)

        # Header Row
        ctk.CTkLabel(self.main_container, text="Nome do Arquivo", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.main_container, text="Ano", font=ctk.CTkFont(weight="bold"), width=60).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.main_container, text="Mês", font=ctk.CTkFont(weight="bold"), width=40).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.main_container, text="Data Criação", font=ctk.CTkFont(weight="bold"), width=120).grid(row=0, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.main_container, text="Ação", font=ctk.CTkFont(weight="bold"), width=60).grid(row=0, column=4, padx=10, pady=5, sticky="w")
        
        self.file_labels: List[ctk.CTkLabel] = []

        # Data Rows
        for i, pdf_info in enumerate(page_items):
            row = i + 1
            pdf_path = pdf_info["path"]
            filename = pdf_info["name"]
            file_year = pdf_info["year"]
            file_month = pdf_info["month"]
            creation_date = pdf_info["creation_date"]

            file_label = ctk.CTkLabel(self.main_container, text=filename, justify="left")
            file_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            self.file_labels.append(file_label)
            
            ctk.CTkLabel(self.main_container, text=file_year, width=60).grid(row=row, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.main_container, text=file_month, width=40).grid(row=row, column=2, padx=10, pady=5)
            ctk.CTkLabel(self.main_container, text=creation_date, width=60).grid(row=row, column=3, padx=10, pady=5)

            btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", width=90)
            btn_frame.grid(row=row, column=4, padx=10, pady=5, sticky="e")
            
            open_file_btn = ctk.CTkButton(
                btn_frame, 
                text=icons.ICON_OPEN_FILE,
                width=28,
                command=lambda p=pdf_path: self._open_file(p),
                fg_color="transparent",
                border_width=2,
                text_color=("black", "white"), 
                font=("Arial", 14)
            )
            open_file_btn.pack(side="left", padx=2)
            
            open_folder_btn = ctk.CTkButton(
                btn_frame, 
                text=icons.ICON_OPEN_FOLDER,
                width=28, 
                command=lambda p=pdf_path: self._open_folder(p), 
                fg_color="transparent",
                border_width=2,
                text_color=("black", "white"), 
                font=("Arial", 14)
            )
            open_folder_btn.pack(side="left", padx=2)

            delete_file_btn = ctk.CTkButton(
                btn_frame, 
                text=f"{icons.ICON_DELETE}",
                width=31, 
                command=lambda p=pdf_path: self._delete_file(p), 
                fg_color="transparent",
                border_width=2,
                text_color=("black", "white"), 
                font=("Arial", 9)
            )
            delete_file_btn.pack(side="left", padx=2)

        self.list_frame.update_idletasks()
        self.list_frame._parent_canvas.configure(scrollregion=self.list_frame._parent_canvas.bbox("all"))
        # Scroll to top when page changes
        self.list_frame._parent_canvas.yview_moveto(0)

    def _open_file(self, file_path: str):
       open_file(file_path)
    
    def _open_folder(self, path: str):
        open_folder(path)

    def _delete_file(self, pdf_path: str):
        if messagebox.askyesno(strings.CONFIRM_TITLE, strings.CONFIRM_DELETE_PDF):
            if data_manager.delete_generated_pdf(pdf_path):
                messagebox.showinfo(strings.SUCCESS_TITLE, "Arquivo excluído com sucesso.")
                self._load_pdfs()
            else:
                messagebox.showerror(strings.ERROR_TITLE, "Não foi possível excluir o arquivo.")

    def _open_pdf_directory(self):
       pdf_dir = data_manager.pdf_base_dir
       open_file_directory(pdf_dir)

    def refresh_data(self):
        self._load_pdfs()
