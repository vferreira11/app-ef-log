"""
3D packing algorithms

This module contains the core algorithms for 3D block packing optimization.
"""

import numpy as np
import streamlit as st
from typing import List, Tuple
from .models import ContainerConfig, Placement
from .utils import get_orientations, validate_placement


def greedy_pack_sequential(container: ContainerConfig, 
                         block_dims: List[Tuple[int, int, int]]) -> List[Placement]:
    """
    Sequential greedy packing algorithm without rotation.
    
    Fills the container sequentially (x -> y -> z) without leaving gaps.
    
    Args:
        container: Container configuration
        block_dims: List of block dimensions
        
    Returns:
        List of block placements
    """
    placements = []
    occupied = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    for block_idx, (lx, ly, lz) in enumerate(block_dims):
        placed = False
        
        # Search sequentially through container space
        for x in range(container.dx - lx + 1):
            if placed:
                break
            for y in range(container.dy - ly + 1):
                if placed:
                    break
                for z in range(container.dz - lz + 1):
                    # Check if space is completely free
                    if not occupied[x:x+lx, y:y+ly, z:z+lz].any():
                        # Mark space as occupied
                        occupied[x:x+lx, y:y+ly, z:z+lz] = True
                        # Add placement
                        placements.append(Placement(x, y, z, block_idx))
                        placed = True
                        break
        
        if not placed:
            st.warning(f"⚠️ Could not place block {block_idx+1}. Stopping at {len(placements)} blocks.")
            break
    
    return placements


def greedy_pack_with_rotation(container: ContainerConfig, 
                            block_dims: List[Tuple[int, int, int]]) -> List[Placement]:
    """
    Sequential greedy packing algorithm with rotation support.
    
    Tries all possible orientations for each block to maximize packing.
    
    Args:
        container: Container configuration
        block_dims: List of block dimensions
        
    Returns:
        List of block placements with orientation info
    """
    placements = []
    occupied = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    for block_idx, original_dims in enumerate(block_dims):
        placed = False
        orientations = get_orientations(*original_dims)
        
        # Try each possible orientation
        for orientation in orientations:
            if placed:
                break
            lx, ly, lz = orientation
            
            # Search sequentially through container space
            for x in range(container.dx - lx + 1):
                if placed:
                    break
                for y in range(container.dy - ly + 1):
                    if placed:
                        break
                    for z in range(container.dz - lz + 1):
                        # Check if space is free
                        if not occupied[x:x+lx, y:y+ly, z:z+lz].any():
                            # Mark as occupied
                            occupied[x:x+lx, y:y+ly, z:z+lz] = True
                            # Add placement with orientation
                            placements.append(Placement(x, y, z, block_idx, orientation))
                            placed = True
                            break
        
        if not placed:
            st.warning(f"⚠️ Block {block_idx+1} could not fit in any orientation. Stopping.")
            break
    
    return placements


def hybrid_pack(container: ContainerConfig, 
               block_dims: List[Tuple[int, int, int]], 
               gpu_placements: List[Placement]) -> List[Placement]:
    """
    Hybrid algorithm: uses GPU results and fills gaps with greedy approach.
    
    Args:
        container: Container configuration
        block_dims: List of block dimensions
        gpu_placements: Initial placements from GPU algorithm
        
    Returns:
        Enhanced list of placements
    """
    occupied = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    final_placements = []
    
    # Mark spaces occupied by GPU placements
    for placement in gpu_placements:
        if placement.orientation:
            lx, ly, lz = placement.orientation
        else:
            lx, ly, lz = block_dims[placement.block_index]
        
        if validate_placement(placement.x, placement.y, placement.z, lx, ly, lz,
                            container.dx, container.dy, container.dz):
            occupied[placement.x:placement.x+lx, 
                    placement.y:placement.y+ly, 
                    placement.z:placement.z+lz] = True
            final_placements.append(placement)
    
    # Try to fit remaining blocks in gaps
    used_blocks = len(final_placements)
    for block_idx in range(used_blocks, len(block_dims)):
        lx, ly, lz = block_dims[block_idx]
        placed = False
        
        for x in range(container.dx - lx + 1):
            if placed:
                break
            for y in range(container.dy - ly + 1):
                if placed:
                    break
                for z in range(container.dz - lz + 1):
                    if not occupied[x:x+lx, y:y+ly, z:z+lz].any():
                        occupied[x:x+lx, y:y+ly, z:z+lz] = True
                        final_placements.append(Placement(x, y, z, block_idx))
                        placed = True
                        break
    
    return final_placements


def gpu_optimize_packing(container: ContainerConfig, 
                        block_dims: List[Tuple[int, int, int]], 
                        target_blocks: int) -> List[Placement]:
    """
    GPU-optimized packing with rotation support.
    
    Args:
        container: Container configuration
        block_dims: List of block dimensions
        target_blocks: Target number of blocks to pack
        
    Returns:
        Optimized list of placements
    """
    st.write(f"🎯 TARGET: Attempting to pack {target_blocks} blocks with ROTATION")
    
    # Use rotation-enabled greedy algorithm
    placements = greedy_pack_with_rotation(container, block_dims[:target_blocks])
    count = len(placements)
    
    st.write(f"📊 Greedy with rotation achieved: {count} blocks")
    st.success(f"🏆 Result: Packing WITH ROTATION: {count} blocks!")
    
    return placements
