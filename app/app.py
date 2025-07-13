import streamlit as st
import sys
import os
from itertools import permutations
import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

dir_app = os.path.dirname(__file__)
scripts_path = os.path.abspath(os.path.join(dir_app, '..', 'scripts'))
sys.path.append(scripts_path)
from distribuir_milp import solve_packing, Cuboid

st.set_page_config(page_title="Empacotamento MILP", layout="wide")
st.title("EF Tetris")

if 'num_blocks' not in st.session_state:
    st.session_state.num_blocks = 2

with st.expander("Célula de Estoque", expanded=True):
    dx = st.number_input("X | Largura em mm", min_value=1, value=3, step=1)
    dy = st.number_input("Y | Altura em mm", min_value=1, value=4, step=1)
    dz = st.number_input("Z | Profundidade em mm", min_value=1, value=5, step=1)

st.subheader("Parâmetros das embalagens")
cols = st.columns([1, 1, 1, 0.5])
with cols[0]:
    st.write(f"**Embalagens distintas:** {st.session_state.num_blocks}")
with cols[3]:
    if st.button("+ Adicionar +1 embalagem"):
        st.session_state.num_blocks += 1

block_dims = []
for i in range(1, st.session_state.num_blocks + 1):
    st.markdown(f"---\n**Embalagem {i}**")
    c1, c2, c3 = st.columns(3)
    with c1: sdx = st.number_input(f"X | Largura em mm", min_value=1, value=1, step=1, key=f"sdx_{i}")
    with c2: sdy = st.number_input(f"Y | Altura em mm", min_value=1, value=1, step=1, key=f"sdy_{i}")
    with c3: sdz = st.number_input(f"Z | Profundidade em mm", min_value=1, value=1, step=1, key=f"sdz_{i}")
    block_dims.append((sdx, sdy, sdz))

st.markdown("---")
if st.button("Distribuir"):
    with st.spinner("Fazendo bruxaria, aguarde..."):
        orientations, block_ranges, idx = [], [], 0
        for dims in block_dims:
            ori = list({o for o in permutations(dims)})
            orientations.extend(ori)
            block_ranges.append((idx, idx + len(ori)))
            idx += len(ori)
        placements = solve_packing(dx, dy, dz, orientations)
        totals = [sum(1 for *_, o in placements if s <= o < e) for s, e in block_ranges]
        st.success("  ".join([f"Bloco{i+1}: {totals[i]}" for i in range(len(totals))]))

        x_dim, y_dim, z_dim = dz, dx, dy
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=20, azim=30)
                ax.set_xlim(0, x_dim)
        ax.set_ylim(0, y_dim)
        ax.set_zlim(0, z_dim)
        # garante que Z vá do 0 até z_dim sem inverter
        ax.invert_zaxis()  # ajusta a orientação do eixo Z
        # ticks dinâmicos: até 10 rótulos por eixo
        step_x = max(1, int(np.ceil(x_dim / 10)))
        step_y = max(1, int(np.ceil(y_dim / 10)))
        step_z = max(1, int(np.ceil(z_dim / 10)))
        ax.set_xticks(np.arange(0, x_dim+1, step_x))
        ax.set_yticks(np.arange(0, y_dim+1, step_y))
        ax.set_zticks(np.arange(0, z_dim+1, step_z))
        ax.set_box_aspect([x_dim, y_dim, z_dim])
        ax.quiver(0, 0, 0, x_dim*1.05, 0, 0, arrow_length_ratio=0.03)
        ax.quiver(0, 0, 0, 0, y_dim*1.05, 0, arrow_length_ratio=0.03)
        ax.quiver(0, 0, 0, 0, 0, z_dim*1.05, arrow_length_ratio=0.03)
        ax.quiver(0, 0, 0, 0, y_dim*1.05, 0, arrow_length_ratio=0.03)
        ax.quiver(0, 0, 0, 0, 0, z_dim*1.05, arrow_length_ratio=0.03)
        ax.text(0, 0, 0, '0', fontsize=10, ha='right', va='bottom')

        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        cmap = cm.get_cmap('viridis', len(block_ranges))

        verts_main = Cuboid(x_dim, y_dim, z_dim)._get_vertices((0,0,0), x_dim, y_dim, z_dim)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            ax.plot(*zip(*pts), color='black', linewidth=1)

        for i, j, k, o in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(x_dim, y_dim, z_dim)._get_vertices((k, i, j), lz, lx, ly)
            faces = [[verts[idx] for idx in face] for face in faces_idx]
            bi = next(b for b,(s,e) in enumerate(block_ranges) if s<=o<e)
            ax.add_collection3d(Poly3DCollection(faces, facecolor=cmap(bi), edgecolor='black', alpha=0.8))

        ax.set_xlabel("Profundidade (Z)")
        ax.set_ylabel("Largura (X)")
        ax.set_zlabel("Altura (Y)")
        st.pyplot(fig)
        plt.close(fig)
