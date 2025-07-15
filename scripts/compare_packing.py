#!/usr/bin/env python3
import subprocess, json, time, re, os, sys, argparse, csv, shutil
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Ensure working directory
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

def run_gpu(dx, dy, dz, pop_size, num_blocks, json_path, plot_path, greedy):
    cmd = [sys.executable, "run_packing_gpu.py",
           "-a", str(dx), "-l", str(dy), "-p", str(dz),
           "--pop-size", str(pop_size)]
    if greedy:
        cmd.append("--greedy")
    else:
        cmd += ["--num-blocks", str(num_blocks)]
    cmd += ["--json", "--output", json_path,
            "--save-plot", "--plot-file", plot_path]
    start = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    if proc.returncode != 0:
        raise RuntimeError(f"Erro GPU: {proc.stderr}")
    data = json.load(open(json_path, encoding='utf-8'))
    return data['count'], elapsed


def run_milp(dx, dy, dz, time_limit, gap, initial_json, plot_path, timeout):
    cmd = [sys.executable, "distribuir_milp.py",
           "-a", str(dx), "-l", str(dy), "-p", str(dz)]
    if initial_json:
        cmd += ["--initial-solution", initial_json]
    if time_limit:
        cmd += ["--time-limit", str(time_limit)]
    if gap:
        cmd += ["--mip-gap", str(gap)]
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        return None, timeout, True
    elapsed = time.time() - start
    if proc.returncode != 0:
        raise RuntimeError(f"Erro MILP: {proc.stderr}")
    m = re.search(r":\s*(\d+)", proc.stdout)
    fitness = int(m.group(1)) if m else None
    if os.path.exists("optimal_solution.png"):
        os.replace("optimal_solution.png", plot_path)
    return fitness, elapsed, timed_out


def combine_images(paths, titles, out_path):
    fig, axes = plt.subplots(1, len(paths), figsize=(6*len(paths),6))
    for ax, (img_path, title) in zip(axes, zip(paths, titles)):
        img = mpimg.imread(img_path)
        ax.imshow(img)
        ax.set_title(title)
        ax.axis('off')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Stress test hybrid Greedy→MILP on multiple container sizes")
    parser.add_argument("--sizes", type=str, required=True,
                        help="Comma-separated list of container sizes, e.g., 20,25,30,35")
    parser.add_argument("--N", type=int, default=200, help="Number of blocks for GPU heuristic")
    parser.add_argument("--pop", type=int, default=2000, help="GPU population size")
    parser.add_argument("--time-limit", type=int, default=600, help="Max MILP solve time (s)")
    parser.add_argument("--gap", type=float, default=0.001, help="MILP relative gap")
    parser.add_argument("--milp-timeout", type=int, default=600,
                        help="Timeout for MILP before fallback (s)")
    parser.add_argument("--greedy", action='store_true',
                        help="Use greedy first-fit warm start instead of random GPU heuristic")
    args = parser.parse_args()

    sizes = [int(s) for s in args.sizes.split(",")]
    N, pop = args.N, args.pop
    tl, gap = args.time_limit, args.gap
    timeout, greedy = args.milp_timeout, args.greedy

    log_file = "stress_all.csv"
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size","method","fitness","tempo_s","timeout"])

        for size in sizes:
            print(f"\n=== Stress {size}×{size}×{size} ===")
            dx = dy = dz = size
            gpu_json = f"gpu_{size}.json"
            gpu_plot = f"gpu_{size}.png"
            gpu_count, gpu_time = run_gpu(dx, dy, dz, pop, N, gpu_json, gpu_plot, greedy)
            method_gpu = "greedy" if greedy else "gpu"
            print(f"{method_gpu.upper():<7} → {gpu_count} blocks in {gpu_time:.2f}s")
            writer.writerow([size, method_gpu, gpu_count, f"{gpu_time:.2f}", False])

            milp_plot = f"milp_{size}.png"
            milp_count, milp_time, milp_to = run_milp(
                dx, dy, dz, tl, gap, gpu_json, milp_plot, timeout)
            if milp_to:
                print(f"MILP   → timed out after {timeout}s, fallback to {method_gpu}")
                final_count, final_time = gpu_count, gpu_time
                final_plot = f"final_{size}.png"
                shutil.copy(gpu_plot, final_plot)
                method = f"{method_gpu}_fallback"
            else:
                print(f"MILP   → {milp_count} blocks in {milp_time:.2f}s")
                final_count, final_time = milp_count, milp_time
                final_plot = f"final_{size}.png"
                os.replace(milp_plot, final_plot)
                method = "milp"
            writer.writerow([size, method, final_count, f"{final_time:.2f}", milp_to])

            comparison = f"comparison_{size}.png"
            combine_images([gpu_plot, final_plot], [method_gpu.upper(), "Final"], comparison)

    print(f"\nStress hybrid completed. Log: {log_file}")
    print("Comparison images: comparison_<size>.png")

if __name__=='__main__':
    main()
