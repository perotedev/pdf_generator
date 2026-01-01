# -*- coding: utf-8 -*-
import os
from typing import List, Dict, Any
from datetime import datetime

def get_pdf_files_info(base_dir: str, year: str = None, month: str = None) -> List[Dict[str, Any]]:
    """
    Obtém informações dos arquivos PDF de forma otimizada usando os.scandir.
    """
    pdf_info_list = []
    
    # Determina os diretórios de busca de forma eficiente
    search_dirs = []
    try:
        if year and month:
            path = os.path.join(base_dir, year, month)
            if os.path.isdir(path):
                search_dirs.append((path, year, month))
        elif year:
            year_path = os.path.join(base_dir, year)
            if os.path.isdir(year_path):
                with os.scandir(year_path) as it:
                    for entry in it:
                        if entry.is_dir() and entry.name.isdigit():
                            search_dirs.append((entry.path, year, entry.name))
        else:
            if os.path.isdir(base_dir):
                with os.scandir(base_dir) as it_y:
                    for entry_y in it_y:
                        if entry_y.is_dir() and entry_y.name.isdigit():
                            with os.scandir(entry_y.path) as it_m:
                                for entry_m in it_m:
                                    if entry_m.is_dir() and entry_m.name.isdigit():
                                        search_dirs.append((entry_m.path, entry_y.name, entry_m.name))
    except OSError:
        return []

    # Coleta informações dos arquivos
    for dir_path, y, m in search_dirs:
        try:
            with os.scandir(dir_path) as it:
                for entry in it:
                    if entry.is_file() and entry.name.lower().endswith(".pdf"):
                        try:
                            stats = entry.stat()
                            ctime = stats.st_ctime
                            pdf_info_list.append({
                                "path": entry.path,
                                "name": entry.name,
                                "year": y,
                                "month": m,
                                "ctime": ctime,
                                "creation_date": datetime.fromtimestamp(ctime).strftime("%d/%m/%y %H:%M")
                            })
                        except OSError:
                            continue
        except OSError:
            continue
    
    # Ordenar por data de criação (mais recente primeiro)
    pdf_info_list.sort(key=lambda x: x["ctime"], reverse=True)
    return pdf_info_list
