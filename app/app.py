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
    with st.expander("Dimensões do Produto A", expanded=True):
        largura_A = st.number_input("Largura A (mm)", min_value=1, value=200, key="lA")
        altura_A = st.number_input("Altura A (mm)", min_value=1, value=200, key="hA")
        profundidade_A = st.number_input("Profundidade A (mm)", min_value=1, value=200, key="pA")
        cor_A = st.color_picker("Cor A", "#636EFA", key="cA")
    with st.expander("Dimensões do Produto B", expanded=True):
        largura_B = st.number_input("Largura B (mm)", min_value=1, value=150, key="lB")
        altura_B = st.number_input("Altura B (mm)", min_value=1, value=150, key="hB")
        profundidade_B = st.number_input("Profundidade B (mm)", min_value=1, value=150, key="pB")
        cor_B = st.color_picker("Cor B", "#EF553B", key="cB")

if st.button("GERAR SIMULAÇÃO"):
    st.caption("⚠️ Gerando simulação...")

    # volumes e máximo por produto
    V = largura_estoque * altura_estoque * profundidade_estoque
    v1 = largura_A * altura_A * profundidade_A
    v2 = largura_B * altura_B * profundidade_B

    max1 = V // v1
    max2 = V // v2

    # otimização em duas fases
    max_pairs = min(V // (v1 + v2), max1, max2)
    V_rest = V - max_pairs * (v1 + v2)
    extra_A = V_rest // v1
    extra_B = V_rest // v2
    if extra_A > extra_B:
        best_n1 = max_pairs + extra_A
        best_n2 = max_pairs
    else:
        best_n1 = max_pairs
        best_n2 = max_pairs + extra_B
    total_count = best_n1 + best_n2

    st.markdown(f"✅ A: {best_n1} un. | B: {best_n2} un. | Total: {total_count}")

    # listar posições A
    placed_A = []
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
                placed_A.append((x0, y0, z0, largura_A, profundidade_A, altura_A))
                count += 1
            if count >= best_n1:
                break
        if count >= best_n1:
            break

    # listar posições B em relação a A
    placed_B = []
    pairs = min(best_n1, best_n2)
    # fase pares
    for idx in range(pairs):
        xA, yA, zA, dxA, dyA, dzA = placed_A[idx]
        xB = xA + dxA if xA + dxA + largura_B <= largura_estoque else xA
        placed_B.append((xB, yA, zA, largura_B, profundidade_B, altura_B))
    # fase extras
    extra = best_n2 - pairs
    for idx in range(extra):
        xA, yA, zA, dxA, dyA, dzA = placed_A[idx]
        # sobre B ao lado ou acima
        if xA + dxA + largura_B <= largura_estoque:
            xB, yB, zB = xA + dxA, yA, zA
        else:
            xB, yB, zB = xA, yA, zA + dzA
        placed_B.append((xB, yB, zB, largura_B, profundidade_B, altura_B))

    # função de plot
    def adicionar_cubo(fig, x0, y0, z0, dx, dy, dz, cor, showlegend=False, name=None):
        verts = [[x0, y0, z0], [x0+dx, y0, z0], [x0+dx, y0+dy, z0], [x0, y0+dy, z0],
                 [x0, y0, z0+dz], [x0+dx, y0, z0+dz], [x0+dx, y0+dy, z0+dz], [x0, y0+dy, z0+dz]]
        x, y, z = zip(*verts)
        faces = [[0,1,2], [0,2,3], [4,5,6], [4,6,7],
                 [0,1,5], [0,5,4], [1,2,6], [1,6,5],
                 [2,3,7], [2,7,6], [3,0,4], [3,4,7]]
        i, j, k = zip(*faces)
        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, opacity=0.6, color=cor, showlegend=showlegend, name=name))
        for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
            fig.add_trace(go.Scatter3d(x=[x[a], x[b]], y=[y[a], y[b]], z=[z[a], z[b]], mode='lines', line=dict(color='black', width=2), showlegend=False))

    # plot 3D
    fig3 = go.Figure()
    for idx, (x0,y0,z0,dx,dy,dz) in enumerate(placed_A):
        adicionar_cubo(fig3, x0, y0, z0, dx, dy, dz, cor_A, showlegend=(idx==0), name='A')
    for idx, (x0,y0,z0,dx,dy,dz) in enumerate(placed_B):
        adicionar_cubo(fig3, x0, y0, z0, dx, dy, dz, cor_B, showlegend=(idx==0), name='B')
    adicionar_cubo(fig3, 0,0,0, largura_estoque, profundidade_estoque, altura_estoque, 'lightgreen', showlegend=False)
    fig3.update_layout(scene=dict(xaxis=dict(range=[0, largura_estoque]), yaxis=dict(range=[0, profundidade_estoque]), zaxis=dict(range=[0, altura_estoque]), aspectmode='data'), margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    # plot 2D frontal
    fig2 = go.Figure()
    pad_x = pad_y = 40
    for cx in range(qtd_horizontal):
        for cy in range(qtd_vertical):
            off_x = cx*(largura_estoque+pad_x)
            off_y = cy*(altura_estoque+pad_y)
            for (x0,y0,z0,dx,dy,dz) in placed_A:
                fig2.add_shape(type='rect', x0=off_x+x0, x1=off_x+x0+dx, y0=off_y+z0, y1=off_y+z0+dz, line=dict(color='black', width=1), fillcolor=cor_A)
            for (x0,y0,z0,dx,dy,dz) in placed_B:
                fig2.add_shape(type='rect', x0=off_x+x0, x1=off_x+x0+dx, y0=off_y+z0, y1=off_y+z0+dz, line=dict(color='black', width=1), fillcolor=cor_B)
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=10, color=cor_A), name='A'))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=10, color=cor_B), name='B'))
    largura_tot = qtd_horizontal*largura_estoque+(qtd_horizontal-1)*pad_x
    altura_tot = qtd_vertical*altura_estoque+(qtd_vertical-1)*pad_y
    fig2.update_layout(title='Visão Frontal', xaxis=dict(range=[0, largura_tot]), yaxis=dict(range=[0, altura_tot], scaleanchor='x'), height=500)
    st.plotly_chart(fig2, use_container_width=True)
