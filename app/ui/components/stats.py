"""
Componentes de estatísticas e métricas.
Fornece cards e visualizações para dados numéricos.
"""

from typing import Optional, Dict, Any
import streamlit as st
from dataclasses import dataclass

@dataclass
class StatCardStyle:
    """Estilo para cards de estatística."""
    background_color: str = "#FFFFFF"
    border_color: str = "#E6EAF1"
    accent_color: str = "#00D4AA"
    text_color: str = "#1A1C24"
    subtitle_color: str = "#5A6474"
    help_color: str = "#8A94A6"

class StatCard:
    """Card de estatística reutilizável."""
    
    def __init__(self, title: str, value: Any, 
                 help_text: str = "", icon: str = "📊",
                 style: Optional[StatCardStyle] = None):
        """
        Inicializa card de estatística.
        
        Args:
            title: Título do card
            value: Valor principal
            help_text: Texto de ajuda
            icon: Ícone do card
            style: Estilo customizado
        """
        self.title = title
        self.value = value
        self.help_text = help_text
        self.icon = icon
        self.style = style or StatCardStyle()
    
    def render(self):
        """Renderiza card de estatística."""
        st.markdown(f"""
        <div class="stat-card">
            <h3>{self.icon} {self.title}</h3>
            <p>{self.value}</p>
            <small>{self.help_text}</small>
        </div>
        """, unsafe_allow_html=True)

class OptimizedStatCard:
    """Card de estatística otimizado com delta."""
    
    def __init__(self, title: str, value: Any, 
                 delta: Optional[str] = None,
                 icon: str = "📊", color: str = "#00D4AA"):
        """
        Inicializa card otimizado.
        
        Args:
            title: Título do card
            value: Valor principal
            delta: Variação (opcional)
            icon: Ícone do card
            color: Cor de destaque
        """
        self.title = title
        self.value = value
        self.delta = delta
        self.icon = icon
        self.color = color
    
    def render(self):
        """Renderiza card otimizado."""
        delta_html = ""
        if self.delta:
            delta_html = f"""
            <small style='color: {self.color}; font-weight: 600;'>
                △ {self.delta}
            </small>
            """
            
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: {self.color};">
            <h3>{self.icon} {self.title}</h3>
            <p style="color: {self.color};">{self.value}</p>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

class StatGroup:
    """Grupo de estatísticas em colunas."""
    
    def __init__(self, num_columns: int = 3):
        """
        Inicializa grupo de estatísticas.
        
        Args:
            num_columns: Número de colunas
        """
        self.num_columns = num_columns
        self.columns = st.columns(num_columns)
        self.current_column = 0
    
    def add_stat(self, title: str, value: Any, 
                 help_text: str = "", icon: str = "📊",
                 style: Optional[StatCardStyle] = None):
        """
        Adiciona estatística ao grupo.
        
        Args:
            title: Título do card
            value: Valor principal
            help_text: Texto de ajuda
            icon: Ícone do card
            style: Estilo customizado
        """
        with self.columns[self.current_column]:
            StatCard(title, value, help_text, icon, style).render()
        
        self.current_column = (self.current_column + 1) % self.num_columns
    
    def add_optimized_stat(self, title: str, value: Any,
                          delta: Optional[str] = None,
                          icon: str = "📊", color: str = "#00D4AA"):
        """
        Adiciona estatística otimizada ao grupo.
        
        Args:
            title: Título do card
            value: Valor principal
            delta: Variação (opcional)
            icon: Ícone do card
            color: Cor de destaque
        """
        with self.columns[self.current_column]:
            OptimizedStatCard(title, value, delta, icon, color).render()
        
        self.current_column = (self.current_column + 1) % self.num_columns