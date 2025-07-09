import streamlit as st
import plotly.graph_objects as go
import random
import math

st.set_page_config(layout="wide")
st.title("📦 Simulador de Armazenamento 3D")

# --- Função de detecção de sobreposição ---
def overlap(b1, b2):
    x0, y0, z0, dx1, dy1, dz1 = b1
    x1, y1, z1, dx2, dy2, dz2 = b2
    return not (
        x0 + dx1 <= x1 or x1 + dx2 <= x0 or
        y0 + dy1 <= y1 or y1 + dy2 <= y0 or
        z0 + dz1 <= z1 or z1 + dz2 <= z0
    )

# --- Entradas ---
col1, col2 = st.columns(2)
with col1:
    largura_cel = st.number_input("Largura célula (mm)", min_value=1, value=1760)
    profundidade_cel = st.number_input("Profundidade célula (mm)", min_value=1, value=400)
    altura_cel = st.number_input("Altura célula (mm)", min_value=1, value=850)
    num_cel = st.number_input("Número de células", min_value=1, value=4)
    layout = st.selectbox("Layout", ["Lado a lado", "Vertical", "Manual"])
    if layout == "Lado a lado":
        cols = num_cel
        rows = 1
    elif layout == "Vertical":
        cols = 1
        rows = num_cel
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
    # --- Distribuição baseada em área de base (x + (1-x) = 1) ---
    base_area = largura_cel * profundidade_cel
    aA = largura_A * profundidade_A
    aB = largura_B * profundidade_B

    x = random.uniform(0.1, 0.9)  # % de área para A
    shareA_area = base_area * x
    shareB_area = base_area * (1 - x)

    colsA = int(shareA_area // aA)
    colsB = int(shareB_area // aB)
    layersA = altura_cel // altura_A
    layersB = altura_cel // altura_B

    nA = colsA * layersA
    nB = colsB * layersB

    st.markdown(f"**Distribuição:** {int(x*100)}% A • {100-int(x*100)}% B")

    # --- Posicionamento de A em grid ---
    nxA = largura_cel // largura_A
    nyA = profundidade_cel // profundidade_A
    nzA = altura_cel // altura_A
    placed_A = []
    cnt = 0
    for z in range(nzA):
        for y in range(nyA):
            for x in range(nxA):
                if cnt >= nA:
                    break
                placed_A.append((x * largura_A,
                                 y * profundidade_A,
                                 z * altura_A,
                                 largura_A,
                                 profundidade_A,
                                 altura_A))
                cnt += 1
            if cnt >= nA:
                break
        if cnt >= nA:
            break

    # --- Posicionamento de B sem lacunas ---
    x_end_A = max(box[0] + box[3] for box in placed_A) if placed_A else 0
    largura_rest = largura_cel - x_end_A
    nxB_reg = largura_rest // largura_B
    nyB = profundidade_cel // profundidade_B
    nzB = altura_cel // altura_B
    placed_B = []
    cnt = 0
    for z in range(nzB):
        for y in range(nyB):
            for i in range(nxB_reg):
                if cnt >= nB:
                    break
                x0 = x_end_A + i * largura_B
                placed_B.append((x0,
                                 y * profundidade_B,
                                 z * altura_B,
                                 largura_B,
                                 profundidade_B,
                                 altura_B))
                cnt += 1
            if cnt >= nB:
                break
        if cnt >= nB:
            break

    # --- Atualiza contagem real ---
    nA = len(placed_A)
    nB = len(placed_B)
    st.markdown(f"**A:** {nA} un. • **B:** {nB} un. • **Total:** {nA + nB}")

    # --- Função para desenhar cubos ---
    def draw_mesh(fig, box, color, opacity, legend, name):
        x0, y0, z0, dx, dy, dz = box
        verts = [
            (x0, y0, z0), (x0 + dx, y0, z0),
            (x0 + dx, y0 + dy, z0), (x0, y0 + dy, z0),
            (x0, y0, z0 + dz), (x0 + dx, y0, z0 + dz),
            (x0 + dx, y0 + dy, z0 + dz), (x0, y0 + dy, z0 + dz)
        ]
        x_vert, y_vert, z_vert = zip(*verts)
        faces = [
            (0,1,2),(0,2,3),(4,5,6),(4,6,7),
            (0,1,5),(0,5,4),(1,2,6),(1,6,5),
            (2,3,7),(2,7,6),(3,0,4),(3,4,7)
        ]
        i, j, k = zip(*faces)
        fig.add_trace(go.Mesh3d(
            x=x_vert, y=y_vert, z=z_vert,
            i=i, j=j, k=k,
            color=color, opacity=opacity,
            showlegend=legend, name=name
        ))
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
    cell = (0, 0, 0, largura_cel, profundidade_cel, altura_cel)
    for a, b in [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]:
        x0, y0, z0, dx, dy, dz = cell
        verts = [
            (x0, y0, z0), (x0 + dx, y0, z0),
            (x0 + dx, y0 + dy, z0), (x0, y0 + dy, z0),
            (x0, y0, z0 + dz), (x0 + dx, y0, z0 + dz),
            (x0 + dx, y0 + dy, z0 + dz), (x0, y0 + dy, z0 + dz)
        ]
        fig3.add_trace(go.Scatter3d(
            x=[verts[a][0], verts[b][0]],
            y=[verts[a][1], verts[b][1]],
            z=[verts[a][2], verts[b][2]],
            mode='lines',
            line=dict(color='white', width=4),
            showlegend=False
        ))

    diag = math.sqrt(largura_cel**2 + profundidade_cel**2 + altura_cel**2)

    fig3.update_layout(
    scene=dict(
        aspectmode='manual',
        aspectratio=dict(x=largura_cel, y=profundidade_cel, z=altura_cel),
        camera=dict(
            projection=dict(type='orthographic'),
            # posiciona a câmera automaticamente baseado na diagonal
            eye=dict(x=diag*1.2, y=diag*1.2, z=diag*1.2)
        ),
        xaxis=dict(title='Largura (mm)'),
        yaxis=dict(title='Profundidade (mm)'),
        zaxis=dict(title='Altura (mm)')
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

    st.plotly_chart(fig3, use_container_width=True)

    # --- Plot 2D ---
    fig2 = go.Figure()
    pad = 40
    for cx in range(cols):
        for cy in range(rows):
            ox = cx * (largura_cel + pad)
            oy = cy * (altura_cel + pad)
            for x0, y0, z0, dx, dy, dz in placed_A:
                fig2.add_shape(
                    type='rect',
                    x0=ox + x0,
                    y0=oy + z0,
                    x1=ox + x0 + dx,
                    y1=oy + z0 + dz,
                    line=dict(color='black', width=1),
                    fillcolor=cor_A
                )
            for x0, y0, z0, dx, dy, dz in placed_B:
                fig2.add_shape(
                    type='rect',
                    x0=ox + x0,
                    y0=oy + z0,
                    x1=ox + x0 + dx,
                    y1=oy + z0 + dz,
                    line=dict(color='black', width=1),
                    fillcolor=cor_B
                )
    fig2.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(color=cor_A), name='A'
    ))
    fig2.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(color=cor_B), name='B'
    ))
    total_w = cols * largura_cel + (cols - 1) * pad
    total_h = rows * altura_cel + (rows - 1) * pad
    fig2.update_layout(
        title='Visão Frontal',
        xaxis=dict(range=[0, total_w]),
        yaxis=dict(range=[0, total_h], scaleanchor='x'),
        height=500,
        margin=dict(l=0, r=0, b=0, t=30)
    )
    st.plotly_chart(fig2, use_container_width=True)
