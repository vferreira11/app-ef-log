"""
Sistema de Empacotamento 3D - Aplicação Principal Streamlit
=========================================================

Interface Streamlit limpa e modular para otimização de empacotamento 3D.
Usa algoritmos acelerados por GPU com suporte a rotação e visualização avançada.

Uso:
    streamlit run app_gpu_fixed.py
"""

import streamlit as st
import pandas as pd
import sys
import os

# Adiciona o diretório scripts ao path para imports
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(scripts_dir)

# Importa componentes modulares
from scripts.core.models import ContainerConfig, Placement
from scripts.core.algorithms import gpu_optimize_packing
from scripts.core.visualization import create_3d_plot
from scripts.core.utils import (
    calculate_max_capacity, 
    map_block_colors, 
    calculate_efficiency,
    format_dimensions,
    validate_block_data
)
from scripts.config.settings import (
    DEFAULT_CONTAINER_DIMS,
    DEFAULT_BLOCK_TYPES, 
    GPU_POPULATION_RANGE,
    MAX_BLOCKS_WARNING,
    UI_MESSAGES
)

# Configura Streamlit
st.set_page_config(
    page_title="Empacotamento 3D GPU", 
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_header():
    """Renderiza cabeçalho e descrição do aplicativo."""
    st.title("🎯 Sistema de Empacotamento 3D GPU")
    st.markdown("""
    *Otimização avançada de empacotamento 3D com aceleração GPU e algoritmos inteligentes de rotação*
    
    📊 **Recursos**: Otimização GPU • Suporte a rotação • Visualização 3D em tempo real • Paleta de cores Viridis
    """)


def render_gpu_parameters() -> int:
    """
    Renderiza parâmetros do algoritmo GPU.
    
    Retorna:
        Tamanho da população para algoritmo GPU
    """
    st.subheader("⚙️ Parâmetros da Heurística GPU")
    
    pop_size = st.slider(
        "Tamanho da População",
        min_value=GPU_POPULATION_RANGE['min'],
        max_value=GPU_POPULATION_RANGE['max'],
        value=GPU_POPULATION_RANGE['default'],
        step=GPU_POPULATION_RANGE['step'],
        help="Valores maiores podem melhorar o resultado, mas aumentam o tempo de execução"
    )
    
    st.markdown("""
    **Recursos do Algoritmo:**
    - ✅ Otimização de rotação
    - ✅ Aceleração GPU  
    - ✅ Preenchimento de lacunas
    - ✅ Maximização de eficiência
    """)
    
    return pop_size


def render_container_section() -> ContainerConfig:
    """
    Renderiza a seção de configuração do container.
    
    Retorna:
        Objeto ContainerConfig configurado
    """
    st.subheader("📐 Configuração do Container")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dx = st.number_input(
            "Largura (X)", 
            min_value=1, 
            value=DEFAULT_CONTAINER_DIMS['dx'],
            help="Dimensão de largura do container"
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
    
    # Exibe informações do container
    st.info(f"📦 Container: {format_dimensions(container.dimensions())} | Volume: {container.volume:,} unidades")
    
    return container


def render_blocks_section() -> pd.DataFrame:
    """
    Renderiza a seção de configuração dos tipos de bloco.
    
    Retorna:
        DataFrame com configuração dos tipos de bloco
    """
    st.subheader("📦 Configuração dos Tipos de Bloco")
    
    # Instruções
    st.markdown("*Defina diferentes tipos de bloco com suas dimensões e quantidades*")
    
    # Editor de dados
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


def process_block_data(types_data) -> list:
    """
    Processa e valida os dados dos tipos de bloco.
    
    Args:
        types_data: DataFrame ou lista com tipos de bloco
        
    Retorna:
        Lista de tuplas de dimensões dos blocos
    """
    # Converte para DataFrame se necessário
    if isinstance(types_data, list):
        types_df = pd.DataFrame(types_data)
    else:
        types_df = types_data
    
    # Usa função utilitária para validação
    block_dims = validate_block_data(types_df)
    
    if not block_dims:
        return []
    
    # Debug: mostra os dados processados
    unique_types = list(set(block_dims))
    st.write(f"🔍 Dados processados: {len(unique_types)} tipos únicos, {len(block_dims)} blocos totais")
    
    for i, block_type in enumerate(unique_types, 1):
        count_this_type = block_dims.count(block_type)
        st.write(f"   • Tipo {i}: {block_type[0]}×{block_type[1]}×{block_type[2]} ({count_this_type} unidades)")
    
    return block_dims


def display_analysis_metrics(container: ContainerConfig, block_dims: list, placements: list):
    """
    Exibe análise e métricas do empacotamento.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        placements: Lista de alocações bem-sucedidas
    """
    st.subheader("📊 Análise do Empacotamento")
    
    # Calcula tipos únicos corretamente
    unique_block_types = list(set(block_dims))
    unique_count = len(unique_block_types)
    
    # Debug: mostra os tipos únicos encontrados
    st.write(f"🔍 Tipos únicos detectados ({unique_count}):")
    for i, block_type in enumerate(unique_block_types, 1):
        count_this_type = block_dims.count(block_type)
        st.write(f"   • Tipo {i}: {block_type[0]}×{block_type[1]}×{block_type[2]} ({count_this_type} unidades)")
    
    # Cria colunas de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Volume do Container",
            f"{container.volume:,}",
            help="Capacidade total do container"
        )
    
    with col2:
        st.metric(
            "Tipos de Bloco", 
            unique_count,
            help="Número de tipos diferentes de bloco"
        )
    
    with col3:
        placed_count = len(placements)
        total_count = len(block_dims)
        st.metric(
            "Blocos Alocados",
            f"{placed_count}/{total_count}",
            help="Blocos alocados com sucesso"
        )
    
    with col4:
        efficiency = calculate_efficiency(placed_count, total_count)
        st.metric(
            "Eficiência",
            f"{efficiency:.1f}%",
            help="Percentual de eficiência do empacotamento"
        )
    
    # Mensagens de status
    placed_count = len(placements)
    total_count = len(block_dims)
    
    if placed_count == total_count:
        st.success(UI_MESSAGES['success_perfect'].format(total_count))
    elif placed_count > 0:
        missing = total_count - placed_count
        st.warning(UI_MESSAGES['warning_partial'].format(missing))
    else:
        st.error(UI_MESSAGES['error_no_blocks'])


def run_packing_algorithm(container: ContainerConfig, block_dims: list, pop_size: int) -> list:
    """
    Executa o algoritmo de empacotamento com indicação de progresso.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        pop_size: Tamanho da população GPU
        
    Retorna:
        Lista de alocações
    """
    if not block_dims:
        st.error("❌ Nenhum bloco válido para empacotar!")
        return []
    
    # Aviso de performance
    if len(block_dims) > MAX_BLOCKS_WARNING:
        st.warning(UI_MESSAGES['warning_performance'].format(len(block_dims)))
    
    # Calcula capacidade
    max_capacity = calculate_max_capacity(container.volume, block_dims)
    st.info(UI_MESSAGES['info_capacity'].format(max_capacity))
    
    # Executa algoritmo com progresso
    with st.spinner("🚀 Executando algoritmo de otimização GPU..."):
        placements = gpu_optimize_packing(container, block_dims, max_capacity)
    
    return placements


def render_visualization(container: ContainerConfig, placements: list, block_dims: list):
    """
    Renderiza a seção de visualização 3D.
    
    Args:
        container: Configuração do container
        placements: Lista de alocações dos blocos
        block_dims: Lista de dimensões dos blocos
    """
    if not placements:
        st.warning("Nenhum bloco para visualizar.")
        return
    
    st.subheader("🎨 Visualização 3D Interativa")
    
    try:
        # Gera cores usando paleta Viridis
        block_colors = map_block_colors(block_dims)
        
        # Cria e exibe gráfico
        fig = create_3d_plot(container, placements, block_dims, block_colors)
        st.plotly_chart(fig, use_container_width=True)
        
        # Informações da visualização
        st.markdown("""
        **Controles da Visualização:**
        - 🖱️ **Rotacionar**: Clique e arraste
        - 🔍 **Zoom**: Roda do mouse ou gesto de pinça
        - 📐 **Mover**: Shift + clique e arraste
        - 🎨 **Cores**: Paleta Viridis para tipos de bloco
        """)
        
    except Exception as e:
        st.error(f"❌ Erro na visualização: {str(e)}")


def main():
    """Ponto de entrada principal da aplicação."""
    
    # Cabeçalho
    render_header()

    # Parâmetros da heurística GPU (acima do container)
    pop_size = render_gpu_parameters()

    # Seções principais de configuração
    container = render_container_section()
    types_df = render_blocks_section()

    # Botão de execução
    show_graph = False
    if st.button("🚀 Executar GPU Heurística", type="primary", use_container_width=True):
        # FORÇA limpeza completa do estado da sessão
        for key in list(st.session_state.keys()):
            if key.startswith(('placements', 'container', 'block_dims', 'last_run', 'tipo_cores')):
                del st.session_state[key]
        
        st.session_state['placements'] = []
        st.session_state['container'] = None
        st.session_state['block_dims'] = []
        st.session_state['last_run'] = False

        # Processa dados de entrada com validação completa
        st.write(UI_MESSAGES['info_processing'])
        block_dims = process_block_data(types_df)
        
        # Remove possíveis valores None ou inválidos
        block_dims = [dims for dims in block_dims if dims is not None and all(d > 0 for d in dims)]
        
        if not block_dims:
            st.error("❌ Configure pelo menos um tipo de bloco válido.")
            return
            
        # Executa algoritmo de empacotamento
        placements = run_packing_algorithm(container, block_dims, pop_size)
        
        # Armazena resultados no estado da sessão
        st.session_state.update({
            'placements': placements,
            'container': container,
            'block_dims': block_dims,
            'last_run': True
        })
        
        # Exibe resultados
        display_analysis_metrics(container, block_dims, placements)
        show_graph = True

    # Seção de visualização (apenas se botão foi pressionado)
    if show_graph and st.session_state.get('last_run', False):
        render_visualization(
            st.session_state['container'],
            st.session_state['placements'],
            st.session_state['block_dims']
        )


if __name__ == "__main__":
    main()
