# PDF Generator v2.0 - Refatorado

Sistema desktop para geração de PDFs em lote a partir de planilhas Excel, com suporte a templates PDF personalizados.

## 🎯 Novidades da Versão 2.0

### ✨ Principais Recursos Adicionados

1. **Estilos de Texto Personalizáveis**
   - Configure fonte, tamanho, cor, negrito, itálico e sublinhado para cada campo
   - Preview em tempo real do estilo
   - Color picker integrado

2. **Múltiplos Formatos de Página**
   - Suporte a A1, A2, A3, A4, A5, A6, Letter e Legal
   - Orientações: Retrato e Paisagem
   - Conversão automática de coordenadas

3. **Scroll com Roda do Mouse**
   - Todas as listas e áreas scrolláveis respondem à roda do mouse
   - Navegação mais fluida e intuitiva

4. **Strings Centralizadas**
   - Facilita manutenção e futuras traduções
   - Todas as mensagens em um único arquivo

5. **Arquitetura Refatorada**
   - Código organizado em módulos
   - Diálogos reutilizáveis
   - Melhor separação de responsabilidades

## 📋 Requisitos

- Python 3.11 ou superior
- Windows (recomendado) ou Linux
- Bibliotecas listadas em `requirements.txt`

## 🚀 Instalação

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Execute o aplicativo:**
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
refactored/
├── assets/              # Ícones e imagens
├── core/                # Lógica central
│   ├── data_manager.py  # Gerenciamento de dados
│   ├── pdf_generator.py # Geração de PDFs
│   └── license_manager.py # Gerenciamento de licenças
├── dialogs/             # Diálogos reutilizáveis
│   ├── progress_dialog.py
│   └── text_style_dialog.py
├── frames/              # Frames da interface
│   ├── document_profile_frame.py
│   ├── spreadsheet_profile_frame.py
│   └── ...
├── models/              # Modelos de dados
│   └── document_models.py
├── resources/           # Recursos
│   └── strings.py       # Strings centralizadas
├── utils/               # Utilitários
│   ├── pdf_utils.py
│   └── scroll_helper.py
└── main.py              # Arquivo principal
```

## 🔄 Compatibilidade

**Totalmente compatível com perfis da versão anterior!**

- Perfis antigos são carregados automaticamente
- Valores padrão são aplicados aos novos campos
- Nenhuma perda de dados

## 📖 Como Usar

### 1. Criar Perfil de Planilha
1. Clique em "Perfis de Planilha"
2. Selecione uma planilha Excel
3. Configure a linha do cabeçalho
4. Personalize os nomes e tipos das colunas
5. Salve o perfil

### 2. Criar Perfil de Documento
1. Clique em "Perfis de Documento"
2. Selecione um template PDF
3. Escolha o formato e orientação da página
4. Selecione um perfil de planilha
5. Clique no PDF para mapear os campos
6. Configure o estilo de cada campo (botão "Estilo")
7. Salve o perfil

### 3. Gerar PDFs em Lote
1. Clique em "Gerar em Lote"
2. Selecione uma planilha com dados
3. Escolha um perfil de documento
4. Clique em "Gerar PDFs"
5. Os PDFs serão salvos em `Documentos/PDF_GENERATOR/ANO/MES/`

## 🎨 Configurando Estilos de Texto

Após mapear um campo no PDF:
1. Localize o campo na lista de mapeamentos
2. Clique no botão "Estilo"
3. Configure:
   - **Fonte**: Escolha entre as fontes disponíveis
   - **Tamanho**: 8 a 58 pontos
   - **Formatação**: Negrito, Itálico, Sublinhado
   - **Cor**: Use o color picker
4. Veja o preview em tempo real
5. Clique em "Salvar"

## 📄 Formatos de Página

### Formatos Disponíveis
- **A1**: 594 x 841 mm
- **A2**: 420 x 594 mm
- **A3**: 297 x 420 mm
- **A4**: 210 x 297 mm (padrão)
- **A5**: 148 x 210 mm
- **A6**: 105 x 148 mm
- **Letter**: 8.5 x 11 polegadas
- **Legal**: 8.5 x 14 polegadas

### Orientações
- **Retrato** (Portrait): Vertical
- **Paisagem** (Landscape): Horizontal

⚠️ **Importante**: Ao alterar o formato ou orientação após criar mapeamentos, todos os mapeamentos serão perdidos.

## 🧪 Testes

Execute o script de teste de compatibilidade:
```bash
python test_compatibility.py
```

Este script verifica:
- Carregamento de perfis antigos
- Salvamento de perfis novos
- Funcionalidade dos estilos de texto

## 📝 Changelog

Veja o arquivo [CHANGELOG.md](CHANGELOG.md) para detalhes completos das alterações.

## 🐛 Solução de Problemas

### Problema: Perfis antigos não carregam
**Solução**: Os perfis antigos são totalmente compatíveis. Verifique se os arquivos JSON não estão corrompidos.

### Problema: Estilos não aparecem no PDF
**Solução**: Certifique-se de que a fonte selecionada está disponível no sistema.

### Problema: Scroll não funciona
**Solução**: O scroll com mouse funciona em todas as áreas, exceto no canvas do PDF (que tem prioridade para navegação).

## 🔧 Compilação para Executável

Para criar um executável Windows:
```bash
python build_exe.py
```

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Entre em contato com o desenvolvedor

## 📜 Licença

Este software requer licença válida para uso completo.

---

**Desenvolvido com ❤️ usando Python e CustomTkinter**
