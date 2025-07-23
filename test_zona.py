#!/usr/bin/env python3
"""Teste simples da zona biomecânica"""

import sys
sys.path.append('scripts')

# Teste direto da função get_zona_biomecanica
print("=== TESTE DA FUNÇÃO ZONA BIOMECÂNICA ===")

# Simula a função (copiada do código)
def get_zona_biomecanica(z, peso):
    """Determina adequação biomecânica por altura e peso - VERSÃO MAIS FLEXÍVEL"""
    if z <= 5:  # 0-5cm: Zona do chão
        return peso >= 1.0  # Aceita peso >= 1kg no chão (mais flexível)
    elif z <= 30:  # 5-30cm: Zona baixa
        return peso >= 0.5  # Aceita peso >= 0.5kg na zona baixa (mais flexível)
    elif z <= 120:  # 30-120cm: Zona ergonômica ideal
        return True  # Qualquer peso
    elif z <= 180:  # 120-180cm: Zona alta
        return peso <= 5.0  # Permite até 5kg na zona alta (mais flexível)
    else:  # >180cm: Zona crítica
        return peso <= 3.0  # Permite até 3kg na zona crítica (mais flexível)

# Testa vários cenários
cenarios = [
    (0, 2.5),   # Z=0, peso 2.5kg
    (5, 2.5),   # Z=5, peso 2.5kg
    (10, 2.5),  # Z=10, peso 2.5kg
    (30, 2.5),  # Z=30, peso 2.5kg
    (50, 2.5),  # Z=50, peso 2.5kg
    (0, 1.8),   # Z=0, peso 1.8kg
    (5, 1.8),   # Z=5, peso 1.8kg
    (10, 1.8),  # Z=10, peso 1.8kg
]

print("Testando cenários (z, peso) -> adequado:")
for z, peso in cenarios:
    adequado = get_zona_biomecanica(z, peso)
    print(f"  Z={z:2d}cm, peso={peso:.1f}kg -> {adequado}")

print("\n=== TESTE CONTAINER BÁSICO ===")
# Dimensões do problema
container_dx, container_dy, container_dz = 30, 40, 50
block_w, block_d, block_h = 9, 7, 10

print(f"Container: {container_dx}x{container_dy}x{container_dz}")
print(f"Bloco: {block_w}x{block_d}x{block_h}")

# Verifica se cabe fisicamente
max_x = container_dx - block_w + 1
max_y = container_dy - block_d + 1  
max_z = container_dz - block_h + 1

print(f"Posições possíveis X: 0 a {max_x-1}")
print(f"Posições possíveis Y: 0 a {max_y-1}")
print(f"Posições possíveis Z: 0 a {max_z-1}")

if max_x > 0 and max_y > 0 and max_z > 0:
    print("✅ Bloco CABE fisicamente no container")
    
    # Testa primeira posição com peso típico
    peso_teste = 2.5
    primeira_adequada = get_zona_biomecanica(0, peso_teste)
    print(f"✅ Posição (0,0,0) adequada para peso {peso_teste}kg? {primeira_adequada}")
else:
    print("❌ Bloco NÃO CABE fisicamente no container")
