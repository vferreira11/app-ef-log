#!/usr/bin/env python3
"""
Teste da lógica de distribuição otimizada - Linha guia Y=0 + Esquerda para direita
"""

import sys
import os
import pandas as pd

# Adiciona o diretório scripts ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.models import ContainerConfig
from scripts.core.algorithms import hybrid_intelligent_packing

def criar_produtos_teste():
    """Cria produtos de teste com diferentes tipos e características"""
    produtos_data = [
        # Tipo 1: Produtos pequenos (demanda alta)
        {"Categoria": "Brinquedos", "Peso (kg)": 0.3, "Previsão Próx. Mês": 80, "Comprimento": 4, "Largura": 3, "Profundidade": 2},
        {"Categoria": "Brinquedos", "Peso (kg)": 0.4, "Previsão Próx. Mês": 70, "Comprimento": 4, "Largura": 3, "Profundidade": 2},
        {"Categoria": "Brinquedos", "Peso (kg)": 0.2, "Previsão Próx. Mês": 90, "Comprimento": 4, "Largura": 3, "Profundidade": 2},
        
        # Tipo 2: Produtos médios (demanda média)
        {"Categoria": "Organizadores", "Peso (kg)": 1.5, "Previsão Próx. Mês": 25, "Comprimento": 6, "Largura": 4, "Profundidade": 3},
        {"Categoria": "Organizadores", "Peso (kg)": 1.2, "Previsão Próx. Mês": 30, "Comprimento": 6, "Largura": 4, "Profundidade": 3},
        {"Categoria": "Organizadores", "Peso (kg)": 1.8, "Previsão Próx. Mês": 20, "Comprimento": 6, "Largura": 4, "Profundidade": 3},
        
        # Tipo 3: Produtos grandes (demanda baixa)
        {"Categoria": "Utilidades", "Peso (kg)": 3.0, "Previsão Próx. Mês": 8, "Comprimento": 8, "Largura": 6, "Profundidade": 4},
        {"Categoria": "Utilidades", "Peso (kg)": 2.5, "Previsão Próx. Mês": 12, "Comprimento": 8, "Largura": 6, "Profundidade": 4},
        {"Categoria": "Utilidades", "Peso (kg)": 3.5, "Previsão Próx. Mês": 5, "Comprimento": 8, "Largura": 6, "Profundidade": 4},
    ]
    
    return pd.DataFrame(produtos_data)

def analisar_distribuicao(alocacoes, block_dims):
    """Analisa a distribuição dos produtos no container"""
    print("\n" + "="*80)
    print("📊 ANÁLISE DA DISTRIBUIÇÃO OTIMIZADA")
    print("="*80)
    
    # Agrupa por Y (profundidade)
    produtos_por_y = {}
    for x, y, z, idx in alocacoes:
        if y not in produtos_por_y:
            produtos_por_y[y] = []
        produtos_por_y[y].append((x, y, z, idx, block_dims[idx]))
    
    # Ordena por Y
    y_ordenados = sorted(produtos_por_y.keys())
    
    print(f"\n🎯 DISTRIBUIÇÃO POR PROFUNDIDADE (Y):")
    for y in y_ordenados:
        produtos = produtos_por_y[y]
        produtos.sort(key=lambda p: p[0])  # Ordena por X (esquerda para direita)
        
        print(f"\nY={y} ({'LINHA GUIA' if y == 0 else 'linha secundária'}): {len(produtos)} produtos")
        for x, y_pos, z, idx, dims in produtos:
            print(f"  • Produto {idx} em X={x}, Z={z} - Dimensões: {dims}")
    
    # Verifica se há produtos na linha guia Y=0
    produtos_linha_guia = len(produtos_por_y.get(0, []))
    print(f"\n🎯 PRODUTOS NA LINHA GUIA (Y=0): {produtos_linha_guia}")
    
    # Analisa distribuição por tipo
    tipos_por_coluna = {}
    for x, y, z, idx in alocacoes:
        tipo = block_dims[idx]
        if tipo not in tipos_por_coluna:
            tipos_por_coluna[tipo] = []
        tipos_por_coluna[tipo].append((x, y, z, idx))
    
    print(f"\n🎯 AGRUPAMENTO POR TIPO:")
    for tipo, produtos in tipos_por_coluna.items():
        y_positions = [p[1] for p in produtos]
        y_min, y_max = min(y_positions), max(y_positions)
        print(f"  • Tipo {tipo}: {len(produtos)} produtos, Y de {y_min} a {y_max}")
    
    print("\n" + "="*80)

def main():
    """Teste principal da distribuição otimizada"""
    print("🎯 TESTE: DISTRIBUIÇÃO OTIMIZADA - LINHA GUIA Y=0 + ESQUERDA→DIREITA")
    print("="*80)
    
    # Configura container
    container = ContainerConfig(dx=30, dy=20, dz=25, quantidade=1)
    print(f"📐 Container: {container.dx}x{container.dy}x{container.dz}")
    
    # Cria produtos de teste
    produtos_df = criar_produtos_teste()
    print(f"\n📦 Produtos de teste: {len(produtos_df)}")
    
    # Gera dimensões dos blocos
    block_dims = []
    for _, row in produtos_df.iterrows():
        demanda = int(row['Previsão Próx. Mês'])
        dims = (int(row['Comprimento']), int(row['Largura']), int(row['Profundidade']))
        
        # Adiciona produtos conforme demanda (mais demanda = mais repetições)
        num_blocos = max(1, demanda // 10)  # 1 bloco a cada 10 de demanda
        for _ in range(num_blocos):
            block_dims.append(dims)
    
    print(f"📊 Total de blocos gerados: {len(block_dims)}")
    
    # Mostra tipos únicos
    tipos_unicos = list(set(block_dims))
    print(f"\n🎯 Tipos únicos de produtos: {len(tipos_unicos)}")
    for i, tipo in enumerate(tipos_unicos):
        count = block_dims.count(tipo)
        print(f"  • Tipo {i+1}: {tipo[0]}x{tipo[1]}x{tipo[2]} - {count} unidades")
    
    # Executa algoritmo híbrido com distribuição otimizada
    print(f"\n🚀 Executando algoritmo híbrido com distribuição otimizada...")
    alocacoes = hybrid_intelligent_packing(container, block_dims, produtos_df)
    
    print(f"\n✅ RESULTADO: {len(alocacoes)} de {len(block_dims)} produtos alocados ({(len(alocacoes)/len(block_dims)*100):.1f}%)")
    
    # Analisa resultados
    if alocacoes:
        analisar_distribuicao(alocacoes, block_dims)
    else:
        print("\n❌ Nenhum produto foi alocado!")

if __name__ == "__main__":
    main()
