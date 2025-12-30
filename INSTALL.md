# Guia de Instalação - PDF Generator v2.0

## Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Windows (recomendado) ou Linux

## Instalação Passo a Passo

### 1. Extrair o Projeto

Extraia o arquivo `pdf_generator_refactored.zip` em uma pasta de sua escolha.

### 2. Abrir Terminal/Prompt de Comando

- **Windows**: Abra o Prompt de Comando ou PowerShell na pasta do projeto
- **Linux**: Abra o Terminal na pasta do projeto

### 3. Instalar Dependências

Execute o seguinte comando:

```bash
pip install -r requirements.txt
```

**Nota para Windows**: Se você tiver problemas com o `wmi`, pode ser necessário instalar o Visual C++ Build Tools.

### 4. Executar o Aplicativo

```bash
python main.py
```

## Solução de Problemas

### Erro: "No module named 'fitz'"

**Solução**: Instale o PyMuPDF manualmente:
```bash
pip install PyMuPDF
```

### Erro: "No module named 'customtkinter'"

**Solução**: Instale o CustomTkinter manualmente:
```bash
pip install customtkinter
```

### Erro: "ModuleNotFoundError: No module named 'data_manager'"

**Solução**: Este erro foi corrigido na versão atual. Certifique-se de estar usando os arquivos mais recentes.

### Erro: "No module named 'dotenv'"

**Solução**: Instale o python-dotenv:
```bash
pip install python-dotenv
```

### Erro com WMI no Windows

**Solução**: Instale o WMI manualmente:
```bash
pip install wmi
```

Se ainda houver problemas, você pode comentar a linha do `wmi` no `requirements.txt` e instalar apenas se necessário.

## Instalação de Todas as Dependências Manualmente

Se o `requirements.txt` não funcionar, instale uma por uma:

```bash
pip install customtkinter
pip install pandas
pip install openpyxl
pip install reportlab
pip install requests
pip install Pillow
pip install python-dateutil
pip install python-dotenv
pip install PyMuPDF
pip install pyinstaller
```

**Nota**: O `wmi` é opcional e só é necessário no Windows para algumas funcionalidades de licença.

## Verificação da Instalação

Para verificar se tudo está instalado corretamente, execute:

```bash
python test_compatibility.py
```

Se todos os testes passarem, a instalação está correta!

## Executando o Aplicativo

Após a instalação bem-sucedida:

```bash
python main.py
```

O aplicativo deve abrir uma janela gráfica.

## Criando um Executável (Opcional)

Para criar um executável standalone:

```bash
python build_exe.py
```

O executável será criado na pasta `dist/`.

## Suporte

Se você encontrar algum problema durante a instalação:

1. Verifique se o Python 3.11+ está instalado: `python --version`
2. Verifique se o pip está atualizado: `pip install --upgrade pip`
3. Tente instalar as dependências uma por uma
4. Verifique se há mensagens de erro específicas e procure soluções online

## Notas Importantes

- **Primeira execução**: Pode demorar um pouco para carregar todas as bibliotecas
- **Licença**: O sistema requer uma licença válida para uso completo
- **Perfis antigos**: São totalmente compatíveis com esta versão
- **Diretório poppler**: Não é mais necessário (foi removido do projeto)
