"""
Algoritmos de empacotamento 3D otimizados.
"""

import numpy as np
import itertools
from typing import List, Tuple
from .models import ContainerConfig


def get_orientations(lx: int, ly: int, lz: int) -> List[Tuple[int, int, int]]:
    """Retorna todas as orientações possíveis de um bloco."""
    dims = [lx, ly, lz]
    return list(set(itertools.permutations(dims)))


def greedy_pack_floor_based(container: ContainerConfig, block_dims: List[Tuple[int, int, int]]) -> List[tuple]:
    """
    Empacotamento baseado no chão do galpão: preenche plano XY completamente antes de subir em Z.
    Simula um armazém real onde produtos são organizados em camadas no chão (XY) e empilhados em altura (Z).
    
    Convenção matemática:
    - X: Largura (esquerda-direita)
    - Y: Profundidade (frente-trás) 
    - Z: Altura (baixo-cima) - DIREÇÃO DO EMPILHAMENTO
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de alocações (x, y, z, block_index, orientation)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    # Debug: rastrear posições Z para verificar empacotamento por camadas (altura)
    z_positions = []
    
    for bloco_idx, original_dims in enumerate(block_dims):
        colocado = False
        orientations = get_orientations(*original_dims)
        
        # Tenta cada orientação
        for orientation in orientations:
            if colocado:
                break
            lx, ly, lz = orientation
            
            # REGRA DO GALPÃO: Preenche camadas Z (altura) de baixo para cima
            # Percorre camadas Z de baixo para cima (empilhamento em altura)
            for z in range(container.dz - lz + 1):
                if colocado:
                    break
                # Para cada camada Z, percorre todo o plano XY (chão do galpão)
                for x in range(container.dx - lx + 1):
                    if colocado:
                        break
                    for y in range(container.dy - ly + 1):
                        # Verifica se o espaço está livre
                        if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                            # Marca como ocupado
                            ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                            # Salva com a orientação usada
                            placements.append((x, y, z, bloco_idx, orientation))
                            z_positions.append(z)
                            colocado = True
                            break
        
        if not colocado:
            break
    
    # Debug: estatísticas das camadas Z (altura)
    if z_positions:
        unique_z = list(set(z_positions))
        unique_z.sort()
        print(f"[DEBUG] Camadas Z (altura) ocupadas: {unique_z}")
        for z_layer in unique_z:
            count = z_positions.count(z_layer)
            print(f"[DEBUG] Camada Z={z_layer}: {count} blocos")
    
    return placements


def greedy_pack_with_rotation(container: ContainerConfig, block_dims: List[Tuple[int, int, int]]) -> List[tuple]:
    """
    Empacotamento sequencial com ROTAÇÃO: maximiza preenchimento.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de alocações (x, y, z, block_index, orientation)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    for bloco_idx, original_dims in enumerate(block_dims):
        colocado = False
        orientations = get_orientations(*original_dims)
        
        # Tenta cada orientação
        for orientation in orientations:
            if colocado:
                break
            lx, ly, lz = orientation
            
            # Percorre o container sequencialmente
            for x in range(container.dx - lx + 1):
                if colocado:
                    break
                for y in range(container.dy - ly + 1):
                    if colocado:
                        break
                    for z in range(container.dz - lz + 1):
                        # Verifica se o espaço está livre
                        if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                            # Marca como ocupado
                            ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                            # Salva com a orientação usada
                            placements.append((x, y, z, bloco_idx, orientation))
                            colocado = True
                            break
        
        if not colocado:
            break
    
    return placements


def gpu_optimize_packing(container: ContainerConfig, block_dims: List[Tuple[int, int, int]], max_capacity: int) -> List[tuple]:
    """
    Otimização de empacotamento com algoritmo GPU simulado.
    Usa regra de chão de galpão (Z=altura) para distribuição realística.
    Distribui blocos por múltiplos containers quando quantidade > 1.
    
    Args:
        container: Configuração do container (pode ter múltiplos containers)
        block_dims: Lista de dimensões dos blocos
        max_capacity: Capacidade máxima de blocos
        
    Returns:
        Lista de alocações otimizadas com offset para múltiplos containers
    """
    # Limita aos blocos que cabem teoricamente
    target_blocks = min(max_capacity, len(block_dims))
    target_dims = block_dims[:target_blocks]
    
    if container.quantidade == 1:
        # Container único - algoritmo original
        placements = greedy_pack_floor_based(container, target_dims)
        return placements
    
    # Múltiplos containers - distribui os blocos
    all_placements = []
    blocks_per_container = len(target_dims) // container.quantidade
    remaining_blocks = len(target_dims) % container.quantidade
    
    print(f"[DEBUG] Distribuindo {len(target_dims)} blocos em {container.quantidade} containers:")
    print(f"[DEBUG] {blocks_per_container} blocos por container, {remaining_blocks} extras")
    
    start_idx = 0
    
    for container_idx in range(container.quantidade):
        # Calcula quantos blocos este container vai ter
        blocks_for_this = blocks_per_container
        if container_idx < remaining_blocks:
            blocks_for_this += 1
            
        if blocks_for_this == 0:
            continue
            
        # Pega os blocos para este container
        container_blocks = target_dims[start_idx:start_idx + blocks_for_this]
        
        # Cria container individual
        single_container = ContainerConfig(container.dx, container.dy, container.dz, 1)
        
        # Empacota neste container
        container_placements = greedy_pack_floor_based(single_container, container_blocks)
        
        # Aplica offset X para separar containers visualmente
        offset_x = container_idx * (container.dx + 10)  # 10 unidades de espaçamento
        
        # Adiciona offset nas coordenadas e ajusta índices dos blocos
        for placement in container_placements:
            if len(placement) == 5:
                x, y, z, block_idx, orientation = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + block_idx, orientation)
            else:
                x, y, z, block_idx = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + block_idx)
            
            all_placements.append(adjusted_placement)
        
        print(f"[DEBUG] Container {container_idx + 1}: {len(container_placements)} blocos colocados (offset X={offset_x})")
        start_idx += blocks_for_this
    
    print(f"[DEBUG] Total final: {len(all_placements)} blocos em {container.quantidade} containers")
    return all_placements


def hybrid_pack(container: ContainerConfig, block_dims: List[Tuple[int, int, int]], gpu_placements: List[tuple]) -> List[tuple]:
    """
    Algoritmo híbrido: usa resultado GPU e preenche buracos com Greedy.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        gpu_placements: Alocações do algoritmo GPU
        
    Returns:
        Lista de alocações híbridas
    """
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    placements = []
    
    # Marca posições ocupadas pelo GPU
    for placement in gpu_placements:
        if len(placement) == 5:
            x0, y0, z0, o, orientation = placement
            lx, ly, lz = orientation
        else:
            x0, y0, z0, o = placement
            lx, ly, lz = block_dims[o]
            
        if x0 + lx <= container.dx and y0 + ly <= container.dy and z0 + lz <= container.dz:
            ocupado[x0:x0+lx, y0:y0+ly, z0:z0+lz] = True
            placements.append(placement)
    
    # Tenta encaixar blocos restantes nos buracos
    used_blocks = len(placements)
    for bloco_idx in range(used_blocks, len(block_dims)):
        lx, ly, lz = block_dims[bloco_idx]
        colocado = False
        
        for x in range(container.dx - lx + 1):
            if colocado: 
                break
            for y in range(container.dy - ly + 1):
                if colocado: 
                    break
                for z in range(container.dz - lz + 1):
                    if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                        ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                        placements.append((x, y, z, bloco_idx))
                        colocado = True
                        break
    
    return placements