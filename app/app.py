
import streamlit as st
import plotly.graph_objects as go

def gerar_caixas(largura_estoque, altura_estoque, profundidade_estoque,
                 largura_produto, altura_produto, profundidade_produto):

    qtd_x = largura_estoque // largura_produto
    qtd_y = altura_estoque // altura_produto
    qtd_z = profundidade_estoque // profundidade_produto
    total_caixas = int(qtd_x * qtd_y * qtd_z)

    caixas = []
    for ix in range(int(qtd_x)):
        for iy in range(int(qtd_y)):
            for iz in range(int(qtd_z)):
                x0 = ix * largura_produto
                y0 = iy * altura_produto
                z0 = iz * profundidade_produto
                caixas.append((x0, y0, z0))
    return caixas, total_caixas

def criar_cubo(x0, y0, z0, dx, dy, dz, cor="blue", opacidade=1.0, nome=""):
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    vertices = list(range(8))
    faces = [
        [0,1,2,3], [4,5,6,7], [0,1,5,4],
        [2,3,7,6], [1,2,6,5], [0,3,7,4]
    ]

    i, j, k = zip(*[(f[0], f[1], f[2]) for f in faces])
    mesh = go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k,
                     color=cor, opacity=opacidade,
                     name=nome, hoverinfo="skip", showscale=False)
    return mesh

st.set_page_config(page_title="Empacotamento 3D", layout="wide")

st.title("📦 Simulador de Empacotamento 3D")

with st.expander("🔻 Dimensões do Estoque (em mm)", expanded=True):
    largura_estoque = st.number_input("Largura do estoque", value=1760, step=10)
    altura_estoque = st.number_input("Altura do estoque", value=850, step=10)
    profundidade_estoque = st.number_input("Profundidade do estoque", value=400, step=10)

with st.expander("📦 Dimensões de 1 produto (em mm)", expanded=True):
    largura_produto = st.number_input("Largura do produto", value=200, step=10)
    altura_produto = st.number_input("Altura do produto", value=200, step=10)
    profundidade_produto = st.number_input("Profundidade do produto", value=200, step=10)

if st.button("Gerar visualização"):
    caixas, total_caixas = gerar_caixas(largura_estoque, altura_estoque, profundidade_estoque,
                                         largura_produto, altura_produto, profundidade_produto)

    st.markdown(f"<h3 style='color:lime'>✅ Máximo de produtos que cabem: {total_caixas}</h3>", unsafe_allow_html=True)

    fig = go.Figure()

    for idx, (x, y, z) in enumerate(caixas):
        cubo = criar_cubo(x, y, z, largura_produto, altura_produto, profundidade_produto,
                          cor="royalblue", opacidade=0.9, nome=f"Caixa {idx}")
        fig.add_trace(cubo)

    # Cubo do volume do estoque
    estoque = criar_cubo(0, 0, 0, largura_estoque, altura_estoque, profundidade_estoque,
                         cor="green", opacidade=0.15, nome="Estoque")
    fig.add_trace(estoque)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Largura (mm)", range=[0, largura_estoque]),
            yaxis=dict(title="Altura (mm)", range=[0, altura_estoque]),
            zaxis=dict(title="Profundidade (mm)", range=[0, profundidade_estoque]),
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
