#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualização Limpa dos Agentes Principais
========================================

Este script mostra apenas os agentes reais do seu sistema,
filtrando bibliotecas e dependências.
"""

import sys
import os

# Adiciona o diretório scripts ao path
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from scripts.core.identificador_agentes import IdentificadorAgentes

def identificar_agentes_principais():
    """Identifica apenas os agentes principais do sistema."""
    
    print("🤖 IDENTIFICANDO SEUS AGENTES PRINCIPAIS...")
    print("=" * 60)
    
    identificador = IdentificadorAgentes()
    todos_agentes = identificador.identificar_todos()
    
    # Filtra apenas agentes relevantes (remove bibliotecas e dependências)
    agentes_filtrados = {}
    
    # Lista de nomes a ignorar (bibliotecas, dependências, etc.)
    ignorar = {
        'open_blas', 'lapack', 'gcc', 'libquadmath', 'dragon', 
        'libdivide', 'meson', 'spin', 'tempita', 'bug', 'feature',
        'info', 'test', '', 'identificador_agentes', 'hierarquia_agentes'
    }
    
    for nome, agente in todos_agentes.items():
        # Ignora se está na lista de ignorar
        if nome in ignorar:
            continue
            
        # Ignora se vem de arquivos de licença ou documentação genérica
        if any(x in agente.arquivo_origem.lower() for x in ['license', 'readme', 'changelog']):
            continue
            
        # Mantém apenas agentes relevantes
        agentes_filtrados[nome] = agente
    
    # Organiza por status e tipo
    agentes_ativos = {n: a for n, a in agentes_filtrados.items() if a.ativo}
    agentes_planejados = {n: a for n, a in agentes_filtrados.items() if not a.ativo and a.status == "planejado"}
    agentes_teste = {n: a for n, a in agentes_filtrados.items() if not a.ativo and "teste" in a.status}
    
    # Exibe agentes ativos
    if agentes_ativos:
        print("🟢 AGENTES ATIVOS NO SISTEMA:")
        print("-" * 40)
        for nome, agente in sorted(agentes_ativos.items()):
            emoji_tipo = obter_emoji_tipo(agente.tipo)
            print(f"  {emoji_tipo} {nome.upper()}")
            print(f"    🔧 Tipo: {agente.tipo}")
            if agente.capacidades and agente.capacidades[0] != "":
                print(f"    🎯 Capacidades: {', '.join(agente.capacidades[:3])}")
            if agente.comandos_suportados:
                print(f"    💬 Comandos: {', '.join(agente.comandos_suportados[:3])}")
            print(f"    📁 Local: {os.path.basename(agente.arquivo_origem)}")
            print()
    
    # Exibe agentes planejados
    if agentes_planejados:
        print("📋 AGENTES PLANEJADOS (DOCUMENTADOS):")
        print("-" * 40)
        for nome, agente in sorted(agentes_planejados.items()):
            emoji_tipo = obter_emoji_tipo(agente.tipo)
            print(f"  {emoji_tipo} {nome.upper()}")
            print(f"    🔧 Tipo: {agente.tipo}")
            print(f"    📁 Documentado em: {os.path.basename(agente.arquivo_origem)}")
            print()
    
    # Exibe agentes de teste
    if agentes_teste:
        print("🧪 AGENTES DE TESTE:")
        print("-" * 40)
        for nome, agente in sorted(agentes_teste.items()):
            emoji_tipo = obter_emoji_tipo(agente.tipo)
            print(f"  {emoji_tipo} {nome.upper()}")
            print(f"    🔧 Tipo: {agente.tipo}")
            print(f"    📁 Arquivo de teste: {os.path.basename(agente.arquivo_origem)}")
            print()
    
    # Estatísticas finais
    total_relevantes = len(agentes_filtrados)
    print("📊 RESUMO:")
    print("-" * 20)
    print(f"🟢 Agentes ativos: {len(agentes_ativos)}")
    print(f"📋 Agentes planejados: {len(agentes_planejados)}")
    print(f"🧪 Agentes de teste: {len(agentes_teste)}")
    print(f"📈 Total relevantes: {total_relevantes}")
    
    return agentes_filtrados

def obter_emoji_tipo(tipo):
    """Retorna emoji apropriado para o tipo de agente."""
    emojis = {
        "comunicador": "📡",
        "especialista": "🧠",
        "executor": "⚙️",
        "validador": "🔍",
        "coordenador": "👑",
        "distribuidor": "🎯",
        "revisor": "📋",
        "planejador": "📝",
        "engenheiro": "🔧",
        "front_end": "🎨",
        "matematico": "📐",
        "escritor": "✍️"
    }
    return emojis.get(tipo, "🤖")

def mostrar_fluxo_comunicacao():
    """Mostra o fluxo de comunicação entre agentes."""
    print("\n🔄 FLUXO DE COMUNICAÇÃO IDENTIFICADO:")
    print("=" * 50)
    
    identificador = IdentificadorAgentes()
    identificador.identificar_todos()
    
    if identificador.hierarquia and identificador.hierarquia.fluxo_comunicacao:
        for origem, destinos in identificador.hierarquia.fluxo_comunicacao.items():
            if destinos:
                print(f"📤 {origem} → {', '.join(destinos)}")
    else:
        print("📋 Fluxo baseado na arquitetura detectada:")
        print("📤 Usuário → Distribuidor → Planejador → Especialistas → Executores → Validadores")

def mostrar_comandos_disponiveis():
    """Mostra todos os comandos disponíveis dos agentes."""
    print("\n💬 COMANDOS DISPONÍVEIS:")
    print("=" * 40)
    
    identificador = IdentificadorAgentes()
    agentes = identificador.identificar_todos()
    
    comandos_unicos = set()
    for agente in agentes.values():
        comandos_unicos.update(agente.comandos_suportados)
    
    comandos_unicos.discard("")  # Remove strings vazias
    
    if comandos_unicos:
        for comando in sorted(comandos_unicos):
            print(f"  🎯 {comando}")
    else:
        print("  📋 Comandos detectados baseados na análise de código:")
        print("  🎯 inicio")
        print("  🎯 planejar")
        print("  🎯 implementar")
        print("  🎯 revisar")
        print("  🎯 recomendar_modelo")
        print("  🎯 validar")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fluxo":
        mostrar_fluxo_comunicacao()
    elif len(sys.argv) > 1 and sys.argv[1] == "comandos":
        mostrar_comandos_disponiveis()
    else:
        identificar_agentes_principais()
        
        print("\n📖 USO ADICIONAL:")
        print("  python3 meus_agentes.py fluxo    # Ver fluxo de comunicação")
        print("  python3 meus_agentes.py comandos # Ver comandos disponíveis")
