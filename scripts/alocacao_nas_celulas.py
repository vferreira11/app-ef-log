import math
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Patch
from typing import List, Tuple
from dataclasses import dataclass

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

# Configuração das dimensões da célula
dimensoes_celula = Celula(largura=1760, profundidade=400, altura=850)

# Definição dos produtos (nome, dimensões, cor)
produtos_info: List[Tuple[str, Produto, str]] = [
    ('Caixa Celular', Produto(largura=160, profundidade=90, altura=30), 'tab:blue'),
    ('Caixa Média',   Produto(largura=200, profundidade=150, altura=50), 'tab:orange'),
    ('Caixa Chapéu',  Produto(largura=350, profundidade=350, altura=200), 'tab:green'),
]

# Estimativa de demanda para 30 dias (baseado em 90d de histórico)
vendas_90 = [171, 172, 168]
demands_30 = [math.ceil(v/90 * 30) for v in vendas_90]

# Função de alocação agrupada: tenta encaixar cada SKU inteiro numa célula antes de passar adiante
def allocate_grouped_cells(demands: List[int], n_cells: int = 3) -> List[List[Tuple[str,int,int,int]]]:
    """
    Aloca demandas de SKUs em células, agrupando cada SKU em blocos por célula.

    Args:
        demands (List[int]): demanda total de cada SKU.
        n_cells (int): número de células disponíveis.

    Returns:
        List[List[Tuple[str, int, int, int]]]:
            Para cada célula, lista de tuplas
            (nome, demanda_total, alocado, faltam).
    """
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
            if demand <= 0:
                alloc = 0
                cols = 0
            else:
                max_cols = rem_width[c] // prod.largura
                needed_cols = min(math.ceil(demand / cap_per_col), max_cols)
                alloc = min(demand, needed_cols * cap_per_col)
                cols = needed_cols
                rem_width[c] -= cols * prod.largura
                rem_dem[idx] -= alloc
            cells_alloc[c][idx] = (label, total, alloc, total - alloc)
    return cells_alloc

# Exemplo de uso: alocar em 3 células
N_CELLS = 3
allocation = allocate_grouped_cells(demands_30, N_CELLS)

# Plotagem 3D para cada célula
def plot_allocation_3d(allocation: List[List[Tuple[str,int,int,int]]], n_cells: int = N_CELLS):
    fig = plt.figure(figsize=(6 * n_cells, 6))
    cel = dimensoes_celula
    for i in range(n_cells):
        ax = fig.add_subplot(1, n_cells, i+1, projection='3d')
        ax.set_box_aspect((cel.largura, cel.profundidade, cel.altura))
        ax.set_xlim(0, cel.largura); ax.set_ylim(0, cel.profundidade); ax.set_zlim(0, cel.altura)
        ax.set_title(f"Célula {i+1}")
        ax.set_xlabel('X (mm)'); ax.set_ylabel('Y (mm)'); ax.set_zlabel('Z (mm)')
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
                        if count >= alloc: break
                        y = row * prod.profundidade
                        ax.bar3d(x, y, z, prod.largura, prod.profundidade, prod.altura,
                                 color=color, edgecolor='black', linewidth=0.5, shade=True)
                        count += 1
                    if count >= alloc: break
                if count >= alloc: break
            x_offset += needed_cols * prod.largura
        ax.legend(handles=handles, loc='upper right')
    plt.tight_layout()
    plt.show()

# Exibir tabela de resultados
def show_allocation_table(allocation: List[List[Tuple[str,int,int,int]]]):
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

# Execução principal
if __name__ == '__main__':
    allocation = allocate_grouped_cells(demands_30, N_CELLS)
    plot_allocation_3d(allocation, N_CELLS)
    show_allocation_table(allocation)
