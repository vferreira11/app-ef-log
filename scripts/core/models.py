"""
Data models for 3D packing system

This module contains the core data structures and classes used throughout
the 3D packing application.
"""

from typing import Tuple


class ContainerConfig:
    """
    Configuration for a 3D container.
    
    Attributes:
        dx (int): Container width
        dy (int): Container depth  
        dz (int): Container height
        volume (int): Total container volume
    """
    
    def __init__(self, dx: int, dy: int, dz: int):
        """
        Initialize container configuration.
        
        Args:
            dx: Container width
            dy: Container depth
            dz: Container height
        """
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.volume = dx * dy * dz
    
    def __repr__(self) -> str:
        return f"ContainerConfig({self.dx}x{self.dy}x{self.dz}, volume={self.volume})"
    
    def dimensions(self) -> Tuple[int, int, int]:
        """Return container dimensions as tuple."""
        return (self.dx, self.dy, self.dz)


class BlockType:
    """
    Definition of a block type with dimensions and quantity.
    
    Attributes:
        dx (int): Block width
        dy (int): Block depth
        dz (int): Block height
        quantidade (int): Number of blocks of this type
        volume (int): Volume of a single block
    """
    
    def __init__(self, dx: int, dy: int, dz: int, quantidade: int):
        """
        Initialize block type.
        
        Args:
            dx: Block width
            dy: Block depth
            dz: Block height
            quantidade: Number of blocks of this type
        """
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.quantidade = quantidade
        self.volume = dx * dy * dz
    
    def __repr__(self) -> str:
        return f"BlockType({self.dx}x{self.dy}x{self.dz}, qty={self.quantidade})"
    
    def dimensions(self) -> Tuple[int, int, int]:
        """Return block dimensions as tuple."""
        return (self.dx, self.dy, self.dz)


class Placement:
    """
    Represents the placement of a block in 3D space.
    
    Attributes:
        x (int): X position
        y (int): Y position
        z (int): Z position
        block_index (int): Index of the block type
        orientation (Tuple[int, int, int], optional): Block orientation if rotated
    """
    
    def __init__(self, x: int, y: int, z: int, block_index: int, 
                 orientation: Tuple[int, int, int] = None):
        """
        Initialize block placement.
        
        Args:
            x: X position
            y: Y position
            z: Z position
            block_index: Index of the block type
            orientation: Block orientation if rotated
        """
        self.x = x
        self.y = y
        self.z = z
        self.block_index = block_index
        self.orientation = orientation
    
    def __repr__(self) -> str:
        if self.orientation:
            return f"Placement({self.x},{self.y},{self.z}, block={self.block_index}, orientation={self.orientation})"
        return f"Placement({self.x},{self.y},{self.z}, block={self.block_index})"
    
    def position(self) -> Tuple[int, int, int]:
        """Return position as tuple."""
        return (self.x, self.y, self.z)
    
    def to_tuple(self) -> tuple:
        """Convert to tuple format for backward compatibility."""
        if self.orientation:
            return (self.x, self.y, self.z, self.block_index, self.orientation)
        return (self.x, self.y, self.z, self.block_index)
