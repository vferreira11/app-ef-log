# -*- coding: utf-8 -*-
# Dimensões padrão do container
DEFAULT_CONTAINER_DIMS = {
    'dx': 15,  # Largura
    'dy': 30,  # Profundidade
    'dz': 20   # Altura
}

# Tipos de bloco padrão
DEFAULT_BLOCK_TYPES = [
    {"dx": 1, "dy": 1, "dz": 2, "quantidade": 100},
    {"dx": 2, "dy": 2, "dz": 3, "quantidade": 50},
    {"dx": 3, "dy": 3, "dz": 4, "quantidade": 25}
]

# Configurações do algoritmo GPU
GPU_POPULATION_RANGE = {
    'min': 64,
    'max': 16384,
    'default': 2048,
    'step': 64
}

# Limite de blocos para aviso de performance
MAX_BLOCKS_WARNING = 1000

# Configurações de visualização
VISUALIZATION_CONFIG = {
    'container_edge_color': 'gray',
    'container_edge_width': 4,
    'block_edge_color': 'black',
    'block_edge_width': 3,
    'block_opacity': 1.0,
    'default_width': 800,
    'default_height': 800
}

# Mensagens da interface
UI_MESSAGES = {
    'success_perfect': "🎉 Empacotamento perfeito! Todos os {} blocos foram alocados.",
    'warning_partial': "⚠️ {} blocos não puderam ser alocados por falta de espaço.",
    'error_no_blocks': "❌ Nenhum bloco foi alocado. Verifique as dimensões do container e dos blocos.",
    'info_processing': "🔄 Processando dados dos blocos...",
    'info_capacity': "🎯 Capacidade máxima teórica: {} blocos",
    'warning_performance': "⚠️ Grande quantidade de blocos ({}) pode afetar a performance."
}
