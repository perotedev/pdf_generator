from datetime import datetime
import json
import os
from typing import List, TypeVar, Type, Dict, Any
from models import SpreadsheetProfile, DocumentProfile, ColumnMapping, PdfFieldMapping

T = TypeVar('T', SpreadsheetProfile, DocumentProfile)

class DataManager:
    def __init__(self, base_dir: str = os.path.expanduser("~/.pdf_generator_app")):
        self.base_dir = base_dir
        self.profiles_dir = os.path.join(base_dir, "profiles")
        self.license_file = os.path.join(base_dir, "license.json")
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Local para salvar PDFs: Documentos/PDF_GENERATOR
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.exists(docs_dir):
            docs_dir = os.path.join(os.path.expanduser("~"), "Documentos")
        
        self.pdf_base_dir = os.path.join(docs_dir, "PDF_GENERATOR")
        os.makedirs(self.pdf_base_dir, exist_ok=True)
        
        # Diretório do Poppler dentro da pasta base da aplicação
        self.poppler_dir = os.path.join(os.getcwd(), "poppler", "Library", "bin")

    def _get_file_path(self, profile_type: Type[T], name: str) -> str:
        # Normalize name to be safe for filenames
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
        if profile_type == SpreadsheetProfile:
            return os.path.join(self.profiles_dir, f"spreadsheet_{safe_name}.json")
        elif profile_type == DocumentProfile:
            return os.path.join(self.profiles_dir, f"document_{safe_name}.json")
        raise ValueError("Invalid profile type")

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        if isinstance(obj, (SpreadsheetProfile, DocumentProfile)):
            data = obj.__dict__.copy()
            data['columns'] = [self._to_dict(c) for c in data.get('columns', [])]
            data['field_mappings'] = [self._to_dict(f) for f in data.get('field_mappings', [])]
            return data
        elif isinstance(obj, (ColumnMapping, PdfFieldMapping)):
            return obj.__dict__.copy()
        return obj

    def _from_dict(self, data: Dict[str, Any], profile_type: Type[T]) -> T:
        if profile_type == SpreadsheetProfile:
            # Filter data to only include keys expected by SpreadsheetProfile
            columns = [ColumnMapping(**c) for c in data.get('columns', [])]
            return SpreadsheetProfile(name=data['name'], columns=columns)
        elif profile_type == DocumentProfile:
            data['field_mappings'] = [PdfFieldMapping(**f) for f in data.get('field_mappings', [])]
            return DocumentProfile(**data)
        raise ValueError("Invalid profile type")

    def save_profile(self, profile: T):
        file_path = self._get_file_path(type(profile), profile.name).replace(" ", "_")
        profile_dict = self._to_dict(profile)

        if isinstance(profile, DocumentProfile):
            # Remove 'name' from the saved data for DocumentProfile
            profile_dict.pop('columns', None)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile_dict, f, indent=4)

    def load_profiles(self, profile_type: Type[T]) -> List[T]:
        profiles = []
        prefix = "spreadsheet_" if profile_type == SpreadsheetProfile else "document_"
        for filename in os.listdir(self.profiles_dir):
            if filename.startswith(prefix) and filename.endswith(".json"):
                file_path = os.path.join(self.profiles_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profiles.append(self._from_dict(data, profile_type))
                except Exception as e:
                    print(f"Error loading profile {filename}: {e}")
        return profiles

    def delete_profile(self, profile: T):
        file_path = self._get_file_path(type(profile), profile.name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def save_license(self, license_info: Dict[str, Any]):
        with open(self.license_file, 'w', encoding='utf-8') as f:
            json.dump(license_info, f, indent=4)

    def load_license(self) -> Dict[str, Any]:
        if os.path.exists(self.license_file):
            with open(self.license_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_generated_pdfs_dir(self) -> str:
        # Estrutura PDF_GENERATOR/ANO/MES
        now = datetime.now()
        year = str(now.year)
        month = now.strftime("%m")
        pdf_dir = os.path.join(self.pdf_base_dir, year, month)
        os.makedirs(pdf_dir, exist_ok=True)
        return pdf_dir

    def get_generated_pdfs(self, year: str = None, month: str = None) -> List[str]:
        pdf_files = []
        
        # Se ano e mês forem fornecidos, busca apenas naquela pasta
        if year and month:
            target_dir = os.path.join(self.pdf_base_dir, year, month)
            if os.path.exists(target_dir):
                pdf_files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith(".pdf")]
        else:
            # Caso contrário, percorre toda a estrutura
            for root, dirs, files in os.walk(self.pdf_base_dir):
                for f in files:
                    if f.endswith(".pdf"):
                        pdf_files.append(os.path.join(root, f))
        
        # Sort by modification time (newest first)
        pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return pdf_files

    def get_available_years(self) -> List[str]:
        if not os.path.exists(self.pdf_base_dir):
            return []
        years = [d for d in os.listdir(self.pdf_base_dir) if os.path.isdir(os.path.join(self.pdf_base_dir, d)) and d.isdigit()]
        return sorted(years, reverse=True)

    def get_available_months(self, year: str) -> List[str]:
        year_dir = os.path.join(self.pdf_base_dir, year)
        if not os.path.exists(year_dir):
            return []
        months = [d for d in os.listdir(year_dir) if os.path.isdir(os.path.join(year_dir, d)) and d.isdigit()]
        return sorted(months)

    def get_poppler_path(self) -> str:
        """Retorna o caminho para os binários do Poppler."""
        # Se estiver rodando como executável (PyInstaller), o Poppler pode estar no _MEIPASS
        import sys
        if getattr(sys, 'frozen', False):
            # No executável, incluiremos o poppler na raiz do pacote
            base_path = sys._MEIPASS
            return os.path.join(base_path, "poppler", "Library", "bin")
        
        # Em desenvolvimento, usa o caminho na pasta de dados
        return self.poppler_dir

# Singleton instance
data_manager = DataManager()
