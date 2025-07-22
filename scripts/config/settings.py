"""
Global configuration settings for 3D packing system
"""

# UI Configuration
DEFAULT_CONTAINER_DIMS = {
    'dx': 30,
    'dy': 40, 
    'dz': 50
}

DEFAULT_BLOCK_TYPES = {
    'dx': [1],
    'dy': [1], 
    'dz': [2],
    'quantidade': [100]
}

# GPU Algorithm Parameters
GPU_POPULATION_RANGE = {
    'min': 64,
    'max': 16384,
    'default': 2048,
    'step': 64
}

# Visualization Settings
VISUALIZATION_CONFIG = {
    'container_edge_color': 'gray',
    'container_edge_width': 4,
    'block_edge_color': 'black',
    'block_edge_width': 4,
    'figure_width': 800,
    'figure_height': 800,
    'color_palette': 'viridis'
}

# Performance Settings
MAX_BLOCKS_WARNING = 1000  # Warn if too many blocks for performance
