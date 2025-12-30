# -*- coding: utf-8 -*-
from .data_manager import data_manager, DataManager
from .pdf_generator import generate_pdf_with_template, batch_generate_pdfs

__all__ = ['data_manager', 'DataManager', 'generate_pdf_with_template', 'batch_generate_pdfs']
