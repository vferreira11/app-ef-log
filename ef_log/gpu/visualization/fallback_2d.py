"""
Sistema de Visualização 2D/3D Híbrido
Usa Scatter2D com projeções 3D para garantir que sempre funcione
"""

import numpy as np
import plotly.graph_objects as go
from typing import List, Tuple, Dict
from .models import ContainerConfig


def create_2d_projection_block(x, y, z, dx, dy, dz, color, fig, view_type='frontal'):
    """
    Cria projeção 2D de um bloco 3D - método 100% confiável.
    """
    if view_type == 'frontal':
        # Vista frontal: X vs Z (largura vs altura)
        rect_x = [x, x+dx, x+dx, x, x]
        rect_y = [z, z, z+dz, z+dz, z]
        xlabel, ylabel = "Largura (cm)", "Altura (cm)"
        
    elif view_type == 'lateral':
        # Vista lateral: Y vs Z (profundidade vs altura)
        rect_x = [y, y+dy, y+dy, y, y]
        rect_y = [z, z, z+dz, z+dz, z]
        xlabel, ylabel = "Profundidade (cm)", "Altura (cm)"
        
    else:  # superior
        # Vista superior: X vs Y (largura vs profundidade)
        rect_x = [x, x+dx, x+dx, x, x]
        rect_y = [y, y, y+dy, y+dy, y]
        xlabel, ylabel = "Largura (cm)", "Profundidade (cm)"
    
    # Adiciona retângulo preenchido
    fig.add_trace(go.Scatter(
        x=rect_x,
        y=rect_y,
        mode='lines',
        fill='toself',
        fillcolor=color,
        line=dict(color='black', width=2),
        opacity=0.7,
        showlegend=False,
        hovertemplate=f"Bloco {dx}×{dy}×{dz}cm<extra></extra>"
    ))
    
    return xlabel, ylabel


def create_2d_container_outline(container: ContainerConfig, fig: go.Figure, view_type='frontal'):
    """Cria contorno 2D do container."""
    dx, dy, dz = container.dx, container.dy, container.dz
    
    for container_idx in range(container.quantidade):
        if view_type == 'frontal':
            offset = container_idx * (dx + 20)
            outline_x = [offset, offset + dx, offset + dx, offset, offset]
            outline_y = [0, 0, dz, dz, 0]
        elif view_type == 'lateral':
            outline_x = [0, dy, dy, 0, 0]
            outline_y = [0, 0, dz, dz, 0]
        else:  # superior
            offset = container_idx * (dx + 20)
            outline_x = [offset, offset + dx, offset + dx, offset, offset]
            outline_y = [0, 0, dy, dy, 0]
        
        fig.add_trace(go.Scatter(
            x=outline_x,
            y=outline_y,
            mode='lines',
            line=dict(color='black', width=4),
            showlegend=False,
            name=f'Container {container_idx + 1}' if container_idx == 0 else ''
        ))


def create_guaranteed_2d_views(container: ContainerConfig, placements: List[Tuple], 
                              block_dims: List[Tuple]) -> List[go.Figure]:
    """
    Cria visualizações 2D que funcionam sempre.
    """
    view_types = ['frontal', 'lateral', 'superior']
    view_names = ['Frontal', 'Lateral', 'Superior']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    figures = []
    
    for view_type, view_name in zip(view_types, view_names):
        fig = go.Figure()
        
        print(f"Criando vista 2D {view_name}...")
        
        # Adiciona container
        create_2d_container_outline(container, fig, view_type)
        
        # Adiciona blocos
        blocks_added = 0
        xlabel, ylabel = "X", "Y"  # default
        
        for idx, placement in enumerate(placements):
            if idx >= len(block_dims):
                continue
                
            try:
                if len(placement) >= 6:
                    x, y, z = placement[0], placement[1], placement[2]
                    dx, dy, dz = placement[3], placement[4], placement[5]
                    container_idx = placement[6] if len(placement) > 6 else 0
                else:
                    continue
                    
                # Ajusta para múltiplos containers apenas na vista frontal e superior
                if view_type in ['frontal', 'superior']:
                    offset_x = container_idx * (container.dx + 20)
                    x_adjusted = x + offset_x
                else:
                    x_adjusted = x
                    
                color = colors[idx % len(colors)]
                
                xlabel, ylabel = create_2d_projection_block(
                    x_adjusted, y, z, dx, dy, dz, color, fig, view_type
                )
                blocks_added += 1
                print(f"   Bloco {idx+1}: {color} em ({x_adjusted}, {y}, {z})")
                
            except Exception as e:
                print(f"   Erro no bloco {idx}: {e}")
                continue
        
        print(f"   {blocks_added} blocos adicionados")
        
        # Layout 2D
        max_x = container.dx * container.quantidade + 20 * (container.quantidade - 1)
        
        if view_type == 'frontal':
            x_range = [0, max_x + 10]
            y_range = [0, container.dz + 10]
        elif view_type == 'lateral':
            x_range = [0, container.dy + 10]
            y_range = [0, container.dz + 10]
        else:  # superior
            x_range = [0, max_x + 10]
            y_range = [0, container.dy + 10]
        
        fig.update_layout(
            title=f"Vista {view_name}",
            xaxis=dict(
                title=xlabel,
                range=x_range,
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title=ylabel,
                range=y_range,
                showgrid=True,
                gridcolor='lightgray',
                scaleanchor="x",
                scaleratio=1
            ),
            width=400,
            height=350,
            margin=dict(l=50, r=10, t=40, b=50),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        figures.append(fig)
        print(f"✅ Vista 2D {view_name} criada com {len(fig.data)} elementos")
    
    return figures


def create_simple_3d_fallback(container: ContainerConfig, placements: List[Tuple], 
                             block_dims: List[Tuple]) -> List[go.Figure]:
    """
    Fallback 3D ultra-simples usando apenas pontos.
    """
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    # Uma única figura 3D simples
    fig = go.Figure()
    
    # Adiciona pontos dos blocos
    for idx, placement in enumerate(placements):
        if idx >= len(block_dims) or len(placement) < 6:
            continue
            
        x, y, z = placement[0], placement[1], placement[2]
        dx, dy, dz = placement[3], placement[4], placement[5]
        color = colors[idx % len(colors)]
        
        # Centro do bloco
        center_x = x + dx/2
        center_y = y + dy/2
        center_z = z + dz/2
        
        fig.add_trace(go.Scatter3d(
            x=[center_x],
            y=[center_y],
            z=[center_z],
            mode='markers',
            marker=dict(
                color=color,
                size=10,
                opacity=0.8
            ),
            showlegend=False,
            text=f"Bloco {dx}×{dy}×{dz}",
            hovertemplate="%{text}<extra></extra>"
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Largura"),
            yaxis=dict(title="Profundidade"), 
            zaxis=dict(title="Altura")
        ),
        title="Vista 3D Simplificada",
        width=400,
        height=400
    )
    
    return [fig]


def create_single_2d_view(container, placements, block_dims, view_index):
    """
    Cria uma única vista 2D específica baseada no índice.
    
    Args:
        container: Dicionário com dimensões do contêiner
        placements: Lista de posicionamentos dos blocos
        block_dims: Lista de dimensões dos blocos
        view_index: 0=frontal, 1=lateral, 2=superior
    
    Returns:
        go.Figure: Figura 2D da vista específica
    """
    try:
        # Configurações de projeção
        projections = [
            {"title": "🔍 Vista Frontal (2D)", "x_axis": "x", "y_axis": "z", "x_label": "Largura", "y_label": "Altura"},
            {"title": "🔍 Vista Lateral (2D)", "x_axis": "y", "y_axis": "z", "x_label": "Profundidade", "y_label": "Altura"},
            {"title": "🔍 Vista Superior (2D)", "x_axis": "x", "y_axis": "y", "x_label": "Largura", "y_label": "Profundidade"}
        ]
        
        if view_index >= len(projections):
            return None
            
        proj = projections[view_index]
        
        # Cria figura 2D
        fig = go.Figure()
        
        # Adiciona contêiner como retângulo
        container_coords = create_2d_projection_block(
            container, proj["x_axis"], proj["y_axis"], 0, 0, 0
        )
        
        fig.add_trace(go.Scatter(
            x=container_coords["x"],
            y=container_coords["y"],
            mode='lines',
            line=dict(color='black', width=3),
            name='Contêiner',
            showlegend=True
        ))
        
        # Adiciona blocos
        for i, (placement, dims) in enumerate(zip(placements, block_dims)):
            if placement is None:
                continue
                
            x, y, z = placement
            block_coords = create_2d_projection_block(dims, proj["x_axis"], proj["y_axis"], x, y, z)
            
            # Cor única para cada bloco
            color = f'hsl({(i * 137) % 360}, 70%, 50%)'
            
            fig.add_trace(go.Scatter(
                x=block_coords["x"],
                y=block_coords["y"],
                mode='lines+markers',
                fill='toself',
                fillcolor=color.replace('50%', '30%'),
                line=dict(color=color, width=2),
                name=f'Produto {i+1}',
                showlegend=False
            ))
        
        # Configurações do layout
        fig.update_layout(
            title=proj["title"],
            xaxis_title=proj["x_label"],
            yaxis_title=proj["y_label"],
            showlegend=True,
            width=400,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar vista 2D individual: {e}")
        return None
