#!/usr/bin/env python3
"""Teste rápido para verificar se a correção da zona biomecânica funcionou"""

import sys
sys.path.append('scripts')

from core.config import ContainerConfig
from core.algorithms import hybrid_intelligent_packing

# Teste com container 30x40x50 e blocos 9x7x10
print("=== TESTE DE CORREÇÃO DA ZONA BIOMECÂNICA ===")

# Container de teste
container = ContainerConfig(30, 40, 50)
print(f"Container: {container.dx}x{container.dy}x{container.dz}")

# Alguns blocos de teste (simulando produtos)
block_dims = [
    (9, 7, 10),   # Bloco 1
    (8, 6, 8),    # Bloco 2
    (5, 5, 5),    # Bloco 3
]
print(f"Blocos de teste: {block_dims}")

# Mock dos dados dos produtos (simulado)
class MockProdutos:
    def __init__(self):
        self.data = [
            {'peso': 2.5, 'categoria': 'móveis'},
            {'peso': 1.8, 'categoria': 'móveis'},
            {'peso': 1.2, 'categoria': 'móveis'},
        ]
    
    def iterrows(self):
        for i, row in enumerate(self.data):
            yield i, row

produtos_df = MockProdutos()

# Testa algoritmo
print("\n=== EXECUTANDO ALGORITMO ===")
try:
    result = hybrid_intelligent_packing(container, block_dims, produtos_df)
    print(f"\n=== RESULTADO ===")
    print(f"Alocações encontradas: {len(result)}")
    print(f"Taxa de sucesso: {len(result)}/{len(block_dims)} ({100*len(result)/len(block_dims):.1f}%)")
    
    if result:
        print("\nPosições alocadas:")
        for i, (x, y, z, produto_idx) in enumerate(result):
            print(f"  Produto {produto_idx}: ({x}, {y}, {z})")
    else:
        print("❌ NENHUM PRODUTO FOI ALOCADO!")
        
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
