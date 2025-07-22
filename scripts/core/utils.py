"""
Funções utilitárias para o sistema de empacotamento.
"""

import random
from typing import List, Tuple, Dict
from matplotlib import cm
import numpy as np


def calculate_max_capacity(container_volume: int, block_dims: List[Tuple[int, int, int]]) -> int:
    """
    Calcula a capacidade máxima teórica do container.
    
    Args:
        container_volume: Volume total do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Número máximo de blocos que cabem teoricamente
    """
    if not block_dims:
        return 0
        
    block_volumes = [lx * ly * lz for lx, ly, lz in block_dims]
    total_block_volume = sum(block_volumes)
    
    # Capacidade baseada no volume
    max_blocks = 0
    used_volume = 0
    for vol in block_volumes:
        if used_volume + vol <= container_volume:
            used_volume += vol
            max_blocks += 1
        else:
            break
    
    return min(max_blocks, len(block_dims))


def map_block_colors(block_dims: List[Tuple[int, int, int]]) -> Dict[Tuple[int, int, int], str]:
    """
    Mapeia cores da paleta Viridis para tipos únicos de bloco.
    
    Args:
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Dicionário mapeando dimensões para cores hexadecimais
    """
    unique_types = list(set(block_dims))
    viridis = cm.get_cmap('viridis')
    
    colors = {}
    for i, block_type in enumerate(unique_types):
        # Mapeia índice para valor entre 0 e 1
        color_value = i / max(1, len(unique_types) - 1) if len(unique_types) > 1 else 0
        rgba = viridis(color_value)
        # Converte RGBA para hex
        hex_color = f"#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}"
        colors[block_type] = hex_color
    
    return colors


def calculate_efficiency(placed_count: int, total_count: int) -> float:
    """
    Calcula a eficiência do empacotamento.
    
    Args:
        placed_count: Número de blocos alocados
        total_count: Número total de blocos
        
    Returns:
        Percentual de eficiência (0-100)
    """
    if total_count == 0:
        return 0.0
    return (placed_count / total_count) * 100


def format_dimensions(dims: Tuple[int, int, int]) -> str:
    """
    Formata dimensões para exibição.
    
    Args:
        dims: Tupla com dimensões (x, y, z)
        
    Returns:
        String formatada das dimensões
    """
    return f"{dims[0]}×{dims[1]}×{dims[2]}"


def generate_random_color() -> str:
    """Gera uma cor hexadecimal aleatória."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def validate_block_data(types_df) -> List[Tuple[int, int, int]]:
    """
    Valida e processa dados dos tipos de bloco.
    
    Args:
        types_df: DataFrame com tipos de bloco
        
    Returns:
        Lista de tuplas de dimensões dos blocos válidos
    """
    # Remove linhas completamente vazias
    valid_df = types_df.dropna(how='all')
    
    # Filtra linhas válidas
    valid_df = valid_df.dropna(subset=["dx", "dy", "dz", "quantidade"])
    valid_df = valid_df[(valid_df["quantidade"] > 0) & 
                       (valid_df["dx"] > 0) & 
                       (valid_df["dy"] > 0) & 
                       (valid_df["dz"] > 0)]
    
    if valid_df.empty:
        return []
    
    # Expande blocos
    block_dims = []
    for _, row in valid_df.iterrows():
        dims = (int(row.dx), int(row.dy), int(row.dz))
        qty = int(row.quantidade)
        block_dims.extend([dims] * qty)
    
    # Ordena por volume (maior primeiro)
    block_dims.sort(key=lambda d: d[0]*d[1]*d[2], reverse=True)
    
    return block_dims