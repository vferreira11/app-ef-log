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
            (x0,     y0+ly,  z0+lz)
        ]

    def plot_solution(self, placements, orientations, output_path="solution.png"):  
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        # define ângulo fixo de visualização
        ax.view_init(elev=20, azim=30)
        ax.grid(False)
        ax.set_axis_off()
        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[4,7,3,0]]
        # desenha wireframe do contêiner
        verts_main = self._get_vertices((0,0,0), self.dx, self.dy, self.dz)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)
        # desenha blocos
        for (i,j,k,o) in placements:
            lx, ly, lz = orientations[o]
            verts = self._get_vertices((i,j,k), lx, ly, lz)
            faces = [[verts[idx] for idx in fi] for fi in faces_idx]
            ax.add_collection3d(Poly3DCollection(
                faces, facecolor='cyan', edgecolor='blue', alpha=0.6
            ))
        # anotação total
        ax.text2D(0.05, 0.95, f"Total blocks: {len(placements)}", transform=ax.transAxes,
                  fontsize=12, verticalalignment='top')
        # limites conforme contêiner
        all_x = [v[0] for v in verts_main]; all_y = [v[1] for v in verts_main]; all_z = [v[2] for v in verts_main]
        ax.set_xlim(min(all_x), max(all_x))
        ax.set_ylim(min(all_y), max(all_y))
        ax.set_zlim(min(all_z), max(all_z))
        ax.set_box_aspect([1,1,1])
        # salva sem show interativo
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        print(f"Solution plot saved as: {output_path}")


def solve_packing(dx, dy, dz, block_dims):
    prob = LpProblem("Packing", LpMaximize)
    b = {}
    # cria variáveis binárias
    for o, (lx, ly, lz) in enumerate(block_dims):
        for i in range(dx - lx + 1):
            for j in range(dy - ly + 1):
                for k in range(dz - lz + 1):
                    b[(i,j,k,o)] = LpVariable(f"b_{i}_{j}_{k}_{o}", cat=LpBinary)
    # objetivo
    prob += lpSum(b.values())
    # restrições de não sobreposição
    for x in range(dx):
        for y in range(dy):
            for z in range(dz):
                cov = []
                for o, (lx, ly, lz) in enumerate(block_dims):
                    for i in range(max(0, x-lx+1), min(x+1, dx-lx+1)):
                        for j in range(max(0, y-ly+1), min(y+1, dy-ly+1)):
                            for k in range(max(0, z-lz+1), min(z+1, dz-lz+1)):
                                if i <= x < i+lx and j <= y < j+ly and k <= z < k+lz:
                                    cov.append(b[(i,j,k,o)])
                prob += lpSum(cov) <= 1
    # resolve
    prob.solve(PULP_CBC_CMD(msg=False))
    # extrai colocações
    return [(i,j,k,o) for (i,j,k,o), var in b.items() if var.value() == 1]

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
