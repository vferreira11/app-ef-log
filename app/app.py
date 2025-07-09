# app.py

import streamlit as st
import plotly.graph_objects as go
import random
import math

st.set_page_config(layout="wide")
st.title("📦 Simulador de Armazenamento 3D")

# --- Função de score ergonômico embutida ---
def score_ergonomico_altura(altura_mm, ideal_mm=1200.0, min_score_baixo=0.1):
    # calcula sigma para que em altura=0 o score seja ~= min_score_baixo
    sigma = ideal_mm / math.sqrt(-2 * math.log(min_score_baixo))
    score = math.exp(-((altura_mm - ideal_mm) ** 2) / (2 * sigma**2))
    return round(score, 4)

# --- Função de detecção de sobreposição (não usada) ---
def overlap(b1, b2):
    x0, y0, z0, dx1, dy1, dz1 = b1
    x1, y1, z1, dx2, dy2, dz2 = b2
    return not (
        x0 + dx1 <= x1 or x1 + dx2 <= x0 or
        y0 + dy1 <= y1 or y1 + dy2 <= y0 or
        z0 + dz1 <= z1 or z1 + dz2 <= z0
    )

# --- Entradas do usuário ---
col1, col2 = st.columns(2)
with col1:
    largura_cel = st.number_input("Largura célula (mm)", min_value=1, value=1760)
    profundidade_cel = st.number_input("Profundidade célula (mm)", min_value=1, value=400)
    altura_cel = st.number_input("Altura célula (mm)", min_value=1, value=850)
    num_cel = st.number_input("Número de células", min_value=1, value=4)
    layout = st.selectbox("Layout", ["Lado a lado", "Vertical", "Manual"])
    if layout == "Lado a lado":
        cols = num_cel; rows = 1
    elif layout == "Vertical":
        cols = 1; rows = num_cel
    else:
        cols = st.number_input("Cols", min_value=1, value=2)
        rows = st.number_input("Rows", min_value=1, value=2)

with col2:
    largura_A = st.number_input("Largura A (mm)", min_value=1, value=200)
    profundidade_A = st.number_input("Profundidade A (mm)", min_value=1, value=200)
    altura_A = st.number_input("Altura A (mm)", min_value=1, value=200)
    cor_A = st.color_picker("Cor A", "#636EFA")
    largura_B = st.number_input("Largura B (mm)", min_value=1, value=150)
    profundidade_B = st.number_input("Profundidade B (mm)", min_value=1, value=150)
    altura_B = st.number_input("Altura B (mm)", min_value=1, value=150)
    cor_B = st.color_picker("Cor B", "#EF553B")

if st.button("GERAR SIMULAÇÃO"):
    # --- Cálculo de quantidades ---
    base_area = largura_cel * profundidade_cel
    aA = largura_A * profundidade_A
    aB = largura_B * profundidade_B
    x = random.uniform(0.1, 0.9)
    shareA = base_area * x
    shareB = base_area * (1 - x)
    colsA = int(shareA // aA)
    colsB = int(shareB // aB)
    layersA = altura_cel // altura_A
    layersB = altura_cel // altura_B
    nA = colsA * layersA
    nB = colsB * layersB

    st.markdown(f"**Distribuição:** {int(x*100)}% A • {100-int(x*100)}% B")

    # --- Posicionamento de A ---
    nxA = largura_cel // largura_A
    nyA = profundidade_cel // profundidade_A
    nzA = altura_cel // altura_A
    placed_A = []
    cnt = 0
    for z in range(nzA):
        for y in range(nyA):
            for xi in range(nxA):
                if cnt >= nA:
                    break
                placed_A.append((
                    xi * largura_A,
                    y * profundidade_A,
                    z * altura_A,
                    largura_A,
                    profundidade_A,
                    altura_A
                ))
                cnt += 1
            if cnt >= nA:
                break
        if cnt >= nA:
            break

    # --- Posicionamento de B ---
    x_end_A = max((b[0] + b[3] for b in placed_A), default=0)
    largura_rest = largura_cel - x_end_A
    nxB = largura_rest // largura_B
    nyB = profundidade_cel // profundidade_B
    nzB = altura_cel // altura_B
    placed_B = []
    cnt = 0
    for z in range(nzB):
        for y in range(nyB):
            for i in range(nxB):
                if cnt >= nB:
                    break
                placed_B.append((
                    x_end_A + i * largura_B,
                    y * profundidade_B,
                    z * altura_B,
                    largura_B,
                    profundidade_B,
                    altura_B
                ))
                cnt += 1
            if cnt >= nB:
                break
        if cnt >= nB:
            break

    # --- Ajuste final de contagem ---
    nA = len(placed_A)
    nB = len(placed_B)
    st.markdown(f"**A:** {nA} un. • **B:** {nB} un. • **Total:** {nA + nB}")

    # --- Função para desenhar cubos ---
    def draw_mesh(fig, box, color, opacity, legend, name):
        x0, y0, z0, dx, dy, dz = box
        verts = [
            (x0, y0, z0), (x0+dx, y0, z0),
            (x0+dx, y0+dy, z0), (x0, y0+dy, z0),
            (x0, y0, z0+dz), (x0+dx, y0, z0+dz),
            (x0+dx, y0+dy, z0+dz), (x0, y0+dy, z0+dz)
        ]
        i, j, k = zip(*[
            (0,1,2),(0,2,3),(4,5,6),(4,6,7),
            (0,1,5),(0,5,4),(1,2,6),(1,6,5),
            (2,3,7),(2,7,6),(3,0,4),(3,4,7)
        ])
        x_vert, y_vert, z_vert = zip(*verts)
        fig.add_trace(go.Mesh3d(
            x=x_vert, y=y_vert, z=z_vert,
            i=i, j=j, k=k,
            color=color, opacity=opacity,
            showlegend=legend, name=name
        ))
        # arestas em preto
        for a, b in [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]:
            fig.add_trace(go.Scatter3d(
                x=[verts[a][0], verts[b][0]],
                y=[verts[a][1], verts[b][1]],
                z=[verts[a][2], verts[b][2]],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False
            ))

    # --- Plot 3D ---
    fig3 = go.Figure()
    for i, box in enumerate(placed_A):
        draw_mesh(fig3, box, cor_A, 0.8, i == 0, 'A')
    for i, box in enumerate(placed_B):
        draw_mesh(fig3, box, cor_B, 0.8, i == 0, 'B')
    # contorno da célula principal em branco
    cell = (0, 0, 0, largura_cel, profundidade_cel, altura_cel)
    for a, b in [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]:
        verts = [
            (cell[0], cell[1], cell[2]),
            (cell[0]+cell[3], cell[1], cell[2]),
            (cell[0]+cell[3], cell[1]+cell[4], cell[2]),
            (cell[0], cell[1]+cell[4], cell[2]),
            (cell[0], cell[1], cell[2]+cell[5]),
            (cell[0]+cell[3], cell[1], cell[2]+cell[5]),
            (cell[0]+cell[3], cell[1]+cell[4], cell[2]+cell[5]),
            (cell[0], cell[1]+cell[4], cell[2]+cell[5])
        ]
        fig3.add_trace(go.Scatter3d(
            x=[verts[a][0], verts[b][0]],
            y=[verts[a][1], verts[b][1]],
            z=[verts[a][2], verts[b][2]],
            mode='lines',
            line=dict(color='white', width=4),
            showlegend=False
        ))

    fig3.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_cel]),
            yaxis=dict(title='Profundidade (mm)', range=[0, profundidade_cel]),
            zaxis=dict(title='Altura (mm)', range=[0, altura_cel]),
            aspectmode='data',
            camera=dict(eye=dict(x=-1.5, y=-1.8, z=0.2))
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )

    # --- Inserir título com Score ---
    score = score_ergonomico_altura(altura_cel / 2)
    fig3.update_layout(
        title_text=f"Score Ergonômico: {score:.2f}",
        title_x=0.5,
        title_y=0.95,
        title_font_size=16
    )

    st.plotly_chart(fig3, use_container_width=True)

    # --- Plot 2D Frontal ---
    fig2 = go.Figure()
    pad = 40
    for cx in range(cols):
        for cy in range(rows):
            ox = cx * (largura_cel + pad)
            oy = cy * (altura_cel + pad)
            for x0, y0, z0, dx, dy, dz in placed_A:
                fig2.add_shape(
                    type="rect",
                    x0=ox + x0,
                    y0=oy + z0,
                    x1=ox + x0 + dx,
                    y1=oy + z0 + dz,
                    line=dict(color=cor_A),
                    fillcolor=cor_A
                )
            for x0, y0, z0, dx, dy, dz in placed_B:
                fig2.add_shape(
                    type="rect",
                    x0=ox + x0,
                    y0=oy + z0,
                    x1=ox + x0 + dx,
                    y1=oy + z0 + dz,
                    line=dict(color=cor_B),
                    fillcolor=cor_B
                )

    fig2.update_layout(
        xaxis=dict(
            title="Largura (mm)",
            range=[0, cols * largura_cel + (cols - 1) * pad]
        ),
        yaxis=dict(
            title="Altura (mm)",
            range=[0, rows * altura_cel + (rows - 1) * pad]
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)
