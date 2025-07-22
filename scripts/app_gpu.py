import streamlit as st
import pandas as pd
import numpy as np
from math import ceil
import warnings
from distribuir_milp import Cuboid
import json

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

if st.button("Executar GPU Heurística"):
    # Prepara dimensões e quantidades dos blocos
    total_blocks = sum(int(row.quantidade) for _, row in types_df.iterrows())
    block_dims = []
    for _, row in types_df.iterrows():
        dims = (int(row.dx), int(row.dy), int(row.dz))
        qtd = int(row.quantidade)
        block_dims.extend([dims] * qtd)
    
    # Executa heurística GPU
    placements = gpu_heuristic_pack(dx, dy, dz, block_dims, pop_size=pop_size, N=total_blocks)
    count = len(placements)
    st.success(f"Solução encontrou {count} blocos de {total_blocks} solicitados!")

    # Plot 3D interativo com Plotly
    try:
        import plotly.graph_objects as go
        from matplotlib import cm
        import numpy as np
        
        # Cria paleta de cores viridis
        viridis = cm.get_cmap('viridis')
        
        cd = Cuboid(dx, dy, dz)
        fig = go.Figure()
        
        # Container
        verts = cd._get_vertices((0,0,0), dx, dy, dz)
        x, y, z = zip(*verts)
        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, opacity=0.1, color='lightgrey', name='Container'))
        
        # Blocos com cores diferentes e formato 3D correto
        for idx, (x0, y0, z0, o) in enumerate(placements):
            lx, ly, lz = block_dims[o]
            
            # Pegar cor da paleta viridis baseado na posição do bloco
            color_idx = idx / len(placements) if len(placements) > 1 else 0
            rgb_color = viridis(color_idx)
            hex_color = f'rgb({int(rgb_color[0]*255)},{int(rgb_color[1]*255)},{int(rgb_color[2]*255)})'
            
            # Criar cubo 3D sólido
            fig.add_trace(go.Mesh3d(
                # Define os 8 vértices do cubo
                x=[x0, x0+lx, x0+lx, x0, x0, x0+lx, x0+lx, x0],
                y=[y0, y0, y0+ly, y0+ly, y0, y0, y0+ly, y0+ly],
                z=[z0, z0, z0, z0, z0+lz, z0+lz, z0+lz, z0+lz],
                # Define os triângulos que formam cada face
                i=[0, 0, 0, 1, 4, 4, 4, 5, 2, 2, 2, 3],
                j=[1, 2, 4, 5, 5, 6, 1, 2, 3, 7, 6, 7],
                k=[2, 3, 5, 6, 6, 7, 2, 3, 7, 6, 5, 4],
                opacity=0.7,
                color=hex_color,
                flatshading=True,
                showscale=False,
                hoverinfo='none'
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[-5, dx+5], title="X"),
                yaxis=dict(range=[-5, dy+5], title="Y (Altura)"),
                zaxis=dict(range=[-5, dz+5], title="Z"),
                camera=dict(
                    eye=dict(x=1.2, y=1.2, z=1.2),
                    up=dict(x=0, y=1, z=0)
                ),
                aspectmode='cube'
            ),
            width=800,
            height=800,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.warning("Instale plotly para visualização interativa.")
