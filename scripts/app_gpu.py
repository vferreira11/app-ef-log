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
num_blocks = st.sidebar.slider("Blocos por indivíduo (N)", min_value=10, max_value=1000, value=300, step=10)

if st.button("Executar GPU Heurística"):
    # Prepara dimenões de blocos (ignora quantidades)
    block_dims = [(int(row.dx), int(row.dy), int(row.dz)) for _, row in types_df.iterrows()]
    # Executa heurística GPU
    placements = gpu_heuristic_pack(dx, dy, dz, block_dims, pop_size=pop_size, N=num_blocks)
    count = len(placements)
    st.success(f"Solução encontrou {count} blocos!")

    # Monta resultado JSON
    result = {
        'method': 'gpu_numba',
        'container': {'dx': dx, 'dy': dy, 'dz': dz, 'block_orientations': block_dims},
        'count': count,
        'placements': [{'x': x, 'y': y, 'z': z, 'orientation': o} for x, y, z, o in placements]
    }
    st.json(result)

    # Plot 3D interativo com Plotly
    try:
        import plotly.graph_objects as go
        cd = Cuboid(dx, dy, dz)
        fig = go.Figure()
        # Container
        verts = cd._get_vertices((0,0,0), dx, dy, dz)
        x, y, z = zip(*verts)
        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, opacity=0.1, color='lightgrey', name='Container'))
        # Blocos
        for x0, y0, z0, o in placements:
            lx, ly, lz = block_dims[o]
            bverts = cd._get_vertices((x0, y0, z0), lx, ly, lz)
            bx, by, bz = zip(*bverts)
            fig.add_trace(go.Mesh3d(x=bx, y=by, z=bz, opacity=0.8, color='blue', showscale=False))
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[0,dx]),
                yaxis=dict(range=[0,dy]),
                zaxis=dict(range=[0,dz]),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.warning("Instale plotly para visualização interativa.")
