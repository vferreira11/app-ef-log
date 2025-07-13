import streamlit as st
import os
from distribute_milp import solve_packing, Cuboid  # assume distribuir_milp.py defines these
import matplotlib.pyplot as plt
from io import BytesIO

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

        # mensagem de resumo
        st.success(f"Máximo de blocos 1×1×2 em {dx}×{dy}×{dz}: {len(placements)}")

        # gera plot em memória
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=20, azim=30)
        ax.grid(False)
        ax.set_axis_off()
        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        # desenha contêiner
        verts_main = Cuboid(dx, dy, dz)._get_vertices((0,0,0), dx, dy, dz)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)
        # desenha blocos
        for (i,j,k,o) in placements:
            lx, ly, lz = orientations[o]
            verts = Cuboid(dx, dy, dz)._get_vertices((i,j,k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            ax.add_collection3d(plt.Poly3DCollection(faces, facecolor='cyan', edgecolor='blue', alpha=0.6))
        # anotação
        ax.text2D(0.05, 0.95, f"Total blocks: {len(placements)}", transform=ax.transAxes,
                  fontsize=12, verticalalignment='top')
        # limites
        all_x = [v[0] for v in verts_main]
        all_y = [v[1] for v in verts_main]
        all_z = [v[2] for v in verts_main]
        ax.set_xlim(min(all_x), max(all_x))
        ax.set_ylim(min(all_y), max(all_y))
        ax.set_zlim(min(all_z), max(all_z))
        ax.set_box_aspect([1,1,1])

        # exibe no Streamlit
        st.pyplot(fig)
