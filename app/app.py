import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📦 Simulador de Armazenamento 3D")

col_estoque, col_produto = st.columns(2)

with col_estoque:
    with st.expander("📦 Célula de Estoque", expanded=True):
        largura_estoque = st.number_input("Largura do estoque (mm)", min_value=1, value=1760)
        altura_estoque = st.number_input("Altura do estoque (mm)", min_value=1, value=850)
        profundidade_estoque = st.number_input("Profundidade do estoque (mm)", min_value=1, value=400)
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
    with st.expander("🛋️ Dimensões do Produto A", expanded=True):
        largura_A = st.number_input("Largura do Produto A (mm)", min_value=1, value=200, key="lA")
        altura_A = st.number_input("Altura do Produto A (mm)", min_value=1, value=200, key="hA")
        profundidade_A = st.number_input("Profundidade do Produto A (mm)", min_value=1, value=200, key="pA")
        cor_A = st.color_picker("Cor do Produto A", "#636EFA", key="cA")
    with st.expander("🎁 Dimensões do Produto B", expanded=True):
        largura_B = st.number_input("Largura do Produto B (mm)", min_value=1, value=150, key="lB")
        altura_B = st.number_input("Altura do Produto B (mm)", min_value=1, value=150, key="hB")
        profundidade_B = st.number_input("Profundidade do Produto B (mm)", min_value=1, value=150, key="pB")
        cor_B = st.color_picker("Cor do Produto B", "#EF553B", key="cB")

if st.button("GERAR SIMULAÇÃO"):
    st.caption("⚠️ Aguarde enquanto os gráficos são gerados. Isso pode levar alguns segundos.")

    # --- otimização por volume (knapsack simples) ---
    V = largura_estoque * altura_estoque * profundidade_estoque
    v1 = largura_A * altura_A * profundidade_A
    v2 = largura_B * altura_B * profundidade_B
    max1 = V // v1
    max2 = V // v2

    best_n1, best_n2, max_count = 0, 0, 0
    for n1 in range(int(max1) + 1):
        for n2 in range(int(max2) + 1):
            if n1 * v1 + n2 * v2 <= V and (n1 + n2) > max_count:
                best_n1, best_n2, max_count = n1, n2, n1 + n2

    st.markdown(
        f"✅ <span style='font-size:20px'>**Produto A:** {best_n1} unidades<br>"
        f"**Produto B:** {best_n2} unidades<br>"
        f"**Total:** {max_count}</span>",
        unsafe_allow_html=True
    )

    # --- figura 3D ---
    fig = go.Figure()

    def adicionar_cubo(x0, y0, z0, dx, dy, dz, cor, opacidade=1, borda=True, show_legend=False, name=None):
        vertices = [
            [x0, y0, z0], [x0+dx, y0, z0], [x0+dx, y0+dy, z0], [x0, y0+dy, z0],
            [x0, y0, z0+dz], [x0+dx, y0, z0+dz], [x0+dx, y0+dy, z0+dz], [x0, y0+dy, z0+dz]
        ]
        x, y, z = zip(*vertices)
        faces = [
            [0,1,2], [0,2,3],
            [4,5,6], [4,6,7],
            [0,1,5], [0,5,4],
            [1,2,6], [1,6,5],
            [2,3,7], [2,7,6],
            [3,0,4], [3,4,7]
        ]
        i, j, k = zip(*faces)
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            opacity=opacidade,
            color=cor,
            showlegend=show_legend,
            name=name
        ))
        if borda:
            for a, b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
                fig.add_trace(go.Scatter3d(
                    x=[x[a], x[b]],
                    y=[y[a], y[b]],
                    z=[z[a], z[b]],
                    mode='lines',
                    line=dict(color='black', width=3),
                    showlegend=False
                ))

    # produtos A
    nxA = largura_estoque // largura_A
    nyA = profundidade_estoque // profundidade_A
    nzA = altura_estoque // altura_A
    count = 0
    for k in range(nzA):
        for j in range(nyA):
            for i in range(nxA):
                if count >= best_n1:
                    break
                x0 = i * largura_A
                y0 = j * profundidade_A
                z0 = k * altura_A
                adicionar_cubo(x0, y0, z0, largura_A, profundidade_A, altura_A,
                              cor_A, borda=True, show_legend=(count==0), name="Produto A")
                count += 1
        if count >= best_n1:
            break

    # produtos B
    nxB = largura_estoque // largura_B
    nyB = profundidade_estoque // profundidade_B
    nzB = altura_estoque // altura_B
    count = 0
    for k in range(nzB):
        for j in range(nyB):
            for i in range(nxB):
                if count >= best_n2:
                    break
                x0 = i * largura_B
                y0 = j * profundidade_B
                z0 = k * altura_B
                adicionar_cubo(x0, y0, z0, largura_B, profundidade_B, altura_B,
                              cor_B, borda=True, show_legend=(count==0), name="Produto B")
                count += 1
        if count >= best_n2:
            break

    # contorno da célula
    adicionar_cubo(0, 0, 0, largura_estoque, profundidade_estoque, altura_estoque,
                  "lightgreen", opacidade=0.1, borda=False)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Largura (mm)', range=[0, largura_estoque]),
            yaxis=dict(title='Profundidade (mm)', range=[0, profundidade_estoque]),
            zaxis=dict(title='Altura (mm)', range=[0, altura_estoque]),
            aspectmode='data',
            camera=dict(eye=dict(x=1.8, y=-2.5, z=1.8))
        ),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- figura 2D frontal ---
    fig2d = go.Figure()
    espaco_x = 40
    espaco_y = 40

    # para cada célula no layout
    for cx in range(qtd_horizontal):
        for cy in range(qtd_vertical):
            base_x = cx * (largura_estoque + espaco_x)
            base_y = cy * (altura_estoque + espaco_y)

            # A
            count = 0
            for k in range(nzA):
                for j in range(nyA):
                    for i in range(nxA):
                        if count >= best_n1:
                            break
                        x0 = base_x + i * largura_A
                        y0 = base_y + k * altura_A
                        fig2d.add_shape(
                            type="rect",
                            x0=x0, x1=x0 + largura_A,
                            y0=y0, y1=y0 + altura_A,
                            line=dict(color="black", width=2),
                            fillcolor=cor_A
                        )
                        count += 1
                    if count >= best_n1:
                        break
                if count >= best_n1:
                    break

            # B
            count = 0
            for k in range(nzB):
                for j in range(nyB):
                    for i in range(nxB):
                        if count >= best_n2:
                            break
                        x0 = base_x + i * largura_B
                        y0 = base_y + k * altura_B
                        fig2d.add_shape(
                            type="rect",
                            x0=x0, x1=x0 + largura_B,
                            y0=y0, y1=y0 + altura_B,
                            line=dict(color="black", width=2),
                            fillcolor=cor_B
                        )
                        count += 1
                    if count >= best_n2:
                        break
                if count >= best_n2:
                    break

    # legendas (marcadores invisíveis)
    fig2d.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(size=10, color=cor_A),
        name="Produto A"
    ))
    fig2d.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(size=10, color=cor_B),
        name="Produto B"
    ))

    largura_total = qtd_horizontal * largura_estoque + (qtd_horizontal - 1) * espaco_x
    altura_total = qtd_vertical * altura_estoque + (qtd_vertical - 1) * espaco_y

    fig2d.update_layout(
        title="📐 Visão Frontal das Células de Estoque",
        xaxis=dict(title="Largura total (mm)", range=[0, largura_total], showgrid=False, zeroline=False),
        yaxis=dict(title="Altura total (mm)", range=[0, altura_total], showgrid=False, zeroline=False, scaleanchor="x"),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig2d, use_container_width=True)
