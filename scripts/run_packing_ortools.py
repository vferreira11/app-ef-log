import json
import argparse
from ortools.sat.python import cp_model
from distribuir_milp import Cuboid

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

def ortools_pack(dx, dy, dz, block_dims, time_limit=300, threads=8):
    model = cp_model.CpModel()
    b = {}
    # Define variável binária para cada orientação e posição possível
    for o, (lx, ly, lz) in enumerate(block_dims):
        for i in range(dx - lx + 1):
            for j in range(dy - ly + 1):
                for k in range(dz - lz + 1):
                    b[o, i, j, k] = model.NewBoolVar(f"b_{o}_{i}_{j}_{k}")

    # Objetivo: maximizar número de blocos
    model.Maximize(sum(b.values()))

    # Restrições de não sobreposição
    for x in range(dx):
        for y in range(dy):
            for z in range(dz):
                cov = []
                for o, (lx, ly, lz) in enumerate(block_dims):
                    for i in range(max(0, x - lx + 1), min(x + 1, dx - lx + 1)):
                        for j in range(max(0, y - ly + 1), min(y + 1, dy - ly + 1)):
                            for k in range(max(0, z - lz + 1), min(z + 1, dz - lz + 1)):
                                if i <= x < i + lx and j <= y < j + ly and k <= z < k + lz:
                                    cov.append(b[o, i, j, k])
                if cov:
                    model.Add(sum(cov) <= 1)

    # Configura o solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = threads
    status = solver.Solve(model)

    placements = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for (o, i, j, k), var in b.items():
            if solver.Value(var):
                placements.append((i, j, k, o))
    return placements

def plot_interactive(dx, dy, dz, placements, block_dims):
    if not PLOTLY_AVAILABLE:
        raise RuntimeError("plotly não está instalado. Instale com 'pip install plotly'.")
    cd = Cuboid(dx, dy, dz)
    fig = go.Figure()
    # Contêiner
    verts = cd._get_vertices((0,0,0), dx, dy, dz)
    x, y, z = zip(*verts)
    fig.add_trace(go.Mesh3d(x=x, y=y, z=z, opacity=0.1, color='lightgrey', name='Container'))
    # Blocos
    for (i, j, k, o) in placements:
        lx, ly, lz = block_dims[o]
        bverts = cd._get_vertices((i, j, k), lx, ly, lz)
        bx, by, bz = zip(*bverts)
        fig.add_trace(go.Mesh3d(x=bx, y=by, z=bz, opacity=0.8, color='blue', showscale=False))
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0,dx], title='X'),
            yaxis=dict(range=[0,dy], title='Y'),
            zaxis=dict(range=[0,dz], title='Z'),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    fig.show()

def main():
    parser = argparse.ArgumentParser(
        description="Packing via OR-Tools CP-SAT with optional JSON output and interactive 3D"
    )
    parser.add_argument('-a', '--dx',       type=int,   required=True,  help='Dimensão X do contêiner')
    parser.add_argument('-l', '--dy',       type=int,   required=True,  help='Dimensão Y do contêiner')
    parser.add_argument('-p', '--dz',       type=int,   required=True,  help='Dimensão Z do contêiner')
    parser.add_argument('-j', '--json',     action='store_true',        help='Imprime JSON no stdout')
    parser.add_argument('-o', '--output',   type=str,                   help='Caminho para salvar JSON em arquivo')
    parser.add_argument('--time-limit',     type=int,   default=300,     help='Tempo máximo de resolução (s)')
    parser.add_argument('--threads',        type=int,   default=8,       help='Número de threads para o solver')
    parser.add_argument('--interactive',    action='store_true',        help='Exibe plot 3D interativo (Plotly)')
    args = parser.parse_args()

    dx, dy, dz = args.dx, args.dy, args.dz
    orientations = [(1,1,2), (2,1,1), (1,2,1)]
    placements = ortools_pack(dx, dy, dz, orientations, args.time_limit, args.threads)

    result = {
        'method': 'ortools',
        'container': {
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'block_orientations': orientations
        },
        'count': len(placements),
        'placements': [
            {'x': i, 'y': j, 'z': k, 'orientation': o}
            for (i,j,k,o) in placements
        ]
    }

    # Salva JSON em arquivo, se solicitado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"JSON salvo em {args.output}")

    # Imprime JSON no stdout, se solicitado
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # Feedback simples
    if not args.json and not args.output:
        print(f"OR-Tools: {result['count']} blocos empacotados em {dx}x{dy}x{dz}.")

    # Plot
    if args.interactive:
        plot_interactive(dx, dy, dz, placements, orientations)
    else:
        cubo = Cuboid(dx, dy, dz)
        cubo.plot_solution(placements, orientations, output_path='ortools_solution.png')

if __name__ == '__main__':
    main()
