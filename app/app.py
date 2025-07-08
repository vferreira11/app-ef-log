
import streamlit as st
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Simulador de Armazenamento", layout="wide")

st.title("📦 Simulador de Acondicionamento de Produtos no Estoque")

with st.sidebar:
    st.header("Dimensões do Estoque (mm)")
    largura_estoque = st.number_input("Largura", min_value=100, value=1200)
    altura_estoque = st.number_input("Altura", min_value=100, value=1200)
    profundidade_estoque = st.number_input("Profundidade", min_value=100, value=1200)

    st.header("Dimensões do Produto (mm)")
    largura_produto = st.number_input("Largura ", min_value=10, value=200)
    altura_produto = st.number_input("Altura ", min_value=10, value=200)
    profundidade_produto = st.number_input("Profundidade ", min_value=10, value=200)

def criar_cubo_borda(x0, y0, z0, dx, dy, dz, cor='blue'):
    pontos = [
        [(x0, y0, z0), (x0+dx, y0, z0)],
        [(x0+dx, y0, z0), (x0+dx, y0+dy, z0)],
        [(x0+dx, y0+dy, z0), (x0, y0+dy, z0)],
        [(x0, y0+dy, z0), (x0, y0, z0)],
        [(x0, y0, z0+dz), (x0+dx, y0, z0+dz)],
        [(x0+dx, y0, z0+dz), (x0+dx, y0+dy, z0+dz)],
        [(x0+dx, y0+dy, z0+dz), (x0, y0+dy, z0+dz)],
        [(x0, y0+dy, z0+dz), (x0, y0, z0+dz)],
        [(x0, y0, z0), (x0, y0, z0+dz)],
        [(x0+dx, y0, z0), (x0+dx, y0, z0+dz)],
        [(x0+dx, y0+dy, z0), (x0+dx, y0+dy, z0+dz)],
        [(x0, y0+dy, z0), (x0, y0+dy, z0+dz)],
    ]
    return [
        go.Scatter3d(
            x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]],
            mode='lines',
            line=dict(color=cor, width=3),
            showlegend=False
        ) for p1, p2 in pontos
    ]

def criar_cubo_preenchido(x0, y0, z0, dx, dy, dz, cor='blue', opacidade=0.2):
    return go.Mesh3d(
        x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
        y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
        z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
        i=[0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6],
        j=[1, 2, 3, 2, 5, 3, 6, 0, 5, 6, 6, 7],
        k=[2, 3, 0, 5, 6, 6, 7, 4, 6, 7, 7, 4],
        opacity=opacidade,
        color=cor,
        showlegend=False
    )

nx = math.floor(largura_estoque / largura_produto)
ny = math.floor(profundidade_estoque / profundidade_produto)
nz = math.floor(altura_estoque / altura_produto)

total_caixas = nx * ny * nz
st.subheader(f"📦 Total de produtos acomodados: {total_caixas}")

cubos = []
for i in range(nx):
    for j in range(ny):
        for k in range(nz):
            x0 = i * largura_produto
            y0 = j * profundidade_produto
            z0 = k * altura_produto
            cubos += criar_cubo_borda(x0, y0, z0, largura_produto, profundidade_produto, altura_produto)
            cubos.append(criar_cubo_preenchido(x0, y0, z0, largura_produto, profundidade_produto, altura_produto))

estrutura = go.Mesh3d(
    x=[0, largura_estoque, largura_estoque, 0, 0, largura_estoque, largura_estoque, 0],
    y=[0, 0, profundidade_estoque, profundidade_estoque, 0, 0, profundidade_estoque, profundidade_estoque],
    z=[0, 0, 0, 0, altura_estoque, altura_estoque, altura_estoque, altura_estoque],
    i=[0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6],
    j=[1, 2, 3, 2, 5, 3, 6, 0, 5, 6, 6, 7],
    k=[2, 3, 0, 5, 6, 6, 7, 4, 6, 7, 7, 4],
    opacity=0.08,
    color='green'
)

fig = go.Figure(data=[estrutura] + cubos)
fig.update_layout(
    scene=dict(
        xaxis_title='Largura (mm)',
        yaxis_title='Profundidade (mm)',
        zaxis_title='Altura (mm)',
        aspectmode='data'
    ),
    title='Visualização 3D do Estoque'
)


if total_caixas == 0:
    st.warning("❗ As dimensões do produto são maiores que as do estoque. Ajuste os valores para visualizar o empacotamento.")
else:
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_estoque]),
            yaxis=dict(title='Profundidade (mm)', range=[0, profundidade_estoque]),
            zaxis=dict(title='Altura (mm)', range=[0, altura_estoque]),
            aspectmode='data'
        ),
        title='Visualização 3D do Estoque'
    )
    st.plotly_chart(fig, use_container_width=True)

