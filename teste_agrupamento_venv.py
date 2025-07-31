#!/usr/bin/env python3
"""
Teste do algoritmo de agrupamento por tipos dentro do venv
"""

import sys
import os

# Adiciona caminhos necessários
sys.path.append('/home/vinao/app-ef-log')
sys.path.append('/home/vinao/app-ef-log/scripts')
sys.path.append('/home/vinao/app-ef-log/scripts/core')

def teste_agrupamento_tipos():
    """Testa a lógica de agrupamento por tipos de produtos"""
    print("=== TESTE DE AGRUPAMENTO POR TIPOS ===")
    
    # Simula produtos com diferentes tipos
    block_dims = [
        (10, 8, 5),   # Tipo 1
        (10, 8, 5),   # Tipo 1 (mesmo)
        (12, 6, 4),   # Tipo 2
        (12, 6, 4),   # Tipo 2 (mesmo)
        (8, 10, 3),   # Tipo 3
        (8, 10, 3),   # Tipo 3 (mesmo)
        (15, 5, 6),   # Tipo 4
    ]
    
    print(f"Total de blocos: {len(block_dims)}")
    
    # 🎯 ETAPA 1: Análise de tipos únicos
    tipos_unicos = list(set(block_dims))
    print(f"Tipos únicos encontrados: {len(tipos_unicos)}")
    
    for i, tipo in enumerate(tipos_unicos):
        count = block_dims.count(tipo)
        print(f"  Tipo {i+1}: {tipo[0]}x{tipo[1]}x{tipo[2]} - {count} unidades")
    
    # 🎯 ETAPA 2: Divisão do container em colunas
    container_dy = 40  # Largura do container
    num_tipos = len(tipos_unicos)
    largura_por_tipo = container_dy // num_tipos
    resto_largura = container_dy % num_tipos
    
    print(f"\n=== DIVISÃO EM COLUNAS ===")
    print(f"Container largura (Y): {container_dy}")
    print(f"Número de tipos: {num_tipos}")
    print(f"Largura base por tipo: {largura_por_tipo}")
    print(f"Resto a distribuir: {resto_largura}")
    
    # Calcula limites de cada coluna
    limites_colunas = {}
    y_atual = 0
    
    for i, tipo in enumerate(tipos_unicos):
        # Distribui o resto nas primeiras colunas
        largura_coluna = largura_por_tipo + (1 if i < resto_largura else 0)
        y_inicio = y_atual
        y_fim = y_atual + largura_coluna
        limites_colunas[tipo] = (y_inicio, y_fim)
        y_atual = y_fim
        
        print(f"  Tipo {tipo}: Coluna Y={y_inicio} até Y={y_fim-1} (largura={largura_coluna})")
    
    # 🎯 ETAPA 3: Verifica se produtos cabem em suas colunas
    print(f"\n=== VERIFICAÇÃO DE COMPATIBILIDADE ===")
    for tipo in tipos_unicos:
        y_inicio, y_fim = limites_colunas[tipo]
        largura_disponivel = y_fim - y_inicio
        produto_largura = tipo[1]  # dimensão Y do produto
        
        compativel = produto_largura <= largura_disponivel
        status = "✅ CABE" if compativel else "❌ NÃO CABE"
        
        print(f"  Tipo {tipo}: precisa {produto_largura}, tem {largura_disponivel} → {status}")
    
    print(f"\n✅ Teste de agrupamento por tipos concluído com sucesso!")
    return True

if __name__ == "__main__":
    try:
        resultado = teste_agrupamento_tipos()
        print(f"\nResultado final: {resultado}")
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
