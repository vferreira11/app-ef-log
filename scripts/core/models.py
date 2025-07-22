"""
Modelos de dados para o sistema de empacotamento 3D.
"""

from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class ContainerConfig:
    """Configuração do container para empacotamento."""
    dx: int
    dy: int
    dz: int
    
    @property
    def volume(self) -> int:
        """Retorna o volume total do container."""
        return self.dx * self.dy * self.dz
    
    def dimensions(self) -> Tuple[int, int, int]:
        """Retorna as dimensões como tupla."""
        return (self.dx, self.dy, self.dz)


@dataclass
class Placement:
    """Representa o posicionamento de um bloco no container."""
    x: int
    y: int
    z: int
    block_index: int
    orientation: Tuple[int, int, int] = None
    
    def to_tuple(self) -> tuple:
        """Converte para tupla para compatibilidade."""
        if self.orientation:
            return (self.x, self.y, self.z, self.block_index, self.orientation)
        return (self.x, self.y, self.z, self.block_index)


@dataclass
class BlockType:
    """Representa um tipo de bloco."""
    dx: int
    dy: int
    dz: int
    quantity: int
    
    @property
    def volume(self) -> int:
        """Retorna o volume do bloco."""
        return self.dx * self.dy * self.dz
    
    def dimensions(self) -> Tuple[int, int, int]:
        """Retorna as dimensões como tupla."""
        return (self.dx, self.dy, self.dz)