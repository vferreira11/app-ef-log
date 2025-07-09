import plotly.graph_objects as go

# Dimensões do cubo
largura_cel, profundidade_cel, altura_cel = 3, 4, 5

# Listas de caixas (vazias para este exemplo)
placed_A = []
placed_B = []
cor_A = 'blue'
cor_B = 'red'

# Função genérica para desenhar uma caixa (prisma retangular) como Mesh3d
def draw_mesh(fig, box, color, opacity, show_surface, name):
    x0, y0, z0, dx, dy, dz = box
    # 8 vértices
    xs = [x0,     x0+dx, x0+dx, x0,     x0,     x0+dx, x0+dx, x0]
    ys = [y0,     y0,    y0+dy, y0+dy, y0,     y0,    y0+dy, y0+dy]
    zs = [z0,     z0,    z0,    z0,    z0+dz,  z0+dz, z0+dz, z0+dz]
    # Faces definidas por índices de vértice
    faces = [
        [0,1,2,3], [4,5,6,7],      # base inferior e superior
        [0,1,5,4], [2,3,7,6],      # laterais
        [1,2,6,5], [0,3,7,4]
    ]
    for face in faces:
        fig.add_trace(go.Mesh3d(
            x=[xs[i] for i in face],
            y=[ys[i] for i in face],
            z=[zs[i] for i in face],
            color=color,
            opacity=opacity,
            showscale=False,
            name=name,
            showlegend=show_surface
        ))

# Cria figura e desenha eventuais caixas A e B
fig3 = go.Figure()
for i, box in enumerate(placed_A):
    draw_mesh(fig3, box, cor_A, 0.8, i == 0, 'A')
for i, box in enumerate(placed_B):
    draw_mesh(fig3, box, cor_B, 0.8, i == 0, 'B')

# Desenha as arestas do cubo de dimensão 3×4×5
cell = (0, 0, 0, largura_cel, profundidade_cel, altura_cel)
edges = [(0,1),(1,2),(2,3),(3,0),
         (4,5),(5,6),(6,7),(7,4),
         (0,4),(1,5),(2,6),(3,7)]
# Calcula vértices
x0, y0, z0, dx, dy, dz = cell
verts = [
    (x0,     y0,     z0    ), (x0+dx, y0,     z0    ),
    (x0+dx,  y0+dy,  z0    ), (x0,    y0+dy,  z0    ),
    (x0,     y0,     z0+dz ), (x0+dx, y0,     z0+dz ),
    (x0+dx,  y0+dy,  z0+dz ), (x0,    y0+dy,  z0+dz )
]
# Adiciona traços para cada aresta
for a, b in edges:
    fig3.add_trace(go.Scatter3d(
        x=[verts[a][0], verts[b][0]],
        y=[verts[a][1], verts[b][1]],
        z=[verts[a][2], verts[b][2]],
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False
    ))

# Configura layout, proporções reais e câmera com mesmo zoom original
fig3.update_layout(
    scene=dict(
        aspectmode='manual',
        aspectratio=dict(x=largura_cel, y=profundidade_cel, z=altura_cel),
        camera=dict(
            projection=dict(type='perspective'),
            eye=dict(x=12, y=-12, z=12)    # >> distância maior para caber todo o cubo
        ),
        xaxis=dict(title='Largura (mm)'),
        yaxis=dict(title='Profundidade (mm)'),
        zaxis=dict(title='Altura (mm)')
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# Exibe
fig3.show()
