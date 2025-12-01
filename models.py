from dataclasses import dataclass, field
from typing import List, Literal

ColumnType = Literal["texto", "numero", "monetario", "data"]

@dataclass
class ColumnMapping:
    original_header: str
    custom_name: str
    column_type: ColumnType = "texto"
    index: int = 0

@dataclass
class SpreadsheetProfile:
    name: str
    columns: List[ColumnMapping] = field(default_factory=list)

@dataclass
class PdfFieldMapping:
    column_name: str
    x: float  # in mm
    y: float  # in mm

@dataclass
class DocumentProfile:
    name: str
    pdf_path: str
    spreadsheet_profile_name: str
    field_mappings: List[PdfFieldMapping] = field(default_factory=list)

@dataclass
class LicenseInfo:
    code: str
    valid: bool
    expire_date: int  # Unix timestamp
    device_id: str

