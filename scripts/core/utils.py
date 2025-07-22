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
        Dicionário mapeando dimensões para cores RGB
    """
    # Primeiro, identifica os tipos únicos
    unique_types = list(set(block_dims))
    unique_types.sort()  # Ordena para consistência
    
    # Cores da paleta Viridis em formato RGB para Plotly
    viridis_colors = [
        "rgb(68, 1, 84)",     # roxo escuro - Tipo 1
        "rgb(49, 104, 142)",  # azul escuro - Tipo 2  
        "rgb(38, 130, 142)",  # azul-verde - Tipo 3
        "rgb(31, 158, 137)",  # verde-azulado - Tipo 4
        "rgb(110, 206, 88)",  # verde claro - Tipo 5
        "rgb(181, 222, 43)",  # verde-amarelo - Tipo 6
        "rgb(254, 232, 37)",  # amarelo - Tipo 7
        "rgb(253, 231, 37)",  # amarelo claro - Tipo 8
        "rgb(53, 183, 121)",  # verde médio - Tipo 9
        "rgb(142, 1, 82)"     # magenta - Tipo 10
    ]
    
    colors = {}
    print(f"[DEBUG] Tipos únicos encontrados: {unique_types}")
    
    for i, block_type in enumerate(unique_types):
        if i < len(viridis_colors):
            # Usa cores predefinidas
            color = viridis_colors[i]
            colors[block_type] = color
            print(f"[DEBUG] Tipo {block_type} -> Cor {color}")
        else:
            # Para mais de 10 tipos, gera cores dinamicamente
            try:
                viridis = cm.get_cmap('viridis')
                color_value = i / max(1, len(unique_types) - 1) if len(unique_types) > 1 else 0
                rgba = viridis(color_value)
                rgb_color = f"rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})"
                colors[block_type] = rgb_color
                print(f"[DEBUG] Tipo {block_type} -> Cor dinâmica {rgb_color}")
            except Exception as e:
                # Fallback para cor padrão se matplotlib falhar
                fallback_color = "rgb(68, 1, 84)"  # roxo escuro
                colors[block_type] = fallback_color
                print(f"[DEBUG] Tipo {block_type} -> Cor fallback {fallback_color} (erro: {e})")
    
    print(f"[DEBUG] Mapeamento final: {colors}")
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