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

    def adicionar_cubo(x0, y0, z0, dx, dy, dz, cor='blue'):
        # Mesh preenchido
        vertices = [
            [x0, y0, z0], [x0+dx, y0, z0], [x0+dx, y0+dy, z0], [x0, y0+dy, z0],
            [x0, y0, z0+dz], [x0+dx, y0, z0+dz], [x0+dx, y0+dy, z0+dz], [x0, y0+dy, z0+dz]
        ]
        x, y, z = zip(*vertices)
        faces = [
            [0, 1, 2], [0, 2, 3],       # base
            [4, 5, 6], [4, 6, 7],       # topo
            [0, 1, 5], [0, 5, 4],       # frente
            [1, 2, 6], [1, 6, 5],       # direita
            [2, 3, 7], [2, 7, 6],       # fundo
            [3, 0, 4], [3, 4, 7]        # esquerda
        ]
        i, j, k = zip(*faces)

        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            opacity=1,
            color=cor,
            showlegend=False
        ))

        # Arestas destacadas
        arestas = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        for a, b in arestas:
            fig.add_trace(go.Scatter3d(
                x=[x[a], x[b]],
                y=[y[a], y[b]],
                z=[z[a], z[b]],
                mode='lines',
                line=dict(color='black', width=6),
                showlegend=False
            ))

    # Criar cubos
    for i in range(n_largura):
        for j in range(n_altura):
            for k in range(n_profundidade):
                x0 = i * largura_produto
                y0 = j * altura_produto
                z0 = k * profundidade_produto
                adicionar_cubo(x0, y0, z0, largura_produto, altura_produto, profundidade_produto)

    # Contorno do volume total (verde claro)
    adicionar_cubo(0, 0, 0, largura_estoque, altura_estoque, profundidade_estoque, cor='lightgreen')

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
