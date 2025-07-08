
import streamlit as st
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Simulador de Empacotamento 3D", layout="wide")

st.title("📦 Simulador de Empacotamento 3D")

with st.expander("🔻 Dimensões do Estoque (em mm)", expanded=True):
    largura_estoque = st.number_input("Largura do estoque", min_value=100, value=1760)
    altura_estoque = st.number_input("Altura do estoque", min_value=100, value=850)
    profundidade_estoque = st.number_input("Profundidade do estoque", min_value=100, value=400)

with st.expander("📦 Dimensões de 1 produto (em mm)", expanded=True):
    largura_produto = st.number_input("Largura do produto", min_value=10, value=200)
    altura_produto = st.number_input("Altura do produto", min_value=10, value=200)
    profundidade_produto = st.number_input("Profundidade do produto", min_value=10, value=200)

if st.button("Gerar visualização"):

    if (
        largura_produto > largura_estoque
        or altura_produto > altura_estoque
        or profundidade_produto > profundidade_estoque
    ):
        st.error("❌ As dimensões do produto são maiores que as do estoque.")
    else:
        # Calcular quantas caixas cabem em cada eixo
        n_x = largura_estoque // largura_produto
        n_y = altura_estoque // altura_produto
        n_z = profundidade_estoque // profundidade_produto
        total_caixas = int(n_x * n_y * n_z)

        st.markdown(f"### ✅ Máximo de produtos que cabem: **:green[{total_caixas}]**")

        fig = go.Figure()

        # Adicionar cubo do estoque (volume total)
        fig.add_trace(go.Mesh3d(
            x=[0, largura_estoque, largura_estoque, 0, 0, largura_estoque, largura_estoque, 0],
            y=[0, 0, profundidade_estoque, profundidade_estoque, 0, 0, profundidade_estoque, profundidade_estoque],
            z=[0, 0, 0, 0, altura_estoque, altura_estoque, altura_estoque, altura_estoque],
            i=[0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 6, 7],
            j=[1, 2, 3, 5, 6, 3, 0, 5, 6, 7, 4, 0],
            k=[2, 3, 0, 6, 7, 0, 4, 6, 7, 4, 5, 1],
            color='rgba(0, 128, 0, 0.1)',
            opacity=0.1,
            name='Estoque',
            showscale=False
        ))

        # Adicionar caixas
        idx = 0
        for i in range(int(n_x)):
            for j in range(int(n_y)):
                for k in range(int(n_z)):
                    x0 = i * largura_produto
                    y0 = k * profundidade_produto
                    z0 = j * altura_produto

                    fig.add_trace(go.Mesh3d(
                        x=[x0, x0+largura_produto, x0+largura_produto, x0, x0, x0+largura_produto, x0+largura_produto, x0],
                        y=[y0, y0, y0+profundidade_produto, y0+profundidade_produto, y0, y0, y0+profundidade_produto, y0+profundidade_produto],
                        z=[z0, z0, z0, z0, z0+altura_produto, z0+altura_produto, z0+altura_produto, z0+altura_produto],
                        i=[0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 6, 7],
                        j=[1, 2, 3, 5, 6, 3, 0, 5, 6, 7, 4, 0],
                        k=[2, 3, 0, 6, 7, 0, 4, 6, 7, 4, 5, 1],
                        color='rgba(0,0,255,0.4)',
                        opacity=0.5,
                        showscale=False,
                        name=f"Caixa {idx}"
                    ))
                    idx += 1

        fig.update_layout(
            scene=dict(
                xaxis=dict(title="Largura (mm)", range=[0, largura_estoque]),
                yaxis=dict(title="Profundidade (mm)", range=[0, profundidade_estoque]),
                zaxis=dict(title="Altura (mm)", range=[0, altura_estoque]),
                aspectmode='data'
            ),
            title="Empacotamento 3D"
        )

        st.plotly_chart(fig, use_container_width=True)
