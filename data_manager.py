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
        file_path = self._get_file_path(type(profile), profile.name)
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
        pdf_dir = os.path.join(self.base_dir, "Generated_PDFs")
        os.makedirs(pdf_dir, exist_ok=True)
        return pdf_dir

    def get_generated_pdfs(self) -> List[str]:
        pdf_dir = self.get_generated_pdfs_dir()
        # List all files in the directory and filter for .pdf
        pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
        # Sort by modification time (newest first)
        pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return pdf_files

# Singleton instance
data_manager = DataManager()
