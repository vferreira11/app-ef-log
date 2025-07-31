#!/usr/bin/env python3
"""
Teste simples de importação e execução básica
"""

import sys
import os

# Adiciona caminhos
sys.path.insert(0, '/home/vinao/app-ef-log')
sys.path.insert(0, '/home/vinao/app-ef-log/scripts')
sys.path.insert(0, '/home/vinao/app-ef-log/scripts/core')

print("=== TESTE BÁSICO DE IMPORTAÇÃO ===")

# Teste 1: Importação do ContainerConfig
try:
    from scripts.core.models import ContainerConfig
    print("✅ ContainerConfig importado com sucesso")
    
    # Teste de criação
    container = ContainerConfig(dx=20, dy=20, dz=20)
    print(f"✅ Container criado: {container.dx}x{container.dy}x{container.dz}")
    
except Exception as e:
    print(f"❌ Erro ContainerConfig: {e}")
    import traceback
    traceback.print_exc()

# Teste 2: Pandas
try:
    import pandas as pd
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    print(f"✅ Pandas funcionando: {df.shape}")
except Exception as e:
    print(f"❌ Erro Pandas: {e}")

# Teste 3: Importação da função (apenas a definição)
try:
    with open('/home/vinao/app-ef-log/scripts/core/algorithms.py', 'r') as f:
        content = f.read()
        if 'def hybrid_intelligent_packing' in content:
            print("✅ Função hybrid_intelligent_packing encontrada no arquivo")
        else:
            print("❌ Função hybrid_intelligent_packing NÃO encontrada")
except Exception as e:
    print(f"❌ Erro lendo arquivo: {e}")

print("\n=== FIM DO TESTE ===")
