# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os
from typing import List, TypeVar, Type, Dict, Any
from models import SpreadsheetProfile, DocumentProfile, ColumnMapping, PdfFieldMapping, TextStyle

T = TypeVar('T', SpreadsheetProfile, DocumentProfile)

class DataManager:
    def __init__(self, base_dir: str = os.path.expanduser("~/.pdf_generator_app")):
        self.base_dir = base_dir
        self.profiles_dir = os.path.join(base_dir, "profiles")
        self.templates_dir = os.path.join(base_dir, "templates")
        self.license_file = os.path.join(base_dir, "license.json")
        self.logo_file = os.path.join(base_dir, "company_logo.png")
        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Local para salvar PDFs: Documentos/PDF_GENERATOR
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.exists(docs_dir):
            docs_dir = os.path.join(os.path.expanduser("~"), "Documentos")
        
        self.pdf_base_dir = os.path.join(docs_dir, "PDF_GENERATOR")
        os.makedirs(self.pdf_base_dir, exist_ok=True)

    def _get_file_path(self, profile_type: Type[T], name: str) -> str:
        # Normalize name to be safe for filenames
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
        if profile_type == SpreadsheetProfile:
            return os.path.join(self.profiles_dir, f"spreadsheet_{safe_name}.json")
        elif profile_type == DocumentProfile:
            return os.path.join(self.profiles_dir, f"document_{safe_name}.json")
        raise ValueError("Invalid profile type")

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Converte objetos para dicionário com suporte aos novos campos"""
        if isinstance(obj, DocumentProfile):
            return obj.to_dict()
        elif isinstance(obj, SpreadsheetProfile):
            data = obj.__dict__.copy()
            data['columns'] = [self._to_dict(c) for c in data.get('columns', [])]
            return data
        elif isinstance(obj, PdfFieldMapping):
            return obj.to_dict()
        elif isinstance(obj, ColumnMapping):
            return obj.__dict__.copy()
        elif isinstance(obj, TextStyle):
            return obj.to_dict()
        return obj

    def _from_dict(self, data: Dict[str, Any], profile_type: Type[T]) -> T:
        """Converte dicionário para objetos com compatibilidade retroativa"""
        if profile_type == SpreadsheetProfile:
            # Filter data to only include keys expected by SpreadsheetProfile
            columns = [ColumnMapping(**c) for c in data.get('columns', [])]
            header_row = data.get('header_row', 1)
            return SpreadsheetProfile(name=data['name'], header_row=header_row, columns=columns)
        elif profile_type == DocumentProfile:
            # Usa o método from_dict do DocumentProfile para compatibilidade
            return DocumentProfile.from_dict(data)
        raise ValueError("Invalid profile type")

    def save_profile(self, profile: T):
        file_path = self._get_file_path(type(profile), profile.name).replace(" ", "_")
        
        if isinstance(profile, DocumentProfile):
            # Copy PDF to local templates directory if it's not already there
            if not profile.pdf_path.startswith(self.templates_dir):
                import shutil
                pdf_filename = os.path.basename(profile.pdf_path)
                # Ensure unique filename to avoid collisions
                local_pdf_path = os.path.join(self.templates_dir, f"{profile.name}_{pdf_filename}")
                shutil.copy(profile.pdf_path, local_pdf_path)
                profile.pdf_path = local_pdf_path

        profile_dict = self._to_dict(profile)

        if isinstance(profile, DocumentProfile):
            # Remove 'name' from the saved data for DocumentProfile
            profile_dict.pop('columns', None)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile_dict, f, indent=4, ensure_ascii=False)

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
        file_path = self._get_file_path(type(profile), profile.name).replace(" ", "_")
        try:
            os.remove(file_path)
            if isinstance(profile, DocumentProfile):
                os.remove(profile.pdf_path)
        except Exception as e:
            print(f"Error deleting profile {file_path}: {e}")
            pass

    def save_license(self, license_info: Dict[str, Any]):
        with open(self.license_file, 'w', encoding='utf-8') as f:
            json.dump(license_info, f, indent=4)

    def load_license(self) -> Dict[str, Any]:
        if os.path.exists(self.license_file):
            with open(self.license_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_logo(self, image_path: str):
        import shutil
        shutil.copy(image_path, self.logo_file)

    def get_logo_path(self) -> str:
        if os.path.exists(self.logo_file):
            return self.logo_file
        return ""

    def delete_logo(self):
        if os.path.exists(self.logo_file):
            os.remove(self.logo_file)

    def export_profiles_to_zip(self, zip_path: str):
        import zipfile
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add profiles
            for filename in os.listdir(self.profiles_dir):
                if filename.endswith(".json"):
                    zipf.write(os.path.join(self.profiles_dir, filename), os.path.join("profiles", filename))
            # Add templates
            for filename in os.listdir(self.templates_dir):
                zipf.write(os.path.join(self.templates_dir, filename), os.path.join("templates", filename))

    def import_profiles_from_zip(self, zip_path: str):
        import zipfile
        import shutil
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for member in zipf.infolist():
                if member.filename.startswith("profiles/") and member.filename.endswith(".json"):
                    filename = os.path.basename(member.filename)
                    target_path = os.path.join(self.profiles_dir, filename)
                    if not os.path.exists(target_path):
                        with zipf.open(member) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                elif member.filename.startswith("templates/"):
                    filename = os.path.basename(member.filename)
                    if not filename: continue
                    target_path = os.path.join(self.templates_dir, filename)
                    if not os.path.exists(target_path):
                        with zipf.open(member) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)

    def get_generated_pdfs_dir(self, base_date: datetime = None) -> str:
        # Estrutura PDF_GENERATOR/ANO/MES
        if base_date is None:
            base_date = datetime.now()
        year = str(base_date.year)
        month = base_date.strftime("%m")
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

# Singleton instance
data_manager = DataManager()
