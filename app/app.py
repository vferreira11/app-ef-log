
import streamlit as st
import plotly.graph_objects as go
from math import floor

st.set_page_config(page_title="Simulador de Empacotamento 3D", layout="wide")

st.title("📦 Simulador de Empacotamento 3D")

st.subheader("🔻 Dimensões do Estoque (em mm)")
largura_estoque = st.number_input("Largura do estoque", min_value=1, value=1760)
altura_estoque = st.number_input("Altura do estoque", min_value=1, value=850)
profundidade_estoque = st.number_input("Profundidade do estoque", min_value=1, value=400)

st.subheader("📦 Dimensões de 1 produto (em mm)")
largura_produto = st.number_input("Largura do produto", min_value=1, value=200)
altura_produto = st.number_input("Altura do produto", min_value=1, value=200)
profundidade_produto = st.number_input("Profundidade do produto", min_value=1, value=200)

if st.button("Gerar visualização"):
    cols = floor(largura_estoque / largura_produto)
    rows = floor(profundidade_estoque / profundidade_produto)
    layers = floor(altura_estoque / altura_produto)
    total_caixas = cols * rows * layers

    st.markdown(f"### 🟩 Máximo de produtos que cabem: :green[{total_caixas}]")

    fig = go.Figure()

    # Adiciona cubo do estoque (transparente)
    fig.add_trace(go.Mesh3d(
        x=[0, largura_estoque, largura_estoque, 0, 0, largura_estoque, largura_estoque, 0],
        y=[0, 0, profundidade_estoque, profundidade_estoque, 0, 0, profundidade_estoque, profundidade_estoque],
        z=[0, 0, 0, 0, altura_estoque, altura_estoque, altura_estoque, altura_estoque],
        color='lightgreen',
        opacity=0.1,
        alphahull=0
    ))

    # Adiciona caixas empacotadas
    count = 0
    for k in range(layers):
        for j in range(rows):
            for i in range(cols):
                x0 = i * largura_produto
                y0 = j * profundidade_produto
                z0 = k * altura_produto
                count += 1
                fig.add_trace(go.Mesh3d(
                    x=[x0, x0+largura_produto, x0+largura_produto, x0, x0, x0+largura_produto, x0+largura_produto, x0],
                    y=[y0, y0, y0+profundidade_produto, y0+profundidade_produto, y0, y0, y0+profundidade_produto, y0+profundidade_produto],
                    z=[z0, z0, z0, z0, z0+altura_produto, z0+altura_produto, z0+altura_produto, z0+altura_produto],
                    color='royalblue',
                    opacity=0.6,
                    flatshading=True,
                    name=f'Caixa {count}',
                    hovertext=f"Caixa {count}",
                    hoverinfo="text"
                ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_estoque]),
            yaxis=dict(title='Profundidade (mm)', range=[0, profundidade_estoque]),
            zaxis=dict(title='Altura (mm)', range=[0, altura_estoque]),
            aspectmode='data',
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=700,
    )

    st.plotly_chart(fig, use_container_width=True)
