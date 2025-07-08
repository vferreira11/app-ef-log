
import plotly.graph_objects as go

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

largura, profundidade, altura = 1760, 400, 850
largura_cubo, profundidade_cubo, altura_cubo = 200, 200, 200

nx = largura // largura_cubo
ny = profundidade // profundidade_cubo
nz = altura // altura_cubo

cubos = []
for i in range(int(nx)):
    for j in range(int(ny)):
        for k in range(int(nz)):
            x0 = i * largura_cubo
            y0 = j * profundidade_cubo
            z0 = k * altura_cubo
            cubos += criar_cubo_borda(x0, y0, z0, largura_cubo, profundidade_cubo, altura_cubo)
            cubos.append(criar_cubo_preenchido(x0, y0, z0, largura_cubo, profundidade_cubo, altura_cubo))

cubo_grande = go.Mesh3d(
    x=[0, largura, largura, 0, 0, largura, largura, 0],
    y=[0, 0, profundidade, profundidade, 0, 0, profundidade, profundidade],
    z=[0, 0, 0, 0, altura, altura, altura, altura],
    i=[0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6],
    j=[1, 2, 3, 2, 5, 3, 6, 0, 5, 6, 6, 7],
    k=[2, 3, 0, 5, 6, 6, 7, 4, 6, 7, 7, 4],
    opacity=0.1,
    color='green'
)

fig = go.Figure(data=[cubo_grande] + cubos)
fig.update_layout(
    scene=dict(
        xaxis_title='Largura (mm)',
        yaxis_title='Profundidade (mm)',
        zaxis_title='Altura (mm)',
        aspectmode='data'
    ),
    title='Empacotamento 3D com Caixas (borda + preenchimento)'
)
fig.show()
