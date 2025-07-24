#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter arquivos Markdown para PDF usando ReportLab
Compatível com Windows, mantém formatação básica
"""

import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def parse_markdown_simple(md_content):
    """
    Parser simples de Markdown para elementos básicos
    """
    lines = md_content.split('\n')
    elements = []
    current_block = []
    in_code_block = False
    
    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                if current_block:
                    elements.append(('code_block', '\n'.join(current_block)))
                    current_block = []
                in_code_block = False
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            current_block.append(line)
            continue
            
        # Headers
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('# ').strip()
            elements.append(('header', level, text))
            continue
            
        # Tables (simple detection)
        if '|' in line and line.strip():
            elements.append(('table_row', line))
            continue
            
        # Lists
        if re.match(r'^\s*[-*+]\s+', line):
            text = re.sub(r'^\s*[-*+]\s+', '', line)
            elements.append(('list_item', text))
            continue
            
        if re.match(r'^\s*\d+\.\s+', line):
            text = re.sub(r'^\s*\d+\.\s+', '', line)
            elements.append(('numbered_item', text))
            continue
            
        # Horizontal rule
        if line.strip() in ['---', '***', '___']:
            elements.append(('hr', ''))
            continue
            
        # Empty line
        if not line.strip():
            elements.append(('space', ''))
            continue
            
        # Regular paragraph
        elements.append(('paragraph', line))
    
    # Add remaining code block
    if current_block and in_code_block:
        elements.append(('code_block', '\n'.join(current_block)))
    
    return elements

def clean_text_for_pdf(text):
    """
    Limpa o texto removendo caracteres que podem causar problemas no PDF
    """
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove markdown bold **text** -> text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # Remove markdown italic *text* -> text
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    # Remove markdown code `code` -> code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Substitui alguns emojis por texto
    emoji_map = {
        '🎯': '[TARGET]',
        '📚': '[BOOKS]',
        '🏗️': '[CONSTRUCTION]',
        '🧠': '[BRAIN]',
        '📊': '[CHART]',
        '🎭': '[THEATER]',
        '🔧': '[TOOL]',
        '⚙️': '[GEAR]',
        '✅': '[CHECK]',
        '❌': '[X]',
        '⚠️': '[WARNING]',
        '🔥': '[FIRE]',
        '💪': '[MUSCLE]',
        '👁️': '[EYE]',
        '📦': '[BOX]',
        '🤖': '[ROBOT]',
        '🏪': '[SHOP]',
        '💊': '[PILL]',
        '👨‍⚕️': '[DOCTOR]',
        '🎬': '[MOVIE]',
        '🧬': '[DNA]',
        '🚀': '[ROCKET]',
        '📐': '[RULER]',
        '🎨': '[PALETTE]',
        '🧍': '[PERSON]',
        '📄': '[DOCUMENT]',
        '📁': '[FOLDER]'
    }
    
    for emoji, replacement in emoji_map.items():
        text = text.replace(emoji, replacement)
    
    return text

def markdown_to_pdf_simple(md_file_path, output_pdf_path):
    """
    Converte arquivo Markdown para PDF usando ReportLab
    """
    try:
        # Lê o conteúdo do arquivo Markdown
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Parse do markdown
        elements = parse_markdown_simple(md_content)
        
        # Cria o documento PDF
        doc = SimpleDocTemplate(
            str(output_pdf_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilos customizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue,
            alignment=TA_LEFT
        )
        
        h2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkred,
            alignment=TA_LEFT
        )
        
        h3_style = ParagraphStyle(
            'CustomH3',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.darkblue,
            alignment=TA_LEFT
        )
        
        h4_style = ParagraphStyle(
            'CustomH4',
            parent=styles['Heading4'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.purple,
            alignment=TA_LEFT
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=8,
            fontName='Courier',
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10,
            backColor=colors.lightgrey
        )
        
        # Constrói os elementos do PDF
        story = []
        
        # Adiciona título do documento
        doc_title = Path(md_file_path).stem.replace('_', ' ').title()
        story.append(Paragraph(clean_text_for_pdf(doc_title), title_style))
        story.append(Spacer(1, 20))
        
        for element in elements:
            if element[0] == 'header':
                level, text = element[1], element[2]
                text = clean_text_for_pdf(text)
                
                if level == 1:
                    story.append(PageBreak())
                    story.append(Paragraph(text, title_style))
                elif level == 2:
                    story.append(Paragraph(text, h2_style))
                elif level == 3:
                    story.append(Paragraph(text, h3_style))
                else:
                    story.append(Paragraph(text, h4_style))
                    
            elif element[0] == 'paragraph':
                text = clean_text_for_pdf(element[1])
                if text.strip():
                    story.append(Paragraph(text, normal_style))
                    
            elif element[0] == 'code_block':
                code_text = element[1]
                story.append(Preformatted(code_text, code_style))
                
            elif element[0] == 'list_item':
                text = clean_text_for_pdf(element[1])
                story.append(Paragraph(f"• {text}", normal_style))
                
            elif element[0] == 'numbered_item':
                text = clean_text_for_pdf(element[1])
                story.append(Paragraph(f"1. {text}", normal_style))
                
            elif element[0] == 'space':
                story.append(Spacer(1, 8))
                
            elif element[0] == 'hr':
                story.append(Spacer(1, 10))
                # Simula linha horizontal
                story.append(Paragraph("_" * 80, normal_style))
                story.append(Spacer(1, 10))
        
        # Gera o PDF
        doc.build(story)
        
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
        base_dir / "ANALISE_TECNICA_ESPECIALIZADA.md",
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
            
            if markdown_to_pdf_simple(str(md_file), str(pdf_file)):
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
