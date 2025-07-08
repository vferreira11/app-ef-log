import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📦 Simulador de Armazenamento 3D")

# --- Inputs ---
col1, col2 = st.columns(2)
with col1:
    largura_cel = st.number_input("Largura célula (mm)", min_value=1, value=1760)
    profundidade_cel = st.number_input("Profundidade célula (mm)", min_value=1, value=400)
    altura_cel = st.number_input("Altura célula (mm)", min_value=1, value=850)
    num_cel = st.number_input("Número de células", min_value=1, value=4)
    layout = st.selectbox("Layout", ["Lado a lado", "Vertical", "Manual"])
    if layout == "Lado a lado": cols = num_cel; rows = 1
    elif layout == "Vertical": cols = 1; rows = num_cel
    else:
        cols = st.number_input("Cols", min_value=1, value=2)
        rows = st.number_input("Rows", min_value=1, value=2)
with col2:
    largura_A = st.number_input("Largura A (mm)", min_value=1, value=200)
    profundidade_A = st.number_input("Profundidade A (mm)", min_value=1, value=200)
    altura_A = st.number_input("Altura A (mm)", min_value=1, value=200)
    cor_A = st.color_picker("Cor A", "#636EFA")
    largura_B = st.number_input("Largura B (mm)", min_value=1, value=150)
    profundidade_B = st.number_input("Profundidade B (mm)", min_value=1, value=150)
    altura_B = st.number_input("Altura B (mm)", min_value=1, value=150)
    cor_B = st.color_picker("Cor B", "#EF553B")

if st.button("GERAR SIMULAÇÃO"):
    # --- cálculo otimização ---
    V = largura_cel * profundidade_cel * altura_cel
    vA = largura_A * profundidade_A * altura_A
    vB = largura_B * profundidade_B * altura_B
    # pares A+B e extras
    max_pairs = min(V // (vA + vB), V // vA, V // vB)
    rest = V - max_pairs * (vA + vB)
    extraA = rest // vA
    extraB = rest // vB
    if extraA >= extraB:
        nA = max_pairs + extraA
        nB = max_pairs
    else:
        nA = max_pairs
        nB = max_pairs + extraB
    st.markdown(f"**A:** {nA} un. • **B:** {nB} un. • **Total:** {nA+nB}")

    # --- posicionamento A (grid simples) ---
    nxA = largura_cel // largura_A
    nyA = profundidade_cel // profundidade_A
    nzA = altura_cel // altura_A
    placed_A = []
    cnt = 0
    for z in range(nzA):
        for y in range(nyA):
            for x in range(nxA):
                if cnt >= nA: break
                placed_A.append((x*largura_A, y*profundidade_A, z*altura_A, largura_A, profundidade_A, altura_A))
                cnt += 1
            if cnt >= nA: break
        if cnt >= nA: break
    # largura ocupada por A
    max_xA = max(x+dx for x,_,_,dx,_,_ in placed_A)

    # --- posicionamento B (zona reservada à direita) ---
    # calculamos quantos B cabem na largura restante
    rem_width = largura_cel - max_xA
    nxB = rem_width // largura_B
    nyB = profundidade_cel // profundidade_B
    nzB = altura_cel // altura_B
    placed_B = []
    cnt = 0
    for z in range(nzB):
        for y in range(nyB):
            for i in range(nxB):
                if cnt >= nB: break
                x0 = max_xA + i * largura_B
                y0 = y * profundidade_B
                z0 = z * altura_B
                placed_B.append((x0, y0, z0, largura_B, profundidade_B, altura_B))
                cnt += 1
            if cnt >= nB: break
        if cnt >= nB: break

    # --- plotagem ---
    def draw(fig, box, color, legend=False, name=None):
        x0,y0,z0,dx,dy,dz = box
        verts = [(x0,y0,z0),(x0+dx,y0,z0),(x0+dx,y0+dy,z0),(x0,y0+dy,z0),
                 (x0,y0,z0+dz),(x0+dx,y0,z0+dz),(x0+dx,y0+dy,z0+dz),(x0,y0+dy,z0+dz)]
        x,y,z = zip(*verts)
        faces = [(0,1,2),(0,2,3),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
        i,j,k = zip(*faces)
        fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=color,opacity=0.6,showlegend=legend,name=name))
        for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
            fig.add_trace(go.Scatter3d(x=[x[a],x[b]],y=[y[a],y[b]],z=[z[a],z[b]],mode='lines',line=dict(color='black',width=2),showlegend=False))

    # 3D
    fig3 = go.Figure()
    for i,box in enumerate(placed_A): draw(fig3, box, cor_A, legend=(i==0), name='A')
    for i,box in enumerate(placed_B): draw(fig3, box, cor_B, legend=(i==0), name='B')
    draw(fig3, (0,0,0,largura_cel,profundidade_cel,altura_cel), 'lightgreen')
    fig3.update_layout(scene=dict(aspectmode='data',xaxis=dict(range=[0,largura_cel]),yaxis=dict(range=[0,profundidade_cel]),zaxis=dict(range=[0,altura_cel])),margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    # 2D frontal
    fig2 = go.Figure()
    pad = 40
    for cx in range(cols):
        for cy in range(rows):
            ox = cx*(largura_cel+pad)
            oy = cy*(altura_cel+pad)
            for box in placed_A:
                x0,y0,z0,dx,dy,dz = box
                fig2.add_shape(type='rect', x0=ox+x0, x1=ox+x0+dx, y0=oy+z0, y1=oy+z0+dz, line=dict(color='black',width=1), fillcolor=cor_A)
            for box in placed_B:
                x0,y0,z0,dx,dy,dz = box
                fig2.add_shape(type='rect', x0=ox+x0, x1=ox+x0+dx, y0=oy+z0, y1=oy+z0+dz, line=dict(color='black',width=1), fillcolor=cor_B)
    fig2.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(color=cor_A),name='A'))
    fig2.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(color=cor_B),name='B'))
    total_w = cols*largura_cel + (cols-1)*pad
    total_h = rows*altura_cel + (rows-1)*pad
    fig2.update_layout(title='Visão Frontal', xaxis=dict(range=[0,total_w]), yaxis=dict(range=[0,total_h],scaleanchor='x'), height=500)
    st.plotly_chart(fig2, use_container_width=True)
