import streamlit as st
import pandas as pd
import numpy as np
from math import ceil
import warnings
from distribuir_milp import Cuboid
import json
import random

# Suprime todos os warnings
warnings.filterwarnings('ignore')

# GPU heuristic pack function (importa direto do módulo)
from run_packing_gpu import gpu_heuristic_pack

st.set_page_config(page_title="GPU Packing UI", layout="wide")
st.title("Empacotamento 3D com GPU")

# Container dimensions
col1, col2, col3 = st.columns(3)
with col1:
    dx = st.number_input("Dimensão X do contêiner", min_value=1, value=30)
with col2:
    dy = st.number_input("Dimensão Y do contêiner", min_value=1, value=40)
with col3:
    dz = st.number_input("Dimensão Z do contêiner", min_value=1, value=50)

# Block types table
st.subheader("Tipos de blocos")
initial = {"dx": [1], "dy": [1], "dz": [2], "quantidade": [100]}
types_raw = st.data_editor(initial, num_rows="dynamic", key="block_types")
if isinstance(types_raw, dict):
    types_df = pd.DataFrame(types_raw)
else:
    types_df = types_raw

# GPU Heuristic parameters
st.sidebar.subheader("Parâmetros da heurística GPU")
pop_size = st.sidebar.slider("Tamanho da população", min_value=64, max_value=16384, value=2048, step=64)

def greedy_pack(dx, dy, dz, block_dims):
    """Empacotamento sequencial ULTRA compacto: preenche sem deixar buracos."""
    placements = []
    ocupado = np.zeros((dx, dy, dz), dtype=bool)
    
    # Para cada bloco, encontra a primeira posição válida sequencialmente
    for bloco_idx, (lx, ly, lz) in enumerate(block_dims):
        colocado = False
        
        # Percorre o container de forma SEQUENCIAL: x -> y -> z
        for x in range(dx - lx + 1):
            if colocado:
                break
            for y in range(dy - ly + 1):
                if colocado:
                    break
                for z in range(dz - lz + 1):
                    # Verifica se o espaço está totalmente livre
                    if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                        # Marca o espaço como ocupado
                        ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                        # Adiciona o bloco
                        placements.append((x, y, z, bloco_idx))
                        colocado = True
                        break
        
        # Se não conseguiu colocar o bloco, para de tentar
        if not colocado:
            st.warning(f"⚠️ Não foi possível encaixar o bloco {bloco_idx+1}. Parando no bloco {len(placements)}.")
            break
    
    return placements

def gpu_calculate_max_capacity(dx, dy, dz, block_dims):
    """Fase 1: Calcula a capacidade máxima teórica do container."""
    container_volume = dx * dy * dz
    block_volumes = [lx * ly * lz for lx, ly, lz in block_dims]
    total_block_volume = sum(block_volumes)
    max_blocks = min(len(block_dims), container_volume // min(block_volumes))
    return min(max_blocks, len(block_dims))

def gpu_optimize_packing(dx, dy, dz, block_dims, target_blocks):
    """Fase 2: Empacotamento compacto COM ROTAÇÃO."""
    st.write(f"🎯 META: Tentar encaixar {target_blocks} blocos com ROTAÇÃO")
    
    # CORREÇÃO: Chama a função com rotação
    placements = greedy_pack_with_rotation(dx, dy, dz, block_dims[:target_blocks])
    count = len(placements)
    st.write(f"📊 Greedy com rotação conseguiu: {count} blocos")
    st.success(f"🏆 Resultado: Empacotamento COM ROTAÇÃO: {count} blocos!")
    
    return placements

def hybrid_pack(dx, dy, dz, block_dims, gpu_placements):
    """Algoritmo híbrido: usa resultado GPU e preenche buracos com Greedy."""
    ocupado = np.zeros((dx, dy, dz), dtype=bool)
    placements = []
    
    # Marca posições ocupadas pelo GPU
    for x0, y0, z0, o in gpu_placements:
        lx, ly, lz = block_dims[o]
        if x0 + lx <= dx and y0 + ly <= dy and z0 + lz <= dz:
            ocupado[x0:x0+lx, y0:y0+ly, z0:z0+lz] = True
            placements.append((x0, y0, z0, o))
    
    # Tenta encaixar blocos restantes nos buracos
    used_blocks = len(placements)
    for bloco_idx in range(used_blocks, len(block_dims)):
        lx, ly, lz = block_dims[bloco_idx]
        colocado = False
        
        for x in range(dx - lx + 1):
            if colocado: break
            for y in range(dy - ly + 1):
                if colocado: break
                for z in range(dz - lz + 1):
                    if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                        ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                        placements.append((x, y, z, bloco_idx))
                        colocado = True
                        break
    
    return placements

def get_orientations(lx, ly, lz):
    """Retorna todas as orientações possíveis de um bloco."""
    orientations = []
    dims = [lx, ly, lz]
    
    # Gera todas as permutações únicas das dimensões
    import itertools
    for perm in set(itertools.permutations(dims)):
        orientations.append(perm)
    
    return orientations

def greedy_pack_with_rotation(dx, dy, dz, block_dims):
    """Empacotamento sequencial com ROTAÇÃO: maximiza preenchimento."""
    placements = []
    ocupado = np.zeros((dx, dy, dz), dtype=bool)
    
    # Para cada bloco, tenta todas as rotações possíveis
    for bloco_idx, original_dims in enumerate(block_dims):
        colocado = False
        orientations = get_orientations(*original_dims)
        
        # Tenta cada orientação
        for orientation in orientations:
            if colocado:
                break
            lx, ly, lz = orientation
            
            # Percorre o container sequencialmente
            for x in range(dx - lx + 1):
                if colocado:
                    break
                for y in range(dy - ly + 1):
                    if colocado:
                        break
                    for z in range(dz - lz + 1):
                        # Verifica se o espaço está livre
                        if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                            # Marca como ocupado
                            ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                            # Salva com a orientação usada
                            placements.append((x, y, z, bloco_idx, orientation))
                            colocado = True
                            # st.write(f"🔄 Bloco {bloco_idx+1}: {original_dims} → {orientation} em ({x},{y},{z})")  # Removido
                            break
        
        if not colocado:
            st.warning(f"⚠️ Bloco {bloco_idx+1} não coube em nenhuma orientação. Parando.")
            break
    
    return placements

def cor_aleatoria():
    """Gera uma cor hexadecimal aleatória."""
    return "#%06x" % random.randint(0, 0xFFFFFF)

if st.button("Executar GPU Heurística"):
    # Filtra linhas válidas (sem NaN e quantidade > 0)
    types_df_valid = types_df.dropna(subset=["dx", "dy", "dz", "quantidade"])
    types_df_valid = types_df_valid[types_df_valid["quantidade"] > 0]

    block_dims = []
    for _, row in types_df_valid.iterrows():
        dims = (int(row.dx), int(row.dy), int(row.dz))
        qtd = int(row.quantidade)
        block_dims.extend([dims] * qtd)

    # Ordena blocos do maior para o menor volume
    block_dims.sort(key=lambda dims: dims[0]*dims[1]*dims[2], reverse=True)

    # Calcula o volume total do container
    container_volume = dx * dy * dz

    # Calcula o volume de cada bloco
    block_volumes = [lx * ly * lz for lx, ly, lz in block_dims]

    # Calcula a capacidade máxima considerando todos os blocos
    max_blocks = 0
    used_volume = 0
    for vol in block_volumes:
        if used_volume + vol <= container_volume:
            used_volume += vol
            max_blocks += 1
        else:
            break

    st.write(f"📏 Container: {dx}×{dy}×{dz} = {container_volume} unidades")
    st.write(f"📦 Tipos de blocos: {set(block_dims)}")
    st.write(f"🎯 Capacidade máxima calculada: {max_blocks} blocos")

    # Na distribuição, percorre todos os blocos da lista
    placements = gpu_optimize_packing(dx, dy, dz, block_dims, max_blocks)
    count = len(placements)
    st.write(f"✅ RESULTADO FINAL: {count} blocos empacotados de {len(block_dims)} solicitados!")
    if count < len(block_dims):
        faltam = len(block_dims) - count
        st.warning(f"⚠️ Atenção: {faltam} blocos ficaram de fora por falta de espaço no container.")

    # Gera o dicionário de cores para cada tipo de bloco único
    tipos_unicos = set(block_dims)
    tipo_cores = {dims: cor_aleatoria() for dims in tipos_unicos}

    # Salve placements e tipo_cores em session_state para uso no gráfico
    st.session_state["placements"] = placements
    st.session_state["tipo_cores"] = tipo_cores

# Plot 3D interativo com Plotly
try:
    import plotly.graph_objects as go
    from matplotlib import cm
    import numpy as np
    
    # Recupere placements e tipo_cores do session_state
    placements = st.session_state.get("placements", [])
    tipo_cores = st.session_state.get("tipo_cores", {})

    # Cria paleta de cores viridis
    viridis = cm.get_cmap('viridis')
    
    cd = Cuboid(dx, dy, dz)
    fig = go.Figure()
    
    # Container como wireframe (arestas)
    verts = cd._get_vertices((0,0,0), dx, dy, dz)
    edges = [
        (0,1), (1,2), (2,3), (3,0), # base inferior
        (4,5), (5,6), (6,7), (7,4), # topo
        (0,4), (1,5), (2,6), (3,7)  # laterais
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
    
    # Visualização: suporta n tipos de bloco
    for idx, placement in enumerate(placements):
        # Suporte para rotação
        if len(placement) == 5:
            x0, y0, z0, o, orientation = placement
            lx, ly, lz = orientation
            original_dims = block_dims[o]
            cor = tipo_cores[original_dims]
        else:
            x0, y0, z0, o = placement
            lx, ly, lz = block_dims[o]
            cor = tipo_cores[(lx, ly, lz)]
        
        # Vértices do cubo com dimensões corretas
        vx = [x0, x0+lx, x0+lx, x0, x0, x0+lx, x0+lx, x0]
        vy = [y0, y0, y0+ly, y0+ly, y0, y0, y0+ly, y0+ly]
        vz = [z0, z0, z0, z0, z0+lz, z0+lz, z0+lz, z0+lz]
        
        fig.add_trace(go.Mesh3d(
            x=vx, y=vy, z=vz,
            i=[0, 0, 0, 1, 4, 4, 4, 5, 2, 2, 2, 3],
            j=[1, 2, 4, 5, 5, 6, 1, 2, 3, 7, 6, 7],
            k=[2, 3, 5, 6, 6, 7, 2, 3, 7, 6, 5, 4],
            opacity=0.85,
            color=cor,
            showscale=False,
            hoverinfo='none'
        ))
        
        # Adiciona borda ao bloco
        arestas = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        for a in arestas:
            fig.add_trace(go.Scatter3d(
                x=[vx[a[0]], vx[a[1]]],
                y=[vy[a[0]], vy[a[1]]],
                z=[vz[a[0]], vz[a[1]]],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False
            ))
        else:
            # Bloco fora do container (não desenha)
            continue
    
    # Após adicionar todos os blocos ao fig, corrija a proporção do gráfico:
    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="manual",
            aspectratio=dict(
                x=dx / max(dx, dy, dz),
                y=dy / max(dx, dy, dz),
                z=dz / max(dx, dy, dz)
            )
        ),
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
except ImportError:
    st.warning("Instale plotly para visualização interativa.")
