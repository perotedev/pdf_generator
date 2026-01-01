# -*- coding: utf-8 -*-
import PyInstaller.__main__
import os
import shutil

def build():
    # Nome do projeto
    project_name = "SGPP"
    
    # Limpar pastas de build anteriores
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # Configurações do PyInstaller
    # Usamos --onedir para melhor performance de inicialização
    params = [
        'main.py',
        f'--name={project_name}',
        '--onedir',
        '--noconsole',
        '--add-data=assets;assets',
        '--add-data=resources;resources',
        '--add-data=.env;.',
        '--icon=assets/sgpp.ico',
        '--splash=assets/splash_sgpp.png',
        '--manifest=dpi_aware.manifest',
        '--clean',
        '--noconfirm',
    ]

    print(f"Iniciando build do {project_name} em modo --onedir...")
    PyInstaller.__main__.run(params)
    print("\nBuild concluído com sucesso! Os arquivos estão na pasta 'dist'.")

if __name__ == "__main__":
    build()