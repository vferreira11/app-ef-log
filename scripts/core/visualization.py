"""
Funções de visualização 3D com Plotly.
"""

import plotly.graph_objects as go
from typing import List, Tuple, Dict
from .models import ContainerConfig


def create_container_wireframe(container: ContainerConfig, fig: go.Figure) -> None:
    """Adiciona wireframe do container ao gráfico."""
    dx, dy, dz = container.dx, container.dy, container.dz
    
    # Vértices do container
    verts = [
        (0, 0, 0), (dx, 0, 0), (dx, dy, 0), (0, dy, 0),  # base
        (0, 0, dz), (dx, 0, dz), (dx, dy, dz), (0, dy, dz)  # topo
    ]
    
    # Arestas do container
    edges = [
        (0,1), (1,2), (2,3), (3,0),  # base inferior
        (4,5), (5,6), (6,7), (7,4),  # topo
        (0,4), (1,5), (2,6), (3,7)   # laterais
    ]
    
    for e in edges:
        x0, y0, z0 = verts[e[0]]
        x1, y1, z1 = verts[e[1]]
        fig.add_trace(go.Scatter3d(
            x=[x0, x1], y=[y0, y1], z=[z0, z1],
            mode='lines',
            line=dict(color='gray', width=4),
            showlegend=False
        ))


def create_block_faces(x0: int, y0: int, z0: int, lx: int, ly: int, lz: int, color_index: int, fig: go.Figure) -> None:
    """Adiciona faces sólidas de um bloco ao gráfico usando Surface."""
    
    # Face inferior (z = z0)
    fig.add_trace(go.Surface(
        x=[[x0, x0+lx], [x0, x0+lx]],
        y=[[y0, y0], [y0+ly, y0+ly]],
        z=[[z0, z0], [z0, z0]],
        surfacecolor=[[color_index, color_index], [color_index, color_index]],
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=1.0,
        showlegend=False
    ))
    
    # Face superior (z = z0+lz)
    fig.add_trace(go.Surface(
        x=[[x0, x0+lx], [x0, x0+lx]],
        y=[[y0, y0], [y0+ly, y0+ly]],
        z=[[z0+lz, z0+lz], [z0+lz, z0+lz]],
        surfacecolor=[[color_index, color_index], [color_index, color_index]],
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=1.0,
        showlegend=False
    ))
    
    # Face frontal (y = y0)
    fig.add_trace(go.Surface(
        x=[[x0, x0+lx], [x0, x0+lx]],
        y=[[y0, y0], [y0, y0]],
        z=[[z0, z0], [z0+lz, z0+lz]],
        surfacecolor=[[color_index, color_index], [color_index, color_index]],
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=1.0,
        showlegend=False
    ))
    
    # Face traseira (y = y0+ly)
    fig.add_trace(go.Surface(
        x=[[x0, x0+lx], [x0, x0+lx]],
        y=[[y0+ly, y0+ly], [y0+ly, y0+ly]],
        z=[[z0, z0], [z0+lz, z0+lz]],
        surfacecolor=[[color_index, color_index], [color_index, color_index]],
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=1.0,
        showlegend=False
    ))
    
    # Face esquerda (x = x0)
    fig.add_trace(go.Surface(
        x=[[x0, x0], [x0, x0]],
        y=[[y0, y0+ly], [y0, y0+ly]],
        z=[[z0, z0], [z0+lz, z0+lz]],
        surfacecolor=[[color_index, color_index], [color_index, color_index]],
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=1.0,
        showlegend=False
    ))
    
    # Face direita (x = x0+lx)
    fig.add_trace(go.Surface(
        x=[[x0+lx, x0+lx], [x0+lx, x0+lx]],
        y=[[y0, y0+ly], [y0, y0+ly]],
        z=[[z0, z0], [z0+lz, z0+lz]],
        surfacecolor=[[color_index, color_index], [color_index, color_index]],
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=1.0,
        showlegend=False
    ))


def create_block_edges(x0: int, y0: int, z0: int, lx: int, ly: int, lz: int, fig: go.Figure) -> None:
    """Adiciona bordas pretas de um bloco ao gráfico."""
    
    # Vértices do bloco
    verts = [
        (x0, y0, z0), (x0+lx, y0, z0), (x0+lx, y0+ly, z0), (x0, y0+ly, z0),  # base
        (x0, y0, z0+lz), (x0+lx, y0, z0+lz), (x0+lx, y0+ly, z0+lz), (x0, y0+ly, z0+lz)  # topo
    ]
    
    # Arestas do bloco
    edges = [
        (0,1), (1,2), (2,3), (3,0),  # base inferior
        (4,5), (5,6), (6,7), (7,4),  # topo
        (0,4), (1,5), (2,6), (3,7)   # laterais
    ]
    
    for e in edges:
        x0e, y0e, z0e = verts[e[0]]
        x1e, y1e, z1e = verts[e[1]]
        fig.add_trace(go.Scatter3d(
            x=[x0e, x1e], y=[y0e, y1e], z=[z0e, z1e],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False
        ))


def create_3d_plot(container: ContainerConfig, placements: List[tuple], block_dims: List[Tuple[int, int, int]], block_colors: Dict[Tuple[int, int, int], str]) -> go.Figure:
    """
    Cria visualização 3D completa do empacotamento.
    
    Args:
        container: Configuração do container
        placements: Lista de alocações dos blocos
        block_dims: Lista de dimensões dos blocos
        block_colors: Dicionário de cores por tipo de bloco
        
    Returns:
        Figura Plotly configurada
    """
    fig = go.Figure()
    
    # Adiciona wireframe do container
    create_container_wireframe(container, fig)
    
    # Cria mapeamento de tipos para índices numéricos da paleta Viridis
    unique_types = list(set(block_dims))
    unique_types.sort()  # Ordena para consistência
    type_to_index = {block_type: i for i, block_type in enumerate(unique_types)}
    
    print(f"[DEBUG] Mapeamento tipo->índice: {type_to_index}")
    
    # Adiciona cada bloco com faces sólidas e bordas
    for placement in placements:
        if len(placement) == 5:
            x0, y0, z0, block_index, orientation = placement
            lx, ly, lz = orientation
            # Sempre usa a cor do tipo original do bloco, não da rotação
            original_dims = block_dims[block_index]
            color_index = type_to_index.get(original_dims, 0)  # fallback para índice 0
        else:
            x0, y0, z0, block_index = placement
            lx, ly, lz = block_dims[block_index]
            color_index = type_to_index.get((lx, ly, lz), 0)  # fallback para índice 0
        
        print(f"[DEBUG] Bloco {block_index}: dim=({lx},{ly},{lz}), color_index={color_index}")
        
        # Adiciona faces sólidas com índice de cor
        create_block_faces(x0, y0, z0, lx, ly, lz, color_index, fig)
        # Adiciona bordas pretas
        create_block_edges(x0, y0, z0, lx, ly, lz, fig)
    
    # Configurações do layout
    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y", 
            zaxis_title="Z",
            aspectmode="manual",
            aspectratio=dict(
                x=container.dx / max(container.dx, container.dy, container.dz),
                y=container.dy / max(container.dx, container.dy, container.dz),
                z=container.dz / max(container.dx, container.dy, container.dz)
            )
        ),
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    return fig