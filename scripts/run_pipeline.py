import subprocess
import sys
import os

def run(cmd):
    print(f">>> {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        sys.exit(res.returncode)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("-n", "--n_produtos", type=int, default=30)
    p.add_argument("-c", "--cells",      type=int, default=3)
    args = p.parse_args()

    # 1) gerar CSV
    run(f"python gerar_base_simulada.py --n_produtos {args.n_produtos}")

    # 2) carregar no SQLite
    run("python carregar_para_sqlite.py")

    # 3) alocar (monta caminho absoluto do DB)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(project_root, "data", "produtos.db")
    run(f"python alocacao_nas_celulas.py --db \"{db_path}\" -c {args.cells}")