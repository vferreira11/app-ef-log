"""
Componente de visualização 3D otimizado.
Fornece visualização interativa do empacotamento.
"""

from typing import List, Tuple, Dict, Optional, Any
import plotly.graph_objects as go
import plotly.colors as pc
import numpy as np
import streamlit as st
from dataclasses import dataclass
from ...utils.error_handling import VisualizationError, error_handler

@dataclass
class VisualizationConfig:
    """Configuração da visualização 3D."""
    width: int = 900
    height: int = 700
    opacity: float = 1.0
    show_floor: bool = True
    show_container: bool = True
    show_wireframe: bool = True
    colorscale: str = "Viridis"

class Visualizer3D:
    """Componente de visualização 3D."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Inicializa visualizador.
        
        Args:
            config: Configuração opcional
        """
        self.config = config or VisualizationConfig()
        self.figure = None
        self.block_colors = {}
    
    @error_handler(show_traceback=True)
    def create_visualization(self, container_dims: Tuple[int, int, int],
                           placements: List[Dict[str, Any]],
                           block_dims: List[Tuple[int, int, int]]) -> go.Figure:
        """
        Cria visualização 3D do empacotamento.
        
        Args:
            container_dims: Dimensões do container (x,y,z)
            placements: Lista de alocações
            block_dims: Lista de dimensões dos blocos
            
        Returns:
            Figure do Plotly
        """
        if not placements:
            raise VisualizationError("Nenhum bloco para visualizar")
            
        # Cria figura base
        self.figure = go.Figure()
        
        # Adiciona elementos
        if self.config.show_floor:
            self._add_floor(container_dims)
        
        if self.config.show_container:
            self._add_container_frame(container_dims)
            
        # Mapeia cores por tipo de bloco
        self._map_block_colors(block_dims)
        
        # Adiciona blocos
        self._add_blocks(placements, block_dims)
        
        # Configura layout
        self._configure_layout(container_dims)
        
        return self.figure
    
    def _add_floor(self, container_dims: Tuple[int, int, int]):
        """
        Adiciona chão do container.
        
        Args:
            container_dims: Dimensões do container
        """
        dx, dy, _ = container_dims
        
        self.figure.add_trace(go.Mesh3d(
            x=[0, dx, dx, 0],
            y=[0, 0, dy, dy],
            z=[0, 0, 0, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='lightgray',
            opacity=0.3,
            name='Chão',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    def _add_container_frame(self, container_dims: Tuple[int, int, int]):
        """
        Adiciona frame do container.
        
        Args:
            container_dims: Dimensões do container
        """
        dx, dy, dz = container_dims
        
        # Vértices do container
        vertices = [
            [0, 0, 0], [dx, 0, 0], [dx, dy, 0], [0, dy, 0],  # base
            [0, 0, dz], [dx, 0, dz], [dx, dy, dz], [0, dy, dz]  # topo
        ]
        
        # Arestas do container
        edges = [(0,1), (1,2), (2,3), (3,0),  # base
                (4,5), (5,6), (6,7), (7,4),  # topo
                (0,4), (1,5), (2,6), (3,7)]  # verticais
        
        for start, end in edges:
            self.figure.add_trace(go.Scatter3d(
                x=[vertices[start][0], vertices[end][0]],
                y=[vertices[start][1], vertices[end][1]],
                z=[vertices[start][2], vertices[end][2]],
                mode='lines',
                line=dict(color='black', width=2),
                name='Container',
                showlegend=False,
                hoverinfo='skip'
            ))
    
    def _map_block_colors(self, block_dims: List[Tuple[int, int, int]]):
        """
        Mapeia cores para tipos de blocos.
        
        Args:
            block_dims: Lista de dimensões dos blocos
        """
        unique_dims = list(set(block_dims))
        colors = pc.sample_colorscale(self.config.colorscale, 
                                    np.linspace(0, 1, len(unique_dims)))
        self.block_colors = {dim: color for dim, color in zip(unique_dims, colors)}
    
    def _add_blocks(self, placements: List[Dict[str, Any]], 
                   block_dims: List[Tuple[int, int, int]]):
        """
        Adiciona blocos à visualização.
        
        Args:
            placements: Lista de alocações
            block_dims: Lista de dimensões dos blocos
        """
        for i, placement in enumerate(placements):
            if placement is None:
                continue
                
            # Extrai coordenadas
            x = placement.get('x', 0)
            y = placement.get('y', 0)
            z = placement.get('z', 0)
            block_idx = placement.get('block_index', i)
            
            # Obtém dimensões do bloco
            if block_idx >= len(block_dims):
                continue
                
            bdx, bdy, bdz = block_dims[block_idx]
            current_dim = block_dims[block_idx]
            
            # Cor baseada no tipo
            color = self.block_colors.get(current_dim, '#000000')
            
            # Adiciona cubo sólido
            self._add_block_cube(x, y, z, bdx, bdy, bdz, color, i)
            
            # Adiciona wireframe se configurado
            if self.config.show_wireframe:
                self._add_block_wireframe(x, y, z, bdx, bdy, bdz)
    
    def _add_block_cube(self, x: int, y: int, z: int, 
                       dx: int, dy: int, dz: int,
                       color: str, index: int):
        """
        Adiciona cubo sólido do bloco.
        
        Args:
            x,y,z: Coordenadas do bloco
            dx,dy,dz: Dimensões do bloco
            color: Cor do bloco
            index: Índice do bloco
        """
        self.figure.add_trace(go.Mesh3d(
            x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
            y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
            z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color,
            opacity=self.config.opacity,
            name=f'Bloco {index+1}',
            showlegend=False,
            hovertemplate=f'<b>Bloco {index+1}</b><br>'+
                         f'Posição: ({x}, {y}, {z})<br>'+
                         f'Dimensões: {dx}×{dy}×{dz}<br>'+
                         '<extra></extra>'
        ))
    
    def _add_block_wireframe(self, x: int, y: int, z: int,
                           dx: int, dy: int, dz: int):
        """
        Adiciona wireframe do bloco.
        
        Args:
            x,y,z: Coordenadas do bloco
            dx,dy,dz: Dimensões do bloco
        """
        vertices = [
            [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z],
            [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]
        ]
        
        edges = [(0,1), (1,2), (2,3), (3,0),
                (4,5), (5,6), (6,7), (7,4),
                (0,4), (1,5), (2,6), (3,7)]
        
        for start, end in edges:
            self.figure.add_trace(go.Scatter3d(
                x=[vertices[start][0], vertices[end][0]],
                y=[vertices[start][1], vertices[end][1]],
                z=[vertices[start][2], vertices[end][2]],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    def _configure_layout(self, container_dims: Tuple[int, int, int]):
        """
        Configura layout da visualização.
        
        Args:
            container_dims: Dimensões do container
        """
        dx, dy, dz = container_dims
        
        self.figure.update_layout(
            title="📦 Visualização 3D do Empacotamento",
            scene=dict(
                xaxis_title="Largura (X) - cm",
                yaxis_title="Profundidade (Y) - cm",
                zaxis_title="Altura (Z) - cm",
                aspectmode='data',
                aspectratio=dict(x=1, y=1, z=1),
                xaxis=dict(
                    range=[0, dx],
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                yaxis=dict(
                    range=[0, dy],
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                zaxis=dict(
                    range=[0, dz],
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                bgcolor='white'
            ),
            width=self.config.width,
            height=self.config.height,
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False
        )
    
    @property
    def color_mapping(self) -> Dict[Tuple[int, int, int], str]:
        """
        Retorna mapeamento de cores.
        
        Returns:
            Dicionário com cores por tipo
        """
        return self.block_colors.copy()

class Legend:
    """Componente de legenda para visualização."""
    
    def __init__(self, columns: int = 4):
        """
        Inicializa legenda.
        
        Args:
            columns: Número de colunas
        """
        self.columns = columns
    
    def render_type_legend(self, color_mapping: Dict[Tuple[int, int, int], str]):
        """
        Renderiza legenda de tipos.
        
        Args:
            color_mapping: Mapeamento de cores
        """
        st.markdown("### 🎨 Legenda de Tipos de Produto")
        
        legend_cols = st.columns(self.columns)
        
        for i, (dims, color) in enumerate(color_mapping.items()):
            col_idx = i % self.columns
            with legend_cols[col_idx]:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 25px; height: 25px; background-color: {color}; 
                                border: 1px solid #000; margin-right: 10px; border-radius: 4px;"></div>
                    <div style="font-size: 14px; font-weight: bold;">
                        {dims[0]}×{dims[1]}×{dims[2]} cm
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_product_legend(self, color_mapping: Dict[Tuple[int, int, int], str],
                            product_info: Optional[Dict[str, Any]] = None):
        """
        Renderiza legenda de produtos.
        
        Args:
            color_mapping: Mapeamento de cores
            product_info: Informações dos produtos
        """
        if not product_info:
            return
            
        st.markdown("### 🏷️ Legenda de Produtos")
        
        legend_cols = st.columns(self.columns)
        
        for i, (product, info) in enumerate(product_info.items()):
            dims = info.get('dimensions')
            if not dims or dims not in color_mapping:
                continue
                
            col_idx = i % self.columns
            with legend_cols[col_idx]:
                color = color_mapping[dims]
                category = info.get('category', '')
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 20px; height: 20px; background-color: {color}; 
                                border: 1px solid #000; margin-right: 10px; border-radius: 3px;"></div>
                    <div style="font-size: 13px; line-height: 1.2;">
                        <strong>{product}</strong><br>
                        <small style="color: #666;">{category}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Instância global do visualizador
visualizer = Visualizer3D()