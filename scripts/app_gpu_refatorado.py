"""
Sistema de Empacotamento 3D com GPU
===================================

Interface Streamlit para visualização e otimização de empacotamento 3D de blocos
utilizando algoritmos GPU heurísticos com suporte a rotação.

Autor: Sistema de Empacotamento
Data: 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib import cm
import warnings
import random
import json
from math import ceil
from distribuir_milp import Cuboid
from run_packing_gpu import gpu_heuristic_pack

# ==========================================
# CONFIGURAÇÕES GLOBAIS
# ==========================================

warnings.filterwarnings('ignore')
st.set_page_config(page_title="GPU Packing 3D", layout="wide")

# ==========================================
# CLASSES E ESTRUTURAS DE DADOS
# ==========================================

class ContainerConfig:
    """Configuração do container 3D"""
    def __init__(self, dx: int, dy: int, dz: int):
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.volume = dx * dy * dz

class BlockType:
    """Tipo de bloco com dimensões e quantidade"""
    def __init__(self, dx: int, dy: int, dz: int, quantidade: int):
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.quantidade = quantidade
        self.volume = dx * dy * dz

# ==========================================
# FUNÇÕES UTILITÁRIAS
# ==========================================

def get_orientations(lx: int, ly: int, lz: int) -> list:
    """
    Retorna todas as orientações possíveis de um bloco (rotações).
    
    Args:
        lx, ly, lz: Dimensões do bloco
        
    Returns:
        Lista de tuplas com todas as orientações possíveis
    """
    import itertools
    dims = [lx, ly, lz]
    return list(set(itertools.permutations(dims)))

def generate_viridis_colors(n_types: int) -> dict:
    """
    Gera cores da paleta viridis para diferentes tipos de blocos.
    
    Args:
        n_types: Número de tipos diferentes de blocos
        
    Returns:
        Dicionário mapeando dimensões para cores hex
    """
    viridis = matplotlib.cm.get_cmap('viridis', n_types)
    return {i: matplotlib.colors.to_hex(viridis(i)) for i in range(n_types)}

def calculate_max_capacity(container: ContainerConfig, block_dims: list) -> int:
    """
    Calcula a capacidade máxima teórica do container.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Número máximo de blocos que cabem teoricamente
    """
    if not block_dims:
        return 0
    
    block_volumes = [lx * ly * lz for lx, ly, lz in block_dims]
    used_volume = 0
    max_blocks = 0
    
    for vol in block_volumes:
        if used_volume + vol <= container.volume:
            used_volume += vol
            max_blocks += 1
        else:
            break
    
    return max_blocks

# ==========================================
# ALGORITMOS DE EMPACOTAMENTO
# ==========================================

def greedy_pack_sequential(container: ContainerConfig, block_dims: list) -> list:
    """
    Empacotamento sequencial ULTRA compacto: preenche sem deixar buracos.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de posicionamentos (x, y, z, block_index)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    # Para cada bloco, encontra a primeira posição válida sequencialmente
    for bloco_idx, (lx, ly, lz) in enumerate(block_dims):
        colocado = False
        
        # Percorre o container de forma SEQUENCIAL: x -> y -> z
        for x in range(container.dx - lx + 1):
            if colocado:
                break
            for y in range(container.dy - ly + 1):
                if colocado:
                    break
                for z in range(container.dz - lz + 1):
                    # Verifica se o espaço está totalmente livre
                    if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                        # Marca o espaço como ocupado
                        ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                        # Adiciona o bloco
                        placements.append((x, y, z, bloco_idx))
                        colocado = True
                        break
        
        # Se não conseguiu colocar o bloco, para de tentar
        if not colocado:
            st.warning(f"⚠️ Não foi possível encaixar o bloco {bloco_idx+1}. Parando no bloco {len(placements)}.")
            break
    
    return placements

def greedy_pack_with_rotation(container: ContainerConfig, block_dims: list) -> list:
    """
    Empacotamento sequencial com ROTAÇÃO: maximiza preenchimento.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de posicionamentos (x, y, z, block_index, orientation)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    # Para cada bloco, tenta todas as rotações possíveis
    for bloco_idx, original_dims in enumerate(block_dims):
        colocado = False
        orientations = get_orientations(*original_dims)
        
        # Tenta cada orientação
        for orientation in orientations:
            if colocado:
                break
            lx, ly, lz = orientation
            
            # Percorre o container sequencialmente
            for x in range(container.dx - lx + 1):
                if colocado:
                    break
                for y in range(container.dy - ly + 1):
                    if colocado:
                        break
                    for z in range(container.dz - lz + 1):
                        # Verifica se o espaço está livre
                        if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                            # Marca como ocupado
                            ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                            # Salva com a orientação usada
                            placements.append((x, y, z, bloco_idx, orientation))
                            colocado = True
                            break
        
        if not colocado:
            st.warning(f"⚠️ Bloco {bloco_idx+1} não coube em nenhuma orientação. Parando.")
            break
    
    return placements

def gpu_optimize_packing(container: ContainerConfig, block_dims: list, target_blocks: int) -> list:
    """
    Fase 2: Empacotamento compacto COM ROTAÇÃO usando GPU.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        target_blocks: Número alvo de blocos para encaixar
        
    Returns:
        Lista de posicionamentos otimizados
    """
    st.write(f"🎯 META: Tentar encaixar {target_blocks} blocos com ROTAÇÃO")
    
    # Chama a função com rotação
    placements = greedy_pack_with_rotation(container, block_dims[:target_blocks])
    count = len(placements)
    st.write(f"📊 Greedy com rotação conseguiu: {count} blocos")
    st.success(f"🏆 Resultado: Empacotamento COM ROTAÇÃO: {count} blocos!")
    
    return placements

# ==========================================
# VISUALIZAÇÃO 3D
# ==========================================

def create_container_wireframe(container: ContainerConfig) -> list:
    """
    Cria o wireframe (arestas) do container.
    
    Args:
        container: Configuração do container
        
    Returns:
        Lista de traços Plotly para as arestas do container
    """
    cd = Cuboid(container.dx, container.dy, container.dz)
    traces = []
    
    # Vértices do container
    verts = cd._get_vertices((0, 0, 0), container.dx, container.dy, container.dz)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # base inferior
        (4, 5), (5, 6), (6, 7), (7, 4),  # topo
        (0, 4), (1, 5), (2, 6), (3, 7)   # laterais
    ]
    
    for e in edges:
        x0, y0, z0 = verts[e[0]]
        x1, y1, z1 = verts[e[1]]
        traces.append(go.Scatter3d(
            x=[x0, x1], y=[y0, y1], z=[z0, z1],
            mode='lines',
            line=dict(color='gray', width=4),
            showlegend=False
        ))
    
    return traces

def create_block_visualization(placement: tuple, block_dims: list, color: str) -> list:
    """
    Cria a visualização de um bloco individual (faces + bordas).
    
    Args:
        placement: Tupla com posicionamento do bloco
        block_dims: Lista de dimensões dos blocos
        color: Cor do bloco em formato hex
        
    Returns:
        Lista de traços Plotly para o bloco
    """
    traces = []
    
    # Extrai informações do posicionamento
    if len(placement) == 5:
        x0, y0, z0, o, orientation = placement
        lx, ly, lz = orientation
    else:
        x0, y0, z0, o = placement
        lx, ly, lz = block_dims[o]
    
    # Faces sólidas sem efeitos extras
    faces_coords = [
        # Face inferior
        dict(x=[[x0, x0+lx], [x0, x0+lx]], y=[[y0, y0], [y0+ly, y0+ly]], z=[[z0, z0], [z0, z0]]),
        # Face superior
        dict(x=[[x0, x0+lx], [x0, x0+lx]], y=[[y0, y0], [y0+ly, y0+ly]], z=[[z0+lz, z0+lz], [z0+lz, z0+lz]]),
        # Face frontal
        dict(x=[[x0, x0+lx], [x0, x0+lx]], y=[[y0, y0], [y0, y0]], z=[[z0, z0], [z0+lz, z0+lz]]),
        # Face traseira
        dict(x=[[x0, x0+lx], [x0, x0+lx]], y=[[y0+ly, y0+ly], [y0+ly, y0+ly]], z=[[z0, z0], [z0+lz, z0+lz]]),
        # Face esquerda
        dict(x=[[x0, x0], [x0, x0]], y=[[y0, y0+ly], [y0, y0+ly]], z=[[z0, z0], [z0+lz, z0+lz]]),
        # Face direita
        dict(x=[[x0+lx, x0+lx], [x0+lx, x0+lx]], y=[[y0, y0+ly], [y0, y0+ly]], z=[[z0, z0], [z0+lz, z0+lz]])
    ]
    
    # Adiciona faces sólidas
    for face in faces_coords:
        traces.append(go.Surface(
            x=face['x'], y=face['y'], z=face['z'],
            colorscale=[[0, color], [1, color]],
            showscale=False
        ))
    
    # Adiciona bordas pretas
    edges = [
        [(x0,y0,z0), (x0+lx,y0,z0)], [(x0+lx,y0,z0), (x0+lx,y0+ly,z0)],
        [(x0+lx,y0+ly,z0), (x0,y0+ly,z0)], [(x0,y0+ly,z0), (x0,y0,z0)],
        [(x0,y0,z0+lz), (x0+lx,y0,z0+lz)], [(x0+lx,y0,z0+lz), (x0+lx,y0+ly,z0+lz)],
        [(x0+lx,y0+ly,z0+lz), (x0,y0+ly,z0+lz)], [(x0,y0+ly,z0+lz), (x0,y0,z0+lz)],
        [(x0,y0,z0), (x0,y0,z0+lz)], [(x0+lx,y0,z0), (x0+lx,y0,z0+lz)],
        [(x0+lx,y0+ly,z0), (x0+lx,y0+ly,z0+lz)], [(x0,y0+ly,z0), (x0,y0+ly,z0+lz)]
    ]
    
    for p1, p2 in edges:
        traces.append(go.Scatter3d(
            x=[p1[0], p2[0]],
            y=[p1[1], p2[1]],
            z=[p1[2], p2[2]],
            mode='lines',
            line=dict(color='black', width=4),
            showlegend=False
        ))
    
    return traces

def create_3d_plot(container: ContainerConfig, placements: list, block_dims: list, tipo_cores: dict) -> go.Figure:
    """
    Cria o gráfico 3D completo com container e blocos.
    
    Args:
        container: Configuração do container
        placements: Lista de posicionamentos dos blocos
        block_dims: Lista de dimensões dos blocos
        tipo_cores: Dicionário de cores por tipo de bloco
        
    Returns:
        Figura Plotly pronta para exibição
    """
    fig = go.Figure()
    
    # Adiciona wireframe do container
    container_traces = create_container_wireframe(container)
    for trace in container_traces:
        fig.add_trace(trace)
    
    # Adiciona blocos
    for placement in placements:
        if len(placement) == 5:
            _, _, _, o, orientation = placement
            original_dims = block_dims[o]
            cor = tipo_cores[original_dims]
        else:
            _, _, _, o = placement
            lx, ly, lz = block_dims[o]
            cor = tipo_cores[(lx, ly, lz)]
        
        block_traces = create_block_visualization(placement, block_dims, cor)
        for trace in block_traces:
            fig.add_trace(trace)
    
    # Configuração do layout
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
            )
        ),
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    return fig

# ==========================================
# INTERFACE STREAMLIT
# ==========================================

def render_header():
    """Renderiza o cabeçalho da aplicação"""
    st.title("🎯 Empacotamento 3D com GPU")
    st.markdown("*Sistema avançado de otimização de empacotamento com algoritmos GPU e suporte a rotação*")

def render_container_config() -> ContainerConfig:
    """
    Renderiza a seção de configuração do container.
    
    Returns:
        Configuração do container
    """
    st.subheader("📐 Configuração do Container")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dx = st.number_input("Dimensão X do contêiner", min_value=1, value=30)
    with col2:
        dy = st.number_input("Dimensão Y do contêiner", min_value=1, value=40)
    with col3:
        dz = st.number_input("Dimensão Z do contêiner", min_value=1, value=50)
    
    return ContainerConfig(dx, dy, dz)

def render_block_types_config() -> pd.DataFrame:
    """
    Renderiza a seção de configuração dos tipos de blocos.
    
    Returns:
        DataFrame com os tipos de blocos configurados
    """
    st.subheader("📦 Tipos de Blocos")
    initial = {"dx": [1], "dy": [1], "dz": [2], "quantidade": [100]}
    types_raw = st.data_editor(initial, num_rows="dynamic", key="block_types")
    
    if isinstance(types_raw, dict):
        return pd.DataFrame(types_raw)
    return types_raw

def render_gpu_parameters():
    """Renderiza os parâmetros da heurística GPU"""
    st.sidebar.subheader("⚙️ Parâmetros da Heurística GPU")
    pop_size = st.sidebar.slider("Tamanho da população", min_value=64, max_value=16384, value=2048, step=64)
    return pop_size

def process_block_data(types_df: pd.DataFrame) -> list:
    """
    Processa os dados dos tipos de blocos.
    
    Args:
        types_df: DataFrame com os tipos de blocos
        
    Returns:
        Lista de dimensões dos blocos expandida
    """
    # Filtra linhas válidas
    types_df_valid = types_df.dropna(subset=["dx", "dy", "dz", "quantidade"])
    types_df_valid = types_df_valid[types_df_valid["quantidade"] > 0]

    # Expande os blocos
    block_dims = []
    for _, row in types_df_valid.iterrows():
        dims = (int(row.dx), int(row.dy), int(row.dz))
        qtd = int(row.quantidade)
        block_dims.extend([dims] * qtd)

    # Ordena do maior para o menor volume
    block_dims.sort(key=lambda dims: dims[0]*dims[1]*dims[2], reverse=True)
    
    return block_dims

def display_analysis_results(container: ContainerConfig, block_dims: list, placements: list):
    """
    Exibe os resultados da análise de empacotamento.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        placements: Lista de posicionamentos resultantes
    """
    st.subheader("📊 Análise de Resultados")
    
    # Informações básicas
    st.write(f"📏 Container: {container.dx}×{container.dy}×{container.dz} = {container.volume} unidades")
    st.write(f"📦 Tipos de blocos únicos: {len(set(block_dims))}")
    st.write(f"🎯 Total de blocos solicitados: {len(block_dims)}")
    
    # Resultados do empacotamento
    count = len(placements)
    st.success(f"✅ RESULTADO FINAL: {count} blocos empacotados de {len(block_dims)} solicitados!")
    
    if count < len(block_dims):
        faltam = len(block_dims) - count
        st.warning(f"⚠️ Atenção: {faltam} blocos ficaram de fora por falta de espaço no container.")

def main():
    """Função principal da aplicação"""
    
    # Renderiza interface
    render_header()
    
    # Configurações
    container = render_container_config()
    types_df = render_block_types_config()
    pop_size = render_gpu_parameters()
    
    # Botão de execução
    if st.button("🚀 Executar GPU Heurística", type="primary"):
        
        # Processa dados dos blocos
        block_dims = process_block_data(types_df)
        
        if not block_dims:
            st.error("❌ Nenhum bloco válido configurado!")
            return
        
        # Calcula capacidade máxima
        max_blocks = calculate_max_capacity(container, block_dims)
        
        # Executa empacotamento
        with st.spinner("🔄 Executando algoritmo de empacotamento..."):
            placements = gpu_optimize_packing(container, block_dims, max_blocks)
        
        # Gera cores usando paleta viridis
        tipos_unicos = list(set(block_dims))
        cores_viridis = generate_viridis_colors(len(tipos_unicos))
        tipo_cores = {dims: cores_viridis[i] for i, dims in enumerate(tipos_unicos)}
        
        # Salva no session state
        st.session_state["placements"] = placements
        st.session_state["tipo_cores"] = tipo_cores
        st.session_state["container"] = container
        st.session_state["block_dims"] = block_dims
        
        # Exibe resultados
        display_analysis_results(container, block_dims, placements)
    
    # Visualização 3D
    if "placements" in st.session_state:
        st.subheader("🎨 Visualização 3D Interativa")
        
        try:
            # Recupera dados do session state
            placements = st.session_state["placements"]
            tipo_cores = st.session_state["tipo_cores"]
            container = st.session_state["container"]
            block_dims = st.session_state["block_dims"]
            
            # Cria e exibe gráfico
            fig = create_3d_plot(container, placements, block_dims, tipo_cores)
            st.plotly_chart(fig, use_container_width=True)
            
        except ImportError:
            st.error("❌ Erro: Plotly não está instalado. Execute: pip install plotly")
        except Exception as e:
            st.error(f"❌ Erro na visualização: {str(e)}")

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":
    main()
