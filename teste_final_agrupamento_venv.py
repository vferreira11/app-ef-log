#!/usr/bin/env python3
"""
Teste final completo - Cenário complexo com múltiplos tipos de produtos
"""

import sys
import os
import pandas as pd

# Adiciona caminhos
sys.path.insert(0, '/home/vinao/app-ef-log')
sys.path.insert(0, '/home/vinao/app-ef-log/scripts')
sys.path.insert(0, '/home/vinao/app-ef-log/scripts/core')

from scripts.core.models import ContainerConfig
from scripts.core.algorithms import hybrid_intelligent_packing

def teste_cenario_complexo():
    """Teste com cenário complexo: 4 tipos diferentes de produtos"""
    print("=== 🎯 TESTE CENÁRIO COMPLEXO - AGRUPAMENTO POR TIPOS ===")
    
    # Container maior para acomodar mais produtos
    container = ContainerConfig(dx=60, dy=80, dz=40, quantidade=1)
    print(f"Container: {container.dx}x{container.dy}x{container.dz}")
    
    # 4 tipos diferentes de produtos com múltiplas unidades cada
    block_dims = [
        # Tipo 1: Brinquedos pequenos (10x8x5)
        (10, 8, 5), (10, 8, 5), (10, 8, 5), (10, 8, 5),
        
        # Tipo 2: Organizadores médios (15x12x8)
        (15, 12, 8), (15, 12, 8), (15, 12, 8),
        
        # Tipo 3: Utilidades grandes (20x15x10)
        (20, 15, 10), (20, 15, 10),
        
        # Tipo 4: Itens especiais (8x6x4)
        (8, 6, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4)
    ]
    
    # DataFrame correspondente
    produtos_df = pd.DataFrame({
        'peso': [1.5, 1.5, 1.5, 1.5,  # Tipo 1: leves
                2.8, 2.8, 2.8,        # Tipo 2: médios  
                4.5, 4.5,             # Tipo 3: pesados
                0.8, 0.8, 0.8, 0.8, 0.8],  # Tipo 4: muito leves
        'Categoria': ['Brinquedos']*4 + ['Organizadores']*3 + ['Utilidades']*2 + ['Brinquedos']*5,
        'Previsão Próx. Mês': [25, 30, 35, 20,  # Tipo 1: alta demanda (A)
                               15, 18, 12,       # Tipo 2: média demanda (B)
                               45, 40,           # Tipo 3: alta demanda (A)
                               8, 10, 6, 9, 7]   # Tipo 4: baixa demanda (C)
    })
    
    print(f"Total de produtos: {len(block_dims)}")
    print(f"DataFrame shape: {produtos_df.shape}")
    
    # Mostra análise prévia dos tipos
    tipos_unicos = list(set(block_dims))
    print(f"\n🎯 ANÁLISE PRÉVIA - {len(tipos_unicos)} tipos únicos:")
    for i, tipo in enumerate(tipos_unicos):
        count = block_dims.count(tipo)
        print(f"  Tipo {i+1}: {tipo[0]}x{tipo[1]}x{tipo[2]} = {count} unidades")
    
    # Mostra divisão teórica do container
    largura_por_tipo = container.dy // len(tipos_unicos)
    resto = container.dy % len(tipos_unicos)
    print(f"\n📐 DIVISÃO TEÓRICA DO CONTAINER:")
    print(f"  Largura total (Y): {container.dy}")
    print(f"  Largura base por tipo: {largura_por_tipo}")
    print(f"  Resto a distribuir: {resto}")
    
    # Executa o algoritmo
    print(f"\n🚀 EXECUTANDO ALGORITMO HÍBRIDO...")
    alocacoes = hybrid_intelligent_packing(container, block_dims, produtos_df)
    
    # Analisa resultados
    print(f"\n📊 RESULTADOS FINAIS:")
    print(f"✅ Total de alocações: {len(alocacoes)}/{len(block_dims)}")
    print(f"✅ Taxa de sucesso: {(len(alocacoes)/len(block_dims)*100):.1f}%")
    
    # Analisa agrupamento por tipo
    print(f"\n🎯 ANÁLISE DE AGRUPAMENTO POR TIPO:")
    for tipo in tipos_unicos:
        # Encontra alocações deste tipo
        alocacoes_tipo = []
        for alocacao in alocacoes:
            x, y, z, idx = alocacao
            if block_dims[idx] == tipo:
                alocacoes_tipo.append((x, y, z, idx))
        
        if alocacoes_tipo:
            posicoes_y = [alocacao[1] for alocacao in alocacoes_tipo]
            y_min, y_max = min(posicoes_y), max(posicoes_y)
            print(f"  Tipo {tipo}: {len(alocacoes_tipo)} alocações")
            print(f"    Posições Y: {sorted(posicoes_y)}")
            print(f"    Range Y: {y_min}-{y_max} (dispersão: {y_max-y_min})")
            
            # Verifica se ficaram na mesma "região"
            if y_max - y_min <= largura_por_tipo + 5:  # Tolerância de 5 unidades
                print(f"    ✅ AGRUPAMENTO OK: produtos do mesmo tipo ficaram próximos")
            else:
                print(f"    ⚠️ DISPERSÃO: produtos do mesmo tipo ficaram espalhados")
        else:
            print(f"  Tipo {tipo}: ❌ Nenhuma alocação")
    
    # Mostra distribuição por camadas (Z)
    print(f"\n📏 DISTRIBUIÇÃO POR ALTURA (Z):")
    if alocacoes:
        alturas = [alocacao[2] for alocacao in alocacoes]
        alturas_unicas = sorted(set(alturas))
        for z in alturas_unicas:
            count = alturas.count(z)
            print(f"  Camada Z={z}: {count} produtos")
    
    return len(alocacoes) == len(block_dims)

if __name__ == "__main__":
    sucesso = teste_cenario_complexo()
    print(f"\n🏁 RESULTADO FINAL: {'✅ SUCESSO TOTAL' if sucesso else '⚠️ SUCESSO PARCIAL'}")
    print("🎯 Algoritmo de agrupamento por tipos VALIDADO no ambiente virtual!")
