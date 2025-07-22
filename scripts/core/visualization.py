"""
3D visualization functions using Plotly

This module handles all 3D visualization aspects of the packing system.
"""

import plotly.graph_objects as go
from typing import List, Dict, Tuple
from .models import ContainerConfig, Placement
from distribuir_milp import Cuboid


def create_container_wireframe(container: ContainerConfig) -> List[go.Scatter3d]:
    """
    Create wireframe (edges) visualization of the container.
    
    Args:
        container: Container configuration
        
    Returns:
        List of Plotly traces for container edges
    """
    cd = Cuboid(container.dx, container.dy, container.dz)
    traces = []
    
    # Container vertices
    verts = cd._get_vertices((0, 0, 0), container.dx, container.dy, container.dz)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # bottom face
        (4, 5), (5, 6), (6, 7), (7, 4),  # top face
        (0, 4), (1, 5), (2, 6), (3, 7)   # vertical edges
    ]
    
    for e in edges:
        x0, y0, z0 = verts[e[0]]
        x1, y1, z1 = verts[e[1]]
        traces.append(go.Scatter3d(
            x=[x0, x1], y=[y0, y1], z=[z0, z1],
            mode='lines',
            line=dict(color='gray', width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return traces


def create_block_faces(x0: int, y0: int, z0: int, lx: int, ly: int, lz: int, 
                      color: str) -> List[go.Surface]:
    """
    Create solid faces for a single block using Surface traces.
    
    Args:
        x0, y0, z0: Block position
        lx, ly, lz: Block dimensions
        color: Block color in hex format
        
    Returns:
        List of Surface traces for all 6 faces
    """
    faces = []
    
    # Define all 6 faces coordinates
    face_coords = [
        # Bottom face (z = z0)
        dict(x=[[x0, x0+lx], [x0, x0+lx]], 
             y=[[y0, y0], [y0+ly, y0+ly]], 
             z=[[z0, z0], [z0, z0]]),
        # Top face (z = z0+lz)
        dict(x=[[x0, x0+lx], [x0, x0+lx]], 
             y=[[y0, y0], [y0+ly, y0+ly]], 
             z=[[z0+lz, z0+lz], [z0+lz, z0+lz]]),
        # Front face (y = y0)
        dict(x=[[x0, x0+lx], [x0, x0+lx]], 
             y=[[y0, y0], [y0, y0]], 
             z=[[z0, z0], [z0+lz, z0+lz]]),
        # Back face (y = y0+ly)
        dict(x=[[x0, x0+lx], [x0, x0+lx]], 
             y=[[y0+ly, y0+ly], [y0+ly, y0+ly]], 
             z=[[z0, z0], [z0+lz, z0+lz]]),
        # Left face (x = x0)
        dict(x=[[x0, x0], [x0, x0]], 
             y=[[y0, y0+ly], [y0, y0+ly]], 
             z=[[z0, z0], [z0+lz, z0+lz]]),
        # Right face (x = x0+lx)
        dict(x=[[x0+lx, x0+lx], [x0+lx, x0+lx]], 
             y=[[y0, y0+ly], [y0, y0+ly]], 
             z=[[z0, z0], [z0+lz, z0+lz]])
    ]
    
    # Create Surface trace for each face
    for face in face_coords:
        faces.append(go.Surface(
            x=face['x'], 
            y=face['y'], 
            z=face['z'],
            colorscale=[[0, color], [1, color]],
            showscale=False,
            hoverinfo='skip'
        ))
    
    return faces


def create_block_edges(x0: int, y0: int, z0: int, lx: int, ly: int, lz: int) -> List[go.Scatter3d]:
    """
    Create black edge lines for a single block.
    
    Args:
        x0, y0, z0: Block position
        lx, ly, lz: Block dimensions
        
    Returns:
        List of Scatter3d traces for all 12 edges
    """
    edges = []
    
    # Define all 12 edges
    edge_coords = [
        # Bottom face edges
        [(x0, y0, z0), (x0+lx, y0, z0)],
        [(x0+lx, y0, z0), (x0+lx, y0+ly, z0)],
        [(x0+lx, y0+ly, z0), (x0, y0+ly, z0)],
        [(x0, y0+ly, z0), (x0, y0, z0)],
        # Top face edges
        [(x0, y0, z0+lz), (x0+lx, y0, z0+lz)],
        [(x0+lx, y0, z0+lz), (x0+lx, y0+ly, z0+lz)],
        [(x0+lx, y0+ly, z0+lz), (x0, y0+ly, z0+lz)],
        [(x0, y0+ly, z0+lz), (x0, y0, z0+lz)],
        # Vertical edges
        [(x0, y0, z0), (x0, y0, z0+lz)],
        [(x0+lx, y0, z0), (x0+lx, y0, z0+lz)],
        [(x0+lx, y0+ly, z0), (x0+lx, y0+ly, z0+lz)],
        [(x0, y0+ly, z0), (x0, y0+ly, z0+lz)]
    ]
    
    # Create Scatter3d trace for each edge
    for p1, p2 in edge_coords:
        edges.append(go.Scatter3d(
            x=[p1[0], p2[0]],
            y=[p1[1], p2[1]],
            z=[p1[2], p2[2]],
            mode='lines',
            line=dict(color='black', width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return edges


def create_block_visualization(placement: Placement, 
                             block_dims: List[Tuple[int, int, int]], 
                             color: str) -> List:
    """
    Create complete visualization for a single block (faces + edges).
    
    Args:
        placement: Block placement information
        block_dims: List of all block dimensions
        color: Block color in hex format
        
    Returns:
        List of Plotly traces for the complete block
    """
    traces = []
    
    # Extract position and dimensions
    x0, y0, z0 = placement.position()
    
    if placement.orientation:
        lx, ly, lz = placement.orientation
    else:
        lx, ly, lz = block_dims[placement.block_index]
    
    # Add solid faces
    faces = create_block_faces(x0, y0, z0, lx, ly, lz, color)
    traces.extend(faces)
    
    # Add black edges
    edges = create_block_edges(x0, y0, z0, lx, ly, lz)
    traces.extend(edges)
    
    return traces


def create_3d_plot(container: ContainerConfig, 
                  placements: List[Placement], 
                  block_dims: List[Tuple[int, int, int]], 
                  block_colors: Dict[Tuple[int, int, int], str]) -> go.Figure:
    """
    Create complete 3D plot with container and all blocks.
    
    Args:
        container: Container configuration
        placements: List of block placements
        block_dims: List of block dimensions
        block_colors: Dictionary mapping block dimensions to colors
        
    Returns:
        Complete Plotly Figure ready for display
    """
    fig = go.Figure()
    
    # Add container wireframe
    container_traces = create_container_wireframe(container)
    for trace in container_traces:
        fig.add_trace(trace)
    
    # Add all blocks
    for placement in placements:
        if placement.orientation:
            original_dims = block_dims[placement.block_index]
            color = block_colors[original_dims]
        else:
            dims = block_dims[placement.block_index]
            color = block_colors[dims]
        
        block_traces = create_block_visualization(placement, block_dims, color)
        for trace in block_traces:
            fig.add_trace(trace)
    
    # Configure layout for optimal viewing
    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y", 
            zaxis_title="Z",
            aspectmode="manual",
            aspectratio=dict(
                x=container.dx / max(container.dx, container.dy, container.dz),
                y=container.dy / max(container.dx, container.dy, container.dz),
                z=container.dz / max(container.dx, container.dy, container.dz)
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        title="3D Packing Visualization"
    )
    
    return fig
