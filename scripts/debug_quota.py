import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt

# Parâmetros
csv_path = r"A:\_Profissional\__VOO SOLO\estoque\data\produtos_simulados.csv"
n_cells = 10
n_produtos = 12

# Carrega dados
try:
    df = pd.read_csv(csv_path)
except Exception as e:
    raise RuntimeError(f"Não conseguiu ler CSV: {e}")

# Limita para N produtos
df = df.head(n_produtos)

# Extração de dados
skus = df['sku'].tolist()
demands = df['qtd_vendida_30d'].astype(int).tolist()
produtos = list(df[['sku','nome_produto','largura_mm','profundidade_mm','altura_mm']]
                 .itertuples(index=False))

# Parâmetros da célula
cel_w, cel_d, cel_h = 1760, 400, 850
min_w = min(p.largura_mm for p in produtos)
cols_max = cel_w // min_w
layers_max = cel_h // min(p.altura_mm for p in produtos)

# Função de alocação (quota mix já validado)
def alloc_quota(demands, produtos, n_cells):
    total = demands.copy()
    records = []
    for c in range(n_cells):
        alloc = [0]*len(produtos)
        rem_w = cel_w
        quotas = [math.ceil(d/n_cells) for d in demands]
        cell_quota = quotas.copy()
        for _ in range(cols_max):
            # escolhe SKU de maior área base dentro de quota e demanda
            best, best_area = None, 0
            for i, p in enumerate(produtos):
                rows = cel_d // p.profundidade_mm
                if total[i]<=0 or cell_quota[i]<=0 or p.largura_mm>rem_w or rows<=0: continue
                area = p.largura_mm * p.profundidade_mm
                if area>best_area:
                    best_area=area; best=i
            if best is None: break
            p=produtos[best]
            rows=cel_d//p.profundidade_mm; layers=cel_h//p.altura_mm
            cap=rows*layers
            qty=min(cap, total[best], cell_quota[best])
            alloc[best]+=qty; total[best]-=qty; cell_quota[best]-=qty; rem_w-=p.largura_mm
        records.append(alloc)
    return records

# Gera alocação
alloc_list = alloc_quota(demands, produtos, n_cells)

# Plot de mapas de ocupação
fig, axes = plt.subplots(2, 5, figsize=(15, 6))
axes = axes.flatten()
for idx, ax in enumerate(axes[:n_cells]):
    grid = np.zeros((layers_max, cols_max), dtype=bool)
    x_off = 0
    for i, p in enumerate(produtos):
        qty = alloc_list[idx][i]
        if qty<=0: continue
        rows = cel_d//p.profundidade_mm
        layers = cel_h//p.altura_mm
        cap = rows*layers
        cols_needed = math.ceil(qty/cap)
        grid[:layers, x_off:x_off+cols_needed] = True
        x_off += cols_needed
    ax.imshow(grid, cmap='Blues', origin='lower')
    ax.set_title(f'Célula {idx+1}')
    ax.set_xticks([]); ax.set_yticks([])
plt.suptitle('Mapa de Ocupação (True=ocupado)')
plt.tight_layout()
plt.show()
