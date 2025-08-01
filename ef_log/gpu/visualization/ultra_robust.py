"""
Sistema de Visualização 3D Ultra-Robusto
Versão garantida que sempre funciona usando apenas Scatter3d
"""

import numpy as np
import plotly.graph_objects as go
from typing import List, Tuple, Dict
from .models import ContainerConfig


def create_robust_3d_block(x, y, z, dx, dy, dz, color, fig):
    """
    Cria um bloco 3D usando apenas Scatter3d - método mais confiável.
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
    
    # 1. Desenha todas as arestas do cubo
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # base inferior
        (4, 5), (5, 6), (6, 7), (7, 4),  # topo superior
        (0, 4), (1, 5), (2, 6), (3, 7)   # arestas verticais
    ]
    
    for edge in edges:
        v1, v2 = edge
        fig.add_trace(go.Scatter3d(
            x=[vertices[v1][0], vertices[v2][0]],
            y=[vertices[v1][1], vertices[v2][1]],
            z=[vertices[v1][2], vertices[v2][2]],
            mode='lines',
            line=dict(color=color, width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # 2. Adiciona faces como linhas conectadas (simulando preenchimento)
    faces = [
        [0, 1, 2, 3, 0],  # base inferior
        [4, 5, 6, 7, 4],  # topo superior
        [0, 1, 5, 4, 0],  # face frontal
        [3, 2, 6, 7, 3],  # face traseira
        [0, 3, 7, 4, 0],  # face esquerda
        [1, 2, 6, 5, 1]   # face direita
    ]
    
    # Desenha cada face
    for i, face in enumerate(faces):
        face_x = [vertices[v][0] for v in face]
        face_y = [vertices[v][1] for v in face]
        face_z = [vertices[v][2] for v in face]
        
        # Linha do contorno da face
        fig.add_trace(go.Scatter3d(
            x=face_x,
            y=face_y,
            z=face_z,
            mode='lines',
            line=dict(color=color, width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Preenche com linhas internas para dar sensação de volume
        if i < 2:  # Apenas base e topo para não sobrecarregar
            center_x = sum(face_x[:-1]) / 4
            center_y = sum(face_y[:-1]) / 4 
            center_z = sum(face_z[:-1]) / 4
            
            # Linhas do centro para os vértices
            for j in range(4):
                fig.add_trace(go.Scatter3d(
                    x=[center_x, face_x[j]],
                    y=[center_y, face_y[j]],
                    z=[center_z, face_z[j]],
                    mode='lines',
                    line=dict(color=color, width=1),
                    opacity=0.6,
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    # 3. Adiciona pontos nos vértices para destacar
    fig.add_trace(go.Scatter3d(
        x=[v[0] for v in vertices],
        y=[v[1] for v in vertices],
        z=[v[2] for v in vertices],
        mode='markers',
        marker=dict(
            color=color,
            size=4,
            opacity=0.9
        ),
        showlegend=False,
        hoverinfo='skip'
    ))


def create_container_wireframe(container: ContainerConfig, fig: go.Figure):
    """Cria wireframe do container usando método ultra-confiável."""
    dx, dy, dz = container.dx, container.dy, container.dz
    
    for container_idx in range(container.quantidade):
        offset_x = container_idx * (dx + 20)
        
        # Vértices do container
        vertices = [
            [offset_x, 0, 0], [offset_x + dx, 0, 0], [offset_x + dx, dy, 0], [offset_x, dy, 0],
            [offset_x, 0, dz], [offset_x + dx, 0, dz], [offset_x + dx, dy, dz], [offset_x, dy, dz]
        ]
        
        # Arestas do container
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # base
            (4,5), (5,6), (6,7), (7,4),  # topo
            (0,4), (1,5), (2,6), (3,7)   # verticais
        ]
        
        # Desenha arestas do container
        for edge in edges:
            v1, v2 = edge
            fig.add_trace(go.Scatter3d(
                x=[vertices[v1][0], vertices[v2][0]],
                y=[vertices[v1][1], vertices[v2][1]],
                z=[vertices[v1][2], vertices[v2][2]],
                mode='lines',
                line=dict(color='black', width=3),
                showlegend=False,
                hoverinfo='skip'
            ))


def create_robust_multiview_3d(container: ContainerConfig, placements: List[Tuple], 
                              block_dims: List[Tuple]) -> List[go.Figure]:
    """
    Cria visualizações 3D usando método ultra-robusto.
    """
    # Configurações de câmera
    cameras = [
        dict(eye=dict(x=0, y=-1.5, z=0.5), center=dict(x=0.5, y=0.5, z=0.5), up=dict(x=0, y=0, z=1)),
        dict(eye=dict(x=1.5, y=0, z=0.5), center=dict(x=0.5, y=0.5, z=0.5), up=dict(x=0, y=0, z=1)),
        dict(eye=dict(x=0.5, y=0.5, z=1.5), center=dict(x=0.5, y=0.5, z=0), up=dict(x=0, y=1, z=0))
    ]
    
    view_names = ['Frontal', 'Lateral', 'Superior']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    figures = []
    
    for i, (camera, name) in enumerate(zip(cameras, view_names)):
        fig = go.Figure()
        
        print(f"Criando vista {name}...")
        
        # Adiciona container
        create_container_wireframe(container, fig)
        
        # Adiciona blocos
        blocks_added = 0
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
                    
                offset_x = container_idx * (container.dx + 20)
                x_adjusted = x + offset_x
                color = colors[idx % len(colors)]
                
                create_robust_3d_block(x_adjusted, y, z, dx, dy, dz, color, fig)
                blocks_added += 1
                print(f"   Bloco {idx+1}: {color} em ({x_adjusted}, {y}, {z})")
                
            except Exception as e:
                print(f"   Erro no bloco {idx}: {e}")
                continue
        
        print(f"   {blocks_added} blocos adicionados")
        
        # Layout
        max_x = container.dx * container.quantidade + 20 * (container.quantidade - 1)
        
        fig.update_layout(
            scene=dict(
                camera=camera,
                aspectmode='cube',
                xaxis=dict(title="Largura (cm)", range=[0, max_x + 10]),
                yaxis=dict(title="Profundidade (cm)", range=[0, container.dy + 10]),
                zaxis=dict(title="Altura (cm)", range=[0, container.dz + 10]),
                bgcolor="white"
            ),
            title=f"Vista {name}",
            width=400,
            height=350,
            margin=dict(l=5, r=5, t=40, b=5),
            showlegend=False
        )
        
        figures.append(fig)
        print(f"✅ Vista {name} criada com {len(fig.data)} elementos")
    
    return figures
