"""
Utility functions for 3D packing system

This module contains helper functions used throughout the application.
"""

import itertools
import matplotlib
import matplotlib.colors
from typing import List, Tuple, Dict


def get_orientations(lx: int, ly: int, lz: int) -> List[Tuple[int, int, int]]:
    """
    Generate all possible orientations (rotations) of a block.
    
    Args:
        lx: Block width
        ly: Block depth
        lz: Block height
        
    Returns:
        List of tuples representing all unique orientations
    """
    dims = [lx, ly, lz]
    return list(set(itertools.permutations(dims)))


def generate_viridis_colors(n_types: int) -> Dict[int, str]:
    """
    Generate colors from the viridis palette for different block types.
    
    Args:
        n_types: Number of different block types
        
    Returns:
        Dictionary mapping type index to hex color
    """
    if n_types == 0:
        return {}
    
    viridis = matplotlib.cm.get_cmap('viridis', n_types)
    return {i: matplotlib.colors.to_hex(viridis(i)) for i in range(n_types)}


def map_block_colors(block_dims: List[Tuple[int, int, int]]) -> Dict[Tuple[int, int, int], str]:
    """
    Map unique block dimensions to viridis colors.
    
    Args:
        block_dims: List of block dimensions
        
    Returns:
        Dictionary mapping block dimensions to hex colors
    """
    unique_dims = list(set(block_dims))
    colors = generate_viridis_colors(len(unique_dims))
    return {dims: colors[i] for i, dims in enumerate(unique_dims)}


def calculate_max_capacity(container_volume: int, block_dims: List[Tuple[int, int, int]]) -> int:
    """
    Calculate theoretical maximum capacity of container.
    
    Args:
        container_volume: Total volume of the container
        block_dims: List of block dimensions
        
    Returns:
        Maximum number of blocks that fit theoretically
    """
    if not block_dims:
        return 0
    
    block_volumes = [lx * ly * lz for lx, ly, lz in block_dims]
    used_volume = 0
    max_blocks = 0
    
    for vol in block_volumes:
        if used_volume + vol <= container_volume:
            used_volume += vol
            max_blocks += 1
        else:
            break
    
    return max_blocks


def validate_placement(x: int, y: int, z: int, lx: int, ly: int, lz: int,
                      container_dx: int, container_dy: int, container_dz: int) -> bool:
    """
    Validate if a block placement fits within container bounds.
    
    Args:
        x, y, z: Block position
        lx, ly, lz: Block dimensions
        container_dx, container_dy, container_dz: Container dimensions
        
    Returns:
        True if placement is valid, False otherwise
    """
    return (x + lx <= container_dx and 
            y + ly <= container_dy and 
            z + lz <= container_dz and
            x >= 0 and y >= 0 and z >= 0)


def format_dimensions(dims: Tuple[int, int, int]) -> str:
    """
    Format dimensions tuple as readable string.
    
    Args:
        dims: Dimensions tuple (x, y, z)
        
    Returns:
        Formatted string like "10x20x30"
    """
    return f"{dims[0]}x{dims[1]}x{dims[2]}"


def calculate_efficiency(placed_blocks: int, total_blocks: int) -> float:
    """
    Calculate packing efficiency as percentage.
    
    Args:
        placed_blocks: Number of successfully placed blocks
        total_blocks: Total number of blocks requested
        
    Returns:
        Efficiency percentage (0-100)
    """
    if total_blocks == 0:
        return 0.0
    return (placed_blocks / total_blocks) * 100.0
