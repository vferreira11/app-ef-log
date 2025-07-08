
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Simulador de Empacotamento 3D")

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
    n_largura = largura_estoque // largura_produto
    n_altura = altura_estoque // altura_produto
    n_profundidade = profundidade_estoque // profundidade_produto

    total_caixas = n_largura * n_altura * n_profundidade

    st.markdown(f"✅ <b>Máximo de produtos que cabem:</b> <span style='color:limegreen;font-size:24px'><b>{total_caixas}</b></span>", unsafe_allow_html=True)

    fig = go.Figure()

    # Caixa do estoque
    fig.add_trace(go.Mesh3d(
        x=[0, largura_estoque, largura_estoque, 0, 0, largura_estoque, largura_estoque, 0],
        y=[0, 0, profundidade_estoque, profundidade_estoque, 0, 0, profundidade_estoque, profundidade_estoque],
        z=[0, 0, 0, 0, altura_estoque, altura_estoque, altura_estoque, altura_estoque],
        color='green',
        opacity=0.1,
        alphahull=0,
        showscale=False
    ))

    # Produtos com borda
    for i in range(n_largura):
        for j in range(n_altura):
            for k in range(n_profundidade):
                x0 = i * largura_produto
                y0 = k * profundidade_produto
                z0 = j * altura_produto

                # Desenha cubo sólido
                fig.add_trace(go.Mesh3d(
                    x=[x0, x0+largura_produto, x0+largura_produto, x0, x0, x0+largura_produto, x0+largura_produto, x0],
                    y=[y0, y0, y0+profundidade_produto, y0+profundidade_produto, y0, y0, y0+profundidade_produto, y0+profundidade_produto],
                    z=[z0, z0, z0, z0, z0+altura_produto, z0+altura_produto, z0+altura_produto, z0+altura_produto],
                    color='blue',
                    opacity=0.7,
                    showscale=False
                ))

                # Desenha bordas do cubo
                arestas = [
                    [0,1],[1,2],[2,3],[3,0],  # base
                    [4,5],[5,6],[6,7],[7,4],  # topo
                    [0,4],[1,5],[2,6],[3,7]   # colunas
                ]
                pontos = [
                    [x0, y0, z0],
                    [x0+largura_produto, y0, z0],
                    [x0+largura_produto, y0+profundidade_produto, z0],
                    [x0, y0+profundidade_produto, z0],
                    [x0, y0, z0+altura_produto],
                    [x0+largura_produto, y0, z0+altura_produto],
                    [x0+largura_produto, y0+profundidade_produto, z0+altura_produto],
                    [x0, y0+profundidade_produto, z0+altura_produto]
                ]
                for a, b in arestas:
                    fig.add_trace(go.Scatter3d(
                        x=[pontos[a][0], pontos[b][0]],
                        y=[pontos[a][1], pontos[b][1]],
                        z=[pontos[a][2], pontos[b][2]],
                        mode='lines',
                        line=dict(color='black', width=1),
                        showlegend=False
                    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_estoque]),
            yaxis=dict(title='Profundidade (mm)', range=[0, profundidade_estoque]),
            zaxis=dict(title='Altura (mm)', range=[0, altura_estoque]),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    st.plotly_chart(fig, use_container_width=True)
