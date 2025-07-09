import math
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Patch
from typing import List, Tuple
from dataclasses import dataclass
import sqlite3
import os
import argparse

@dataclass
class Produto:
    largura: int
    profundidade: int
    altura: int

@dataclass
class Celula:
    largura: int
    profundidade: int
    altura: int

# Dimensões da célula (em mm)
dimensoes_celula = Celula(largura=1760, profundidade=400, altura=850)

def allocate_grouped_cells(
    produtos_info: List[Tuple[str, Produto, str]],
    demands: List[int],
    n_cells: int
) -> List[List[Tuple[str, int, int, int]]]:
    cel = dimensoes_celula
    rem_width = [cel.largura] * n_cells
    rem_dem = demands.copy()
    cells_alloc = [[None] * len(produtos_info) for _ in range(n_cells)]

    for idx, (label, prod, _) in enumerate(produtos_info):
        rows = cel.profundidade // prod.profundidade
        layers = cel.altura // prod.altura
        cap_per_col = rows * layers
        total = demands[idx]
        for c in range(n_cells):
            demand = rem_dem[idx]
            if demand <= 0 or cap_per_col == 0:
                alloc = 0
            else:
                max_cols = rem_width[c] // prod.largura
                needed_cols = min(math.ceil(demand / cap_per_col), max_cols)
                alloc = min(demand, needed_cols * cap_per_col)
                rem_width[c] -= needed_cols * prod.largura
                rem_dem[idx] -= alloc
            cells_alloc[c][idx] = (label, total, alloc, total - alloc)

    return cells_alloc

def plot_allocation_3d(
    allocation: List[List[Tuple[str, int, int, int]]],
    produtos_info: List[Tuple[str, Produto, str]],
    n_cells: int
):
    fig = plt.figure(figsize=(6 * n_cells, 6))
    cel = dimensoes_celula
    for i in range(n_cells):
        ax = fig.add_subplot(1, n_cells, i+1, projection='3d')
        ax.set_box_aspect((cel.largura, cel.profundidade, cel.altura))
        ax.set_xlim(0, cel.largura)
        ax.set_ylim(0, cel.profundidade)
        ax.set_zlim(0, cel.altura)
        ax.set_title(f"Célula {i+1}")
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        x_offset = 0
        handles = []
        for j, (label, total, alloc, falt) in enumerate(allocation[i]):
            prod = produtos_info[j][1]
            color = produtos_info[j][2]
            if alloc <= 0:
                continue
            rows = cel.profundidade // prod.profundidade
            layers = cel.altura // prod.altura
            cap_per_col = rows * layers
            needed_cols = math.ceil(alloc / cap_per_col) if cap_per_col else 0
            count = 0
            handles.append(Patch(facecolor=color, edgecolor='black', label=label))
            for layer in range(layers):
                z = layer * prod.altura
                for col in range(needed_cols):
                    x = x_offset + col * prod.largura
                    for row in range(rows):
                        if count >= alloc:
                            break
                        y = row * prod.profundidade
                        ax.bar3d(
                            x, y, z,
                            prod.largura,
                            prod.profundidade,
                            prod.altura,
                            color=color,
                            edgecolor='black',
                            linewidth=0.5,
                            shade=True
                        )
                        count += 1
                    if count >= alloc:
                        break
                if count >= alloc:
                    break
            x_offset += needed_cols * prod.largura
        ax.legend(handles=handles, loc='upper right')

    plt.tight_layout()
    plt.show()

def show_allocation_table(
    allocation: List[List[Tuple[str, int, int, int]]]
):
    rows = []
    for i, cell in enumerate(allocation, start=1):
        for label, total, alloc, falt in cell:
            rows.append({
                'Célula': f'Célula {i}',
                'Produto': label,
                'Demanda': total,
                'Alocado': alloc,
                'Faltam': falt
            })
    df = pd.DataFrame(rows)
    pivot = df.pivot(index='Produto', columns='Célula', values=['Demanda','Alocado','Faltam'])
    print(pivot)

def main():
    parser = argparse.ArgumentParser(
        description="Aloca produtos em células usando dados do SQLite."
    )
    parser.add_argument(
        "--db", type=str,
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "produtos.db")
        ),
        help="Caminho para o arquivo SQLite."
    )
    parser.add_argument(
        "-c", "--cells",
        type=int, default=3,
        help="Número de células disponíveis."
    )
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()

    colors = [
        'tab:blue','tab:orange','tab:green','tab:red',
        'tab:purple','tab:brown','tab:pink','tab:gray',
        'tab:olive','tab:cyan'
    ]
    produtos_info: List[Tuple[str, Produto, str]] = []
    demands: List[int] = []
    for idx, row in df.iterrows():
        produtos_info.append((
            row['nome_produto'],  # agora usa o nome do produto
            Produto(
                largura=int(row['largura_mm']),
                profundidade=int(row['profundidade_mm']),
                altura=int(row['altura_mm'])
            ),
            colors[idx % len(colors)]
        ))
        demands.append(int(row['qtd_vendida_30d']))

    allocation = allocate_grouped_cells(produtos_info, demands, args.cells)
    plot_allocation_3d(allocation, produtos_info, args.cells)
    show_allocation_table(allocation)

if __name__ == '__main__':
    main()
