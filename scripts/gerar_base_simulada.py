import pandas as pd
import random
import numpy as np
import os
import math
import argparse

def calcular_volume_disponivel(altura_mm, largura_mm, profundidade_mm):
    volume_mm3 = altura_mm * largura_mm * profundidade_mm
    volume_litros = volume_mm3 / 1_000_000
    volume_m3 = volume_mm3 / 1_000_000_000
    return {
        "volume_mm3": volume_mm3,
        "volume_litros": volume_litros,
        "volume_m3": volume_m3
    }

def gerar_produtos_simulados(n_produtos=30):
    
    categorias = ['Brinquedos', 'Utilidades Domésticas']
    nomes_brinquedos = [
        'Carrinho de Controle', 'Boneca Interativa', 'Jogo Educativo',
        'Kit de Pintura', 'Quebra-Cabeça', 'Blocos de Montar',
        'Carrinho Elétrico', 'Puzzle 3D'
    ]
    produtos = []
    for i in range(n_produtos):
        sku = f"SKU-{i+1:04d}"
        categoria = random.choice(categorias)
        nome = random.choice(nomes_brinquedos) if categoria == 'Brinquedos' else f"Item HD-{i+1}"
        preco = round(random.uniform(20, 500), 2)

        # vendas dos últimos 90 dias
        tamanho = random.choice(['Pequeno', 'Médio', 'Grande'])
        if tamanho == 'Grande':
            qtd_venda = np.random.poisson(30)
        elif tamanho == 'Médio':
            qtd_venda = np.random.poisson(60)
        else:
            qtd_venda = np.random.poisson(120)

        # dimensões em metros
        largura = round(random.uniform(0.05, 0.5), 3)
        profundidade = round(random.uniform(0.05, 0.5), 3)
        altura = round(random.uniform(0.05, 0.5), 3)
        volume_m3 = largura * profundidade * altura
        peso = round(volume_m3 * random.uniform(0.5, 2.0), 2)

        produtos.append({
            'sku': sku,
            'nome_produto': nome,
            'categoria': categoria,
            'preco': preco,
            'qtd_vendida_90d': int(qtd_venda),
            'qtd_vendida_30d': int(math.ceil(qtd_venda / 90 * 30)),
            'largura_m': largura,
            'profundidade_m': profundidade,
            'altura_m': altura,
            'largura_mm': int(largura * 1000),
            'profundidade_mm': int(profundidade * 1000),
            'altura_mm': int(altura * 1000),
            'volume_embalado_m3': round(volume_m3, 6),
            'peso_embalado_kg': peso,
        })

    df = pd.DataFrame(produtos)
    vols = df.apply(
        lambda row: pd.Series(
            calcular_volume_disponivel(
                row['altura_mm'],
                row['largura_mm'],
                row['profundidade_mm']
            )
        ),
        axis=1
    )
    return pd.concat([df, vols], axis=1)

def main():
    parser = argparse.ArgumentParser(
        description="Gera CSV de produtos simulados com dimensões, vendas e volumes."
    )
    parser.add_argument(
        "-n", "--n_produtos",
        type=int,
        default=30,
        help="Número de produtos distintos a gerar"
    )
    args = parser.parse_args()

    df = gerar_produtos_simulados(n_produtos=args.n_produtos)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(base_dir, exist_ok=True)
    caminho_arquivo = os.path.join(base_dir, "produtos_simulados.csv")
    df.to_csv(caminho_arquivo, index=False, encoding='utf-8-sig')
    print(f"Base de {args.n_produtos} produtos salva em: {caminho_arquivo}")

if __name__ == "__main__":
    main()
