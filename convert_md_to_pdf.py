#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter arquivos Markdown para PDF
Mantém formatação e emojis quando possível
"""

import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

def markdown_to_pdf(md_file_path, output_pdf_path):
    """
    Converte arquivo Markdown para PDF
    """
    try:
        # Lê o conteúdo do arquivo Markdown
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Converte Markdown para HTML
        html_content = markdown2.markdown(
            md_content, 
            extras=[
                'fenced-code-blocks',
                'tables', 
                'task_list',
                'strike',
                'target-blank-links',
                'header-ids'
            ]
        )
        
        # CSS para melhor formatação
        css_content = """
        @page {
            margin: 2cm;
            size: A4;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-before: always;
        }
        h1:first-child {
            page-break-before: auto;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 5px;
            margin-top: 30px;
        }
        h3 {
            color: #2980b9;
            margin-top: 25px;
        }
        h4 {
            color: #8e44ad;
            margin-top: 20px;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            line-height: 1.4;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #666;
            font-style: italic;
        }
        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        li {
            margin: 5px 0;
        }
        hr {
            border: none;
            border-top: 2px solid #eee;
            margin: 30px 0;
        }
        .emoji {
            font-size: 1.2em;
        }
        """
        
        # HTML completo
        full_html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{Path(md_file_path).stem}</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Converte HTML para PDF
        HTML(string=full_html).write_pdf(
            output_pdf_path,
            stylesheets=[CSS(string=css_content)]
        )
        
        print(f"✅ PDF criado: {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao converter {md_file_path}: {str(e)}")
        return False

def main():
    """
    Função principal - converte todos os arquivos .md para PDF
    """
    # Diretório atual
    base_dir = Path(__file__).parent
    
    # Arquivos para converter
    md_files = [
        base_dir / "README_ALGORITMOS.md",
        base_dir / "docs" / "ALGORITMOS_VISUAL.md", 
        base_dir / "docs" / "CONTAINER_SPECS.md",
        base_dir / "docs" / "README.md"
    ]
    
    print("🚀 Iniciando conversão MD para PDF...")
    print("=" * 50)
    
    converted_count = 0
    
    for md_file in md_files:
        if md_file.exists():
            # Nome do arquivo PDF (mesmo diretório)
            pdf_file = md_file.with_suffix('.pdf')
            
            print(f"📄 Convertendo: {md_file.name}")
            
            if markdown_to_pdf(str(md_file), str(pdf_file)):
                converted_count += 1
            
            print("-" * 30)
        else:
            print(f"⚠️  Arquivo não encontrado: {md_file}")
    
    print("=" * 50)
    print(f"🎯 Conversão concluída: {converted_count} arquivo(s) convertido(s)")
    
    # Lista arquivos PDF criados
    print("\n📁 Arquivos PDF criados:")
    for md_file in md_files:
        pdf_file = md_file.with_suffix('.pdf')
        if pdf_file.exists():
            size_kb = pdf_file.stat().st_size / 1024
            print(f"   ✅ {pdf_file.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
