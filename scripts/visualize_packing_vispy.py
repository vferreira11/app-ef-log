import json
import argparse
from vispy import scene, app
from vispy.scene import visuals

def load_results(json_file):
    with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    start = content.find('{')
    end = content.rfind('}') + 1
    if start == -1 or end == -1:
        raise ValueError(f"Não foi encontrado JSON válido em {json_file}")
    data = json.loads(content[start:end])
    return data.get('placements', []), data.get('container', {})

def visualize(dx, dy, dz, placements, block_dims):
    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='white')
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(fov=45, azimuth=30, elevation=30)

    # Desenha contêiner
    container = visuals.Box(width=dx, height=dz, depth=dy,
                            color=(0.8,0.8,0.8,0.2), edge_color='black', parent=view.scene)
    trc = scene.transforms.MatrixTransform()
    trc.rotate(-90, (1,0,0))
    trc.translate((dx/2, dy/2, dz/2))
    container.transform = trc

    # Desenha blocos
    for p in placements:
        # suporte a formatos: dict ou tuple
        if isinstance(p, dict):
            i, j, k, o = p['x'], p['y'], p['z'], p['orientation']
        else:
            i, j, k, o = p
        lx, ly, lz = block_dims[o]
        block = visuals.Box(width=lx, height=lz, depth=ly,
                             color=(0.2,0.5,0.8,0.9), edge_color='black', parent=view.scene)
        tr = scene.transforms.MatrixTransform()
        tr.rotate(-90, (1,0,0))
        tr.translate((i + lx/2, j + ly/2, k + lz/2))
        block.transform = tr

    view.camera.set_range(x=(0,dx), y=(0,dy), z=(0,dz))
    canvas.show()
    app.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Visualização 3D acelerada por GPU com Vispy'
    )
    parser.add_argument('-j', '--json', type=str, required=True, help='Arquivo JSON com resultados')
    parser.add_argument('-a', '--dx', type=int, help='Dimensão X do contêiner')
    parser.add_argument('-l', '--dy', type=int, help='Dimensão Y do contêiner')
    parser.add_argument('-p', '--dz', type=int, help='Dimensão Z do contêiner')
    args = parser.parse_args()

    placements, container = load_results(args.json)

    dx = container.get('dx') if container.get('dx') is not None else args.dx
    dy = container.get('dy') if container.get('dy') is not None else args.dy
    dz = container.get('dz') if container.get('dz') is not None else args.dz
    if dx is None or dy is None or dz is None:
        parser.error('Dimensões do contêiner devem estar no JSON ou ser passadas via -a, -l, -p')

    block_dims = container.get('block_orientations', [(1,1,2),(2,1,1),(1,2,1)])

    visualize(dx, dy, dz, placements, block_dims)
