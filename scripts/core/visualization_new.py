"""
Sistema de Visualização 3D Reconstruído do Zero
Abordagem simplificada e robusta para renderização de empacotamento.
"""

import numpy as np
import plotly.graph_objects as go
from typing import List, Tuple, Dict
from .models import ContainerConfig


def create_simple_3d_block(x, y, z, dx, dy, dz, color, fig):
    """
    Cria um bloco 3D simples usando apenas linhas (wireframe).
    Mais confiável que mesh para visualização estática.
    """
    # Vértices do cubo
    vertices = [
        [x, y, z],           # 0: base inferior esquerda frente
        [x+dx, y, z],        # 1: base inferior direita frente
        [x+dx, y+dy, z],     # 2: base inferior direita trás
        [x, y+dy, z],        # 3: base inferior esquerda trás
        [x, y, z+dz],        # 4: topo esquerda frente
        [x+dx, y, z+dz],     # 5: topo direita frente
        [x+dx, y+dy, z+dz],  # 6: topo direita trás
        [x, y+dy, z+dz]      # 7: topo esquerda trás
    ]
    
    # Define as arestas do cubo
    edges = [
        # Base inferior
        (0, 1), (1, 2), (2, 3), (3, 0),
        # Topo superior
        (4, 5), (5, 6), (6, 7), (7, 4),
        # Arestas verticais
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    # Adiciona cada aresta como uma linha espessa
    for edge in edges:
        v1, v2 = edge
        x_coords = [vertices[v1][0], vertices[v2][0]]
        y_coords = [vertices[v1][1], vertices[v2][1]]
        z_coords = [vertices[v1][2], vertices[v2][2]]
        
        fig.add_trace(go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='lines',
            line=dict(color=color, width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Adiciona pontos nos vértices para melhor visualização
    all_x = [v[0] for v in vertices]
    all_y = [v[1] for v in vertices]
    all_z = [v[2] for v in vertices]
    
    fig.add_trace(go.Scatter3d(
        x=all_x,
        y=all_y,
        z=all_z,
        mode='markers',
        marker=dict(
            color=color,
            size=3,
            opacity=0.8
        ),
        showlegend=False,
        hoverinfo='skip'
    ))


def create_container_outline(container: ContainerConfig, fig: go.Figure):
    """Cria o contorno do container de forma simples e robusta."""
    dx, dy, dz = container.dx, container.dy, container.dz
    
    for container_idx in range(container.quantidade):
        # Offset para múltiplos containers
        offset_x = container_idx * (dx + 20)
        
        # Vértices do container
        vertices = [
            [offset_x, 0, 0],           # 0
            [offset_x + dx, 0, 0],      # 1
            [offset_x + dx, dy, 0],     # 2
            [offset_x, dy, 0],          # 3
            [offset_x, 0, dz],          # 4
            [offset_x + dx, 0, dz],     # 5
            [offset_x + dx, dy, dz],    # 6
            [offset_x, dy, dz]          # 7
        ]
        
        # Arestas do container
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # base
            (4,5), (5,6), (6,7), (7,4),  # topo
            (0,4), (1,5), (2,6), (3,7)   # verticais
        ]
        
        # Adiciona arestas do container
        for edge in edges:
            v1, v2 = edge
            fig.add_trace(go.Scatter3d(
                x=[vertices[v1][0], vertices[v2][0]],
                y=[vertices[v1][1], vertices[v2][1]],
                z=[vertices[v1][2], vertices[v2][2]],
                mode='lines',
                line=dict(color='black', width=4),
                showlegend=False,
                name=f'Container {container_idx + 1}' if container_idx == 0 else ''
            ))


def get_block_color(block_index: int) -> str:
    """Retorna uma cor consistente para cada tipo de bloco."""
    colors = [
        '#FF6B6B',  # Vermelho claro
        '#4ECDC4',  # Turquesa
        '#45B7D1',  # Azul claro
        '#96CEB4',  # Verde claro
        '#FFEAA7',  # Amarelo claro
        '#DDA0DD',  # Roxo claro
        '#98D8C8',  # Verde agua
        '#F7DC6F',  # Amarelo ouro
        '#BB8FCE',  # Lilás
        '#85C1E9'   # Azul céu
    ]
    return colors[block_index % len(colors)]


def create_3d_view(container: ContainerConfig, placements: List[Tuple], 
                   block_dims: List[Tuple], view_name: str, camera_config: dict) -> go.Figure:
    """
    Cria uma única visualização 3D com configuração de câmera específica.
    """
    fig = go.Figure()
    
    # Adiciona contorno do container
    create_container_outline(container, fig)
    
    # Adiciona blocos posicionados
    for idx, placement in enumerate(placements):
        if idx >= len(block_dims):
            continue
            
        try:
            # Desempacota posição (suporta formatos diferentes)
            if len(placement) >= 6:
                x, y, z = placement[0], placement[1], placement[2]
                dx, dy, dz = placement[3], placement[4], placement[5]
                container_idx = placement[6] if len(placement) > 6 else 0
            else:
                continue  # Pula se formato inválido
                
            # Ajusta posição para múltiplos containers
            offset_x = container_idx * (container.dx + 20)
            x_adjusted = x + offset_x
            
            # Cor do bloco baseada no índice
            color = get_block_color(idx)
            
            # Cria o bloco
            create_simple_3d_block(x_adjusted, y, z, dx, dy, dz, color, fig)
            
        except Exception as e:
            print(f"Erro ao processar bloco {idx}: {e}")
            continue
    
    # Configuração do layout
    max_x = container.dx * container.quantidade + 20 * (container.quantidade - 1)
    
    fig.update_layout(
        scene=dict(
            camera=camera_config,
            aspectmode='cube',
            xaxis=dict(
                title="Largura (cm)",
                range=[0, max_x + 10],
                showgrid=True,
                gridcolor="lightgray"
            ),
            yaxis=dict(
                title="Profundidade (cm)",
                range=[0, container.dy + 10],
                showgrid=True,
                gridcolor="lightgray"
            ),
            zaxis=dict(
                title="Altura (cm)",
                range=[0, container.dz + 10],
                showgrid=True,
                gridcolor="lightgray"
            ),
            bgcolor="white"
        ),
        title=dict(
            text=f"Vista {view_name}",
            x=0.5,
            font=dict(size=14)
        ),
        width=400,
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_multiview_3d_simple(container: ContainerConfig, placements: List[Tuple], 
                              block_dims: List[Tuple]) -> List[go.Figure]:
    """
    Cria 3 visualizações 3D com ângulos diferentes.
    Versão simplificada e robusta.
    """
    # Configurações de câmera para cada vista
    cameras = [
        # Vista Frontal
        dict(
            eye=dict(x=0, y=-1.5, z=0.5),
            center=dict(x=0.5, y=0.5, z=0.5),
            up=dict(x=0, y=0, z=1)
        ),
        # Vista Lateral
        dict(
            eye=dict(x=1.5, y=0, z=0.5),
            center=dict(x=0.5, y=0.5, z=0.5),
            up=dict(x=0, y=0, z=1)
        ),
        # Vista Superior
        dict(
            eye=dict(x=0.5, y=0.5, z=1.5),
            center=dict(x=0.5, y=0.5, z=0),
            up=dict(x=0, y=1, z=0)
        )
    ]
    
    view_names = ['Frontal', 'Lateral', 'Superior']
    figures = []
    
    for i, (camera, name) in enumerate(zip(cameras, view_names)):
        try:
            fig = create_3d_view(container, placements, block_dims, name, camera)
            figures.append(fig)
            print(f"✅ Vista {name} criada com {len(fig.data)} elementos")
        except Exception as e:
            print(f"❌ Erro ao criar vista {name}: {e}")
            # Cria figura vazia em caso de erro
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title=f"Erro na Vista {name}",
                annotations=[dict(text="Erro na renderização", x=0.5, y=0.5)]
            )
            figures.append(empty_fig)
    
    return figures


def generate_block_legend(block_dims: List[Tuple]) -> Dict[Tuple, str]:
    """Gera legenda de cores para os blocos."""
    unique_dims = list(set(block_dims))
    legend = {}
    
    for i, dims in enumerate(unique_dims):
        color = get_block_color(i)
        legend[dims] = color
    
    return legend
