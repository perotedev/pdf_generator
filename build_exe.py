# -*- coding: utf-8 -*-
import os
import subprocess
import shutil
import sys

def build():
    # Nome do executável
    app_name = "SGPP"
    
    # Arquivo principal
    main_script = "main.py"
    
    # Ícone
    icon_path = os.path.join("assets", "sgpp.ico")
    
    # Diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Remover pastas anteriores
    for folder in ["build", "dist"]:
        folder_path = os.path.join(script_dir, folder)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"Pasta ‘{folder}’ removida.")
            except Exception as e:
                print(f"Erro ao remover pasta ‘{folder}’: {e}")
    
    # Comando base do PyInstaller
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={app_name}",
        f"--icon={icon_path}",
        "--splash=assets/splash_min.png",
        "--manifest=dpi_aware.manifest",
        # Inclui os diretórios de recursos e módulos
        "--add-data=assets;assets",
        "--add-data=resources;resources",
        "--add-data=core;core",
        "--add-data=frames;frames",
        "--add-data=dialogs;dialogs",
        "--add-data=models;models",
        "--add-data=utils;utils",
        # Inclui o arquivo .env se existir
        "--add-data=.env;.",
        # Garante que o customtkinter seja incluído corretamente
        "--collect-all=customtkinter",
        # Garante que o PyMuPDF (fitz) seja incluído corretamente
        "--collect-all=fitz",
        # Define o caminho de busca para módulos
        f"--paths={script_dir}"
    ]
    
    # Adicionar o script principal
    cmd.append(main_script)

    print(f"Iniciando build do {app_name} com a nova estrutura v2.0...")
    
    try:
        # No Windows, o separador de add-data é ‘;’
        # No Linux/macOS, o separador de add-data é ‘:’
        if sys.platform != "win32":
            for i in range(len(cmd)):
                if cmd[i].startswith("--add-data="):
                    cmd[i] = cmd[i].replace(";", ":")
            
        subprocess.run(cmd, check=True)
        print("\nBuild concluído com sucesso! O executável está na pasta ‘dist’.")
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante o build: {e}")
    except Exception as e:
        print(f"\nErro inesperado: {e}")

if __name__ == "__main__":
    build()