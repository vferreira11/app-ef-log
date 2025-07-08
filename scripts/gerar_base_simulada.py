
import pandas as pd
import random
import numpy as np
import os
import plotly.graph_objects as go
from plotly.graph_objects import Figure, Mesh3d, Layout

def gerar_produtos_simulados(n_produtos=30, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    categorias = ['Brinquedos', 'Utilidades Domésticas']
    nomes_brinquedos = [
        'Carrinho de Controle', 'Boneca Interativa', 'Jogo Educativo',
        'Kit de Pintura', 'Quebra-Cabeça', 'Blocos de Montar',
        'Carrinho Elétrico', 'Pelúcia Musical'
    ]
    nomes_utilidades = [
        'Panela Antiaderente', 'Conjunto de Copos', 'Escorredor Inox',
        'Faqueiro Colorido', 'Ventilador Portátil', 'Mini Liquidificador',
        'Grill Elétrico', 'Porta-Temperos'
    ]

    tamanhos = ['Muito Pequeno'] * 8 + ['Pequeno'] * 12 + ['Médio'] * 6 + ['Grande'] * 4

    faixas_dim = {
        'Muito Pequeno': {'largura': (0.05, 0.10), 'profundidade': (0.05, 0.10), 'altura': (0.02, 0.10)},
        'Pequeno': {'largura': (0.10, 0.20), 'profundidade': (0.10, 0.20), 'altura': (0.05, 0.20)},
        'Médio': {'largura': (0.20, 0.40), 'profundidade': (0.20, 0.40), 'altura': (0.10, 0.40)},
        'Grande': {'largura': (0.40, 0.80), 'profundidade': (0.30, 0.80), 'altura': (0.20, 1.20)},
    }

    faixas_peso = {
        'Brinquedos': {
            'Muito Pequeno': (0.03, 0.1), 'Pequeno': (0.1, 0.4),
            'Médio': (0.3, 1.5), 'Grande': (1.0, 5.0),
        },
        'Utilidades Domésticas': {
            'Muito Pequeno': (0.05, 0.3), 'Pequeno': (0.3, 1.0),
            'Médio': (0.8, 3.0), 'Grande': (2.0, 8.0),
        }
    }

    faixas_preco = {
        'Brinquedos': {
            'Muito Pequeno': (15, 39), 'Pequeno': (30, 99),
            'Médio': (80, 249), 'Grande': (199, 799),
        },
        'Utilidades Domésticas': {
            'Muito Pequeno': (10, 49), 'Pequeno': (30, 149),
            'Médio': (80, 299), 'Grande': (149, 899),
        }
    }

    def classificar_tamanho(volume):
        if volume <= 0.002:
            return 'Muito Pequeno'
        elif volume <= 0.01:
            return 'Pequeno'
        elif volume <= 0.05:
            return 'Médio'
        else:
            return 'Grande'

    produtos = []
    for i in range(n_produtos):
        sku = f"SKU{i+1:04d}"
        categoria = random.choice(categorias)
        tamanho = random.choice(tamanhos)
        nome = random.choice(nomes_brinquedos if categoria == 'Brinquedos' else nomes_utilidades)

        dim = faixas_dim[tamanho]
        for _ in range(100):
            largura = round(random.uniform(*dim['largura']), 3)
            profundidade = round(random.uniform(*dim['profundidade']), 3)
            altura_temp = round(random.uniform(*dim['altura']), 3)
            volume = round(largura * profundidade * altura_temp, 4)
            if classificar_tamanho(volume) == tamanho:
                altura = altura_temp
                break
        else:
            largura, profundidade, altura = 0.1, 0.1, 0.1
            volume = round(largura * profundidade * altura, 4)

        peso = round(random.uniform(*faixas_peso[categoria][tamanho]), 2)
        preco = round(random.uniform(*faixas_preco[categoria][tamanho]), 2)

        if tamanho == 'Muito Pequeno':
            qtd_venda = np.random.poisson(200)
        elif tamanho == 'Pequeno':
            qtd_venda = np.random.poisson(120)
        elif tamanho == 'Médio':
            qtd_venda = np.random.poisson(60)
        else:
            qtd_venda = np.random.poisson(25)

        produtos.append([
            sku, nome, categoria, preco, qtd_venda,
            largura, profundidade, altura, volume, peso
        ])

    df = pd.DataFrame(produtos, columns=[
        'sku', 'nome_produto', 'categoria', 'preco', 'qtd_vendida_90d',
        'largura_m', 'profundidade_m', 'altura_m',
        'volume_embalado_m3', 'peso_embalado_kg'
    ])

    return df

if __name__ == "__main__":
    df = gerar_produtos_simulados(n_produtos=30)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(base_dir, exist_ok=True)
    caminho_arquivo = os.path.join(base_dir, "produtos_simulados.csv")
    df.to_csv(caminho_arquivo, index=False, encoding='utf-8-sig')
    print(f"Base salva com sucesso em: {caminho_arquivo}")

def calcular_volume_disponivel(altura_mm, largura_mm, profundidade_mm):
    volume_mm3 = altura_mm * largura_mm * profundidade_mm
    volume_litros = volume_mm3 / 1_000_000
    volume_m3 = volume_mm3 / 1_000_000_000

    return {
        "volume_mm3": volume_mm3,
        "volume_litros": volume_litros,
        "volume_m3": volume_m3
    }

def plot_cubo_3d(largura_mm, profundidade_mm, altura_mm, title="Área CIMA"):
    # Vértices do cubo
    x = [0, largura_mm, largura_mm, 0, 0, largura_mm, largura_mm, 0]
    y = [0, 0, profundidade_mm, profundidade_mm, 0, 0, profundidade_mm, profundidade_mm]
    z = [0, 0, 0, 0, altura_mm, altura_mm, altura_mm, altura_mm]
    
    # Faces do cubo
    faces = [
        [0, 1, 2], [0, 2, 3],       # Base inferior
        [4, 5, 6], [4, 6, 7],       # Topo
        [0, 1, 5], [0, 5, 4],       # Frente
        [1, 2, 6], [1, 6, 5],       # Direita
        [2, 3, 7], [2, 7, 6],       # Fundo
        [3, 0, 4], [3, 4, 7]        # Esquerda
    ]
    i, j, k = zip(*faces)

    # Mesh do cubo
    mesh = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        opacity=0.5,
        color='lightgreen',
        name="Volume"
    )

    # Determina o centro do cubo e maior dimensão
    centro_x = largura_mm / 2
    centro_y = profundidade_mm / 2
    centro_z = altura_mm / 2
    max_dim = max(largura_mm, profundidade_mm, altura_mm)

    # Layout e câmera ajustados
    fig = go.Figure(data=[mesh])
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='Largura (mm)',
            yaxis_title='Profundidade (mm)',
            zaxis_title='Altura (mm)',
            aspectmode='manual',
            aspectratio=dict(
                x=largura_mm / max_dim,
                y=profundidade_mm / max_dim,
                z=altura_mm / max_dim
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
                center=dict(x=0, y=0, z=0)
            )
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )

    fig.show()

if __name__ == "__main__":
    plot_cubo_3d(
        largura_mm=1760,
        profundidade_mm=400,
        altura_mm=850,
        cor="lightgreen",
        nome="Área CIMA"
    )

def criar_cubo_preenchido(x0, y0, z0, dx, dy, dz, cor='blue', opacidade=0.2):
    return go.Mesh3d(
        x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
        y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
        z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
        i=[0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6],
        j=[1, 2, 3, 2, 5, 3, 6, 0, 5, 6, 6, 7],
        k=[2, 3, 0, 5, 6, 6, 7, 4, 6, 7, 7, 4],
        opacity=opacidade,
        color=cor,
        showlegend=False
    )
