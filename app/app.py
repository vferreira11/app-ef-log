import streamlit as st
import sys
import os
from itertools import permutations

# adiciona pasta scripts (um nível acima de app) ao path
dir_app = os.path.dirname(__file__)
scripts_path = os.path.abspath(os.path.join(dir_app, '..', 'scripts'))
sys.path.append(scripts_path)

from distribuir_milp import solve_packing, Cuboid
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

st.set_page_config(page_title="Empacotamento MILP", layout="wide")
st.title("Empacotamento de Blocos Variáveis em Volume 3D")

# Controls para o contêiner
st.sidebar.header("Parâmetros do Contêiner")
dx = st.sidebar.number_input("Aresta X do contêiner (dx)", min_value=1, value=3, step=1)
dy = st.sidebar.number_input("Aresta Y do contêiner (dy)", min_value=1, value=4, step=1)
dz = st.sidebar.number_input("Aresta Z do contêiner (dz)", min_value=1, value=5, step=1)

# Inicializa estado de blocos
if 'num_blocks' not in st.session_state:
    st.session_state.num_blocks = 2

# Botão para adicionar bloco
if st.sidebar.button("+ Adicionar bloco"):
    st.session_state.num_blocks += 1

# Parâmetros dinâmicos para N blocos
block_dims = []
for i in range(1, st.session_state.num_blocks + 1):
    st.sidebar.header(f"Parâmetros do Bloco {i}")
    sdx = st.sidebar.number_input(f"Aresta X do bloco {i} (sdx{i})", min_value=1, value=1, step=1, key=f"sdx_{i}")
    sdy = st.sidebar.number_input(f"Aresta Y do bloco {i} (sdy{i})", min_value=1, value=1, step=1, key=f"sdy_{i}")
    sdz = st.sidebar.number_input(f"Aresta Z do bloco {i} (sdz{i})", min_value=1, value=1, step=1, key=f"sdz_{i}")
    block_dims.append((sdx, sdy, sdz))

# Cores predefinidas para até 6 blocos
face_colors = ['cyan', 'magenta', 'yellow', 'green', 'orange', 'purple']
edge_colors = ['blue', 'red', 'black', 'darkgreen', 'darkorange', 'indigo']

if st.sidebar.button("Calcular e Visualizar"):
    with st.spinner("Resolvendo MILP e gerando visualização..."):
        # gera orientações e índices para cada bloco
        orientations = []
        block_ranges = []  # indica range de índices de orientações por bloco
        idx = 0
        for dims in block_dims:
            ori = list({o for o in permutations(dims)})
            orientations.extend(ori)
            block_ranges.append((idx, idx + len(ori)))
            idx += len(ori)

        # resolve a alocação ótima
        placements = solve_packing(dx, dy, dz, orientations)

        # contabiliza resultados por tipo
        totals = []
        for start, end in block_ranges:
            count = sum(1 for (_, _, _, o) in placements if start <= o < end)
            totals.append(count)

        # exibe resultados
        totals_str = ", ".join([f"bloco{i+1}={totals[i]}" for i in range(len(totals))])
        st.success(f"Total: {totals_str} (em {dx}×{dy}×{dz})")

        # plot 3D
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=20, azim=30)
        ax.grid(False)
        ax.set_axis_off()

        # contêiner wireframe
        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        verts_main = Cuboid(dx, dy, dz)._get_vertices((0,0,0), dx, dy, dz)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)

        # blocos aplicados
        for (i, j, k, o) in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(dx, dy, dz)._get_vertices((i, j, k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            # identifica tipo pelo bloco_ranges
            for bi, (start, end) in enumerate(block_ranges):
                if start <= o < end:
                    color_face = face_colors[bi % len(face_colors)]
                    color_edge = edge_colors[bi % len(edge_colors)]
                    break
            ax.add_collection3d(Poly3DCollection(faces, facecolor=color_face, edgecolor=color_edge, alpha=0.6))

        # anotação total
        label = "; ".join([f"Bloco{i+1}: {totals[i]}" for i in range(len(totals))])
        ax.text2D(0.05, 0.95, label, transform=ax.transAxes,
                  fontsize=12, verticalalignment='top')

        # limites -> contêiner
        xs_main, ys_main, zs_main = zip(*verts_main)
        ax.set_xlim(min(xs_main), max(xs_main))
        ax.set_ylim(min(ys_main), max(ys_main))
        ax.set_zlim(min(zs_main), max(zs_main))
        ax.set_box_aspect([1,1,1])

        # exibe
        st.pyplot(fig)
        plt.close(fig)
