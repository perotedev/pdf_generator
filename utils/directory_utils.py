# -*- coding: utf-8 -*-
import os
from typing import List, Dict, Any
from datetime import datetime

def get_pdf_files_info(base_dir: str, year: str = None, month: str = None) -> List[Dict[str, Any]]:
    """
    Obtém informações dos arquivos PDF de forma otimizada.
    """
    pdf_info_list = []
    
    if year and month:
        target_dirs = [os.path.join(base_dir, year, month)]
    elif year:
        year_dir = os.path.join(base_dir, year)
        if os.path.exists(year_dir):
            target_dirs = [os.path.join(year_dir, m) for m in os.listdir(year_dir) if os.path.isdir(os.path.join(year_dir, m))]
        else:
            target_dirs = []
    else:
        target_dirs = []
        if os.path.exists(base_dir):
            for y in os.listdir(base_dir):
                y_path = os.path.join(base_dir, y)
                if os.path.isdir(y_path) and y.isdigit():
                    for m in os.listdir(y_path):
                        m_path = os.path.join(y_path, m)
                        if os.path.isdir(m_path) and m.isdigit():
                            target_dirs.append(m_path)

    for d in target_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".pdf"):
                    file_path = os.path.join(d, f)
                    try:
                        stats = os.stat(file_path)
                        path_parts = os.path.normpath(file_path).split(os.sep)
                        pdf_info_list.append({
                            "path": file_path,
                            "name": f,
                            "year": path_parts[-3] if len(path_parts) >= 3 else "-",
                            "month": path_parts[-2] if len(path_parts) >= 2 else "-",
                            "ctime": stats.st_ctime,
                            "creation_date": datetime.fromtimestamp(stats.st_ctime).strftime("%d/%m/%y %H:%M")
                        })
                    except Exception:
                        continue
    
    # Ordenar por data de criação (mais recente primeiro)
    pdf_info_list.sort(key=lambda x: x["ctime"], reverse=True)
    return pdf_info_list
