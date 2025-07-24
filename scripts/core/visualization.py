"""
Funções de visualização 3D com Plotly.
"""

import numpy as np
import plotly.graph_objects as go
from typing import List, Tuple, Dict
from .models import ContainerConfig


def create_container_wireframe(container: ContainerConfig, fig: go.Figure) -> None:
    """Adiciona wireframe do(s) container(s) ao gráfico."""
    dx, dy, dz = container.dx, container.dy, container.dz
    
    # Cria wireframe para cada container
    for container_idx in range(container.quantidade):
        # Offset X para separar containers visualmente
        offset_x = container_idx * (dx + 10)  # 10 unidades de espaçamento
        
        # Vértices do container com offset
        verts = [
            (offset_x, 0, 0), (offset_x + dx, 0, 0), (offset_x + dx, dy, 0), (offset_x, dy, 0),  # base
            (offset_x, 0, dz), (offset_x + dx, 0, dz), (offset_x + dx, dy, dz), (offset_x, dy, dz)  # topo
        ]
        
        # Arestas do container
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # base inferior
            (4,5), (5,6), (6,7), (7,4),  # topo
            (0,4), (1,5), (2,6), (3,7)   # laterais
        ]
        
        # Cor diferente para cada container para diferenciação
        container_color = 'gray' if container_idx == 0 else f'rgb({100 + container_idx * 50}, {100 + container_idx * 50}, {100 + container_idx * 50})'
        
        for e in edges:
            x0, y0, z0 = verts[e[0]]
            x1, y1, z1 = verts[e[1]]
            fig.add_trace(go.Scatter3d(
                x=[x0, x1], y=[y0, y1], z=[z0, z1],
                mode='lines',
                line=dict(color=container_color, width=4),
                showlegend=False,
                name=f'Container {container_idx + 1}' if container_idx == 0 else ''
            ))



def create_floor_plane(container, fig):
    """
    Cria um plano de base/chão para dar contexto visual profissional.
    Adiciona uma superfície sutil no Z=0 para evitar aparência "flutuante".
    """
    # Calcula dimensões totais incluindo múltiplos containers
    total_width = container.dx * container.quantidade + (container.quantidade - 1) * 10
    
    # Expande o plano ligeiramente além dos containers para melhor visualização
    floor_margin = 20  # margem em cm
    floor_x_max = total_width + floor_margin
    floor_y_max = container.dy + floor_margin
    
    # Cria uma grade de pontos para o plano do chão
    x_points = [0, floor_x_max, floor_x_max, 0]
    y_points = [0, 0, floor_y_max, floor_y_max]
    z_points = [0, 0, 0, 0]  # Plano em Z=0

    # Adiciona plano principal (base sólida) com cor mais escura e menos transparência
    fig.add_trace(go.Mesh3d(
        x=x_points,
        y=y_points,
        z=z_points,
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color='rgba(80, 120, 180, 0.5)',  # Azul acinzentado mais escuro, mais opaco
        opacity=0.5,
        showscale=False,
        hoverinfo='skip',
        name='Base'
    ))

    # Adiciona contorno preto ao redor do plano
    fig.add_trace(go.Scatter3d(
        x=[0, floor_x_max, floor_x_max, 0, 0],
        y=[0, 0, floor_y_max, floor_y_max, 0],
        z=[0, 0, 0, 0, 0],
        mode='lines',
        line=dict(color='black', width=5),
        showlegend=False,
        hoverinfo='skip',
        name='Contorno Piso'
    ))

    # Adiciona linhas de grade para dar profissionalismo
    grid_spacing = 50  # espaçamento da grade em cm

    # Linhas verticais da grade (paralelas ao eixo Y)
    for x in range(0, int(floor_x_max) + 1, grid_spacing):
        fig.add_trace(go.Scatter3d(
            x=[x, x],
            y=[0, floor_y_max],
            z=[0, 0],
            mode='lines',
            line=dict(color='rgba(120, 120, 120, 0.7)', width=2),
            showlegend=False,
            hoverinfo='skip',
            name='Grade'
        ))

    # Linhas horizontais da grade (paralelas ao eixo X)
    for y in range(0, int(floor_y_max) + 1, grid_spacing):
        fig.add_trace(go.Scatter3d(
            x=[0, floor_x_max],
            y=[y, y],
            z=[0, 0],
            mode='lines',
            line=dict(color='rgba(200, 200, 200, 0.4)', width=1),
            showlegend=False,
            hoverinfo='skip',
            name='Grade'
        ))


def create_block_mesh(x0: int, y0: int, z0: int, lx: int, ly: int, lz: int, color_index: int, fig: go.Figure) -> None:
    """Adiciona um bloco como mesh 3D otimizada com bordas pretas ao gráfico."""
    
    # Vértices do cubo
    vertices = np.array([
        [x0, y0, z0],           # 0: base frontal esquerda
        [x0+lx, y0, z0],        # 1: base frontal direita  
        [x0+lx, y0+ly, z0],     # 2: base traseira direita
        [x0, y0+ly, z0],        # 3: base traseira esquerda
        [x0, y0, z0+lz],        # 4: topo frontal esquerda
        [x0+lx, y0, z0+lz],     # 5: topo frontal direita
        [x0+lx, y0+ly, z0+lz],  # 6: topo traseira direita
        [x0, y0+ly, z0+lz]      # 7: topo traseira esquerda
    ])
    
    # Faces do cubo (cada face = 2 triângulos)
    faces = np.array([
        # Base inferior (z=z0)
        [0, 1, 2], [0, 2, 3],
        # Topo superior (z=z0+lz)  
        [4, 6, 5], [4, 7, 6],
        # Face frontal (y=y0)
        [0, 4, 5], [0, 5, 1],
        # Face traseira (y=y0+ly)
        [3, 2, 6], [3, 6, 7],
        # Face esquerda (x=x0)
        [0, 3, 7], [0, 7, 4],
        # Face direita (x=x0+lx)
        [1, 5, 6], [1, 6, 2]
    ])
    
    # Cores por vértice (mesmo índice para todo o bloco)
    vertex_colors = [color_index] * 8
    
    # Adiciona mesh 3D (faces sólidas)
    fig.add_trace(go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1], 
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        intensity=vertex_colors,
        colorscale='Viridis',
        cmin=0,
        cmax=10,
        showscale=False,
        opacity=0.9,
        showlegend=False
    ))
    
    # Adiciona bordas pretas finas
    edges = [
        (0,1), (1,2), (2,3), (3,0),  # base inferior
        (4,5), (5,6), (6,7), (7,4),  # topo superior
        (0,4), (1,5), (2,6), (3,7)   # arestas verticais
    ]
    
    for edge in edges:
        v1, v2 = edge
        fig.add_trace(go.Scatter3d(
            x=[vertices[v1, 0], vertices[v2, 0]],
            y=[vertices[v1, 1], vertices[v2, 1]],
            z=[vertices[v1, 2], vertices[v2, 2]],
            mode='lines',
            line=dict(color='black', width=1.5),
            showlegend=False,
            hoverinfo='skip'
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
    
    print(f"[DEBUG] Criando visualização 3D: container={container.dimensions()}, placements={len(placements)}")
    
    # Adiciona wireframe do container
    create_container_wireframe(container, fig)
    print(f"[DEBUG] Wireframe adicionado: {len(fig.data)} traces")
    
    # Adiciona plano de base/chão para contexto visual profissional
    create_floor_plane(container, fig)
    print(f"[DEBUG] Plano de base adicionado: {len(fig.data)} traces")
    
    # Cria mapeamento de tipos para índices numéricos da paleta Viridis
    unique_types = list(set(block_dims))
    unique_types.sort()  # Ordena para consistência
    type_to_index = {block_type: i for i, block_type in enumerate(unique_types)}
    
    print(f"[DEBUG] Mapeamento tipo->índice: {type_to_index}")
    
    # Adiciona cada bloco com mesh otimizada e bordas
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
        
        # Adiciona bloco como mesh 3D otimizada com bordas (13 traces por bloco: 1 mesh + 12 bordas)
        create_block_mesh(x0, y0, z0, lx, ly, lz, color_index, fig)
    
    print(f"[DEBUG] Total de traces após adicionar blocos: {len(fig.data)}")
    print(f"[DEBUG] Blocos renderizados: {len(placements)} (cada bloco = 13 traces: 1 mesh + 12 bordas)")
    
    # Calcula dimensões totais para ajustar câmera
    total_width = container.dx * container.quantidade + (container.quantidade - 1) * 10  # dx + espaçamentos
    max_dimension = max(total_width, container.dy, container.dz)
    
    # Ajusta posição da câmera baseado no número de containers para visualização ótima inicial
    if container.quantidade == 1:
        # Container único - posição clássica isométrica mais afastada
        camera_eye = dict(x=2.5, y=2.5, z=2.0)
        camera_distance_factor = 1.0
    else:
        # Múltiplos containers - afasta mais e ajusta proporcionalmente
        camera_distance_factor = 1.2 + (container.quantidade - 1) * 0.4
        camera_eye = dict(
            x=2.0 * camera_distance_factor, 
            y=2.0 * camera_distance_factor, 
            z=1.8 * camera_distance_factor
        )
    
    center_x = total_width / 2  # Centro real de todos os containers
    center_y = container.dy / 2
    center_z = container.dz / 2
    
    # Configurações do layout com visualização estacionária e convenção matemática correta
    fig.update_layout(
        scene=dict(
            xaxis_title="Largura (cm)",     # Horizontal (esquerda-direita)
            yaxis_title="Profundidade (cm)",  # Profundidade (frente-trás) 
            zaxis_title="Altura (cm)",      # Altura (baixo-cima)
            aspectmode="manual",         # Controle manual das proporções
            aspectratio=dict(
                x=total_width/max_dimension, 
                y=container.dy/max_dimension, 
                z=container.dz/max_dimension
            ),
            # Configurações de câmera para visualização isométrica correta
            camera=dict(
                eye=camera_eye,  # Câmera isométrica ajustada dinamicamente
                center=dict(x=center_x, y=center_y, z=center_z),  # Centro calculado corretamente
                up=dict(x=0, y=0, z=1)          # Z para cima (convenção matemática)
            ),
            dragmode="orbit",  # Permite rotação para visualização
            # Configurações dos eixos para melhor visualização
            xaxis=dict(
                showgrid=True,
                gridcolor="dimgray",
                backgroundcolor="white",
                tickcolor="darkgray",
                linecolor="dimgray",
                title=dict(font=dict(color="black")),
                tickfont=dict(color="black"),
                range=[0, total_width + 5]  # Container começa em 0
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="dimgray",
                backgroundcolor="white",
                tickcolor="darkgray",
                linecolor="dimgray",
                title=dict(font=dict(color="black")),
                tickfont=dict(color="black"),
                range=[0, container.dy + 5]  # Container começa em 0
            ),
            zaxis=dict(
                showgrid=True,
                gridcolor="dimgray",
                backgroundcolor="white",
                tickcolor="darkgray",
                linecolor="dimgray",
                title=dict(font=dict(color="black")),
                tickfont=dict(color="black"),
                range=[0, container.dz + 5]  # Container começa em 0
            ),
            bgcolor="white"
        ),
        width=min(1200, 800 + container.quantidade * 100),  # Aumenta largura para múltiplos containers
        height=800,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
        title=dict(
            text=f"Visualização 3D - {container.quantidade} Container{'s' if container.quantidade > 1 else ''}",
            x=0.5,
            font=dict(size=16)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        # Configuração adicional para garantir câmera inicial correta
        scene_camera_projection_type="perspective"
    )
    
    print(f"[DEBUG] Layout configurado. Retornando figura com {len(fig.data)} traces")
    return fig


def create_static_multiview_3d(container: ContainerConfig, placements: List[Tuple], block_dims: List[Tuple], orders_df=None) -> List[go.Figure]:
    """
    Cria 3 visualizações estáticas com ângulos diferentes para substituir a visualização interativa.
    
    Args:
        container: Configuração do container
        placements: Lista de posicionamentos dos blocos
        block_dims: Dimensões dos blocos
        orders_df: DataFrame com dados dos pedidos (opcional)
        
    Returns:
        Lista com 3 figuras (frontal, lateral, superior)
    """
    from .utils import map_block_colors
    
    # Mapeia cores dos blocos
    block_colors = map_block_colors(block_dims, orders_df)
    
    figures = []
    view_names = ['Frontal', 'Lateral Direita', 'Superior']
    
    # Configurações de câmera para cada vista
    camera_configs = [
        # Vista Frontal (olhando de frente)
        dict(
            eye=dict(x=0, y=-2, z=0.5),
            center=dict(x=0.5, y=0.5, z=0.5),
            up=dict(x=0, y=0, z=1)
        ),
        # Vista Lateral Direita
        dict(
            eye=dict(x=2, y=0, z=0.5),
            center=dict(x=0.5, y=0.5, z=0.5),
            up=dict(x=0, y=0, z=1)
        ),
        # Vista Superior (olhando de cima)
        dict(
            eye=dict(x=0.5, y=0.5, z=2),
            center=dict(x=0.5, y=0.5, z=0.5),
            up=dict(x=0, y=1, z=0)
        )
    ]
    
    for i, (view_name, camera) in enumerate(zip(view_names, camera_configs)):
        fig = go.Figure()
        
        # Adiciona container wireframe
        create_container_wireframe(container, fig)
        
        # Adiciona plano do chão
        create_floor_plane(container, fig)
        
        # Adiciona blocos posicionados
        for idx, (x, y, z, dx, dy, dz, container_idx) in enumerate(placements):
            if idx < len(block_colors):
                color = block_colors[idx]
                
                # Offset para múltiplos containers
                offset_x = container_idx * (container.dx + 10)
                x_adjusted = x + offset_x
                
                # Cria bloco 3D
                fig.add_trace(create_3d_block(
                    x_adjusted, y, z, dx, dy, dz, color, f"Bloco {idx + 1}"
                ))
        
        # Configuração específica do layout para cada vista
        fig.update_layout(
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(x=1, y=0.8, z=0.6),
                camera=camera,
                xaxis=dict(
                    showgrid=True,
                    gridcolor="lightgray",
                    backgroundcolor="white",
                    tickcolor="darkgray",
                    linecolor="dimgray",
                    title=dict(text="Largura (cm)", font=dict(color="black")),
                    tickfont=dict(color="black"),
                    range=[0, container.dx * container.quantidade + 10 * (container.quantidade - 1) + 5]
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="lightgray",
                    backgroundcolor="white",
                    tickcolor="darkgray",
                    linecolor="dimgray",
                    title=dict(text="Profundidade (cm)", font=dict(color="black")),
                    tickfont=dict(color="black"),
                    range=[0, container.dy + 5]
                ),
                zaxis=dict(
                    showgrid=True,
                    gridcolor="lightgray",
                    backgroundcolor="white",
                    tickcolor="darkgray",
                    linecolor="dimgray",
                    title=dict(text="Altura (cm)", font=dict(color="black")),
                    tickfont=dict(color="black"),
                    range=[0, container.dz + 5]
                ),
                bgcolor="white"
            ),
            width=400,  # Menor para visualizações estáticas
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            title=dict(
                text=f"Vista {view_name}",
                x=0.5,
                font=dict(size=12)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        figures.append(fig)
    
    return figures