"""
3D Packing System - Main Streamlit Application
==============================================

Clean and modular Streamlit interface for 3D block packing optimization.
Uses GPU-accelerated algorithms with rotation support and advanced visualization.

Usage:
    streamlit run app_gpu.py
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import modular components
from core.models import ContainerConfig, Placement
from core.algorithms import gpu_optimize_packing
from core.visualization import create_3d_plot
from core.utils import (
    calculate_max_capacity, 
    map_block_colors, 
    calculate_efficiency,
    format_dimensions
)
from config.settings import (
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
    st.markdown("""
    *Advanced 3D block packing optimization with GPU acceleration and intelligent rotation algorithms*
    
    📊 **Features**: GPU optimization • Rotation support • Real-time 3D visualization • Viridis color palette
    """)


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
        )
    with col2:
        dy = st.number_input(
            "Depth (Y)", 
            min_value=1, 
            value=DEFAULT_CONTAINER_DIMS['dy'],
            help="Container depth dimension"
        )
    with col3:
        dz = st.number_input(
            "Height (Z)", 
            min_value=1, 
            value=DEFAULT_CONTAINER_DIMS['dz'],
            help="Container height dimension"
        )
    
    container = ContainerConfig(dx, dy, dz)
    
    # Display container info
    st.info(f"📦 Container: {format_dimensions(container.dimensions())} | Volume: {container.volume:,} units")
    
    return container


def render_blocks_section() -> pd.DataFrame:
    """
    Render block types configuration section.
    
    Returns:
        DataFrame with block types configuration
    """
    st.subheader("📦 Block Types Configuration")
    
    # Instructions
    st.markdown("*Define different block types with their dimensions and quantities*")
    
    # Data editor
    types_raw = st.data_editor(
        DEFAULT_BLOCK_TYPES,
        num_rows="dynamic",
        key="block_types",
        use_container_width=True,
        column_config={
            "dx": st.column_config.NumberColumn("Width", min_value=1),
            "dy": st.column_config.NumberColumn("Depth", min_value=1), 
            "dz": st.column_config.NumberColumn("Height", min_value=1),
            "quantidade": st.column_config.NumberColumn("Quantity", min_value=1)
        }
    )
    
    return pd.DataFrame(types_raw) if isinstance(types_raw, dict) else types_raw


def render_gpu_parameters() -> int:
    """
    Render GPU algorithm parameters in sidebar.
    
    Returns:
        Population size for GPU algorithm
    """
    st.sidebar.subheader("⚙️ GPU Algorithm Settings")
    
    pop_size = st.sidebar.slider(
        "Population Size",
        min_value=GPU_POPULATION_RANGE['min'],
        max_value=GPU_POPULATION_RANGE['max'],
        value=GPU_POPULATION_RANGE['default'],
        step=GPU_POPULATION_RANGE['step'],
        help="Larger values may give better results but take more time"
    )
    
    st.sidebar.markdown("""
    **Algorithm Features:**
    - ✅ Rotation optimization
    - ✅ GPU acceleration  
    - ✅ Gap filling
    - ✅ Efficiency maximization
    """)
    
    return pop_size


def process_block_data(types_df: pd.DataFrame) -> list:
    """
    Process and validate block types data.
    
    Args:
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
            "Blocks Placed",
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
        container: Container configuration
        placements: List of block placements
        block_dims: List of block dimensions
    """
    if not placements:
        st.warning("No blocks to visualize.")
        return
    
    st.subheader("🎨 3D Interactive Visualization")
    
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
        
    except Exception as e:
        st.error(f"❌ Visualization error: {str(e)}")


def main():
    """Main application entry point."""
    
    # Header
    render_header()
    
    # Main configuration sections
    container = render_container_section()
    types_df = render_blocks_section()
    pop_size = render_gpu_parameters()
    
    # Execution button
    if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
        
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
    
    # Visualization section (if results available)
    if st.session_state.get('last_run', False):
        render_visualization(
            st.session_state['container'],
            st.session_state['placements'],
            st.session_state['block_dims']
        )


if __name__ == "__main__":
    main()
