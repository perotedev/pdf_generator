import sys
import requests
import platform
import subprocess
import uuid
from datetime import datetime
from typing import Optional
from core.data_manager import data_manager
from models import LicenseInfo
from dotenv import load_dotenv
import os

def load_env():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    env_path = os.path.join(base_path, ".env")
    load_dotenv(env_path)

load_env()

API_URL = os.getenv("PDF_GENERATOR_ACTIVATE_API_URL")
VALIDATE_API_URL = os.getenv("PDF_GENERATOR_VALIDATE_API_URL")
API_KEY = os.getenv("PDF_GENERATOR_ACTIVATE_API_KEY")

class LicenseManager:
    DEVICE_TYPE = "windows" # Fixed for this Python desktop application

    def __init__(self):
        self._license_info: Optional[LicenseInfo] = None
        self._load_license_from_disk()

    def _get_device_id(self) -> str:
        try:
            if platform.system() == "Windows":
                # Configuração para esconder a janela do CMD
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0 # SW_HIDE

                # Adicionamos o startupinfo na chamada
                result = subprocess.check_output(
                    ["wmic", "csproduct", "get", "UUID"],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW # Garante que nenhuma janela seja criada
                )
                device_id = result.decode().split("\n")[1].strip()
            else:
                device_id = str(uuid.getnode())
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

    def get_expiration_date(self) -> str:
        if self._license_info and self._license_info.expire_date:
            return datetime.fromtimestamp(self._license_info.expire_date).strftime("%d/%m/%Y")
        return "--/--/----"

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
                    device_id=response_data["device_id"],
                    company=response_data.get("company", ""),
                    last_verification=int(datetime.now().timestamp())
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

    def check_internet(self) -> bool:
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.exceptions.RequestException:
            return False
    
    def _same_day_local(ts1, ts2):
        d1 = datetime.fromtimestamp(ts1).date()
        d2 = datetime.fromtimestamp(ts2).date()
        return d1 == d2

    def validate_license_online(self) -> bool:
        """
        Validates the current license with the online API.
        Returns True if valid, False otherwise.
        """
        if not self._license_info or not self._license_info.code:
            return False
        
        d1 = datetime.fromtimestamp(self._license_info.last_verification).date()
        d2 = datetime.now().date()

        if d1 == d2 and self.is_licensed:
            return self.is_licensed  # Already verified today

        if not self.check_internet():
            return self.is_licensed # Fallback to local check if no internet

        try:
            payload = {
                "code": self._license_info.code,
                "device_id": self._get_device_id()
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            }
            
            response = requests.post(VALIDATE_API_URL, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                is_valid = response_data.get("is_valid", False)
                
                if is_valid:
                    # Update local info with latest from server
                    self._license_info.valid = True
                    if "expiration_date" in response_data:
                        self._license_info.expire_date = response_data["expiration_date"]
                    if "company" in response_data:
                        self._license_info.company = response_data["company"]
                    self._license_info.last_verification = int(datetime.now().timestamp())
                    data_manager.save_license(self._license_info.__dict__)
                    return True
                else:
                    self._license_info.valid = False
                    data_manager.save_license(self._license_info.__dict__)
                    return False
            else:
                # If server error, we might want to trust local state or not.
                # For now, let's trust local state to avoid locking out users on server downtime.
                return self.is_licensed

        except Exception:
            # On any error (timeout, etc.), fallback to local check
            return self.is_licensed

license_manager = LicenseManager()
