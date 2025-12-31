# -*- coding: utf-8 -*-
"""
Arquivo centralizado de strings do sistema
Similar ao strings.xml do Android
"""

class Strings:
    # Títulos principais
    APP_TITLE = "PDF Generator"
    
    # Menu de navegação
    NAV_SPREADSHEET_PROFILES = "Perfis de Planilha"
    NAV_DOCUMENT_PROFILES = "Perfis de Documento"
    NAV_BATCH_GENERATE = "Gerar em Lote"
    NAV_GENERATED_PDFS = "PDFs Gerados"
    NAV_EXPORT_PROFILES = "Exportar Perfis (ZIP)"
    NAV_IMPORT_PROFILES = "Importar Perfis (ZIP)"
    NAV_MANAGE_LICENSE = "Gerenciar Licença"
    
    # Logo
    LOGO_ADD = "Adicionar Logo"
    LOGO_REMOVE = "Remover Logo"
    
    # Licença
    LICENSE_ACTIVE = "Licença: Ativa"
    LICENSE_INACTIVE = "Licença: Inativa"
    LICENSE_VALID_UNTIL = "Válido até {}"
    LICENSE_INVALID_TITLE = "Licença Inválida"
    LICENSE_INVALID_MESSAGE = "Sua licença foi invalidada ou expirou. Por favor, verifique sua assinatura."
    
    # Perfil de Documento
    DOC_PROFILE_TITLE = "Gerenciamento de Perfis de Documento"
    DOC_SELECT_PDF = "Selecionar Template PDF"
    DOC_PDF_SELECTED = "PDF Selecionado: {}"
    DOC_PROFILE_NAME_PLACEHOLDER = "Nome do Perfil de Documento"
    DOC_SELECT_SPREADSHEET_PROFILE = "Selecione um Perfil de Planilha"
    DOC_TITLE_COLUMN = "Coluna para Título do PDF:"
    DOC_SELECT_COLUMN = "Selecione a Coluna"
    DOC_STEP_1 = "Coluna em Mapeamento:"
    DOC_CURRENT_MAPPINGS = "Mapeamentos Atuais"
    DOC_NO_MAPPINGS = "Nenhum mapeamento adicionado."
    DOC_SAVE_PROFILE = "Salvar Perfil de Documento"
    DOC_SAVE_CHANGES = "Salvar Alterações"
    DOC_SELECT_PDF_VIEWER = "Selecione um PDF para visualizar o template."
    DOC_PAGE_PREFIX = "pág. "
    DOC_VIEW_BUTTON = "Ver"
    DOC_REMOVE_BUTTON = "X"
    DOC_PAGE_LABEL = "Página: {} / {}"
    DOC_PREVIOUS_PAGE = "Anterior"
    DOC_NEXT_PAGE = "Próxima"
    DOC_EDIT_STYLE = "Estilo"
    DOC_PAGE_FORMAT = "Formato da Página:"
    DOC_PAGE_ORIENTATION = "Orientação:"
    DOC_ORIENTATION_PORTRAIT = "Retrato"
    DOC_ORIENTATION_LANDSCAPE = "Paisagem"
    
    # Diálogos de estilo de texto
    STYLE_DIALOG_TITLE = "Configurar Estilo do Texto"
    STYLE_FONT_LABEL = "Fonte:"
    STYLE_SIZE_LABEL = "Tamanho:"
    STYLE_COLOR_LABEL = "Cor:"
    STYLE_BOLD = "Negrito"
    STYLE_ITALIC = "Itálico"
    STYLE_UNDERLINE = "Sublinhado"
    STYLE_CHOOSE_COLOR = "Escolher Cor"
    STYLE_SAVE = "Salvar"
    STYLE_CANCEL = "Cancelar"
    
    # Perfil de Planilha
    SHEET_PROFILE_TITLE = "Gerenciamento de Perfis de Planilha"
    SHEET_SELECT_FILE = "Selecionar Planilha"
    SHEET_FILE_SELECTED = "Planilha Selecionada: {}"
    SHEET_PROFILE_NAME_PLACEHOLDER = "Nome do Perfil de Planilha"
    SHEET_HEADER_ROW = "Linha do Cabeçalho:"
    SHEET_SAVE_PROFILE = "Salvar Perfil de Planilha"
    SHEET_SAVE_CHANGES = "Salvar Alterações"
    
    # Geração em Lote
    BATCH_TITLE = "Geração em Lote de PDFs"
    BATCH_SELECT_SPREADSHEET = "Selecionar Planilha"
    BATCH_SELECT_DOCUMENT_PROFILE = "Selecione um Perfil de Documento"
    BATCH_GENERATE = "Gerar PDFs"
    
    # Lista de PDFs
    PDF_LIST_TITLE = "PDFs Gerados"
    PDF_LIST_REFRESH = "Atualizar Lista"
    PDF_LIST_OPEN = "Abrir"
    PDF_LIST_DELETE = "Excluir"
    PDF_LIST_NO_PDFS = "Nenhum PDF gerado ainda."
    
    # Mensagens de erro
    ERROR_TITLE = "Erro"
    ERROR_SELECT_COLUMN = "Selecione uma coluna para mapear."
    ERROR_RENDER_PDF_TITLE = "Erro de Renderização"
    ERROR_RENDER_PDF_MESSAGE = "Não foi possível renderizar o PDF."
    ERROR_NO_PROFILE_NAME = "Por favor, insira um nome para o perfil."
    ERROR_NO_PDF_SELECTED = "Por favor, selecione um template PDF."
    ERROR_NO_SPREADSHEET_PROFILE = "Por favor, selecione um perfil de planilha."
    ERROR_NO_TITLE_COLUMN = "Por favor, selecione uma coluna para título."
    ERROR_NO_MAPPINGS = "Por favor, adicione pelo menos um mapeamento."
    ERROR_PROFILE_EXISTS = "Já existe um perfil com este nome."
    
    # Mensagens de sucesso
    SUCCESS_TITLE = "Sucesso"
    SUCCESS_PROFILE_SAVED = "Perfil salvo com sucesso!"
    SUCCESS_PROFILE_UPDATED = "Perfil atualizado com sucesso!"
    SUCCESS_PROFILE_DELETED = "Perfil excluído com sucesso!"
    SUCCESS_PDFS_GENERATED = "PDFs gerados com sucesso!"
    
    # Mensagens de confirmação
    CONFIRM_TITLE = "Confirmação"
    CONFIRM_DELETE_PROFILE = "Tem certeza que deseja excluir este perfil?"
    CONFIRM_DELETE_PDF = "Tem certeza que deseja excluir este PDF?"
    CONFIRM_FORMAT_CHANGE_TITLE = "Alteração de Formato"
    CONFIRM_FORMAT_CHANGE_MESSAGE = "Ao alterar o formato ou orientação da página, todos os mapeamentos serão perdidos. Deseja continuar?"
    
    # Diálogos de progresso
    PROGRESS_PROCESSING = "Processando..."
    PROGRESS_WAIT = "Por favor, aguarde..."
    PROGRESS_LOADING_PDF = "Carregando PDF..."
    PROGRESS_RENDERING_PAGE = "Renderizando página {}..."
    PROGRESS_READING_SPREADSHEET = "Lendo planilha..."
    PROGRESS_PROCESSING_ROW = "Processando linha {} de {}..."
    PROGRESS_GENERATION_COMPLETE = "Geração concluída. {} PDFs criados."

    # Diálogo de estilo
    STYLE_DIALOG_TITLE = "Configurar Estilo"
    STYLE_DIALOG_FONT_LABEL = "Fonte:"
    STYLE_DIALOG_SIZE_LABEL = "Tamanho:"
    STYLE_DIALOG_COLOR_LABEL = "Cor:"
    STYLE_DIALOG_BOLD = "Negrito"
    STYLE_DIALOG_ITALIC = "Itálico"
    STYLE_DIALOG_UNDERLINE = "Sublinhado"
    STYLE_DIALOG_CHOOSE_COLOR = "Escolher Cor"
    STYLE_DIALOG_TEXT_EXAMPLE = "Texto de Exemplo"
    STYLE_DIALOG_SAVE = "Salvar"
    STYLE_DIALOG_CANCEL = "Cancelar"

    # Diálogo de licença
    LICENSE_DIALOG_TITLE = "Ativação de Licença"
    LICENSE_DIALOG_ENTER_CODE = "Insira seu código de licença de 25 dígitos:"
    LICENSE_DIALOG_CODE_PLACEHOLDER = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
    LICENSE_DIALOG_CANCEL = "Cancelar"
    LICENSE_DIALOG_CONFIRM = "Confirmar"

    # Outros
    NO_PROFILES_FOUND = "Nenhum Perfil de Planilha Encontrado"
    FILE_FILTERS_PDF = "Arquivos PDF"
    FILE_FILTERS_EXCEL = "Arquivos Excel"
    FILE_FILTERS_ZIP = "Arquivos ZIP"

strings = Strings()
