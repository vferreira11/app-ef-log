#!/usr/bin/env python3
"""
Teste direto da importação da função hybrid_intelligent_packing
"""

import sys
import os

# Adiciona caminhos
sys.path.insert(0, '/home/vinao/app-ef-log')
sys.path.insert(0, '/home/vinao/app-ef-log/scripts')
sys.path.insert(0, '/home/vinao/app-ef-log/scripts/core')

print("=== TESTE IMPORTAÇÃO DIRETA DA FUNÇÃO ===")

try:
    print("1. Importando numpy...")
    import numpy as np
    print("✅ numpy importado")
    
    print("2. Importando pandas...")
    import pandas as pd
    print("✅ pandas importado")
    
    print("3. Importando ContainerConfig...")
    from scripts.core.models import ContainerConfig
    print("✅ ContainerConfig importado")
    
    print("4. Tentando importar hybrid_intelligent_packing...")
    from scripts.core.algorithms import hybrid_intelligent_packing
    print("✅ hybrid_intelligent_packing importado com sucesso!")
    
    print("5. Testando execução básica...")
    container = ContainerConfig(dx=20, dy=20, dz=20)
    block_dims = [(5, 5, 5), (6, 4, 3)]
    produtos_df = pd.DataFrame({
        'peso': [1.0, 2.0],
        'Categoria': ['Teste', 'Teste'],
        'Previsão Próx. Mês': [10, 15]
    })
    
    print("6. Executando função...")
    resultado = hybrid_intelligent_packing(container, block_dims, produtos_df)
    print(f"✅ Função executada! Resultado: {len(resultado)} alocações")
    
    for i, alocacao in enumerate(resultado):
        print(f"  Alocação {i}: {alocacao}")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Erro na execução: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
