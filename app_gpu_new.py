"""
3D Packing System - Main Streamlit Application
==============================================

Clean and modular Streamlit interface for 3D block packing optimization.
Uses GPU-accelerated algorithms with rotation support and advanced visualization.

Usage:
    streamlit run app_gpu_new.py
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add scripts directory to path for imports
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(scripts_dir)

# Import modular components
from scripts.core.models import ContainerConfig, Placement
from scripts.core.algorithms import gpu_optimize_packing
from scripts.core.visualization import create_3d_plot
from scripts.core.utils import (
    calculate_max_capacity, 
    map_block_colors, 
    calculate_efficiency,
    format_dimensions
)
from scripts.config.settings import (
    DEFAULT_CONTAINER_DIMS,
    DEFAULT_BLOCK_TYPES, 
    GPU_POPULATION_RANGE,
    MAX_BLOCKS_WARNING
)

# Configure Streamlit
st.set_page_config(
    page_title="GPU Packing 3D", 
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_header():
    """Render application header and description."""
    st.title("🎯 3D Packing System")
    st.markdown(
        """*Advanced 3D block packing optimization with GPU acceleration and intelligent rotation algorithms*\n\n
        📊 **Features**: GPU optimization • Rotation support • Real-time 3D visualization • Viridis color palette"""
    )


def render_container_section() -> ContainerConfig:
    """
    Render container configuration section.
    
    Returns:
        Configured ContainerConfig object
    """
    st.subheader("📐 Container Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dx = st.number_input(
            "Width (X)", 
            min_value=1, 
            value=DEFAULT_CONTAINER_DIMS['dx'],
            help="Container width dimension"
st.set_page_config(
    page_title="Empacotamento 3D GPU", 
    layout="wide",
    initial_sidebar_state="expanded"
)
    with col2:
            "Largura (X)", 
            "Depth (Y)", 
    st.title("🎯 Empacotamento 3D GPU")
            help="Dimensão de largura do container"
    *Otimização avançada de empacotamento 3D com aceleração GPU e algoritmos inteligentes de rotação*
    
    📊 **Recursos**: Otimização GPU • Suporte a rotação • Visualização 3D em tempo real • Paleta de cores Viridis
            "Profundidade (Y)", 
            "Height (Z)", 
            min_value=1, 
            help="Dimensão de profundidade do container"
            help="Container height dimension"
        )
    
            "Altura (Z)", 
    
    st.subheader("📐 Configuração do Container")
    
    return container


def render_blocks_section() -> pd.DataFrame:
    """
        )
    with col2:
        dy = st.number_input(
            "Profundidade (Y)", 
            min_value=1, 
            value=DEFAULT_CONTAINER_DIMS['dy'],
            help="Dimensão de profundidade do container"
        )
    with col3:
        dz = st.number_input(
            "Altura (Z)", 
            min_value=1, 
            value=DEFAULT_CONTAINER_DIMS['dz'],
            help="Dimensão de altura do container"
        )
    container = ContainerConfig(dx, dy, dz)
    st.info(f"📦 Container: {format_dimensions(container.dimensions())} | Volume: {container.volume:,} unidades")
    return container
            "dz": st.column_config.NumberColumn("Height", min_value=1),
            "quantidade": st.column_config.NumberColumn("Quantity", min_value=1)
    st.info(f"📦 Container: {format_dimensions(container.dimensions())} | Volume: {container.volume:,} unidades")
    )
    
    return pd.DataFrame(types_raw) if isinstance(types_raw, dict) else types_raw


def render_gpu_parameters() -> int:
    """
    Render GPU algorithm parameters in sidebar.
    
    Returns:
    st.subheader("📦 Configuração dos Tipos de Bloco")
    """
    st.sidebar.subheader("⚙️ GPU Algorithm Settings")
    st.markdown("*Defina diferentes tipos de bloco com suas dimensões e quantidades*")
    pop_size = st.sidebar.slider(
    st.subheader("📦 Configuração dos Tipos de Bloco")
    st.markdown("*Defina diferentes tipos de bloco com suas dimensões e quantidades*")
    types_raw = st.data_editor(
        DEFAULT_BLOCK_TYPES,
        num_rows="dynamic",
        key="block_types",
        use_container_width=True,
        column_config={
            "dx": st.column_config.NumberColumn("Largura", min_value=1),
            "dy": st.column_config.NumberColumn("Profundidade", min_value=1),
            "dz": st.column_config.NumberColumn("Altura", min_value=1),
            "quantidade": st.column_config.NumberColumn("Quantidade", min_value=1)
        }
    )
    return pd.DataFrame(types_raw) if isinstance(types_raw, dict) else types_raw
def process_block_data(types_df: pd.DataFrame) -> list:
    """
    Process and validate block types data.
    
    st.subheader("⚙️ Parâmetros da Heurística GPU")
        types_df: DataFrame with block types
        
    Returns:
        List of block dimensions tuples
    """
    # Filter valid rows
    valid_df = types_df.dropna(subset=["dx", "dy", "dz", "quantidade"])
    valid_df = valid_df[valid_df["quantidade"] > 0]
    
    if valid_df.empty:
        return []
    
    # Expand blocks
    block_dims = []
    for _, row in valid_df.iterrows():
        dims = (int(row.dx), int(row.dy), int(row.dz))
        qty = int(row.quantidade)
        block_dims.extend([dims] * qty)
    
    # Sort by volume (largest first)
    block_dims.sort(key=lambda d: d[0]*d[1]*d[2], reverse=True)
    
    return block_dims


def display_analysis_metrics(container: ContainerConfig, block_dims: list, placements: list):
    """
    Display packing analysis and metrics.
    
    Args:
        container: Container configuration
        block_dims: List of block dimensions
        placements: List of successful placements
    """
    st.subheader("📊 Packing Analysis")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Container Volume",
            f"{container.volume:,}",
            help="Total container capacity"
        )
    
    with col2:
        unique_types = len(set(block_dims))
        st.metric(
            "Block Types", 
            unique_types,
            help="Number of different block types"
        )
    
    with col3:
        placed_count = len(placements)
        total_count = len(block_dims)
        st.metric(
    st.subheader("📊 Análise do Empacotamento")
            f"{placed_count}/{total_count}",
            help="Successfully placed blocks"
        )
    
    with col4:
        efficiency = calculate_efficiency(placed_count, total_count)
        st.metric(
            "Efficiency",
            f"{efficiency:.1f}%",
            help="Packing efficiency percentage"
        )
    
    # Status messages
    if placed_count == total_count:
        st.success(f"🎉 Perfect packing! All {total_count} blocks successfully placed.")
    elif placed_count > 0:
        missing = total_count - placed_count
        st.warning(f"⚠️ {missing} blocks could not be placed due to space constraints.")
    else:
        st.error("❌ No blocks could be placed. Check container and block dimensions.")


def run_packing_algorithm(container: ContainerConfig, block_dims: list, pop_size: int) -> list:
    """
    Execute the packing algorithm with progress indication.
    
    Args:
        container: Container configuration
        block_dims: List of block dimensions
        pop_size: GPU population size
        
    Returns:
        List of placements
    """
    if not block_dims:
        st.error("❌ No valid blocks to pack!")
        return []
    
    # Performance warning
    if len(block_dims) > MAX_BLOCKS_WARNING:
        st.warning(f"⚠️ Large number of blocks ({len(block_dims)}) may affect performance.")
    
    # Calculate capacity
    max_capacity = calculate_max_capacity(container.volume, block_dims)
    st.info(f"🎯 Theoretical maximum capacity: {max_capacity} blocks")
    
    # Run algorithm with progress
    with st.spinner("🚀 Running GPU optimization algorithm..."):
        placements = gpu_optimize_packing(container, block_dims, max_capacity)
    
    return placements


def render_visualization(container: ContainerConfig, placements: list, block_dims: list):
    """
    Render 3D visualization section.
    
    Args:
        st.error("❌ Nenhum bloco válido para empacotar!")
        placements: List of block placements
        block_dims: List of block dimensions
    """
    if not placements:
        st.warning("No blocks to visualize.")
        return
    
    st.subheader("🎨 3D Interactive Visualization")
    st.info(f"🎯 Capacidade máxima teórica: {max_capacity} blocos")
    try:
        # Generate colors
        block_colors = map_block_colors(block_dims)
        
        # Create and display plot
        fig = create_3d_plot(container, placements, block_dims, block_colors)
        st.plotly_chart(fig, use_container_width=True)
        
        # Visualization info
        st.markdown("""
        **Visualization Controls:**
        - 🖱️ **Rotate**: Click and drag
        - 🔍 **Zoom**: Mouse wheel or pinch
        - 📐 **Pan**: Shift + click and drag
        - 🎨 **Colors**: Viridis palette for block types
        """)
        
        st.warning("Nenhum bloco para visualizar.")
        st.error(f"❌ Visualization error: {str(e)}")


def main():
    """Main application entry point."""
    
    # Header
    render_header()

    # Heuristic parameters (GPU slider) FIRST
    pop_size = render_gpu_parameters()

    # Main configuration sections
    container = render_container_section()
    types_df = render_blocks_section()

    # Execution button
    show_graph = False
    if st.button("🚀 Executar CPU Heurística", type="primary", use_container_width=True):
        # Process input data
        block_dims = process_block_data(types_df)
        if not block_dims:
            st.error("❌ Please configure at least one valid block type.")
            return
        # Run packing algorithm
        placements = run_packing_algorithm(container, block_dims, pop_size)
        # Store results in session state
        st.session_state.update({
            'placements': placements,
            'container': container,
            'block_dims': block_dims,
            'last_run': True
        })
        # Display results
        display_analysis_metrics(container, block_dims, placements)
        show_graph = True

    # Visualization section (only if button was pressed)
    if show_graph:
        render_visualization(
            st.session_state['container'],
            st.session_state['placements'],
            st.session_state['block_dims']
            st.error("❌ Configure pelo menos um tipo de bloco válido.")


if __name__ == "__main__":
    main()
