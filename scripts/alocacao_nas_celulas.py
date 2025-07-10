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
    # Definir grid de subplots (linhas x colunas)
    n_cols = int(math.ceil(math.sqrt(n_cells)))
    n_rows = int(math.ceil(n_cells / n_cols))
    fig = plt.figure(figsize=(6 * n_cols + 3, 6 * n_rows))  # +3 para legenda lateral
    cel = dimensoes_celula

    # coletar handles/labels globais de produtos
    global_handles = []
    global_labels = []

    for i in range(n_cells):
        ax = fig.add_subplot(n_rows, n_cols, i+1, projection='3d')
        ax.set_box_aspect((cel.largura, cel.profundidade, cel.altura))
        ax.set_xlim(0, cel.largura)
        ax.set_ylim(0, cel.profundidade)
        ax.set_zlim(0, cel.altura)
        ax.set_title(f"Célula {i+1}")
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')

        needed_cols_list = []
        total_width = 0
        for j, (_, total, alloc, _) in enumerate(allocation[i]):
            prod = produtos_info[j][1]
            rows = cel.profundidade // prod.profundidade
            layers = cel.altura // prod.altura
            cap_per_col = rows * layers
            cols = math.ceil(alloc / cap_per_col) if cap_per_col else 0
            needed_cols_list.append(cols)
            total_width += cols * prod.largura

        # Centralizar horizontalmente
        x_offset = (cel.largura - total_width) / 2

        for j, (label, total, alloc, falt) in enumerate(allocation[i]):
            prod = produtos_info[j][1]
            color = produtos_info[j][2]
            cols = needed_cols_list[j]

            # registrar para legenda global, apenas primeira ocorrência
            if label not in global_labels:
                global_handles.append(Patch(facecolor=color, edgecolor='black'))
                global_labels.append(label)

            if alloc <= 0 or cols == 0:
                continue

            rows = cel.profundidade // prod.profundidade
            layers = cel.altura // prod.altura
            count = 0
            y_offset = 0

            for layer in range(layers):
                z = layer * prod.altura
                for col in range(cols):
                    x = x_offset + col * prod.largura
                    for row in range(rows):
                        if count >= alloc:
                            break
                        y = y_offset + row * prod.profundidade
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

            x_offset += cols * prod.largura

    # legenda global à direita
    fig.legend(global_handles, global_labels, title='Produtos',
               loc='upper right', bbox_to_anchor=(1.02, 0.98))

    plt.tight_layout(rect=[0, 0, 0.85, 1])  # reservar espaço à direita para legenda


def main():
    parser = argparse.ArgumentParser(
        description="Aloca produtos em célula usando dados do SQLite."
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

    # Preparar informações de produtos e demandas
    colors = [
        'tab:blue','tab:orange','tab:green','tab:red',
        'tab:purple','tab:brown','tab:pink','tab:gray',
        'tab:olive','tab:cyan'
    ]
    produtos_info: List[Tuple[str, Produto, str]] = []
    demands: List[int] = []
    for idx, row in df.iterrows():
        label = f"{row['sku']} - {row['nome_produto']}"
        produtos_info.append((
            label,
            Produto(
                largura=int(row['largura_mm']),
                profundidade=int(row['profundidade_mm']),
                altura=int(row['altura_mm'])
            ),
            colors[idx % len(colors)]
        ))
        demands.append(int(row['qtd_vendida_30d']))

    # Executar alocação
    allocation = allocate_grouped_cells(produtos_info, demands, args.cells)
    plot_allocation_3d(allocation, produtos_info, args.cells)

    # Montar tabela detalhada
    skus   = [info[0].split(' - ')[0] for info in produtos_info]
    nomes  = [info[0].split(' - ')[1] for info in produtos_info]
    total_dem = [allocation[0][j][1] for j in range(len(skus))]
    total_alloc = [sum(allocation[i][j][2] for i in range(len(allocation))) for j in range(len(skus))]

    detail_rows = []
    n_cells = len(allocation)
    for j, (sku, nome) in enumerate(zip(skus, nomes)):
        falt = total_dem[j] - total_alloc[j]
        row = {
            'sku': sku,
            'nome_produto': nome,
            'total_necessario': total_dem[j],
            'total_alocado': total_alloc[j],
            'total_que_nao_coube': falt
        }
        for i in range(n_cells):
            row[f'celula_{i+1}'] = allocation[i][j][2]
        detail_rows.append(row)

    detail_df = pd.DataFrame(detail_rows)

    # Determinar pasta de produtos_simulados.csv e salvar lá
    # partimos do DB para determinar pasta data
    data_dir = os.path.dirname(args.db)
    output_path = os.path.join(data_dir, "resumo_alocacao_detalhada.csv")
    detail_df.to_csv(output_path, index=False)

    # Exibir tabela em nova janela como figura matplotlib
    fig2, ax2 = plt.subplots(figsize=(12, max(2, len(detail_df)*0.5)))
    ax2.axis('off')
    tbl = ax2.table(
        cellText=detail_df.values,
        colLabels=detail_df.columns,
        loc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.5)
    plt.tight_layout()

    print(f"Tabela detalhada salva em: {output_path}")

    plt.show()

if __name__ == '__main__':
    main()
