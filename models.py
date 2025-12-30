from dataclasses import dataclass, field
from typing import List, Literal

ColumnType = Literal["texto", "numero", "monetario", "data", "data e hora", "cpf", "cnpj", "telefone", "email"]

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

@dataclass
class DocumentProfile:
    name: str
    pdf_path: str
    spreadsheet_profile_name: str
    title_column: str = ""
    field_mappings: List[PdfFieldMapping] = field(default_factory=list)

@dataclass
class LicenseInfo:
    code: str
    valid: bool
    expire_date: int  # Unix timestamp
    device_id: str
    company: str = ""
    last_verification: int # Unix timestamp

