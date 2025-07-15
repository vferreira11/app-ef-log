import json
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

    def _swap_axes(self, vertex):
        x, y, z = vertex
        return (x, z, y)

    def plot_solution(self, placements, block_dims, output_path="solution.png"):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # Desenha contêiner com eixos trocados
        faces = [
            [(0,0,0), (self.dx,0,0), (self.dx,self.dy,0), (0,self.dy,0)],
            [(0,0,self.dz), (self.dx,0,self.dz), (self.dx,self.dy,self.dz), (0,self.dy,self.dz)],
            [(0,0,0), (self.dx,0,0), (self.dx,0,self.dz), (0,0,self.dz)],
            [(0,self.dy,0), (self.dx,self.dy,0), (self.dx,self.dy,self.dz), (0,self.dy,self.dz)],
            [(0,0,0), (0,self.dy,0), (0,self.dy,self.dz), (0,0,self.dz)],
            [(self.dx,0,0), (self.dx,self.dy,0), (self.dx,self.dy,self.dz), (self.dx,0,self.dz)],
        ]
        faces = [[self._swap_axes(v) for v in face] for face in faces]
        ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', edgecolors='red', linewidths=1, alpha=0.1))

        # Imprime placements para debug
        print("Placements (x, y, z, orientation):", placements)

        # Desenha blocos sólidos
        for x, y, z, o in placements:
            lx, ly, lz = block_dims[o]
            verts = self._get_vertices((x, y, z), lx, ly, lz)
            faces_blk = [
                [verts[i] for i in [0,1,2,3]],
                [verts[i] for i in [4,5,6,7]],
                [verts[i] for i in [0,1,5,4]],
                [verts[i] for i in [2,3,7,6]],
                [verts[i] for i in [1,2,6,5]],
                [verts[i] for i in [4,7,3,0]],
            ]
            faces_blk = [[self._swap_axes(v) for v in face] for face in faces_blk]
            poly = Poly3DCollection(faces_blk, facecolors='orange', edgecolors='k', linewidths=0.5, alpha=0.8)
            ax.add_collection3d(poly)

        # Ajuste de eixos
        ax.set_xlim(0, self.dx)
        ax.set_ylim(0, self.dz)
        ax.set_zlim(0, self.dy)
        ax.set_box_aspect((self.dx, self.dz, self.dy))
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_zlabel('Y')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()


def solve_packing(dx, dy, dz, orientations, time_limit=None, mip_gap=None, initial_solution=None):
    prob = LpProblem('3D_Packing', LpMaximize)
    b_vars = {}
    # Define variáveis e warm start
    for i in range(dx):
        for j in range(dy):
            for k in range(dz):
                for o, (lx, ly, lz) in enumerate(orientations):
                    if i + lx <= dx and j + ly <= dy and k + lz <= dz:
                        var = LpVariable(f'b_{i}_{j}_{k}_{o}', cat=LpBinary)
                        b_vars[(i,j,k,o)] = var
                        if initial_solution and (i,j,k,o) in initial_solution:
                            var.start = 1

    # Objetivo
    prob += lpSum(b_vars.values())

    # Restrição não sobreposição
    for i in range(dx):
        for j in range(dy):
            for k in range(dz):
                prob += lpSum(
                    b_vars[(x,y,z,o)]
                    for (x,y,z,o) in b_vars
                    if x <= i < x + orientations[o][0]
                    and y <= j < y + orientations[o][1]
                    and z <= k < z + orientations[o][2]
                ) <= 1

    # Configura solver
    solver_params = {}
    if time_limit is not None:
        solver_params['timeLimit'] = time_limit
    if mip_gap is not None:
        solver_params['gapRel'] = mip_gap
    solver = PULP_CBC_CMD(msg=False, **solver_params)
    prob.solve(solver)

    # Extrai solução
    placements = [key for key, var in b_vars.items() if var.value() == 1]
    return placements

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--dx', type=int, default=5)
    parser.add_argument('-l', '--dy', type=int, default=5)
    parser.add_argument('-p', '--dz', type=int, default=5)
    parser.add_argument('--time-limit', type=float, default=None)
    parser.add_argument('--mip-gap',    type=float, default=None)
    parser.add_argument('--initial-solution', type=str, default=None)
    args = parser.parse_args()

    orientations = [(1,1,2), (2,1,1), (1,2,1)]
    initial = None
    if args.initial_solution:
        with open(args.initial_solution, encoding='utf-8') as f:
            data = json.load(f)
            initial = set((p['x'], p['y'], p['z'], p['orientation']) for p in data.get('placements', []))

    placements = solve_packing(
        args.dx, args.dy, args.dz,
        orientations,
        time_limit=args.time_limit,
        mip_gap=args.mip_gap,
        initial_solution=initial
    )
    print(f"Máximo de blocos 1×1×2 em {args.dx}×{args.dy}×{args.dz}: {len(placements)}")
    print("Placements (x, y, z, orientation):", placements)

    cubo = Cuboid(args.dx, args.dy, args.dz)
    cubo.plot_solution(placements, orientations, output_path="optimal_solution.png")
import os