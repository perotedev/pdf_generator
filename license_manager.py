import requests
import platform
import subprocess
import uuid
from datetime import datetime
from typing import Optional
from data_manager import data_manager
from models import LicenseInfo
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

class LicenseManager:
    DEVICE_TYPE = "windows" # Fixed for this Python desktop application

    def __init__(self):
        self._license_info: Optional[LicenseInfo] = None
        self._load_license_from_disk()

    def _get_device_id(self) -> str:
        """
        Generates a unique device ID for Windows.
        Using a combination of system info for a reasonably unique, non-MAC-address ID.
        """
        try:
            # For a real Windows app, using WMI to get a hardware ID is more robust.
            # For this environment, we will use a simple UUID based on platform info.
            # This is a fallback that will work in the sandbox.
            if platform.system() == "Windows":
                # This command is more reliable on Windows
                result = subprocess.check_output(["wmic", "csproduct", "get", "UUID"])
                device_id = result.decode().split("\n")[1].strip()
            else:
                # Fallback for non-Windows (like the sandbox)
                device_id = str(uuid.getnode()) # MAC address
            return f"WIN-{device_id}"
        except Exception:
            return f"WIN-FALLBACK-{platform.node()}"

    def _load_license_from_disk(self):
        license_data = data_manager.load_license()
        if license_data:
            try:
                self._license_info = LicenseInfo(**license_data)
                # Basic local check for expiration
                if self._license_info.valid and datetime.fromtimestamp(self._license_info.expire_date) < datetime.now():
                    self._license_info.valid = False
            except Exception:
                self._license_info = None

    @property
    def is_licensed(self) -> bool:
        if not self._license_info or not self._license_info.valid:
            return False
        # Check expiration date
        return datetime.fromtimestamp(self._license_info.expire_date) > datetime.now()

    @property
    def license_info(self) -> Optional[LicenseInfo]:
        return self._license_info

    def activate_license(self, code: str) -> str:
        device_id = self._get_device_id()
        payload = {
            "code": code.strip().upper(),
            "type": self.DEVICE_TYPE,
            "device_id": device_id
        }

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            }
            response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            response_data = response.json()
            
            if response_data.get("valid"):
                license_info = LicenseInfo(
                    code=response_data["code"],
                    valid=response_data["valid"],
                    expire_date=response_data["expire_date"],
                    device_id=response_data["device_id"]
                )
                self._license_info = license_info
                data_manager.save_license(license_info.__dict__)
                
                expire_date_str = datetime.fromtimestamp(license_info.expire_date).strftime("%Y-%m-%d")
                return f"Licença ativada com sucesso! Expira em {expire_date_str}"
            else:
                return "Falha na ativação: Código de licença inválido."

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return "Falha na ativação: Licença já vinculada a outro dispositivo."
            elif e.response.status_code == 400:
                return "Falha na ativação: Requisição inválida ou formato de licença incorreto."
            else:
                return f"Falha na ativação: Erro do servidor ({e.response.status_code})."
        except requests.exceptions.RequestException:
            return "Falha na ativação: Não foi possível conectar ao servidor."
        except Exception as e:
            return f"Erro inesperado durante a ativação: {e}"

license_manager = LicenseManager()
