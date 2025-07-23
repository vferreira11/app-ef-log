#!/usr/bin/env python3
"""
Script de teste para visualizar o novo plano de base profissional.
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from core.algorithms import hybrid_intelligent_packing
from core.visualization import create_3d_plot
from core.models import ContainerConfig

def test_floor_visualization():
    """Teste da visualização com plano de base profissional"""
    
    # Configuração básica de teste
    container = ContainerConfig(
        dx=200, dy=150, dz=120,  # Container menor para teste
        quantidade=1
    )
    
    # Blocos de teste simples
    blocos = [
        (40, 30, 20),  # Bloco pequeno
        (60, 40, 30),  # Bloco médio  
        (50, 35, 25),  # Bloco médio-pequeno
        (30, 30, 40),  # Bloco alto e fino
        (70, 20, 15),  # Bloco comprido e baixo
    ]
    
    # Cria DataFrame de produtos simulado
    produtos_df = pd.DataFrame({
        'largura': [40, 60, 50, 30, 70],
        'profundidade': [30, 40, 35, 30, 20],
        'altura': [20, 30, 25, 40, 15],
        'peso': [5, 10, 8, 6, 7],
        'quantidade': [2, 1, 3, 2, 1]
    })
    
    print("🚀 Testando visualização com plano de base profissional...")
    print(f"Container: {container.dimensions()}")
    print(f"Blocos: {len(blocos)} tipos diferentes")
    
    # Executa algoritmo híbrido
    print("\n📦 Executando empacotamento híbrido...")
    resultado = hybrid_intelligent_packing(container, blocos, produtos_df)
    
    if not resultado:
        print("❌ Falha no empacotamento")
        return
    
    placements = resultado
    print(f"✅ Empacotamento realizado: {len(placements)} blocos posicionados")
    
    # Cria cores para os tipos de blocos
    block_colors = {}
    colors = ['red', 'blue', 'green', 'yellow', 'purple']
    for i, bloco in enumerate(set(blocos)):
        block_colors[bloco] = colors[i % len(colors)]
    
    # Cria visualização com plano de base
    print("\n🎨 Criando visualização 3D com plano de base...")
    fig = create_3d_plot(container, placements, blocos, block_colors)
    
    # Salva visualização
    output_path = "test_floor_visualization.html"
    fig.write_html(output_path)
    print(f"💾 Visualização salva em: {output_path}")
    print(f"🌐 Abra o arquivo em um navegador para ver o resultado")
    
    # Mostra a figura (se disponível)
    try:
        fig.show()
        print("📱 Visualização aberta no navegador padrão")
    except Exception as e:
        print(f"⚠️  Não foi possível abrir automaticamente: {e}")
        print(f"🔗 Abra manualmente o arquivo: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    test_floor_visualization()
