import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📦 Simulador de Armazenamento 3D")

col_estoque, col_produto = st.columns(2)

with col_estoque:
    with st.expander("Célula de Estoque", expanded=True):
        largura_estoque = st.number_input("Largura da célula (mm)", min_value=1, value=1760)
        altura_estoque = st.number_input("Altura da célula (mm)", min_value=1, value=850)
        profundidade_estoque = st.number_input("Profundidade da célula (mm)", min_value=1, value=400)
        quantidade_celulas = st.number_input("Número de células", min_value=1, value=4)

        layout = st.selectbox("Layout", ["Lado a lado", "Vertical", "Manual"])
        if layout == "Lado a lado":
            qtd_horiz = quantidade_celulas
            qtd_vert = 1
        elif layout == "Vertical":
            qtd_horiz = 1
            qtd_vert = quantidade_celulas
        else:
            qtd_horiz = st.number_input("Cols", min_value=1, value=2)
            qtd_vert = st.number_input("Rows", min_value=1, value=2)

with col_produto:
    with st.expander("Produto A", expanded=True):
        largura_A = st.number_input("Largura A (mm)", min_value=1, value=200, key="lA")
        altura_A = st.number_input("Altura A (mm)", min_value=1, value=200, key="hA")
        profundidade_A = st.number_input("Profundidade A (mm)", min_value=1, value=200, key="pA")
        cor_A = st.color_picker("Cor A", "#636EFA", key="cA")
    with st.expander("Produto B", expanded=True):
        largura_B = st.number_input("Largura B (mm)", min_value=1, value=150, key="lB")
        altura_B = st.number_input("Altura B (mm)", min_value=1, value=150, key="hB")
        profundidade_B = st.number_input("Profundidade B (mm)", min_value=1, value=150, key="pB")
        cor_B = st.color_picker("Cor B", "#EF553B", key="cB")

# detecção de colisão

def overlap(b1, b2):
    x0,y0,z0,dx1,dy1,dz1 = b1
    x1,y1,z1,dx2,dy2,dz2 = b2
    return not (
        x0+dx1 <= x1 or x1+dx2 <= x0 or
        y0+dy1 <= y1 or y1+dy2 <= y0 or
        z0+dz1 <= z1 or z1+dz2 <= z0
    )

if st.button("GERAR SIMULAÇÃO"):
    st.caption("Gerando simulação...")

    # volumes
    V = largura_estoque * altura_estoque * profundidade_estoque
    v1 = largura_A * altura_A * profundidade_A
    v2 = largura_B * altura_B * profundidade_B

    # otimização
    max_pairs = min(V // (v1+v2), V//v1, V//v2)
    V_rest = V - max_pairs*(v1+v2)
    extra_A = V_rest//v1
    extra_B = V_rest//v2
    if extra_A > extra_B:
        nA = max_pairs + extra_A
        nB = max_pairs
    else:
        nA = max_pairs
        nB = max_pairs + extra_B

    st.markdown(f"**A:** {nA} un. • **B:** {nB} un. • **Total:** {nA+nB}")

    # posicionar A
    placed_A = []
    nxA, nyA, nzA = largura_estoque//largura_A, profundidade_estoque//profundidade_A, altura_estoque//altura_A
    cnt=0
    for z in range(nzA):
        for y in range(nyA):
            for x in range(nxA):
                if cnt>=nA: break
                placed_A.append((x*largura_A, y*profundidade_A, z*altura_A, largura_A, profundidade_A, altura_A))
                cnt+=1
            if cnt>=nA: break
        if cnt>=nA: break

    # posicionar B sem sobreposição
    placed_B = []
    nxB, nyB, nzB = largura_estoque//largura_B, profundidade_estoque//profundidade_B, altura_estoque//altura_B
    cnt=0
    for z in range(nzB):
        for y in range(nyB):
            for x in range(nxB):
                if cnt>=nB: break
                box=(x*largura_B, y*profundidade_B, z*altura_B, largura_B, profundidade_B, altura_B)
                if any(overlap(box,a) for a in placed_A): continue
                if any(overlap(box,b) for b in placed_B): continue
                placed_B.append(box)
                cnt+=1
            if cnt>=nB: break
        if cnt>=nB: break

    # função de plotagem
    def draw_cube(fig, box, cor, showleg=False, name=None):
        x0,y0,z0,dx,dy,dz = box
        verts=[[x0,y0,z0],[x0+dx,y0,z0],[x0+dx,y0+dy,z0],[x0,y0+dy,z0],
               [x0,y0,z0+dz],[x0+dx,y0,z0+dz],[x0+dx,y0+dy,z0+dz],[x0,y0+dy,z0+dz]]
        x,y,z=zip(*verts)
        faces=[[0,1,2],[0,2,3],[4,5,6],[4,6,7],
               [0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
        i,j,k=zip(*faces)
        fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=cor,opacity=0.6,showlegend=showleg,name=name))
        for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
            fig.add_trace(go.Scatter3d(x=[x[a],x[b]],y=[y[a],y[b]],z=[z[a],z[b]],mode='lines',line=dict(color='black',width=2),showlegend=False))

    # render 3D
    fig3=go.Figure()
    for i,box in enumerate(placed_A): draw_cube(fig3,box,cor_A,showleg=(i==0),name='A')
    for i,box in enumerate(placed_B): draw_cube(fig3,box,cor_B,showleg=(i==0),name='B')
    draw_cube(fig3,(0,0,0,largura_estoque,profundidade_estoque,altura_estoque),'lightgreen')
    fig3.update_layout(scene=dict(aspectmode='data',xaxis=dict(range=[0,largura_estoque]),yaxis=dict(range=[0,profundidade_estoque]),zaxis=dict(range=[0,altura_estoque])),margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig3,use_container_width=True)

    # render 2D frontal
    fig2=go.Figure()
    pad=40
    for cx in range(qtd_horiz):
        for cy in range(qtd_vert):
            ox,oy=cx*(largura_estoque+pad),cy*(altura_estoque+pad)
            for box in placed_A: x0,y0,z0,dx,dy,dz=box; fig2.add_shape('rect',x0=ox+x0,x1=ox+x0+dx,y0=oy+z0,y1=oy+z0+dz,line=dict(width=1),fillcolor=cor_A)
            for box in placed_B: x0,y0,z0,dx,dy,dz=box; fig2.add_shape('rect',x0=ox+x0,x1=ox+x0+dx,y0=oy+z0,y1=oy+z0+dz,line=dict(width=1),fillcolor=cor_B)
    fig2.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(color=cor_A),name='A'))
    fig2.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(color=cor_B),name='B'))
    fig2.update_layout(title='Visão Frontal',xaxis=dict(range=[0,qtd_horiz*largura_estoque+(qtd_horiz-1)*pad]),yaxis=dict(range=[0,qtd_vert*altura_estoque+(qtd_vert-1)*pad],scaleanchor='x'),height=500)
    st.plotly_chart(fig2,use_container_width=True)
