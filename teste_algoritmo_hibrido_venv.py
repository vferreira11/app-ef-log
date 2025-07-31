#!/usr/bin/env python3
"""
Teste completo do algoritmo híbrido com agrupamento por tipos
"""

import sys
import os
import pandas as pd

# Adiciona caminhos necessários
sys.path.append('/home/vinao/app-ef-log')
sys.path.append('/home/vinao/app-ef-log/scripts')
sys.path.append('/home/vinao/app-ef-log/scripts/core')

try:
    from scripts.core.models import ContainerConfig
    from scripts.core.algorithms import hybrid_intelligent_packing
    print("✅ Importações realizadas com sucesso")
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    sys.exit(1)

def teste_algoritmo_hibrido_completo():
    """Testa o algoritmo híbrido completo com agrupamento por tipos"""
    print("=== TESTE ALGORITMO HÍBRIDO COM AGRUPAMENTO ===")
    
    # Container de teste
    container = ContainerConfig(dx=50, dy=40, dz=30, quantidade=1)
    print(f"Container: {container.dx}x{container.dy}x{container.dz}")
    
    # Produtos com tipos diferentes para testar agrupamento
    block_dims = [
        (10, 8, 5),   # Tipo 1
        (10, 8, 5),   # Tipo 1 (mesmo)
        (10, 8, 5),   # Tipo 1 (mesmo)
        (12, 6, 4),   # Tipo 2
        (12, 6, 4),   # Tipo 2 (mesmo)
        (8, 10, 3),   # Tipo 3
        (8, 10, 3),   # Tipo 3 (mesmo)
        (15, 5, 6),   # Tipo 4
    ]
    
    # DataFrame com dados dos produtos
    produtos_df = pd.DataFrame({
        'peso': [2.5, 2.5, 2.5, 1.8, 1.8, 3.2, 3.2, 4.1],
        'Categoria': ['Brinquedos', 'Brinquedos', 'Brinquedos', 'Utilidades', 'Utilidades', 'Organizadores', 'Organizadores', 'Utilidades'],
        'Previsão Próx. Mês': [25, 30, 35, 15, 20, 8, 12, 40]
    })
    
    print(f"Produtos para testar: {len(block_dims)}")
    print(f"DataFrame shape: {produtos_df.shape}")
    
    # Executa o algoritmo híbrido
    print("\n🚀 Executando algoritmo híbrido com agrupamento...")
    try:
        alocacoes = hybrid_intelligent_packing(container, block_dims, produtos_df)
        
        print(f"\n📊 RESULTADOS:")
        print(f"Total de alocações: {len(alocacoes)}")
        print(f"Taxa de sucesso: {len(alocacoes)}/{len(block_dims)} = {(len(alocacoes)/len(block_dims)*100):.1f}%")
        
        # Analisa alocações por tipo
        tipos_unicos = list(set(block_dims))
        print(f"\n🎯 ANÁLISE POR TIPO:")
        
        for tipo in tipos_unicos:
            # Encontra todas as alocações deste tipo
            alocacoes_tipo = []
            for alocacao in alocacoes:
                x, y, z, idx = alocacao
                if block_dims[idx] == tipo:
                    alocacoes_tipo.append((x, y, z, idx))
            
            print(f"Tipo {tipo}: {len(alocacoes_tipo)} alocações")
            
            # Mostra posições Y (para verificar agrupamento em colunas)
            if alocacoes_tipo:
                posicoes_y = [alocacao[1] for alocacao in alocacoes_tipo]
                y_min, y_max = min(posicoes_y), max(posicoes_y)
                print(f"  Posições Y: {posicoes_y} (range: {y_min}-{y_max})")
        
        # Mostra algumas alocações detalhadas
        print(f"\n📍 PRIMEIRAS 5 ALOCAÇÕES:")
        for i, alocacao in enumerate(alocacoes[:5]):
            x, y, z, idx = alocacao
            tipo = block_dims[idx]
            print(f"  {i+1}. Produto {idx} ({tipo}) → posição ({x},{y},{z})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = teste_algoritmo_hibrido_completo()
    print(f"\n🏁 Resultado final: {'✅ SUCESSO' if resultado else '❌ FALHA'}")
