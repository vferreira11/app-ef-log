#!/usr/bin/env python3
"""
Análise Comparativa de Algoritmos de Empacotamento
=================================================

Este script testa todos os algoritmos disponíveis com o mesmo conjunto de dados
para determinar qual realmente oferece o melhor empacotamento.
"""

import sys
import os
import pandas as pd
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from core.models import ContainerConfig
from core.algorithms import gpu_optimize_packing, hybrid_intelligent_packing
from core.utils import calculate_efficiency

def create_test_dataset():
    """Cria um dataset de teste consistente para comparação"""
    return pd.DataFrame({
        'SKU': ['SDK1000', 'SDK1001', 'SDK1002', 'SDK1003', 'SDK1004'],
        'Produto': ['Quebra Cabeça', 'Divisória', 'Bandeja', 'Robô', 'Bandeja'],
        'largura': [7, 9, 8, 3, 10], 
        'profundidade': [7, 10, 4, 9, 5],
        'altura': [4, 7, 8, 10, 5],
        'peso': [2, 3, 2.5, 1.5, 4],
        'quantidade': [20, 15, 25, 30, 18]  # Total: 108 blocos
    })

def extract_block_dims(produtos_df):
    """Extrai dimensões dos blocos do DataFrame"""
    block_dims = []
    for _, row in produtos_df.iterrows():
        dims = (int(row['largura']), int(row['profundidade']), int(row['altura']))
        for _ in range(int(row['quantidade'])):
            block_dims.append(dims)
    return block_dims

def calculate_volume_efficiency(placements, block_dims, container):
    """Calcula eficiência volumétrica do empacotamento"""
    if not placements:
        return 0
    
    # Volume total dos blocos empacotados
    total_block_volume = 0
    for placement in placements:
        if len(placement) >= 4:  # x, y, z, block_index
            block_index = placement[3]
            if block_index < len(block_dims):
                lx, ly, lz = block_dims[block_index]
                total_block_volume += lx * ly * lz
    
    # Volume total disponível do container
    container_volume = container.volume_total
    
    return (total_block_volume / container_volume) * 100 if container_volume > 0 else 0

def analyze_gaps(placements, block_dims, container):
    """Analisa gaps e distribuição espacial"""
    if not placements:
        return {"gaps": 0, "compactness": 0, "distribution": "N/A"}
    
    # Calcula bounding box dos blocos empacotados
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = 0
    
    for placement in placements:
        if len(placement) >= 4:
            x, y, z, block_index = placement[:4]
            if block_index < len(block_dims):
                lx, ly, lz = block_dims[block_index]
                min_x = min(min_x, x)
                min_y = min(min_y, y) 
                min_z = min(min_z, z)
                max_x = max(max_x, x + lx)
                max_y = max(max_y, y + ly)
                max_z = max(max_z, z + lz)
    
    # Volume da bounding box
    if min_x != float('inf'):
        bounding_volume = (max_x - min_x) * (max_y - min_y) * (max_z - min_z)
        
        # Volume ocupado pelos blocos
        occupied_volume = sum(block_dims[placement[3]][0] * block_dims[placement[3]][1] * block_dims[placement[3]][2] 
                            for placement in placements if placement[3] < len(block_dims))
        
        compactness = (occupied_volume / bounding_volume * 100) if bounding_volume > 0 else 0
        
        return {
            "bounding_box": (max_x - min_x, max_y - min_y, max_z - min_z),
            "compactness": compactness,
            "gap_ratio": 100 - compactness
        }
    
    return {"bounding_box": (0, 0, 0), "compactness": 0, "gap_ratio": 100}

def test_algorithm(algorithm_name, algorithm_func, container, block_dims, produtos_df):
    """Testa um algoritmo específico e coleta métricas"""
    print(f"\n🧪 Testando: {algorithm_name}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = algorithm_func()
        execution_time = time.time() - start_time
        
        if not result:
            return {
                "algorithm": algorithm_name,
                "success": False,
                "blocks_placed": 0,
                "efficiency": 0,
                "execution_time": execution_time,
                "error": "Nenhum resultado retornado"
            }
        
        # Extrai placements dependendo do tipo de retorno
        if isinstance(result, list):
            placements = result
        else:
            placements = result
        
        blocks_placed = len(placements)
        efficiency = calculate_volume_efficiency(placements, block_dims, container)
        gap_analysis = analyze_gaps(placements, block_dims, container)
        
        print(f"✅ Blocos posicionados: {blocks_placed}/{len(block_dims)}")
        print(f"📊 Eficiência volumétrica: {efficiency:.2f}%")
        print(f"⏱️ Tempo de execução: {execution_time:.3f}s")
        print(f"📐 Compactação: {gap_analysis['compactness']:.2f}%")
        print(f"🕳️ Taxa de gaps: {gap_analysis['gap_ratio']:.2f}%")
        
        return {
            "algorithm": algorithm_name,
            "success": True,
            "blocks_placed": blocks_placed,
            "total_blocks": len(block_dims),
            "placement_rate": (blocks_placed / len(block_dims)) * 100,
            "efficiency": efficiency,
            "compactness": gap_analysis['compactness'],
            "gap_ratio": gap_analysis['gap_ratio'],
            "bounding_box": gap_analysis['bounding_box'],
            "execution_time": execution_time,
            "placements": placements
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Erro: {str(e)}")
        return {
            "algorithm": algorithm_name,
            "success": False,
            "blocks_placed": 0,
            "efficiency": 0,
            "execution_time": execution_time,
            "error": str(e)
        }

def main():
    """Executa análise comparativa completa"""
    print("🔬 ANÁLISE COMPARATIVA DE ALGORITMOS DE EMPACOTAMENTO")
    print("=" * 60)
    
    # Setup do teste
    container = ContainerConfig(dx=100, dy=80, dz=60, quantidade=1)
    produtos_df = create_test_dataset()
    block_dims = extract_block_dims(produtos_df)
    
    print(f"📦 Container: {container.dimensions()}")
    print(f"📊 Dataset: {len(produtos_df)} tipos de produtos")
    print(f"🧱 Total de blocos: {len(block_dims)}")
    print(f"📏 Volume container: {container.volume:,} cm³")
    print(f"📏 Volume total blocos: {sum(l*w*h for l,w,h in block_dims):,} cm³")
    
    # Testa diferentes algoritmos
    results = []
    
    # 1. Algoritmo Híbrido Inteligente
    results.append(test_algorithm(
        "Híbrido Inteligente", 
        lambda: hybrid_intelligent_packing(container, block_dims, produtos_df),
        container, block_dims, produtos_df
    ))
    
    # 2. GPU com Floor Forçado (Chão do Galpão)
    results.append(test_algorithm(
        "GPU + Chão Forçado",
        lambda: gpu_optimize_packing(container, block_dims, len(block_dims), None, force_floor=True),
        container, block_dims, produtos_df
    ))
    
    # 3. GPU Biomecânico
    results.append(test_algorithm(
        "GPU Biomecânico",
        lambda: gpu_optimize_packing(container, block_dims, len(block_dims), produtos_df, force_floor=False),
        container, block_dims, produtos_df
    ))
    
    # 4. GPU Padrão
    results.append(test_algorithm(
        "GPU Padrão",
        lambda: gpu_optimize_packing(container, block_dims, len(block_dims), None, force_floor=False),
        container, block_dims, produtos_df
    ))
    
    # Análise final
    print("\n" + "=" * 60)
    print("📈 RESUMO COMPARATIVO")
    print("=" * 60)
    
    successful_results = [r for r in results if r['success']]
    
    if not successful_results:
        print("❌ Nenhum algoritmo teve sucesso!")
        return
    
    # Ordena por eficiência
    successful_results.sort(key=lambda x: x['efficiency'], reverse=True)
    
    print(f"{'Algoritmo':<20} {'Blocos':<8} {'Efic.%':<8} {'Compact.%':<10} {'Tempo(s)':<8}")
    print("-" * 65)
    
    for result in successful_results:
        print(f"{result['algorithm']:<20} "
              f"{result['blocks_placed']:<8} "
              f"{result['efficiency']:<8.1f} "
              f"{result['compactness']:<10.1f} "
              f"{result['execution_time']:<8.3f}")
    
    # Melhor algoritmo
    best = successful_results[0]
    print(f"\n🏆 MELHOR ALGORITMO: {best['algorithm']}")
    print(f"   ✅ {best['blocks_placed']}/{best['total_blocks']} blocos posicionados")
    print(f"   📊 {best['efficiency']:.2f}% de eficiência volumétrica")
    print(f"   📐 {best['compactness']:.2f}% de compactação")
    print(f"   🕳️ {best['gap_ratio']:.2f}% de gaps")
    
    # Responde à pergunta do usuário
    print(f"\n🤔 RESPOSTA À SUA PERGUNTA:")
    print(f"   • Essa é a melhor possibilidade? {'SIM' if best['efficiency'] > 80 else 'PROVAVELMENTE NÃO'}")
    print(f"   • O algoritmo {best['algorithm']} conseguiu {best['efficiency']:.1f}% de eficiência")
    print(f"   • Taxa de gaps: {best['gap_ratio']:.1f}% (quanto menor, melhor)")
    
    if best['gap_ratio'] > 20:
        print(f"   ⚠️ Alta taxa de gaps sugere possibilidade de melhoria")
    else:
        print(f"   ✅ Baixa taxa de gaps indica empacotamento eficiente")

if __name__ == "__main__":
    main()
