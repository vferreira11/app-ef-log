"""
Funções utilitárias para o sistema de empacotamento.
"""

import random
from typing import List, Tuple, Dict
from matplotlib import cm
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def calculate_max_capacity(container_volume: int, block_dims: List[Tuple[int, int, int]]) -> int:
    """
    Calcula a capacidade máxima teórica do container.
    
    Args:
        container_volume: Volume total do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Número máximo de blocos que cabem teoricamente
    """
    if not block_dims:
        return 0
        
    block_volumes = [lx * ly * lz for lx, ly, lz in block_dims]
    total_block_volume = sum(block_volumes)
    
    # Capacidade baseada no volume
    max_blocks = 0
    used_volume = 0
    for vol in block_volumes:
        if used_volume + vol <= container_volume:
            used_volume += vol
            max_blocks += 1
        else:
            break
    
    return min(max_blocks, len(block_dims))


def map_block_colors(block_dims: List[Tuple[int, int, int]]) -> Dict[Tuple[int, int, int], str]:
    """
    Mapeia cores da paleta Viridis para tipos únicos de bloco.
    
    Args:
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Dicionário mapeando dimensões para cores RGB
    """
    # Primeiro, identifica os tipos únicos
    unique_types = list(set(block_dims))
    unique_types.sort()  # Ordena para consistência
    
    # Cores da paleta Viridis em formato RGB para Plotly
    viridis_colors = [
        "rgb(68, 1, 84)",     # roxo escuro - Tipo 1
        "rgb(49, 104, 142)",  # azul escuro - Tipo 2  
        "rgb(38, 130, 142)",  # azul-verde - Tipo 3
        "rgb(31, 158, 137)",  # verde-azulado - Tipo 4
        "rgb(110, 206, 88)",  # verde claro - Tipo 5
        "rgb(181, 222, 43)",  # verde-amarelo - Tipo 6
        "rgb(254, 232, 37)",  # amarelo - Tipo 7
        "rgb(253, 231, 37)",  # amarelo claro - Tipo 8
        "rgb(53, 183, 121)",  # verde médio - Tipo 9
        "rgb(142, 1, 82)"     # magenta - Tipo 10
    ]
    
    colors = {}
    print(f"[DEBUG] Tipos únicos encontrados: {unique_types}")
    
    for i, block_type in enumerate(unique_types):
        if i < len(viridis_colors):
            # Usa cores predefinidas
            color = viridis_colors[i]
            colors[block_type] = color
            print(f"[DEBUG] Tipo {block_type} -> Cor {color}")
        else:
            # Para mais de 10 tipos, gera cores dinamicamente
            try:
                viridis = cm.get_cmap('viridis')
                color_value = i / max(1, len(unique_types) - 1) if len(unique_types) > 1 else 0
                rgba = viridis(color_value)
                rgb_color = f"rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})"
                colors[block_type] = rgb_color
                print(f"[DEBUG] Tipo {block_type} -> Cor dinâmica {rgb_color}")
            except Exception as e:
                # Fallback para cor padrão se matplotlib falhar
                fallback_color = "rgb(68, 1, 84)"  # roxo escuro
                colors[block_type] = fallback_color
                print(f"[DEBUG] Tipo {block_type} -> Cor fallback {fallback_color} (erro: {e})")
    
    print(f"[DEBUG] Mapeamento final: {colors}")
    return colors


def calculate_efficiency(placed_count: int, total_count: int) -> float:
    """
    Calcula a eficiência do empacotamento.
    
    Args:
        placed_count: Número de blocos alocados
        total_count: Número total de blocos
        
    Returns:
        Percentual de eficiência (0-100)
    """
    if total_count == 0:
        return 0.0
    return (placed_count / total_count) * 100


def format_dimensions(dims: Tuple[int, int, int]) -> str:
    """
    Formata dimensões para exibição.
    
    Args:
        dims: Tupla com dimensões (x, y, z)
        
    Returns:
        String formatada das dimensões
    """
    return f"{dims[0]}×{dims[1]}×{dims[2]}"


def generate_random_color() -> str:
    """Gera uma cor hexadecimal aleatória."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def validate_block_data(types_df) -> List[Tuple[int, int, int]]:
    """
    Valida e processa dados dos tipos de bloco.
    
    Args:
        types_df: DataFrame com tipos de bloco
        
    Returns:
        Lista de tuplas de dimensões dos blocos válidos
    """
    # Remove linhas completamente vazias
    valid_df = types_df.dropna(how='all')
    
    # Filtra linhas válidas
    valid_df = valid_df.dropna(subset=["dx", "dy", "dz", "quantidade"])
    valid_df = valid_df[(valid_df["quantidade"] > 0) & 
                       (valid_df["dx"] > 0) & 
                       (valid_df["dy"] > 0) & 
                       (valid_df["dz"] > 0)]
    
    if valid_df.empty:
        return []
    
    # Expande blocos
    block_dims = []
    for _, row in valid_df.iterrows():
        dims = (int(row.dx), int(row.dy), int(row.dz))
        qty = int(row.quantidade)
        block_dims.extend([dims] * qty)
    
    # Ordena por volume (maior primeiro)
    block_dims.sort(key=lambda d: d[0]*d[1]*d[2], reverse=True)
    
    return block_dims


def calculate_realistic_weight(category: str, volume_cm3: int, length: int, width: int, depth: int) -> float:
    """
    Calcula peso realista baseado na categoria e volume do produto.
    Peso limitado a máximo 1kg conforme especificação.
    
    Args:
        category: Categoria do produto
        volume_cm3: Volume em cm³
        length, width, depth: Dimensões em cm
        
    Returns:
        Peso em kg (limitado a 1kg)
    """
    # Densidade base por categoria (g/cm³)
    density_ranges = {
        "Brinquedos": (0.3, 0.8),      # Plástico leve, pelúcia, etc.
        "Utilidades": (0.5, 1.2),      # Plástico, cerâmica, vidro
        "Organizadores": (0.4, 0.9)    # Plástico estrutural, papelão reforçado
    }
    
    # Seleciona densidade aleatória dentro da faixa da categoria
    min_density, max_density = density_ranges.get(category, (0.5, 1.0))
    density = random.uniform(min_density, max_density)
    
    # Calcula peso base (volume * densidade)
    weight_grams = volume_cm3 * density
    
    # Adiciona variação por formato (produtos alongados podem ser mais leves)
    max_dim = max(length, width, depth)
    min_dim = min(length, width, depth)
    aspect_ratio = max_dim / max_dim if min_dim == 0 else max_dim / min_dim
    
    # Produtos muito alongados (ex: réguas) tendem a ser mais leves
    if aspect_ratio > 3:
        weight_grams *= random.uniform(0.7, 0.9)
    
    # Converte para kg
    weight_kg = weight_grams / 1000
    
    # Aplica limite máximo de 1kg
    weight_kg = min(weight_kg, 1.0)
    
    # Garante peso mínimo realista (mínimo 10g)
    weight_kg = max(weight_kg, 0.01)
    
    return round(weight_kg, 3)


def generate_random_orders(n_orders: int) -> pd.DataFrame:
    """
    Gera pedidos aleatórios com SDK, nome do produto, categoria, dimensões,
    histórico de vendas, previsão e preços realistas.
    
    Args:
        n_orders: Número de pedidos a gerar
        
    Returns:
        DataFrame com os pedidos gerados
    """
    categories = ["Brinquedos", "Utilidades", "Organizadores"]
    
    # Nomes de produtos por categoria
    product_names = {
        "Brinquedos": ["Boneca", "Carrinho", "Quebra-cabeça", "Pelúcia", "Blocos", "Bola", "Jogo", "Figura", "Robô", "Bichos"],
        "Utilidades": ["Garrafa", "Caneca", "Prato", "Tigela", "Talheres", "Bandeja", "Organizador", "Cesto", "Porta-objetos", "Suporte"],
        "Organizadores": ["Caixa", "Gaveta", "Estante", "Prateleira", "Divisória", "Porta-documentos", "Arquivo", "Pasta", "Separador", "Container"]
    }
    
    # Faixas de preço por categoria (em R$)
    price_ranges = {
        "Brinquedos": (15.90, 89.90),      # Brinquedos: R$ 15,90 - R$ 89,90
        "Utilidades": (8.50, 45.90),       # Utilidades: R$ 8,50 - R$ 45,90
        "Organizadores": (25.90, 129.90)   # Organizadores: R$ 25,90 - R$ 129,90
    }
    
    orders = []
    
    for i in range(n_orders):
        # Gera SDK único
        sdk = f"SDK{1000 + i:04d}"
        
        # Escolhe categoria aleatória
        category = random.choice(categories)
        
        # Escolhe nome do produto baseado na categoria
        product_name = random.choice(product_names[category])
        
        # Gera dimensões realistas baseadas na categoria
        if category == "Brinquedos":
            # Brinquedos: dimensões pequenas (máximo 10cm)
            length = random.randint(3, 10)
            width = random.randint(3, 10)
            depth = random.randint(2, 10)
        elif category == "Utilidades":
            # Utilidades: dimensões compactas (máximo 10cm)
            length = random.randint(4, 10)
            width = random.randint(4, 10)
            depth = random.randint(3, 10)
        else:  # Organizadores
            # Organizadores: dimensões limitadas (máximo 10cm)
            length = random.randint(5, 10)
            width = random.randint(5, 10)
            depth = random.randint(4, 10)
        
        # Gera preço unitário baseado na categoria e volume
        volume_cm3 = length * width * depth
        min_price, max_price = price_ranges[category]
        
        # Preço base + variação por volume (produtos maiores tendem a ser mais caros)
        volume_factor = min(volume_cm3 / 1000, 3.0)  # Fator de 0 a 3 baseado no volume
        base_price = random.uniform(min_price, max_price)
        unit_price = round(base_price * (1 + volume_factor * 0.3), 2)
        
        # Gera histórico de vendas dos últimos 90 dias
        # Vendas variam por categoria e sazonalidade
        if category == "Brinquedos":
            # Brinquedos: vendas maiores, mais variação sazonal
            base_sales = random.randint(50, 200)
            seasonal_factor = random.uniform(0.7, 1.8)  # Variação sazonal alta
        elif category == "Utilidades":
            # Utilidades: vendas constantes, menor variação
            base_sales = random.randint(80, 150)
            seasonal_factor = random.uniform(0.9, 1.2)  # Variação sazonal baixa
        else:  # Organizadores
            # Organizadores: vendas médias, variação moderada
            base_sales = random.randint(30, 120)
            seasonal_factor = random.uniform(0.8, 1.4)  # Variação sazonal moderada
        
        sales_90_days = max(1, int(base_sales * seasonal_factor))
        
        # Gera previsão para próximo mês baseada no histórico
        # Usa tendência + variação aleatória
        monthly_avg = sales_90_days / 3  # Média mensal dos últimos 90 dias
        trend_factor = random.uniform(0.85, 1.25)  # Tendência de crescimento/queda
        next_month_forecast = max(1, int(monthly_avg * trend_factor))
        
        # Calcula peso realista baseado na categoria e volume
        weight_kg = calculate_realistic_weight(category, volume_cm3, length, width, depth)
        
        orders.append({
            "SDK": sdk,
            "Nome Produto": product_name,
            "Categoria": category,
            "Comprimento": length,
            "Largura": width,
            "Profundidade": depth,
            "Peso (kg)": weight_kg,
            "Preço Unitário": f"R$ {unit_price:.2f}",
            "Vendas 90 Dias": sales_90_days,
            "Previsão Próx. Mês": next_month_forecast
        })
    
    return pd.DataFrame(orders)


def convert_orders_to_block_dims(orders_df: pd.DataFrame) -> List[Tuple[int, int, int]]:
    """
    Converte DataFrame de pedidos para lista de dimensões de blocos,
    usando a previsão de vendas do próximo mês como quantidade.
    Aplica validação para garantir máximo de 20cm por lado.
    
    Args:
        orders_df: DataFrame com pedidos
        
    Returns:
        Lista de tuplas de dimensões dos blocos (repetidas conforme previsão)
    """
    block_dims = []
    
    for _, row in orders_df.iterrows():
        dims = (int(row["Comprimento"]), int(row["Largura"]), int(row["Profundidade"]))
        quantity = int(row["Previsão Próx. Mês"])  # Usa a previsão como quantidade
        
        # Adiciona a quantidade prevista de cada produto
        for _ in range(quantity):
            block_dims.append(dims)
    
    # Aplica validação de dimensões máximas
    block_dims = validate_block_dimensions(block_dims, max_size=10)
    
    # Ordena por volume (maior primeiro)
    block_dims.sort(key=lambda d: d[0]*d[1]*d[2], reverse=True)
    
    return block_dims


def calculate_sales_analytics(orders_df: pd.DataFrame) -> Dict:
    """
    Calcula estatísticas de vendas, previsões e pesos dos pedidos.
    
    Args:
        orders_df: DataFrame com pedidos
        
    Returns:
        Dicionário com estatísticas calculadas
    """
    if orders_df.empty:
        return {}
    
    # Remove 'R$' e converte preços para float
    prices = orders_df['Preço Unitário'].str.replace('R$ ', '').str.replace(',', '.').astype(float)
    
    # Estatísticas de peso
    weights = orders_df['Peso (kg)'] if 'Peso (kg)' in orders_df.columns else pd.Series([0] * len(orders_df))
    total_weight_forecast = (weights * orders_df['Previsão Próx. Mês']).sum()
    
    # Calcula estatísticas por categoria
    analytics = {
        'total_products': len(orders_df),
        'total_sales_90d': orders_df['Vendas 90 Dias'].sum(),
        'total_forecast': orders_df['Previsão Próx. Mês'].sum(),
        'avg_price': prices.mean(),
        'avg_weight': weights.mean(),
        'max_weight': weights.max(),
        'total_weight_forecast': total_weight_forecast,
        'total_revenue_90d': (prices * orders_df['Vendas 90 Dias']).sum(),
        'forecast_revenue': (prices * orders_df['Previsão Próx. Mês']).sum(),
        'by_category': {}
    }
    
    # Estatísticas por categoria
    for category in orders_df['Categoria'].unique():
        cat_data = orders_df[orders_df['Categoria'] == category]
        cat_prices = prices[orders_df['Categoria'] == category]
        cat_weights = weights[orders_df['Categoria'] == category]
        
        analytics['by_category'][category] = {
            'count': len(cat_data),
            'sales_90d': cat_data['Vendas 90 Dias'].sum(),
            'forecast': cat_data['Previsão Próx. Mês'].sum(),
            'avg_price': cat_prices.mean(),
            'avg_weight': cat_weights.mean(),
            'total_weight_forecast': (cat_weights * cat_data['Previsão Próx. Mês']).sum(),
            'revenue_90d': (cat_prices * cat_data['Vendas 90 Dias']).sum()
        }
    
    return analytics


def validate_block_dimensions(block_dims: List[Tuple[int, int, int]], max_size: int = 10) -> List[Tuple[int, int, int]]:
    """
    Valida e corrige dimensões de blocos para não exceder o tamanho máximo.
    
    Args:
        block_dims: Lista de dimensões dos blocos
        max_size: Tamanho máximo permitido para qualquer dimensão
        
    Returns:
        Lista de dimensões validadas e corrigidas
    """
    validated_dims = []
    corrections_made = 0
    
    for dims in block_dims:
        length, width, depth = dims
        original_dims = dims
        
        # Aplica limitação de tamanho máximo
        length = min(length, max_size)
        width = min(width, max_size)
        depth = min(depth, max_size)
        
        new_dims = (length, width, depth)
        validated_dims.append(new_dims)
        
        if original_dims != new_dims:
            corrections_made += 1
    
    if corrections_made > 0:
        print(f"[INFO] {corrections_made} blocos tiveram dimensões corrigidas para máximo {max_size}cm")
    
    return validated_dims


def generate_packing_summary(orders_df: pd.DataFrame, placements: List, total_blocks: int) -> Dict:
    """
    Gera resumo detalhado do empacotamento por produto.
    
    Args:
        orders_df: DataFrame com pedidos
        placements: Lista de alocações bem-sucedidas
        total_blocks: Número total de blocos a empacotar
        
    Returns:
        Dicionário com resumo do empacotamento
    """
    packed_blocks = len(placements)
    efficiency = (packed_blocks / total_blocks * 100) if total_blocks > 0 else 0
    
    # Calcula blocos por produto
    product_summary = []
    for _, row in orders_df.iterrows():
        forecast = int(row["Previsão Próx. Mês"])
        dims = (int(row["Comprimento"]), int(row["Largura"]), int(row["Profundidade"]))
        
        # Conta quantos blocos deste produto foram empacotados
        packed_count = 0
        for placement in placements:
            if len(placement) >= 4:
                # Verifica se as dimensões batem (considerando rotações)
                if len(placement) == 5:
                    # Com rotação
                    _, _, _, _, orientation = placement
                    if set(orientation) == set(dims):
                        packed_count += 1
                else:
                    # Sem rotação - precisaria comparar com block_dims[block_index]
                    # Por simplificação, usaremos estimativa baseada na eficiência geral
                    pass
        
        # Estimativa baseada na eficiência geral se não conseguir contar exato
        if packed_count == 0:
            packed_count = int(forecast * (efficiency / 100))
        
        product_summary.append({
            'sdk': row["SDK"],
            'produto': row["Nome Produto"],
            'categoria': row["Categoria"],
            'previsao': forecast,
            'empacotado': min(packed_count, forecast),
            'pendente': max(0, forecast - packed_count),
            'dimensoes': f"{dims[0]}×{dims[1]}×{dims[2]}"
        })
    
    return {
        'total_blocks': total_blocks,
        'packed_blocks': packed_blocks,
        'efficiency': efficiency,
        'products': product_summary
    }