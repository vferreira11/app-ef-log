#!/usr/bin/env python3
import json
import argparse
import numpy as np
from math import ceil
from numba import cuda
from distribuir_milp import Cuboid

# -----------------------------------------------------------------------------
# CUDA kernel: avalia o “fitness” de cada indivíduo na população.
# fitness = número de blocos válidos (dentro do contêiner, sem colisão simplificada)
# -----------------------------------------------------------------------------
@cuda.jit
def fitness_kernel(sols, block_dims, dx, dy, dz, fitness):
    pop_size, N, _ = sols.shape
    idx = cuda.grid(1)
    if idx < pop_size:
        count = 0
        for t in range(N):
            x = sols[idx, t, 0]
            y = sols[idx, t, 1]
            z = sols[idx, t, 2]
            o = int(sols[idx, t, 3])
            lx = block_dims[o, 0]
            ly = block_dims[o, 1]
            lz = block_dims[o, 2]
            # testa se cabe no container
            if 0 <= x <= dx - lx and 0 <= y <= dy - ly and 0 <= z <= dz - lz:
                count += 1
        fitness[idx] = count

# -----------------------------------------------------------------------------
# Função que gera população aleatória, dispara o kernel e retorna a melhor sol.
# -----------------------------------------------------------------------------
def gpu_heuristic_pack(dx, dy, dz, block_dims, pop_size=1024, N=200):
    # gera população (pop_size x N x 4): x, y, z, orientação
    sols = np.empty((pop_size, N, 4), dtype=np.int32)
    for i in range(pop_size):
        sols[i, :, 0] = np.random.randint(0, dx, size=N)
        sols[i, :, 1] = np.random.randint(0, dy, size=N)
        sols[i, :, 2] = np.random.randint(0, dz, size=N)
        sols[i, :, 3] = np.random.randint(0, len(block_dims), size=N)

    # copia para GPU
    d_sols       = cuda.to_device(sols)
    d_block_dims = cuda.to_device(np.array(block_dims, dtype=np.int32))
    d_fitness    = cuda.device_array(pop_size, dtype=np.int32)

    # configura kernel
    threads = 256
    blocks  = ceil(pop_size / threads)
    fitness_kernel[blocks, threads](d_sols, d_block_dims, dx, dy, dz, d_fitness)
    cuda.synchronize()

    # recupera resultados
    host_fitness = d_fitness.copy_to_host()
    best_idx     = int(np.argmax(host_fitness))
    best_sol     = sols[best_idx]

    # retorna lista de tuplas (x, y, z, o)
    return [(int(x), int(y), int(z), int(o)) for x, y, z, o in best_sol]

# -----------------------------------------------------------------------------
# Script principal
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Packing heurístico paralelo na GPU (Numba/CUDA)")
    parser.add_argument('-a', '--dx',       type=int,   required=True, help='Dimensão X do contêiner')
    parser.add_argument('-l', '--dy',       type=int,   required=True, help='Dimensão Y do contêiner')
    parser.add_argument('-p', '--dz',       type=int,   required=True, help='Dimensão Z do contêiner')
    parser.add_argument('--pop-size',       type=int,   default=1024,    help='Tamanho da população')
    parser.add_argument('--num-blocks',     type=int,   default=200,     help='Número de blocos por indivíduo')
    parser.add_argument('-j', '--json',     action='store_true',        help='Imprime saída JSON no stdout')
    parser.add_argument('-o', '--output',   type=str,                   help='Salva saída JSON em arquivo')
    parser.add_argument('--save-plot',      action='store_true',        help='Salva plot estático via matplotlib')
    parser.add_argument('--plot-file',      type=str,   default='gpu_solution.png', help='Caminho do PNG de saída')
    args = parser.parse_args()

    dx, dy, dz = args.dx, args.dy, args.dz
    # orientações possíveis do bloco
    block_dims = [(1,1,2), (2,1,1), (1,2,1)]

    # roda heurística na GPU
    placements = gpu_heuristic_pack(dx, dy, dz, block_dims,
                                    pop_size=args.pop_size,
                                    N=args.num_blocks)

    result = {
        'method': 'gpu_numba',
        'container': {'dx': dx, 'dy': dy, 'dz': dz, 'block_orientations': block_dims},
        'count': len(placements),
        'placements': [{'x': x, 'y': y, 'z': z, 'orientation': o}
                       for (x, y, z, o) in placements]
    }

    # saída JSON em arquivo
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"JSON salvo em {args.output}")

    # imprime JSON
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # feedback simples
    if not args.json and not args.output:
        print(f"GPU Heurística: {result['count']} blocos em {dx}×{dy}×{dz}")

    # opcional: salva plot via matplotlib
    if args.save_plot:
        cube = Cuboid(dx, dy, dz)
        cube.plot_solution(placements, block_dims, output_path=args.plot_file)

if __name__ == '__main__':
    main()
