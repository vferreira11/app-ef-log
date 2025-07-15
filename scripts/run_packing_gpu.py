#!/usr/bin/env python3
import json
import argparse
import numpy as np
import random
from math import ceil
from numba import cuda
from distribuir_milp import Cuboid

# -----------------------------------------------------------------------------
def filter_collisions(placements, block_dims, dx, dy, dz):
    occupancy = np.zeros((dx, dy, dz), dtype=bool)
    filtered = []
    for x, y, z, o in placements:
        lx, ly, lz = block_dims[o]
        if x+lx <= dx and y+ly <= dy and z+lz <= dz:
            region = occupancy[x:x+lx, y:y+ly, z:z+lz]
            if not region.any():
                filtered.append((x,y,z,o))
                occupancy[x:x+lx, y:y+ly, z:z+lz] = True
    return filtered

@cuda.jit
def fitness_kernel(sols, block_dims, dx, dy, dz, fitness):
    pop_size, N, _ = sols.shape
    idx = cuda.grid(1)
    if idx < pop_size:
        count = 0
        for t in range(N):
            x = sols[idx,t,0]; y = sols[idx,t,1]; z = sols[idx,t,2]
            o = int(sols[idx,t,3])
            lx = block_dims[o,0]; ly = block_dims[o,1]; lz = block_dims[o,2]
            if 0 <= x <= dx-lx and 0 <= y <= dy-ly and 0 <= z <= dz-lz:
                count += 1
        fitness[idx] = count

def gpu_heuristic_pack(dx, dy, dz, block_dims, pop_size, N):
    sols = np.empty((pop_size, N, 4), dtype=np.int32)
    for i in range(pop_size):
        sols[i,:,0] = np.random.randint(0, dx, size=N)
        sols[i,:,1] = np.random.randint(0, dy, size=N)
        sols[i,:,2] = np.random.randint(0, dz, size=N)
        sols[i,:,3] = np.random.randint(0, len(block_dims), size=N)

    d_sols       = cuda.to_device(sols)
    d_block_dims = cuda.to_device(np.array(block_dims, dtype=np.int32))
    fitness_arr  = np.zeros(pop_size, dtype=np.int32)
    d_fitness    = cuda.to_device(fitness_arr)

    threads_per_block = 128
    blocks_per_grid   = ceil(pop_size / threads_per_block)
    fitness_kernel[blocks_per_grid, threads_per_block](
        d_sols, d_block_dims, dx, dy, dz, d_fitness
    )

    fitness_arr = d_fitness.copy_to_host()
    best_idx    = int(np.argmax(fitness_arr))
    best_sol    = sols[best_idx]
    placements  = [
        (int(best_sol[t,0]), int(best_sol[t,1]), int(best_sol[t,2]), int(best_sol[t,3]))
        for t in range(N)
    ]
    return placements

def greedy_pack(dx, dy, dz, block_dims):
    coords = []
    for o,(lx,ly,lz) in enumerate(block_dims):
        for x in range(dx-lx+1):
            for y in range(dy-ly+1):
                for z in range(dz-lz+1):
                    coords.append((x,y,z,o))
    random.shuffle(coords)
    occupancy = np.zeros((dx, dy, dz), dtype=bool)
    placements = []
    for x,y,z,o in coords:
        lx,ly,lz = block_dims[o]
        region = occupancy[x:x+lx, y:y+ly, z:z+lz]
        if not region.any():
            placements.append((x,y,z,o))
            occupancy[x:x+lx, y:y+ly, z:z+lz] = True
    return placements

# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Packing GPU com opção greedy")
    parser.add_argument('-a','--dx',       type=int, required=True)
    parser.add_argument('-l','--dy',       type=int, required=True)
    parser.add_argument('-p','--dz',       type=int, required=True)
    parser.add_argument('--pop-size',      type=int, default=1024)
    parser.add_argument('--num-blocks',    type=int, default=None,
                        help='Número fixo de blocos; ou use --auto-blocks')
    parser.add_argument('--auto-blocks',   action='store_true',
                        help='Define num_blocks = floor(dx*dy*dz/2)')
    parser.add_argument('--greedy',        action='store_true',
                        help='Usa método greedy first‑fit')
    parser.add_argument('-j','--json',     action='store_true')
    parser.add_argument('-o','--output',   type=str)
    parser.add_argument('--save-plot',     action='store_true')
    parser.add_argument('--plot-file',     type=str, default='gpu_solution.png')
    args = parser.parse_args()

    dx,dy,dz = args.dx, args.dy, args.dz
    block_dims = [(1,1,2),(2,1,1),(1,2,1)]

    if args.greedy:
        placements = greedy_pack(dx, dy, dz, block_dims)
    else:
        if args.auto_blocks:
            N = (dx*dy*dz)//2
        elif args.num_blocks is not None:
            N = args.num_blocks
        else:
            parser.error("Use --num-blocks ou --auto-blocks ou --greedy")
        placements = gpu_heuristic_pack(dx, dy, dz, block_dims,
                                        pop_size=args.pop_size, N=N)
        placements = filter_collisions(placements, block_dims, dx, dy, dz)

    result = {
        'method': 'greedy' if args.greedy else 'gpu_numba',
        'container': {'dx':dx,'dy':dy,'dz':dz,'block_orientations':block_dims},
        'count': len(placements),
        'placements': [{'x':x,'y':y,'z':z,'orientation':o} for x,y,z,o in placements]
    }

    if args.output:
        with open(args.output,'w',encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"JSON salvo em {args.output}")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.save_plot:
        cube = Cuboid(dx, dy, dz)
        cube.plot_solution(placements, block_dims, output_path=args.plot_file)

if __name__=='__main__':
    main()
