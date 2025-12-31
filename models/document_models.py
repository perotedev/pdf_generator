# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Literal, Optional

ColumnType = Literal["texto", "numero", "monetario", "data", "data e hora", "cpf", "cnpj", "telefone", "email"]
PageFormat = Literal["A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal"]
PageOrientation = Literal["portrait", "landscape"]

@dataclass
class TextStyle:
    """Estilo de texto para campos mapeados"""
    font_family: str = "Arial"
    font_size: int = 12
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str = "#000000"  # Cor em formato hexadecimal
    
    def to_dict(self):
        return {
            'font_family': self.font_family,
            'font_size': self.font_size,
            'bold': self.bold,
            'italic': self.italic,
            'underline': self.underline,
            'color': self.color
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return cls()
        return cls(
            font_family=data.get('font_family', 'Helvetica'),
            font_size=data.get('font_size', 10),
            bold=data.get('bold', False),
            italic=data.get('italic', False),
            underline=data.get('underline', False),
            color=data.get('color', '#000000')
        )

@dataclass
class ColumnMapping:
    original_header: str
    custom_name: str
    column_type: ColumnType = "texto"
    index: int = 0

@dataclass
class SpreadsheetProfile:
    name: str
    header_row: int = 1
    columns: List[ColumnMapping] = field(default_factory=list)

@dataclass
class PdfFieldMapping:
    column_name: str
    x: float  # in mm
    y: float  # in mm
    page_index: int = 0  # 0-indexed page number
    style: Optional[TextStyle] = None  # Estilo do texto
    
    def to_dict(self):
        return {
            'column_name': self.column_name,
            'x': self.x,
            'y': self.y,
            'page_index': self.page_index,
            'style': self.style.to_dict() if self.style else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        style_data = data.get('style')
        style = TextStyle.from_dict(style_data) if style_data else TextStyle()
        return cls(
            column_name=data['column_name'],
            x=data['x'],
            y=data['y'],
            page_index=data.get('page_index', 0),
            style=style
        )

@dataclass
class DocumentProfile:
    name: str
    pdf_path: str
    spreadsheet_profile_name: str
    title_column: str = ""
    field_mappings: List[PdfFieldMapping] = field(default_factory=list)
    page_format: PageFormat = "A4"  # Formato da página
    page_orientation: PageOrientation = "portrait"  # Orientação da página
    
    def to_dict(self):
        return {
            'name': self.name,
            'pdf_path': self.pdf_path,
            'spreadsheet_profile_name': self.spreadsheet_profile_name,
            'title_column': self.title_column,
            'field_mappings': [m.to_dict() for m in self.field_mappings],
            'page_format': self.page_format,
            'page_orientation': self.page_orientation
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        # Suporte para perfis antigos sem os novos campos
        mappings_data = data.get('field_mappings', [])
        mappings = []
        for m in mappings_data:
            if isinstance(m, dict):
                mappings.append(PdfFieldMapping.from_dict(m))
            else:
                # Compatibilidade com formato antigo
                mappings.append(PdfFieldMapping(
                    column_name=m.column_name,
                    x=m.x,
                    y=m.y,
                    page_index=getattr(m, 'page_index', 0),
                    style=TextStyle()  # Estilo padrão
                ))
        
        return cls(
            name=data['name'],
            pdf_path=data['pdf_path'],
            spreadsheet_profile_name=data['spreadsheet_profile_name'],
            title_column=data.get('title_column', ''),
            field_mappings=mappings,
            page_format=data.get('page_format', 'A4'),
            page_orientation=data.get('page_orientation', 'portrait')
        )

@dataclass
class LicenseInfo:
    code: str
    valid: bool
    expire_date: int  # Unix timestamp
    device_id: str
    company: str = ""
    last_verification: int = 0  # Unix timestamp
