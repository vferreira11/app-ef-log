import numpy as np
import time
from numba import cuda

# CUDA kernel: multiplicação matricial simples
@cuda.jit
def matmul_kernel(a, b, c, N):
    i, j = cuda.grid(2)
    if i < N and j < N:
        tmp = 0.0
        for k in range(N):
            tmp += a[i, k] * b[k, j]
        c[i, j] = tmp

def main():
    # Tamanho da matriz (ajuste pra usar boa parte da VRAM)
    N = 2048

    # Cria matrizes no host
    a = np.random.rand(N, N).astype(np.float32)
    b = np.random.rand(N, N).astype(np.float32)
    c = np.zeros((N, N), dtype=np.float32)

    # Move para a GPU
    d_a = cuda.to_device(a)
    d_b = cuda.to_device(b)
    d_c = cuda.device_array((N, N), dtype=np.float32)

    # Define grid e block
    threads_per_block = (16, 16)
    blocks_per_grid = (
        (N + threads_per_block[0] - 1) // threads_per_block[0],
        (N + threads_per_block[1] - 1) // threads_per_block[1],
    )

    # Warm-up (compila o kernel e aquece a GPU)
    matmul_kernel[blocks_per_grid, threads_per_block](d_a, d_b, d_c, N)
    cuda.synchronize()

    # Mede tempo do kernel
    start = time.time()
    matmul_kernel[blocks_per_grid, threads_per_block](d_a, d_b, d_c, N)
    cuda.synchronize()
    elapsed = time.time() - start

    print(f"Kernel CUDA matmul {N}×{N} levou {elapsed:.2f}s")

if __name__ == "__main__":
    main()
