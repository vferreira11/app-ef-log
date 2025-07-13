import streamlit as st
import sys
import os
# adiciona pasta scripts (um nível acima de app) ao path
dir_app = os.path.dirname(__file__)
scripts_path = os.path.abspath(os.path.join(dir_app, '..', 'scripts'))
sys.path.append(scripts_path)

from distribuir_milp import solve_packing, Cuboid
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

st.set_page_config(page_title="Empacotamento MILP", layout="wide")
st.title("Empacotamento de Blocos 1×1×2 em Volume 3D")

st.sidebar.header("Parâmetros do Contêiner")
dx = st.sidebar.number_input("Aresta X (dx)", min_value=1, value=3, step=1)
dy = st.sidebar.number_input("Aresta Y (dy)", min_value=1, value=4, step=1)
dz = st.sidebar.number_input("Aresta Z (dz)", min_value=1, value=5, step=1)

if st.sidebar.button("Calcular e Visualizar"):
    with st.spinner("Resolvendo MILP e gerando visualização..."):
        # resolve a alocação ótima
        orientations = [(1,1,2), (2,1,1), (1,2,1)]
        placements = solve_packing(dx, dy, dz, orientations)

        # mostra resultado
        st.success(f"Máximo de blocos 1×1×2 em {dx}×{dy}×{dz}: {len(placements)}")

        # plota estático
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=20, azim=30)
        ax.grid(False)
        ax.set_axis_off()
        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]

        # contêiner wireframe
        verts_main = Cuboid(dx, dy, dz)._get_vertices((0,0,0), dx, dy, dz)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)

        # blocos
        for (i,j,k,o) in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(dx, dy, dz)._get_vertices((i,j,k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            ax.add_collection3d(Poly3DCollection(faces, facecolor='cyan', edgecolor='blue', alpha=0.6))

        # anotação total
        ax.text2D(0.05, 0.95, f"Total blocks: {len(placements)}", transform=ax.transAxes,
                  fontsize=12, verticalalignment='top')

        # limites
        xs = [v[0] for v in verts_main]
        ys = [v[1] for v in verts_main]
        zs = [v[2] for v in verts_main]
        ax.set_xlim(min(xs), max(xs))
        ax.set_ylim(min(ys), max(ys))
        ax.set_zlim(min(zs), max(zs))
        ax.set_box_aspect([1,1,1])

        # exibe
        st.pyplot(fig)
        plt.close(fig)
