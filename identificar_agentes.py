#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Identificação Rápida de Agentes
========================================

Uso rápido:
    python identificar_agentes.py

Ou importe no seu código:
    from identificar_agentes import identificar_meus_agentes
    agentes = identificar_meus_agentes()
"""

import sys
import os

# Adiciona o diretório scripts ao path
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from scripts.core.identificador_agentes import IdentificadorAgentes

def identificar_meus_agentes():
    """
    Função simples para identificar todos os agentes do seu projeto.
    
    Returns:
        Dict com informações de todos os agentes encontrados
    """
    print("🔍 Identificando seus agentes...")
    
    identificador = IdentificadorAgentes()
    agentes = identificador.identificar_todos()
    
    print("\n" + identificador.gerar_relatorio_visual())
    
    return agentes

def listar_agentes_rapido():
    """Lista rápida apenas com nomes e status."""
    identificador = IdentificadorAgentes()
    agentes = identificador.identificar_todos()
    
    print("🤖 SEUS AGENTES:")
    print("=" * 40)
    
    for nome, agente in sorted(agentes.items()):
        status_emoji = "🟢" if agente.ativo else "🔴"
        print(f"{status_emoji} {nome} ({agente.tipo})")
    
    print(f"\n📊 Total: {len(agentes)} agentes")
    return agentes

def mostrar_agente_especifico(nome_agente):
    """Mostra detalhes de um agente específico."""
    identificador = IdentificadorAgentes()
    agentes = identificador.identificar_todos()
    
    agente = agentes.get(nome_agente)
    if not agente:
        print(f"❌ Agente '{nome_agente}' não encontrado!")
        print(f"Agentes disponíveis: {', '.join(agentes.keys())}")
        return None
    
    print(f"🤖 DETALHES DO AGENTE: {nome_agente}")
    print("=" * 50)
    print(f"📍 Tipo: {agente.tipo}")
    print(f"🟢 Status: {agente.status}")
    print(f"🎯 Ativo: {'Sim' if agente.ativo else 'Não'}")
    print(f"🎨 Cor: {agente.cor_codigo}")
    print(f"📂 Arquivo: {agente.arquivo_origem}")
    print(f"⭐ Prioridade: {agente.prioridade}")
    
    if agente.capacidades:
        print(f"🛠️  Capacidades: {', '.join(agente.capacidades)}")
    
    if agente.comandos_suportados:
        print(f"💬 Comandos: {', '.join(agente.comandos_suportados)}")
    
    if agente.descricao:
        print(f"📝 Descrição: {agente.descricao}")
    
    return agente

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "lista":
            listar_agentes_rapido()
        elif comando == "detalhes" and len(sys.argv) > 2:
            nome_agente = sys.argv[2]
            mostrar_agente_especifico(nome_agente)
        else:
            print("Uso:")
            print("  python identificar_agentes.py           # Relatório completo")
            print("  python identificar_agentes.py lista     # Lista rápida")
            print("  python identificar_agentes.py detalhes <nome>  # Detalhes de um agente")
    else:
        # Identificação completa
        identificar_meus_agentes()
