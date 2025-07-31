"""
Sistema de Visualização 3D em 2D Ultra-Simples
Desenha cubos 3D em perspectiva isométrica numa imagem 2D estática
"""
import plotly.graph_objects as go
import math


def project_3d_to_2d(x, y, z, angle_x=30, angle_y=45):
    """
    Projeta coordenadas 3D para 2D usando projeção isométrica.
    
    Args:
        x, y, z: Coordenadas 3D
        angle_x, angle_y: Ângulos de rotação em graus
    
    Returns:
        tuple: (x_2d, y_2d) coordenadas 2D projetadas
    """
    # Converte ângulos para radianos
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    
    # Projeção isométrica simplificada
    x_2d = x * math.cos(ay) + z * math.sin(ay)
    y_2d = y * math.cos(ax) + (z * math.cos(ay) - x * math.sin(ay)) * math.sin(ax)
    
    return x_2d, y_2d


def create_cube_wireframe_2d(x, y, z, dx, dy, dz):
    """
    Cria as linhas de um cubo 3D projetado em 2D.
    
    Args:
        x, y, z: Posição do cubo
        dx, dy, dz: Dimensões do cubo
    
    Returns:
        list: Lista de linhas do cubo [(x1, y1, x2, y2), ...]
    """
    # 8 vértices do cubo
    vertices_3d = [
        (x, y, z),           # 0: frente-baixo-esquerda
        (x+dx, y, z),        # 1: frente-baixo-direita
        (x+dx, y+dy, z),     # 2: trás-baixo-direita
        (x, y+dy, z),        # 3: trás-baixo-esquerda
        (x, y, z+dz),        # 4: frente-cima-esquerda
        (x+dx, y, z+dz),     # 5: frente-cima-direita
        (x+dx, y+dy, z+dz),  # 6: trás-cima-direita
        (x, y+dy, z+dz)      # 7: trás-cima-esquerda
    ]
    
    # Projeta vértices para 2D
    vertices_2d = []
    for vx, vy, vz in vertices_3d:
        x2d, y2d = project_3d_to_2d(vx, vy, vz)
        vertices_2d.append((x2d, y2d))
    
    # Define as 12 arestas do cubo
    edges = [
        # Base inferior
        (0, 1), (1, 2), (2, 3), (3, 0),
        # Base superior
        (4, 5), (5, 6), (6, 7), (7, 4),
        # Conexões verticais
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    # Cria linhas 2D
    lines = []
    for start_idx, end_idx in edges:
        x1, y1 = vertices_2d[start_idx]
        x2, y2 = vertices_2d[end_idx]
        lines.append((x1, y1, x2, y2))
    
    return lines, vertices_2d


def create_cube_faces_2d(x, y, z, dx, dy, dz, color):
    """
    Cria faces preenchidas do cubo para dar sensação 3D.
    
    Args:
        x, y, z: Posição do cubo
        dx, dy, dz: Dimensões do cubo
        color: Cor base do cubo
    
    Returns:
        list: Lista de traces do Plotly para as faces
    """
    # Obter vértices projetados
    lines, vertices_2d = create_cube_wireframe_2d(x, y, z, dx, dy, dz)
    
    traces = []
    
    # Face frontal (mais clara)
    front_face = [vertices_2d[0], vertices_2d[1], vertices_2d[5], vertices_2d[4], vertices_2d[0]]
    x_coords = [p[0] for p in front_face]
    y_coords = [p[1] for p in front_face]
    
    traces.append(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='lines',
        fill='toself',
        fillcolor=color,
        opacity=0.8,
        line=dict(color='black', width=1),
        showlegend=False
    ))
    
    # Face direita (mais escura)
    right_face = [vertices_2d[1], vertices_2d[2], vertices_2d[6], vertices_2d[5], vertices_2d[1]]
    x_coords = [p[0] for p in right_face]
    y_coords = [p[1] for p in right_face]
    
    # Cor mais escura para a face lateral
    dark_color = color.replace('70%', '50%') if 'hsl' in color else color
    
    traces.append(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='lines',
        fill='toself',
        fillcolor=dark_color,
        opacity=0.6,
        line=dict(color='black', width=1),
        showlegend=False
    ))
    
    # Face superior (tom médio)
    top_face = [vertices_2d[4], vertices_2d[5], vertices_2d[6], vertices_2d[7], vertices_2d[4]]
    x_coords = [p[0] for p in top_face]
    y_coords = [p[1] for p in top_face]
    
    # Cor média para a face superior
    medium_color = color.replace('70%', '60%') if 'hsl' in color else color
    
    traces.append(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='lines',
        fill='toself',
        fillcolor=medium_color,
        opacity=0.7,
        line=dict(color='black', width=1),
        showlegend=False
    ))
    
    return traces


def create_simple_3d_2d_view(container, placements, block_dims):
    """
    Cria UMA visualização 3D desenhada em 2D (projeção isométrica estática).
    
    Args:
        container: Dicionário com dimensões do contêiner  
        placements: Lista de posicionamentos dos blocos
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        go.Figure: Uma única figura com cubos 3D desenhados em 2D
    """
    try:
        # Cria figura vazia
        fig = go.Figure()
        
        # 1. Desenha o contêiner como cubo wireframe
        container_lines, _ = create_cube_wireframe_2d(
            0, 0, 0, 
            container.dx, container.dy, container.dz
        )
        
        # Adiciona todas as linhas do contêiner
        for x1, y1, x2, y2 in container_lines:
            fig.add_trace(go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode='lines',
                line=dict(color='black', width=3),
                showlegend=False
            ))
        
        # 2. Desenha cada bloco como cubo com faces coloridas
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta']
        
        for i, (placement, dims) in enumerate(zip(placements, block_dims)):
            if placement is None:
                continue
                
            x, y, z = placement
            dx, dy, dz = dims['dx'], dims['dy'], dims['dz']
            
            # Usa cor HSL para melhor controle de tonalidade
            color = f'hsl({(i * 50) % 360}, 70%, 60%)'
            
            # Cria faces do cubo
            cube_faces = create_cube_faces_2d(x, y, z, dx, dy, dz, color)
            
            # Adiciona todas as faces do cubo
            for face_trace in cube_faces:
                fig.add_trace(face_trace)
            
            # Adiciona wireframe por cima para definir as bordas
            cube_lines, _ = create_cube_wireframe_2d(x, y, z, dx, dy, dz)
            for x1, y1, x2, y2 in cube_lines:
                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode='lines',
                    line=dict(color='black', width=1),
                    showlegend=False
                ))
        
        # 3. Configurações da figura
        fig.update_layout(
            title="📦 Empacotamento 3D (Vista Isométrica)",
            xaxis_title="Projeção X",
            yaxis_title="Projeção Y",
            showlegend=False,  # Remove legenda para ficar mais limpo
            width=700,
            height=500,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(
                showgrid=False,  # Remove grid para ficar mais limpo
                zeroline=False,
                scaleanchor="y",  # Mantém proporção 1:1
                scaleratio=1
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False
            ),
            plot_bgcolor='white'
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro na visualização 3D-2D: {e}")
        
        # Se tudo falhar, cria um gráfico vazio básico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='markers', name='Teste'))
        fig.update_layout(title="Gráfico de Teste", width=400, height=300)
        return fig
    """
    Cria UMA visualização 2D simples que sempre funciona.
    Vista frontal (x vs z) - largura vs altura
    
    Args:
        container: Dicionário com dimensões do contêiner  
        placements: Lista de posicionamentos dos blocos
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        go.Figure: Uma única figura 2D
    """
    try:
        # Cria figura vazia
        fig = go.Figure()
        
        # 1. Desenha o contêiner como um retângulo
        container_x = [0, container['dx'], container['dx'], 0, 0]
        container_z = [0, 0, container['dz'], container['dz'], 0]
        
        fig.add_trace(go.Scatter(
            x=container_x,
            y=container_z,
            mode='lines',
            line=dict(color='black', width=3),
            name='Contêiner',
            showlegend=True
        ))
        
        # 2. Desenha cada bloco como um retângulo
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta']
        
        for i, (placement, dims) in enumerate(zip(placements, block_dims)):
            if placement is None:
                continue
                
            x, y, z = placement
            dx, dy, dz = dims['dx'], dims['dy'], dims['dz']
            
            # Retângulo do bloco (vista frontal: x vs z)
            block_x = [x, x + dx, x + dx, x, x]
            block_z = [z, z, z + dz, z + dz, z]
            
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=block_x,
                y=block_z,
                mode='lines',
                fill='toself',
                fillcolor=color,
                opacity=0.7,
                line=dict(color=color, width=2),
                name=f'Produto {i+1}',
                showlegend=True
            ))
        
        # 3. Configurações básicas
        fig.update_layout(
            title="📦 Vista Frontal do Empacotamento",
            xaxis_title="Largura (mm)",
            yaxis_title="Altura (mm)",
            showlegend=True,
            width=600,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            plot_bgcolor='white'
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro na visualização 2D simples: {e}")
        
        # Se tudo falhar, cria um gráfico vazio básico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='markers', name='Teste'))
        fig.update_layout(title="Gráfico de Teste", width=400, height=300)
        return fig


def test_simple_visualization():
    """Testa a visualização 3D-2D com dados fictícios"""
    
    # Simula container como objeto com atributos
    class Container:
        def __init__(self):
            self.dx = 1000
            self.dy = 800  
            self.dz = 600
    
    container = Container()
    
    # Blocos teste
    placements = [(0, 0, 0), (300, 0, 0), (0, 300, 0)]
    block_dims = [
        {'dx': 200, 'dy': 200, 'dz': 100},
        {'dx': 150, 'dy': 150, 'dz': 200},
        {'dx': 250, 'dy': 100, 'dz': 150}
    ]
    
    fig = create_simple_3d_2d_view(container, placements, block_dims)
    print(f"Figura 3D-2D criada com {len(fig.data)} elementos")
    return fig


if __name__ == "__main__":
    # Teste direto
    fig = test_simple_visualization()
    fig.show()
