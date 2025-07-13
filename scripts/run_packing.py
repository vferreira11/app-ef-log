import json
import argparse
from distribuir_milp import solve_packing, Cuboid
import plotly.graph_objects as go


def interactive_plotly(dx, dy, dz, placements, block_dims):
    """
    Plota interativamente usando Plotly WebGL para rotação e zoom suaves.
    """
    fig = go.Figure()

    # Desenha contêiner como um paralelepípedo transparente
    cd = Cuboid(dx, dy, dz)
    verts = cd._get_vertices((0, 0, 0), dx, dy, dz)
    x, y, z = zip(*verts)
    # faces RGB: transparent grey
    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z,
        i=[0, 0, 0, 1, 2, 4],
        j=[1, 2, 3, 5, 3, 5],
        k=[3, 3, 1, 4, 6, 6],
        opacity=0.1,
        color='lightgrey',
        name='Container'
    ))

    # Desenha blocos
    for idx, (x0, y0, z0, o) in enumerate(placements):
        lx, ly, lz = block_dims[o]
        verts = Cuboid(dx, dy, dz)._get_vertices((x0, y0, z0), lx, ly, lz)
        x, y, z = zip(*verts)
        # faces padrão de um cubo
        i = [0,0,0,1,2,4]
        j = [1,2,3,5,3,5]
        k = [3,3,1,4,6,6]
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            opacity=0.8,
            color='blue',
            name=f'Block {idx}',
            showlegend=False
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X', range=[0, dx]),
            yaxis=dict(title='Y', range=[0, dy]),
            zaxis=dict(title='Z', range=[0, dz]),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        title=f"Packing {len(placements)} blocks in {dx}×{dy}×{dz}"
    )
    fig.show()


def main():
    parser = argparse.ArgumentParser(description="Run MILP packing and show text + interactive 3D plot with Plotly.")
    parser.add_argument('-a', '--dx', type=int, required=True, help='Contêiner dimensão X')
    parser.add_argument('-l', '--dy', type=int, required=True, help='Contêiner dimensão Y')
    parser.add_argument('-p', '--dz', type=int, required=True, help='Contêiner dimensão Z')
    parser.add_argument('-o', '--orientations', nargs='+', metavar='ORIENT', type=int,
                        help='Orientações de blocos como triplets, ex: 1 1 2 2 1 1 1 2 1',
                        default=[1,1,2, 2,1,1, 1,2,1])
    parser.add_argument('-j', '--json', action='store_true', help='Imprime resultados em JSON')
    args = parser.parse_args()

    dx, dy, dz = args.dx, args.dy, args.dz
    ori_vals = args.orientations
    if len(ori_vals) % 3 != 0:
        parser.error('O número de valores em --orientations deve ser múltiplo de 3.')
    block_dims = [(ori_vals[i], ori_vals[i+1], ori_vals[i+2]) for i in range(0, len(ori_vals), 3)]

    # Resolve empacotamento
    placements = solve_packing(dx, dy, dz, block_dims)
    count = len(placements)

    # Saída textual
    if args.json:
        result = {
            'container': {'dx': dx, 'dy': dy, 'dz': dz},
            'block_orientations': block_dims,
            'placements': [{'x': i, 'y': j, 'z': k, 'orientation_index': o} for (i,j,k,o) in placements],
            'count': count
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Empacotou {count} blocos no contêiner {dx}x{dy}x{dz}.")

    # Plot interativo suave
    interactive_plotly(dx, dy, dz, placements, block_dims)


if __name__ == '__main__':
    main()
