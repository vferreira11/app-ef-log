"""
Módulo de gerenciamento de estado da aplicação.
Centraliza acesso e manipulação do estado global.
"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import streamlit as st
from enum import Enum, auto

class StateKeys(Enum):
    """Enumeração de chaves válidas do estado."""
    PLACEMENTS = auto()
    CONTAINER = auto()
    BLOCK_DIMS = auto()
    ORDERS_DF = auto()
    LAST_RUN = auto()
    SHOW_COMPLETION = auto()

@dataclass
class AppState:
    """
    Gerenciador de estado global da aplicação.
    Encapsula acesso ao st.session_state.
    """
    
    def __init__(self):
        """Inicializa ou recupera estado."""
        if not hasattr(st, 'session_state'):
            st.session_state = {}
            
    def get(self, key: StateKeys, default: Any = None) -> Any:
        """
        Recupera valor do estado.
        
        Args:
            key: Chave do estado
            default: Valor padrão se não existir
            
        Returns:
            Valor armazenado ou default
        """
        return st.session_state.get(key.name.lower(), default)
        
    def set(self, key: StateKeys, value: Any):
        """
        Define valor no estado.
        
        Args:
            key: Chave do estado
            value: Valor a armazenar
        """
        st.session_state[key.name.lower()] = value
        
    def update(self, **kwargs):
        """
        Atualiza múltiplos valores no estado.
        
        Args:
            **kwargs: Pares chave-valor a atualizar
        """
        for key, value in kwargs.items():
            if isinstance(key, str):
                key = StateKeys[key.upper()]
            self.set(key, value)
            
    def clear(self, key: Optional[StateKeys] = None):
        """
        Limpa estado parcial ou totalmente.
        
        Args:
            key: Chave específica ou None para limpar tudo
        """
        if key:
            if key.name.lower() in st.session_state:
                del st.session_state[key.name.lower()]
        else:
            for key in StateKeys:
                self.clear(key)
                
    def has_data(self) -> bool:
        """Verifica se existe algum dado relevante no estado."""
        return any(key.name.lower() in st.session_state for key in StateKeys)
        
    def is_processing_complete(self) -> bool:
        """Verifica se processamento foi concluído."""
        return bool(self.get(StateKeys.LAST_RUN))
        
    def save_processing_results(self, placements, container, block_dims, orders_df):
        """
        Salva resultados do processamento.
        
        Args:
            placements: Lista de alocações
            container: Configuração do container
            block_dims: Dimensões dos blocos
            orders_df: DataFrame de pedidos
        """
        self.update(
            PLACEMENTS=placements,
            CONTAINER=container,
            BLOCK_DIMS=block_dims,
            ORDERS_DF=orders_df,
            LAST_RUN=True,
            SHOW_COMPLETION=True
        )
        
    def clear_processing_results(self):
        """Limpa resultados do último processamento."""
        for key in [StateKeys.PLACEMENTS, StateKeys.CONTAINER, StateKeys.BLOCK_DIMS, 
                   StateKeys.LAST_RUN, StateKeys.SHOW_COMPLETION]:
            self.clear(key)
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte estado para dicionário.
        
        Returns:
            Dict com estado atual
        """
        return {key.name.lower(): self.get(key) for key in StateKeys}

# Instância global do gerenciador de estado
state = AppState()