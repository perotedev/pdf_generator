import os
import subprocess

def build():
    # Nome do executável
    app_name = "PDF_Generator"
    
    # Arquivo principal
    main_script = "main.py"
    
    # Ícone
    icon_path = os.path.join("assets", "pdf_generator.ico")
    
    # Comando base do PyInstaller
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={app_name}",
        f"--icon={icon_path}",
        "--add-data=assets;assets",
        "--add-data=poppler;poppler",
        "--add-data=.env;."
    ]
    
    # Adicionar o script principal
    cmd.append(main_script)

    print("IMPORTANTE: Certifique-se de que a pasta 'poppler' (com Library/bin) estava presente no diretório raiz durante o build.")
    print(f"Iniciando build do {app_name}...")
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild concluído com sucesso! O executável está na pasta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante o build: {e}")

if __name__ == "__main__":
    build()
