#!/usr/bin/env python3
"""
Teste específico para o problema de alocação
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from core.models import ContainerConfig
from core.algorithms import hybrid_intelligent_packing

def test_specific_case():
    """Testa o cenário específico que está falhando"""
    
    # Container exato do problema
    container = ContainerConfig(dx=30, dy=40, dz=50, quantidade=1)
    
    # Blocos específicos do problema
    block_dims = [(9, 7, 10)] * 5  # 5 blocos iguais
    
    # DataFrame específico
    produtos_df = pd.DataFrame({
        'peso': [2.0, 2.0, 2.0, 2.0, 2.0],
        'Categoria': ['Organizadores', 'Organizadores', 'Utilidades', 'Organizadores', 'Utilidades']
    })
    
    print("🔍 TESTE ESPECÍFICO - CONTAINER E BLOCOS DO PROBLEMA")
    print(f"📦 Container: {container.dx}x{container.dy}x{container.dz}")
    print(f"🧱 Bloco: 9x7x10 (cabe? X: {9 <= 30}, Y: {7 <= 40}, Z: {10 <= 50})")
    print(f"📊 Dataset: {len(produtos_df)} produtos")
    
    # Executa algoritmo
    resultado = hybrid_intelligent_packing(container, block_dims, produtos_df)
    
    print(f"\n✅ Resultado: {len(resultado)} blocos alocados de {len(block_dims)} disponíveis")
    
    if len(resultado) == 0:
        print("❌ PROBLEMA CONFIRMADO: Nenhum bloco foi alocado!")
        
        # Teste manual básico
        print("\n🔧 TESTE MANUAL BÁSICO:")
        print(f"- Primeiro bloco (9x7x10) na posição (0,0,0)")
        print(f"- Cabe em X? {9 <= 30} (9 <= 30)")
        print(f"- Cabe em Y? {7 <= 40} (7 <= 40)")  
        print(f"- Cabe em Z? {10 <= 50} (10 <= 50)")
        print(f"- Peso 2.0kg adequado para Z=0? Deveria ser SIM")
        
    return resultado

if __name__ == "__main__":
    test_specific_case()
