
import streamlit as st
import plotly.graph_objects as go

def criar_cubo(x, y, z, dx, dy, dz, cor="blue", opacidade=1.0):
    # Define os vértices do cubo
    vertices = [
        [x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z],
        [x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]
    ]

    # Define as 12 faces (2 triângulos por face de cubo)
    faces = [
        [0, 1, 2], [0, 2, 3],  # base
        [4, 5, 6], [4, 6, 7],  # topo
        [0, 1, 5], [0, 5, 4],  # frente
        [2, 3, 7], [2, 7, 6],  # trás
        [1, 2, 6], [1, 6, 5],  # direita
        [3, 0, 4], [3, 4, 7]   # esquerda
    ]

    x_vals, y_vals, z_vals = zip(*vertices)
    i, j, k = zip(*faces)

    return go.Mesh3d(
        x=x_vals, y=y_vals, z=z_vals,
        i=i, j=j, k=k,
        color=cor,
        opacity=opacidade,
        flatshading=True,
        showscale=False
    )

st.set_page_config(page_title="Empacotamento 3D", layout="wide")
st.title("📦 Simulador de Empacotamento 3D")

with st.expander("📉 Dimensões do Estoque (em mm)", expanded=True):
    largura_estoque = st.number_input("Largura do estoque", value=1760)
    altura_estoque = st.number_input("Altura do estoque", value=850)
    profundidade_estoque = st.number_input("Profundidade do estoque", value=400)

with st.expander("📦 Dimensões de 1 produto (em mm)", expanded=True):
    largura_produto = st.number_input("Largura do produto", value=200)
    altura_produto = st.number_input("Altura do produto", value=200)
    profundidade_produto = st.number_input("Profundidade do produto", value=200)

if st.button("Gerar visualização"):
    # Cálculo de quantos produtos cabem por eixo
    nx = largura_estoque // largura_produto
    ny = altura_estoque // altura_produto
    nz = profundidade_estoque // profundidade_produto
    total_caixas = nx * ny * nz

    st.markdown(f"✅ <b>Máximo de produtos que cabem:</b> <span style='color:limegreen; font-size:24px'><b>{total_caixas}</b></span>", unsafe_allow_html=True)

    # Plotly: cubo do estoque
    cubos = []

    # Estoque externo em verde transparente
    cubos.append(criar_cubo(
        x=0, y=0, z=0,
        dx=largura_estoque,
        dy=profundidade_estoque,
        dz=altura_estoque,
        cor='green', opacidade=0.15
    ))

    # Produtos
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                cubos.append(criar_cubo(
                    x=ix * largura_produto,
                    y=iz * profundidade_produto,
                    z=iy * altura_produto,
                    dx=largura_produto,
                    dy=profundidade_produto,
                    dz=altura_produto,
                    cor='royalblue',
                    opacidade=0.95
                ))

    fig = go.Figure(data=cubos)
    fig.update_layout(
        scene=dict(
            xaxis_title="Largura (mm)",
            yaxis_title="Profundidade (mm)",
            zaxis_title="Altura (mm)",
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    st.plotly_chart(fig, use_container_width=True)
