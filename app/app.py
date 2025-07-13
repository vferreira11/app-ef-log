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
st.title("EF Tetris")

# inicializa estado
if 'num_blocks' not in st.session_state:
    st.session_state.num_blocks = 2

with st.expander("Célula de Estoque", expanded=True):
    dx = st.number_input("X | Largura", min_value=1, value=3, step=1)
    dy = st.number_input("Y | Altura", min_value=1, value=4, step=1)
    dz = st.number_input("Z | Profundidade", min_value=1, value=5, step=1)

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
        sdx = st.number_input(f"X | Largura", min_value=1, value=1, step=1, key=f"sdx_{i}")
    with c2:
        sdy = st.number_input(f"Y | Altura", min_value=1, value=1, step=1, key=f"sdy_{i}")
    with c3:
        sdz = st.number_input(f"Z | Profundidade", min_value=1, value=1, step=1, key=f"sdz_{i}")
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
        # exibe
        st.success("  ".join([f"Bloco{i+1}: {totals[i]}" for i in range(len(totals))]))
        # plot
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=20, azim=30)
        ax.grid(False)
        ax.set_axis_off()
        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        verts_main = Cuboid(dx, dy, dz)._get_vertices((0,0,0), dx, dy, dz)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)
        face_colors = ['cyan', 'magenta', 'yellow', 'green', 'orange', 'purple']
        edge_colors = ['blue', 'red', 'black', 'darkgreen', 'darkorange', 'indigo']
        for (i, j, k, o) in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(dx, dy, dz)._get_vertices((i, j, k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            for bi, (start, end) in enumerate(block_ranges):
                if start <= o < end:
                    face_color = face_colors[bi % len(face_colors)]
                    edge_color = edge_colors[bi % len(edge_colors)]
                    break
            ax.add_collection3d(Poly3DCollection(faces, facecolor=face_color, edgecolor=edge_color, alpha=0.6))
        xsm, ysm, zsm = zip(*verts_main)
        ax.set_xlim(min(xsm), max(xsm))
        ax.set_ylim(min(ysm), max(ysm))
        ax.set_zlim(min(zsm), max(zsm))
        ax.set_box_aspect([1,1,1])
        st.pyplot(fig)
        plt.close(fig)
