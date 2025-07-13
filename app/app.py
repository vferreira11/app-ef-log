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

# Controls para blocos
st.sidebar.header("Parâmetros do Bloco 1")
sdx1 = st.sidebar.number_input("Aresta X do bloco 1 (sdx1)", min_value=1, value=1, step=1)
sdy1 = st.sidebar.number_input("Aresta Y do bloco 1 (sdy1)", min_value=1, value=1, step=1)
sdz1 = st.sidebar.number_input("Aresta Z do bloco 1 (sdz1)", min_value=1, value=2, step=1)

st.sidebar.header("Parâmetros do Bloco 2")
sdx2 = st.sidebar.number_input("Aresta X do bloco 2 (sdx2)", min_value=1, value=1, step=1)
sdy2 = st.sidebar.number_input("Aresta Y do bloco 2 (sdy2)", min_value=1, value=2, step=1)
sdz2 = st.sidebar.number_input("Aresta Z do bloco 2 (sdz2)", min_value=1, value=1, step=1)

if st.sidebar.button("Calcular e Visualizar"):
    with st.spinner("Resolvendo MILP e gerando visualização..."):
        # gera todas as orientações únicas para cada bloco
        ori1 = list({o for o in permutations((sdx1, sdy1, sdz1))})
        ori2 = list({o for o in permutations((sdx2, sdy2, sdz2))})
        orientations = ori1 + ori2

        # resolve a alocação ótima para ambos blocos
        placements = solve_packing(dx, dy, dz, orientations)

        # contabiliza resultados
        total1 = sum(1 for (_, _, _, o) in placements if o < len(ori1))
        total2 = len(placements) - total1
        st.success(f"Total: bloco1={total1}, bloco2={total2} (em {dx}×{dy}×{dz})")

        # plota estático 3D
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

        # blocos aplicados com cores distintas
        for (i, j, k, o) in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(dx, dy, dz)._get_vertices((i, j, k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            # define cor por bloco
            if o < len(ori1):
                face_color, edge_color = 'cyan', 'blue'
            else:
                face_color, edge_color = 'magenta', 'red'
            ax.add_collection3d(Poly3DCollection(faces, facecolor=face_color, edgecolor=edge_color, alpha=0.6))

        # anotação total
        ax.text2D(0.05, 0.95, f"Bloco1: {total1} | Bloco2: {total2}", transform=ax.transAxes,
                  fontsize=12, verticalalignment='top')

        # limites do eixo conforme contêiner
        xs_main, ys_main, zs_main = zip(*verts_main)
        ax.set_xlim(min(xs_main), max(xs_main))
        ax.set_ylim(min(ys_main), max(ys_main))
        ax.set_zlim(min(zs_main), max(zs_main))
        ax.set_box_aspect([1,1,1])

        # exibe o plot
        st.pyplot(fig)
        plt.close(fig)
