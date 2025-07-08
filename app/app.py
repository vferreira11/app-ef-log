import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📦 Simulador de Armazenamento 3D")

col1, col2 = st.columns(2)

col_estoque, col_produto = st.columns(2)

with col_estoque:
    with st.container():
        with st.expander("📦 Célula de Estoque", expanded=True):
            largura_estoque = st.number_input("Largura do estoque", min_value=1, value=1760)
            altura_estoque = st.number_input("Altura do estoque", min_value=1, value=850)
            profundidade_estoque = st.number_input("Profundidade do estoque", min_value=1, value=400)
            quantidade_celulas = st.number_input("Quantidade de células de estoque", min_value=1, value=4)

            layout_opcao = st.selectbox(
                "Layout de empacotamento",
                ["📏 Lado a lado", "📐 Vertical", "🔢 Definir manualmente"]
            )

            if layout_opcao == "📏 Lado a lado":
                qtd_horizontal = quantidade_celulas
                qtd_vertical = 1
            elif layout_opcao == "📐 Vertical":
                qtd_horizontal = 1
                qtd_vertical = quantidade_celulas
            else:
                qtd_horizontal = st.number_input("Qtd. horizontal", min_value=1, value=2)
                qtd_vertical = st.number_input("Qtd. vertical", min_value=1, value=2)


with col_produto:
    with st.container():
        with st.expander("🛋️ Dimensões de 1 produto (em mm)", expanded=True):
            largura_produto = st.number_input("Largura do produto", min_value=1, value=200)
            altura_produto = st.number_input("Altura do produto", min_value=1, value=200)
            profundidade_produto = st.number_input("Profundidade do produto", min_value=1, value=200)

if st.button("GERAR SIMULAÇÃO"):
    
    st.caption("⚠️ Pode demorar alguns segundos. Aguarde!")
   
    n_largura = largura_estoque // largura_produto
    n_altura = altura_estoque // altura_produto
    n_profundidade = profundidade_estoque // profundidade_produto
    total_caixas = int(n_largura * n_altura * n_profundidade)

    st.markdown(f"✅ <span style='font-size:24px'>**Máximo de produtos:**</span> <span style='color:lime;font-size:28px'><b>{total_caixas}</b></span>", unsafe_allow_html=True)

    fig = go.Figure()

    def adicionar_cubo(x0, y0, z0, dx, dy, dz, cor='blue', opacidade=1, borda=True):
        vertices = [
            [x0, y0, z0], [x0+dx, y0, z0], [x0+dx, y0+dy, z0], [x0, y0+dy, z0],
            [x0, y0, z0+dz], [x0+dx, y0, z0+dz], [x0+dx, y0+dy, z0+dz], [x0, y0+dy, z0+dz]
        ]
        x, y, z = zip(*vertices)

        faces = [
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4],
            [1, 2, 6], [1, 6, 5],
            [2, 3, 7], [2, 7, 6],
            [3, 0, 4], [3, 4, 7]
        ]
        i, j, k = zip(*faces)

        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            opacity=opacidade,
            color=cor,
            showlegend=False
        ))

        if borda:
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

    # Centralizar os blocos na LARGURA (X) e PROFUNDIDADE (Y)
    largura_total_usada = n_largura * largura_produto
    offset_x = (largura_estoque - largura_total_usada) / 2

    profundidade_total_usada = n_profundidade * profundidade_produto
    offset_y = (profundidade_estoque - profundidade_total_usada) / 2

    for i in range(n_largura):
        for j in range(n_profundidade):
            for k in range(n_altura):
                x0 = offset_x + i * largura_produto      # deslocamento lateral
                y0 = offset_y + j * profundidade_produto # deslocamento para centralizar profundidade
                z0 = k * altura_produto                  # começa do chão
                adicionar_cubo(x0, y0, z0, largura_produto, profundidade_produto, altura_produto, cor='royalblue', opacidade=1, borda=True)

    # Volume total da estante (verde claro e transparente)
    adicionar_cubo(0, 0, 0, largura_estoque, profundidade_estoque, altura_estoque, cor='lightgreen', opacidade=0.1, borda=False)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_estoque]),          # esquerda ↔ direita
            yaxis=dict(title='Profundidade (mm)', range=[0, profundidade_estoque]),# frente ↔ fundo
            zaxis=dict(title='Altura (mm)', range=[0, altura_estoque]),            # baixo ↔ cima
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.8, y=-2.5, z=1.8)  # visão frontal elevada
            )
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # === Gráfico 2D (vista frontal) ===
    import plotly.express as px

    fig2d = go.Figure()

    n_largura = largura_estoque // largura_produto
    n_altura = altura_estoque // altura_produto
    n_total = n_largura * n_altura

    qtd_plotar = min(quantidade_celulas, n_total)

    for idx in range(qtd_plotar):
        i = idx % n_largura
        j = idx // n_largura
        if j >= n_altura:
            break
        x0 = i * largura_produto
        y0 = j * altura_produto

        fig2d.add_shape(
            type="rect",
            x0=x0, x1=x0 + largura_produto,
            y0=y0, y1=y0 + altura_produto,
            line=dict(color="black", width=2),
            fillcolor="royalblue"
        )

    fig2d.update_layout(
        title="📐 Visão Frontal da Célula de Estoque",
        xaxis=dict(title="Largura (mm)", range=[0, largura_estoque], showgrid=False, zeroline=False),
        yaxis=dict(title="Altura (mm)", range=[0, altura_estoque], showgrid=False, zeroline=False, scaleanchor="x"),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig2d, use_container_width=True)

