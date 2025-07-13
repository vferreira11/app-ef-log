import streamlit as st
import sys
import os
from itertools import permutations
import numpy as np

# adiciona pasta scripts (um nível acima de app) ao path
dir_app = os.path.dirname(__file__)
scripts_path = os.path.abspath(os.path.join(dir_app, '..', 'scripts'))
sys.path.append(scripts_path)

from distribuir_milp import solve_packing, Cuboid
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

st.set_page_config(page_title="Empacotamento MILP", layout="wide")
st.title("EF Tetris")

# inicializa estado
if 'num_blocks' not in st.session_state:
    st.session_state.num_blocks = 2

with st.expander("Célula de Estoque", expanded=True):
    dx = st.number_input("X | Largura em mm", min_value=1, value=3, step=1)
    dy = st.number_input("Y | Altura em mm", min_value=1, value=4, step=1)
    dz = st.number_input("Z | Profundidade em mm", min_value=1, value=5, step=1)

# controles de blocos sempre visíveis
st.subheader("Parâmetros das embalagens")
cols = st.columns([1,1,1,0.5])
with cols[0]:
    st.write(f"**Embalagens distintas:** {st.session_state.num_blocks}")
with cols[3]:
    if st.button("+ Adicionar +1 embalagem"):
        st.session_state.num_blocks += 1

block_dims = []
for i in range(1, st.session_state.num_blocks + 1):
    st.markdown(f"---\n**Embalagem {i}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        sdx = st.number_input(f"X | Largura em mm", min_value=1, value=1, step=1, key=f"sdx_{i}")
    with c2:
        sdy = st.number_input(f"Y | Altura em mm", min_value=1, value=1, step=1, key=f"sdy_{i}")
    with c3:
        sdz = st.number_input(f"Z | Profundidade em mm", min_value=1, value=1, step=1, key=f"sdz_{i}")
    block_dims.append((sdx, sdy, sdz))

st.markdown("---")
if st.button("Distribuir"):
    with st.spinner("Fazendo bruxaria, aguarde..."):
        # gera orientações e índices
        orientations = []
        block_ranges = []
        idx = 0
        for dims in block_dims:
            ori = list({o for o in permutations(dims)})
            orientations.extend(ori)
            block_ranges.append((idx, idx + len(ori)))
            idx += len(ori)

        placements = solve_packing(dx, dy, dz, orientations)
        # contabiliza
        totals = [sum(1 for (_, _, _, o) in placements if start <= o < end)
                  for start, end in block_ranges]
        st.success("  ".join([f"Bloco{i+1}: {totals[i]}" for i in range(len(totals))]))

        # plot
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=20, azim=30)
        ax.grid(False)

                # limites e ticks (sem o zero padrão)
        ax.set_xlim(0, dx)
        ax.set_ylim(0, dy)
        ax.set_zlim(0, dz)
        ax.set_xticks(np.arange(1, dx+1, 1))
        ax.set_yticks(np.arange(1, dy+1, 1))
        ax.set_zticks(np.arange(1, dz+1, 1))
        ax.set_box_aspect([1,1,1])

        # dimensões ajustadas para as setas (10% além)
        x_max = dx * 1.1
        y_max = dy * 1.1
        z_max = dz * 1.1

        # eixos com setas, todos a partir de origem (0,0,0)
        ax.quiver(0, 0, 0, x_max, 0, 0, arrow_length_ratio=0.02, linewidth=1)
        ax.quiver(0, 0, 0, 0, y_max, 0, arrow_length_ratio=0.02, linewidth=1)
        ax.quiver(0, 0, 0, 0, 0, z_max, arrow_length_ratio=0.02, linewidth=1)

        # anotações manuais para zero no ponto de origem
        ax.text(0, 0, 0, '0', fontsize=10, ha='right', va='bottom')

        # Desenha contêiner, todos a partir de origem (0,0,0)
        ax.quiver(0, 0, 0, x_max, 0, 0, arrow_length_ratio=0.02, linewidth=1)
        ax.quiver(0, 0, 0, 0, y_max, 0, arrow_length_ratio=0.02, linewidth=1)
        ax.quiver(0, 0, 0, 0, 0, z_max, arrow_length_ratio=0.02, linewidth=1)

        # Desenha contêiner
        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        verts_main = Cuboid(dx, dy, dz)._get_vertices((0,0,0), dx, dy, dz)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)

        # cores viridis
        cmap = cm.get_cmap('viridis', len(block_ranges))
        for (i, j, k, o) in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(dx, dy, dz)._get_vertices((i, j, k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            for bi, (start, end) in enumerate(block_ranges):
                if start <= o < end:
                    color = cmap(bi)
                    break
            ax.add_collection3d(Poly3DCollection(faces, facecolor=color, edgecolor='black', alpha=0.8))

        # rótulos
        ax.set_xlabel("Largura (X)")
        ax.set_ylabel("Altura (Y)")
        ax.set_zlabel("Profundidade (Z)")

        st.pyplot(fig)
        plt.close(fig)
