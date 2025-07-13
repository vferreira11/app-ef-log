import numpy as np
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, PULP_CBC_CMD

class Cuboid:
    def __init__(self, dx: int, dy: int, dz: int):
        self.dx, self.dy, self.dz = dx, dy, dz

    def _get_vertices(self, origin, lx, ly, lz):
        x0, y0, z0 = origin
        return [
            (x0,     y0,     z0),
            (x0+lx,  y0,     z0),
            (x0+lx,  y0+ly,  z0),
            (x0,     y0+ly,  z0),
            (x0,     y0,     z0+lz),
            (x0+lx,  y0,     z0+lz),
            (x0+lx,  y0+ly,  z0+lz),
            (x0,     y0+ly,  z0+lz),
        ]

    def plot_solution(self, placements, block_dims, output_path="solution.png"):
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        all_x, all_y, all_z = [], [], []

        # desenha cubo contêiner
        verts = self._get_vertices((0,0,0), self.dx, self.dy, self.dz)
        faces = [
            [verts[i] for i in [0,1,2,3]],
            [verts[i] for i in [4,5,6,7]],
            [verts[i] for i in [0,1,5,4]],
            [verts[i] for i in [2,3,7,6]],
            [verts[i] for i in [1,2,6,5]],
            [verts[i] for i in [4,7,3,0]],
        ]
        ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

        # desenha blocos
        for (x, y, z, o) in placements:
            lx, ly, lz = block_dims[o]
            verts = self._get_vertices((x,y,z), lx, ly, lz)
            faces = [
                [verts[i] for i in [0,1,2,3]],
                [verts[i] for i in [4,5,6,7]],
                [verts[i] for i in [0,1,5,4]],
                [verts[i] for i in [2,3,7,6]],
                [verts[i] for i in [1,2,6,5]],
                [verts[i] for i in [4,7,3,0]],
            ]
            ax.add_collection3d(Poly3DCollection(faces, linewidths=0.5, edgecolors='k', alpha=0.75))

            all_x += [x, x+lx]
            all_y += [y, y+ly]
            all_z += [z, z+lz]

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_xlim([0, self.dx])
        ax.set_ylim([0, self.dy])
        ax.set_zlim([0, self.dz])
        ax.set_box_aspect([1,1,1])
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        print(f"Solution plot saved as: {output_path}")

def solve_packing(dx, dy, dz, block_dims):
    prob = LpProblem("Packing", LpMaximize)
    b = {}

    # variáveis binárias para cada posição e orientação
    for o, (lx, ly, lz) in enumerate(block_dims):
        for i in range(dx - lx + 1):
            for j in range(dy - ly + 1):
                for k in range(dz - lz + 1):
                    b[(i, j, k, o)] = LpVariable(f"b_{i}_{j}_{k}_{o}", cat=LpBinary)

    # função objetivo: maximizar número de blocos
    prob += lpSum(b.values())

    # restrição de não sobreposição
    for x in range(dx):
        for y in range(dy):
            for z in range(dz):
                cov = []
                for o, (lx, ly, lz) in enumerate(block_dims):
                    for i in range(max(0, x - lx + 1), min(x + 1, dx - lx + 1)):
                        for j in range(max(0, y - ly + 1), min(y + 1, dy - ly + 1)):
                            for k in range(max(0, z - lz + 1), min(z + 1, dz - lz + 1)):
                                if i <= x < i + lx and j <= y < j + ly and k <= z < k + lz:
                                    cov.append(b[(i, j, k, o)])
                prob += lpSum(cov) <= 1

    # resolve com time‐limit de 300s, gap 1% e 4 threads
    solver = PULP_CBC_CMD(
        timeLimit=300,    # para após 300s e retorna a melhor solução
        gapRel=0.01,      # aceita até 1% de gap de optimalidade
        threads=4,        # usa 4 núcleos em paralelo
        msg=True          # exibe progresso
    )
    prob.solve(solver)

    # extrai colocações
    return [(i, j, k, o) for (i, j, k, o), var in b.items() if var.value() == 1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack 1×1×2 blocks into a cuboid.")
    parser.add_argument('-a', '--dx', type=int, default=3, help='Tamanho da aresta X')
    parser.add_argument('-l', '--dy', type=int, default=4, help='Tamanho da aresta Y')
    parser.add_argument('-p', '--dz', type=int, default=5, help='Tamanho da aresta Z')
    args = parser.parse_args()

    dx, dy, dz = args.dx, args.dy, args.dz
    orientations = [(1,1,2), (2,1,1), (1,2,1)]
    placements = solve_packing(dx, dy, dz, orientations)
    print(f"Máximo de blocos 1×1×2 em {dx}×{dy}×{dz}: {len(placements)}")

    cubo = Cuboid(dx, dy, dz)
    cubo.plot_solution(
        placements,
        orientations,
        output_path="optimal_solution.png"
    )
