#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste de compatibilidade com perfis antigos
"""
import json
import sys
from models import DocumentProfile, SpreadsheetProfile, PdfFieldMapping, TextStyle

def test_old_profile_format():
    """Testa se perfis antigos podem ser carregados"""
    print("Testando compatibilidade com perfis antigos...")
    
    # Simula um perfil antigo (sem os novos campos)
    old_profile_data = {
        "name": "Teste_Antigo",
        "pdf_path": "/path/to/template.pdf",
        "spreadsheet_profile_name": "Planilha_Teste",
        "title_column": "Nome",
        "field_mappings": [
            {
                "column_name": "Nome",
                "x": 10.0,
                "y": 20.0,
                "page_index": 0
            },
            {
                "column_name": "CPF",
                "x": 10.0,
                "y": 30.0,
                "page_index": 0
            }
        ]
    }
    
    try:
        # Tenta carregar o perfil antigo
        profile = DocumentProfile.from_dict(old_profile_data)
        
        # Verifica se os valores padrão foram aplicados
        assert profile.page_format == "A4", "Formato padrão deveria ser A4"
        assert profile.page_orientation == "portrait", "Orientação padrão deveria ser portrait"
        
        # Verifica se os mapeamentos têm estilos padrão
        for mapping in profile.field_mappings:
            assert mapping.style is not None, "Mapeamento deveria ter estilo"
            assert mapping.style.font_family == "Helvetica", "Fonte padrão deveria ser Helvetica"
            assert mapping.style.font_size == 10, "Tamanho padrão deveria ser 10"
            assert mapping.style.color == "#000000", "Cor padrão deveria ser preta"
        
        print("✓ Perfil antigo carregado com sucesso!")
        print(f"  - Formato: {profile.page_format}")
        print(f"  - Orientação: {profile.page_orientation}")
        print(f"  - Mapeamentos: {len(profile.field_mappings)}")
        print(f"  - Estilo do primeiro mapeamento: {profile.field_mappings[0].style.font_family} {profile.field_mappings[0].style.font_size}pt")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao carregar perfil antigo: {e}")
        return False

def test_new_profile_format():
    """Testa se perfis novos são salvos corretamente"""
    print("\nTestando perfis novos...")
    
    # Cria um perfil novo com todos os campos
    new_profile = DocumentProfile(
        name="Teste_Novo",
        pdf_path="/path/to/template.pdf",
        spreadsheet_profile_name="Planilha_Teste",
        title_column="Nome",
        field_mappings=[
            PdfFieldMapping(
                column_name="Nome",
                x=10.0,
                y=20.0,
                page_index=0,
                style=TextStyle(
                    font_family="Arial",
                    font_size=12,
                    bold=True,
                    italic=False,
                    underline=False,
                    color="#FF0000"
                )
            )
        ],
        page_format="A3",
        page_orientation="landscape"
    )
    
    try:
        # Converte para dict
        profile_dict = new_profile.to_dict()
        
        # Verifica se todos os campos estão presentes
        assert "page_format" in profile_dict, "Formato deveria estar no dict"
        assert "page_orientation" in profile_dict, "Orientação deveria estar no dict"
        assert profile_dict["page_format"] == "A3", "Formato deveria ser A3"
        assert profile_dict["page_orientation"] == "landscape", "Orientação deveria ser landscape"
        
        # Verifica se o estilo está presente
        mapping_dict = profile_dict["field_mappings"][0]
        assert "style" in mapping_dict, "Estilo deveria estar no mapeamento"
        assert mapping_dict["style"]["font_family"] == "Arial", "Fonte deveria ser Arial"
        assert mapping_dict["style"]["font_size"] == 12, "Tamanho deveria ser 12"
        assert mapping_dict["style"]["bold"] == True, "Bold deveria ser True"
        assert mapping_dict["style"]["color"] == "#FF0000", "Cor deveria ser vermelha"
        
        # Tenta recarregar do dict
        reloaded_profile = DocumentProfile.from_dict(profile_dict)
        assert reloaded_profile.page_format == "A3", "Formato recarregado deveria ser A3"
        assert reloaded_profile.page_orientation == "landscape", "Orientação recarregada deveria ser landscape"
        assert reloaded_profile.field_mappings[0].style.font_family == "Arial", "Fonte recarregada deveria ser Arial"
        
        print("✓ Perfil novo salvo e recarregado com sucesso!")
        print(f"  - Formato: {reloaded_profile.page_format}")
        print(f"  - Orientação: {reloaded_profile.page_orientation}")
        print(f"  - Estilo: {reloaded_profile.field_mappings[0].style.font_family} {reloaded_profile.field_mappings[0].style.font_size}pt {reloaded_profile.field_mappings[0].style.color}")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao salvar/recarregar perfil novo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_style():
    """Testa a classe TextStyle"""
    print("\nTestando TextStyle...")
    
    try:
        # Cria um estilo
        style = TextStyle(
            font_family="Times New Roman",
            font_size=14,
            bold=True,
            italic=True,
            underline=True,
            color="#0000FF"
        )
        
        # Converte para dict
        style_dict = style.to_dict()
        
        # Recarrega do dict
        reloaded_style = TextStyle.from_dict(style_dict)
        
        assert reloaded_style.font_family == "Times New Roman"
        assert reloaded_style.font_size == 14
        assert reloaded_style.bold == True
        assert reloaded_style.italic == True
        assert reloaded_style.underline == True
        assert reloaded_style.color == "#0000FF"
        
        print("✓ TextStyle funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"✗ Erro no TextStyle: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTE DE COMPATIBILIDADE - PDF Generator v2.0")
    print("=" * 60)
    
    results = []
    
    results.append(("Perfis Antigos", test_old_profile_format()))
    results.append(("Perfis Novos", test_new_profile_format()))
    results.append(("TextStyle", test_text_style()))
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ Todos os testes passaram! Sistema compatível.")
        return 0
    else:
        print("\n✗ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
