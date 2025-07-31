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
    Cria um bloco 3D robusto que sempre aparece.
    Combina wireframe com superfície para garantir visibilidade.
    """
    # Vértices do cubo
    vertices = np.array([
        [x, y, z],           # 0: base inferior esquerda frente
        [x+dx, y, z],        # 1: base inferior direita frente
        [x+dx, y+dy, z],     # 2: base inferior direita trás
        [x, y+dy, z],        # 3: base inferior esquerda trás
        [x, y, z+dz],        # 4: topo esquerda frente
        [x+dx, y, z+dz],     # 5: topo direita frente
        [x+dx, y+dy, z+dz],  # 6: topo direita trás
        [x, y+dy, z+dz]      # 7: topo esquerda trás
    ])
    
    try:
        # Tenta criar Mesh3d primeiro (mais bonito)
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # base inferior
            [4, 6, 5], [4, 7, 6],  # topo superior
            [0, 4, 5], [0, 5, 1],  # face frontal
            [3, 2, 6], [3, 6, 7],  # face traseira
            [0, 3, 7], [0, 7, 4],  # face esquerda
            [1, 5, 6], [1, 6, 2]   # face direita
        ])
        
        fig.add_trace(go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1], 
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color=color,
            opacity=0.7,
            showlegend=False,
            flatshading=True,
            hoverinfo='skip'
        ))
        
    except Exception as e:
        print(f"Mesh3d falhou, usando wireframe: {e}")
        
        # Fallback: wireframe + marcadores nos vértices
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # base inferior
            (4, 5), (5, 6), (6, 7), (7, 4),  # topo superior
            (0, 4), (1, 5), (2, 6), (3, 7)   # arestas verticais
        ]
        
        # Adiciona wireframe espesso
        for edge in edges:
            v1, v2 = edge
            fig.add_trace(go.Scatter3d(
                x=[vertices[v1, 0], vertices[v2, 0]],
                y=[vertices[v1, 1], vertices[v2, 1]],
                z=[vertices[v1, 2], vertices[v2, 2]],
                mode='lines',
                line=dict(color=color, width=6),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Adiciona marcadores nos vértices para dar volume visual
        fig.add_trace(go.Scatter3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            mode='markers',
            marker=dict(
                color=color,
                size=8,
                opacity=0.8
            ),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # SEMPRE adiciona wireframe de contorno (garantia de visibilidade)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # base inferior
        (4, 5), (5, 6), (6, 7), (7, 4),  # topo superior
        (0, 4), (1, 5), (2, 6), (3, 7)   # arestas verticais
    ]
    
    for edge in edges:
        v1, v2 = edge
        fig.add_trace(go.Scatter3d(
            x=[vertices[v1, 0], vertices[v2, 0]],
            y=[vertices[v1, 1], vertices[v2, 1]],
            z=[vertices[v1, 2], vertices[v2, 2]],
            mode='lines',
            line=dict(color='rgba(0,0,0,0.6)', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))


def create_container_outline(container: ContainerConfig, fig: go.Figure):
    """Cria o contorno do container com melhor visibilidade."""
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
        
        # Arestas do container com cores diferentes para melhor identificação
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # base
            (4,5), (5,6), (6,7), (7,4),  # topo
            (0,4), (1,5), (2,6), (3,7)   # verticais
        ]
        
        # Adiciona arestas do container com linha mais espessa
        for edge in edges:
            v1, v2 = edge
            fig.add_trace(go.Scatter3d(
                x=[vertices[v1][0], vertices[v2][0]],
                y=[vertices[v1][1], vertices[v2][1]],
                z=[vertices[v1][2], vertices[v2][2]],
                mode='lines',
                line=dict(color='rgba(50,50,50,0.8)', width=3),
                showlegend=False,
                hoverinfo='skip',
                name=f'Container {container_idx + 1}' if container_idx == 0 else ''
            ))
        
        # Adiciona pontos nos cantos para melhor visualização
        fig.add_trace(go.Scatter3d(
            x=[v[0] for v in vertices],
            y=[v[1] for v in vertices],
            z=[v[2] for v in vertices],
            mode='markers',
            marker=dict(
                color='rgba(50,50,50,0.6)',
                size=4,
                symbol='square'
            ),
            showlegend=False,
            hoverinfo='skip'
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
            print(f"   Bloco {idx+1}: {color} em ({x_adjusted}, {y}, {z}) tamanho ({dx}, {dy}, {dz})")
            
        except Exception as e:
            print(f"Erro ao processar bloco {idx}: {e}")
            continue
    
    # Configuração do layout com proporções corretas
    max_x = container.dx * container.quantidade + 20 * (container.quantidade - 1)
    
    fig.update_layout(
        scene=dict(
            camera=camera_config,
            aspectmode='manual',
            aspectratio=dict(
                x=max_x / 100,
                y=container.dy / 100, 
                z=container.dz / 100
            ),
            xaxis=dict(
                title="Largura (cm)",
                range=[0, max_x + 10],
                showgrid=True,
                gridcolor="rgba(200,200,200,0.3)",
                gridwidth=1,
                zeroline=True,
                zerolinecolor="rgba(100,100,100,0.5)",
                backgroundcolor="rgba(240,240,240,0.8)",
                showbackground=True
            ),
            yaxis=dict(
                title="Profundidade (cm)",
                range=[0, container.dy + 10],
                showgrid=True,
                gridcolor="rgba(200,200,200,0.3)",
                gridwidth=1,
                zeroline=True,
                zerolinecolor="rgba(100,100,100,0.5)",
                backgroundcolor="rgba(240,240,240,0.8)",
                showbackground=True
            ),
            zaxis=dict(
                title="Altura (cm)",
                range=[0, container.dz + 10],
                showgrid=True,
                gridcolor="rgba(200,200,200,0.3)",
                gridwidth=1,
                zeroline=True,
                zerolinecolor="rgba(100,100,100,0.5)",
                backgroundcolor="rgba(240,240,240,0.8)",
                showbackground=True
            ),
            bgcolor="rgba(255,255,255,1)"
        ),
        title=dict(
            text=f"Vista {view_name}",
            x=0.5,
            font=dict(size=14, color="black")
        ),
        width=380,
        height=350,
        margin=dict(l=5, r=5, t=40, b=5),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", color="black")
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
