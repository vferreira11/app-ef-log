
import streamlit as st
import plotly.graph_objects as go
import math

def plot_cubo_3d_com_itens(container_dims, item_dims):
    largura_c, altura_c, profundidade_c = container_dims
    largura_i, altura_i, profundidade_i = item_dims

    fig = go.Figure()

    # Container (estoque)
    fig.add_trace(go.Mesh3d(
        x=[0, largura_c, largura_c, 0, 0, largura_c, largura_c, 0],
        y=[0, 0, profundidade_c, profundidade_c, 0, 0, profundidade_c, profundidade_c],
        z=[0, 0, 0, 0, altura_c, altura_c, altura_c, altura_c],
        color='lightgray',
        opacity=0.1,
        name='Estoque'
    ))

    cols = math.floor(largura_c / largura_i)
    rows = math.floor(profundidade_c / profundidade_i)
    stacks = math.floor(altura_c / altura_i)
    total_fit = cols * rows * stacks

    st.markdown(f"### 🧮 Máximo de produtos que cabem: `{total_fit}`")

    count = 0
    for i in range(cols):
        for j in range(rows):
            for k in range(stacks):
                x0 = i * largura_i
                y0 = j * profundidade_i
                z0 = k * altura_i

                fig.add_trace(go.Mesh3d(
                    x=[x0, x0+largura_i, x0+largura_i, x0, x0, x0+largura_i, x0+largura_i, x0],
                    y=[y0, y0, y0+profundidade_i, y0+profundidade_i, y0, y0, y0+profundidade_i, y0+profundidade_i],
                    z=[z0, z0, z0, z0, z0+altura_i, z0+altura_i, z0+altura_i, z0+altura_i],
                    color='royalblue',
                    opacity=0.5,
                    name=f'Caixa {count+1}'
                ))
                count += 1

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, largura_c]),
            yaxis=dict(range=[0, profundidade_c]),
            zaxis=dict(range=[0, altura_c]),
            aspectmode='data',
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="Empacotamento 3D",
        showlegend=False
    )

    return fig

# Streamlit App
st.set_page_config(page_title="Empacotamento 3D", layout="centered")

st.title("📦 Simulador de Empacotamento 3D")

st.subheader("📐 Dimensões do Estoque (em mm)")
largura_c = st.number_input("Largura do estoque", min_value=1, value=1760)
altura_c = st.number_input("Altura do estoque", min_value=1, value=850)
profundidade_c = st.number_input("Profundidade do estoque", min_value=1, value=400)

st.subheader("📦 Dimensões de 1 produto (em mm)")
largura_i = st.number_input("Largura do produto", min_value=1, value=200)
altura_i = st.number_input("Altura do produto", min_value=1, value=200)
profundidade_i = st.number_input("Profundidade do produto", min_value=1, value=200)

if st.button("Gerar visualização"):
    fig = plot_cubo_3d_com_itens(
        container_dims=(largura_c, altura_c, profundidade_c),
        item_dims=(largura_i, altura_i, profundidade_i)
    )
    st.plotly_chart(fig, use_container_width=True)
