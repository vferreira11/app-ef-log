"""
Módulo de configuração centralizada da aplicação.
Define constantes, configurações e mensagens do sistema.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, List
import streamlit as st

@dataclass
class UIConfig:
    """Configurações da interface do usuário."""
    page_title: str = ".: PARADOXO :."
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    def apply(self):
        """Aplica configurações ao Streamlit."""
        st.set_page_config(
            page_title=self.page_title,
            layout=self.layout,
            initial_sidebar_state=self.initial_sidebar_state
        )

@dataclass
class ContainerDefaults:
    """Dimensões padrão do container."""
    dx: int = 100
    dy: int = 100
    dz: int = 100
    quantidade: int = 1

@dataclass
class BlockDefaults:
    """Configurações padrão para blocos."""
    min_dimension: int = 1
    max_dimension: int = 50
    categories: List[str] = None
    
    def __post_init__(self):
        self.categories = [
            "Eletrônicos", "Vestuário", "Alimentos",
            "Cosméticos", "Ferramentas", "Utilidades"
        ]

@dataclass
class AlgorithmConfig:
    """Configurações dos algoritmos."""
    max_blocks_warning: int = 1000
    gpu_population_range: Tuple[int, int] = (100, 1000)
    default_precision: str = "balanced"
    enable_physics: bool = True
    enable_evolution: bool = True

@dataclass
class SystemMessages:
    """Mensagens do sistema."""
    success_perfect: str = "✅ Empacotamento perfeito! {} blocos alocados com sucesso."
    warning_partial: str = "⚠️ {} blocos não puderam ser alocados."
    error_no_blocks: str = "❌ Nenhum bloco foi alocado!"
    warning_performance: str = "⚠️ Grande volume de blocos ({}). O processamento pode demorar."
    info_capacity: str = "ℹ️ Capacidade máxima estimada: {} blocos"

class AppConfig:
    """Configuração centralizada da aplicação."""
    
    def __init__(self):
        self.ui = UIConfig()
        self.container = ContainerDefaults()
        self.block = BlockDefaults()
        self.algorithm = AlgorithmConfig()
        self.messages = SystemMessages()
        
    def setup(self):
        """Configura ambiente da aplicação."""
        self.ui.apply()
        
    @property
    def block_types(self) -> Dict[str, Dict[str, int]]:
        """Retorna tipos de blocos pré-definidos."""
        return {
            'small': {'dx': 10, 'dy': 10, 'dz': 10},
            'medium': {'dx': 20, 'dy': 20, 'dz': 20},
            'large': {'dx': 30, 'dy': 30, 'dz': 30}
        }

# Instância global de configuração
config = AppConfig()