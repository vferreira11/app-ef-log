import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("📦 Simulador de Empacotamento 3D")

with st.expander("📉 Dimensões do Estoque (em mm)", expanded=True):
    largura_estoque = st.number_input("Largura do estoque", min_value=1, value=1760)
    altura_estoque = st.number_input("Altura do estoque", min_value=1, value=850)
    profundidade_estoque = st.number_input("Profundidade do estoque", min_value=1, value=400)

with st.expander("🛋️ Dimensões de 1 produto (em mm)", expanded=True):
    largura_produto = st.number_input("Largura do produto", min_value=1, value=200)
    altura_produto = st.number_input("Altura do produto", min_value=1, value=200)
    profundidade_produto = st.number_input("Profundidade do produto", min_value=1, value=200)

if st.button("Gerar visualização"):

    n_largura = largura_estoque // largura_produto
    n_altura = altura_estoque // altura_produto
    n_profundidade = profundidade_estoque // profundidade_produto
    total_caixas = int(n_largura * n_altura * n_profundidade)

    st.markdown(f"✅ <span style='font-size:24px'>**Máximo de produtos que cabem:**</span> <span style='color:lime;font-size:28px'><b>{total_caixas}</b></span>", unsafe_allow_html=True)

    fig = go.Figure()

    # desenhar caixas
    for i in range(n_largura):
        for j in range(n_altura):
            for k in range(n_profundidade):
                x0 = i * largura_produto
                y0 = j * altura_produto
                z0 = k * profundidade_produto
                x1 = x0 + largura_produto
                y1 = y0 + altura_produto
                z1 = z0 + profundidade_produto

                # faces da caixa (sem Mesh3D)
                arestas = [
                    [(x0,y0,z0), (x1,y0,z0)], [(x1,y0,z0), (x1,y1,z0)], [(x1,y1,z0), (x0,y1,z0)], [(x0,y1,z0), (x0,y0,z0)],
                    [(x0,y0,z1), (x1,y0,z1)], [(x1,y0,z1), (x1,y1,z1)], [(x1,y1,z1), (x0,y1,z1)], [(x0,y1,z1), (x0,y0,z1)],
                    [(x0,y0,z0), (x0,y0,z1)], [(x1,y0,z0), (x1,y0,z1)],
                    [(x1,y1,z0), (x1,y1,z1)], [(x0,y1,z0), (x0,y1,z1)]
                ]

                for edge in arestas:
                    fig.add_trace(go.Scatter3d(
                        x=[edge[0][0], edge[1][0]],
                        y=[edge[0][1], edge[1][1]],
                        z=[edge[0][2], edge[1][2]],
                        mode='lines',
                        line=dict(color='black', width=4),
                        showlegend=False
                    ))

    # desenhar o contorno do estoque
    estoque_bordas = [
        [(0, 0, 0), (largura_estoque, 0, 0)],
        [(largura_estoque, 0, 0), (largura_estoque, altura_estoque, 0)],
        [(largura_estoque, altura_estoque, 0), (0, altura_estoque, 0)],
        [(0, altura_estoque, 0), (0, 0, 0)],

        [(0, 0, profundidade_estoque), (largura_estoque, 0, profundidade_estoque)],
        [(largura_estoque, 0, profundidade_estoque), (largura_estoque, altura_estoque, profundidade_estoque)],
        [(largura_estoque, altura_estoque, profundidade_estoque), (0, altura_estoque, profundidade_estoque)],
        [(0, altura_estoque, profundidade_estoque), (0, 0, profundidade_estoque)],

        [(0, 0, 0), (0, 0, profundidade_estoque)],
        [(largura_estoque, 0, 0), (largura_estoque, 0, profundidade_estoque)],
        [(largura_estoque, altura_estoque, 0), (largura_estoque, altura_estoque, profundidade_estoque)],
        [(0, altura_estoque, 0), (0, altura_estoque, profundidade_estoque)]
    ]

    for edge in estoque_bordas:
        fig.add_trace(go.Scatter3d(
            x=[edge[0][0], edge[1][0]],
            y=[edge[0][1], edge[1][1]],
            z=[edge[0][2], edge[1][2]],
            mode='lines',
            line=dict(color='green', width=6),
            showlegend=False
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_estoque]),
            yaxis=dict(title='Altura (mm)', range=[0, altura_estoque]),
            zaxis=dict(title='Profundidade (mm)', range=[0, profundidade_estoque]),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    st.plotly_chart(fig, use_container_width=True)
