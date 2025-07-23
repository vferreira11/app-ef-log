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
    validate_block_data,
    generate_random_orders,
    convert_orders_to_block_dims,
    calculate_sales_analytics,
    generate_packing_summary,
    validate_block_dimensions
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


def render_gpu_parameters() -> tuple:
    """
    Renderiza parâmetros do algoritmo GPU.
    
    Retorna:
        Tuple: (Tamanho da população, Tipo de algoritmo)
    """
    st.subheader("⚙️ Configuração do Algoritmo")
    
    # Seleção do tipo de algoritmo
    algoritmo_tipo = st.selectbox(
        "Algoritmo de Empacotamento",
        options=["Híbrido Inteligente", "GPU Padrão", "Biomecânico (Ergonômico)", "Chão do Galpão"],
        index=0,  # Híbrido como padrão
        help="Escolha o algoritmo de empacotamento mais adequado para seu caso"
    )
    
    pop_size = st.slider(
        "Tamanho da População",
        min_value=GPU_POPULATION_RANGE['min'],
        max_value=GPU_POPULATION_RANGE['max'],
        value=GPU_POPULATION_RANGE['default'],
        step=GPU_POPULATION_RANGE['step'],
        help="Valores maiores podem melhorar o resultado, mas aumentam o tempo de execução"
    )
    
    # Mostra informações específicas do algoritmo selecionado
    if algoritmo_tipo == "Híbrido Inteligente":
        st.markdown("""
        **🎯 Algoritmo Híbrido Inteligente:**
        - ✅ **GPU**: Motor de otimização para múltiplas soluções
        - ✅ **Biomecânico**: Zoneamento ergonômico por classe ABC
        - ✅ **Chão do Galpão**: Empilhamento estável a partir de Z=0
        - ✅ **Greedy**: Seleção da melhor solução entre as ótimas
        """)
        st.info("🎯 **Melhor dos 3 Mundos**: Combina performance computacional, ergonomia humana e realismo físico para a solução ideal.")
    
    elif algoritmo_tipo == "Biomecânico (Ergonômico)":
        st.markdown("""
        **🧬 Algoritmo Biomecânico:**
        - ✅ Otimização ergonômica para operadores
        - ✅ Produtos pesados em altura ideal (100-160cm)
        - ✅ Produtos frequentes em zona de fácil acesso
        - ✅ Redução de lesões e fadiga
        """)
        st.info("🏥 **Foco Ergonômico**: Prioriza a saúde do operador alocando produtos baseado na frequência de uso e peso em zonas ergonômicas otimizadas.")
    
    elif algoritmo_tipo == "Chão do Galpão":
        st.markdown("""
        **🏭 Algoritmo Chão do Galpão:**
        - ✅ Empilhamento a partir do chão (Z=0)
        - ✅ Maximização de densidade
        - ✅ Simulação de armazém real
        - ✅ Fácil implementação física
        """)
        st.info("🏭 **Simulação Real**: Empilha produtos começando do chão, simulando um ambiente real de armazém.")
    
    else:  # GPU Padrão
        st.markdown("""
        **🚀 Algoritmo GPU Padrão:**
        - ✅ Otimização de rotação
        - ✅ Algoritmo genético acelerado
        - ✅ Empilhamento otimizado
        - ✅ Maximização de eficiência
        """)
        st.info("🚀 **Alto Desempenho**: Usa otimização genética com aceleração GPU para máxima eficiência de empacotamento.")
    
    return pop_size, algoritmo_tipo


def render_container_section() -> ContainerConfig:
    """
    Renderiza a seção de configuração do container.
    
    Retorna:
        Objeto ContainerConfig configurado
    """
    st.subheader("📐 Configuração do Container")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    with col4:
        quantidade = st.number_input(
            "Quantidade", 
            min_value=1, 
            max_value=10,
            value=1,
            help="Número de containers disponíveis"
        )
    
    container = ContainerConfig(dx, dy, dz, quantidade)
    
    # Exibe informações do container
    if container.quantidade == 1:
        st.info(f"📦 Container: {format_dimensions(container.dimensions())} | Volume: {container.volume:,} unidades")
    else:
        st.info(f"📦 {container.quantidade} Containers: {format_dimensions(container.dimensions())} cada | Volume total: {container.volume_total:,} unidades")
    
    return container


def render_blocks_section() -> pd.DataFrame:
    """
    Renderiza a seção de geração de pedidos aleatórios.
    
    Retorna:
        DataFrame com pedidos gerados
    """
    st.subheader("📦 Geração de Pedidos")
    
    # Instruções
    st.markdown("*Configure a quantidade de pedidos que serão gerados aleatoriamente*")
    st.info("ℹ️ **Limitação de Dimensões**: Todos os blocos são limitados a **máximo 10cm** em cada lado para garantir praticidade no manuseio e compactação otimizada.")
    
    # Slider para quantidade de pedidos
    n_orders = st.slider(
        "Número de Pedidos",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        help="Quantidade de pedidos que serão gerados automaticamente"
    )
    
    # Botão para gerar novos pedidos
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🎲 Gerar Pedidos", type="primary"):
            st.session_state.orders_df = generate_random_orders(n_orders)
            st.success(f"✅ {n_orders} pedidos gerados!")
    
    # Gera pedidos iniciais se não existirem
    if 'orders_df' not in st.session_state:
        st.session_state.orders_df = generate_random_orders(n_orders)
    
    # Atualiza se a quantidade mudou
    if len(st.session_state.orders_df) != n_orders:
        st.session_state.orders_df = generate_random_orders(n_orders)
    
    # Exibe a tabela de pedidos (somente leitura)
    st.markdown("### 📋 Pedidos Gerados")
    st.dataframe(
        st.session_state.orders_df,
        use_container_width=True,
        column_config={
            "SDK": st.column_config.TextColumn("SDK", width="small"),
            "Nome Produto": st.column_config.TextColumn("Produto", width="medium"),
            "Categoria": st.column_config.TextColumn("Categoria", width="small"),
            "Comprimento": st.column_config.NumberColumn("Comp.(cm)", width="small"),
            "Largura": st.column_config.NumberColumn("Larg.(cm)", width="small"), 
            "Profundidade": st.column_config.NumberColumn("Prof.(cm)", width="small"),
            "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", width="small", format="%.3f"),
            "Preço Unitário": st.column_config.TextColumn("Preço Unit.", width="small"),
            "Vendas 90 Dias": st.column_config.NumberColumn("Vendas 90d", width="small"),
            "Previsão Próx. Mês": st.column_config.NumberColumn("Prev. Mês", width="small")
        }
    )
    
    # Calcula e exibe estatísticas de vendas
    analytics = calculate_sales_analytics(st.session_state.orders_df)
    if analytics:
        st.markdown("### 📊 Análise de Vendas")
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Produtos", analytics['total_products'])
        with col2:
            st.metric("Vendas 90 Dias", f"{analytics['total_sales_90d']:,}")
        with col3:
            st.metric("Previsão Mês", f"{analytics['total_forecast']:,}")
        with col4:
            st.metric("Preço Médio", f"R$ {analytics['avg_price']:.2f}")
        
        # Receitas e peso
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Receita 90 Dias", f"R$ {analytics['total_revenue_90d']:,.2f}")
        with col2:
            st.metric("Receita Prevista", f"R$ {analytics['forecast_revenue']:,.2f}")
        with col3:
            st.metric("Peso Médio", f"{analytics['avg_weight']:.3f} kg")
        with col4:
            st.metric("Peso Total Previsto", f"{analytics['total_weight_forecast']:.2f} kg")
        
        # Análise por categoria
        st.markdown("#### 📈 Por Categoria")
        for category, data in analytics['by_category'].items():
            with st.expander(f"🏷️ {category} ({data['count']} produtos)"):
                subcol1, subcol2, subcol3 = st.columns(3)
                with subcol1:
                    st.write(f"**Vendas 90d:** {data['sales_90d']:,}")
                    st.write(f"**Previsão:** {data['forecast']:,}")
                    st.write(f"**Peso Médio:** {data['avg_weight']:.3f} kg")
                with subcol2:
                    st.write(f"**Preço Médio:** R$ {data['avg_price']:.2f}")
                    st.write(f"**Receita 90d:** R$ {data['revenue_90d']:,.2f}")
                    st.write(f"**Peso Total:** {data['total_weight_forecast']:.2f} kg")
                with subcol3:
                    growth = ((data['forecast'] * 3) / data['sales_90d'] - 1) * 100 if data['sales_90d'] > 0 else 0
                    trend = "📈" if growth > 0 else "📉" if growth < 0 else "➡️"
                    st.write(f"**Tendência:** {trend} {growth:+.1f}%")
                    # Densidade média da categoria
                    avg_volume = 0
                    if 'Comprimento' in st.session_state.orders_df.columns:
                        cat_orders = st.session_state.orders_df[st.session_state.orders_df['Categoria'] == category]
                        if not cat_orders.empty:
                            volumes = cat_orders['Comprimento'] * cat_orders['Largura'] * cat_orders['Profundidade']
                            avg_volume = volumes.mean()
                            if avg_volume > 0:
                                density = (data['avg_weight'] * 1000) / avg_volume  # g/cm³
                                st.write(f"**Densidade:** {density:.2f} g/cm³")
    
    return st.session_state.orders_df


def process_block_data(orders_data) -> list:
    """
    Processa e valida os dados dos pedidos baseado nas previsões de venda.
    
    Args:
        orders_data: DataFrame com pedidos gerados
        
    Retorna:
        Lista de tuplas de dimensões dos blocos (repetidos conforme previsão)
    """
    # Converte pedidos para dimensões de blocos usando previsões
    block_dims = convert_orders_to_block_dims(orders_data)
    
    if not block_dims:
        return []
    
    # Calcula totais para exibição
    total_forecast = orders_data['Previsão Próx. Mês'].sum()
    unique_products = len(orders_data)
    unique_types = list(set(block_dims))
    
    st.write(f"🔍 **Processamento para próximos 30 dias:**")
    st.write(f"   • **{unique_products} produtos únicos** gerando **{total_forecast:,} blocos totais**")
    st.write(f"   • **{len(unique_types)} tipos de dimensões** diferentes")
    
    # Agrupa por categoria para análise
    category_forecast = orders_data.groupby('Categoria')['Previsão Próx. Mês'].sum()
    st.write("� **Blocos por Categoria:**")
    for category, forecast in category_forecast.items():
        st.write(f"   • {category}: {forecast:,} blocos")
    
    return block_dims


def display_analysis_metrics(container: ContainerConfig, block_dims: list, placements: list, orders_df=None):
    """
    Exibe análise e métricas do empacotamento.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        placements: Lista de alocações bem-sucedidas
        orders_df: DataFrame com pedidos (opcional, para resumo detalhado)
    """
    st.subheader("📊 Análise do Empacotamento")
    
    # Calcula tipos únicos corretamente
    unique_block_types = list(set(block_dims))
    unique_count = len(unique_block_types)
    
    # Tipos únicos suprimidos para interface mais limpa
    # (disponível em expander se necessário para debug)
    with st.expander("🔍 Ver detalhes dos tipos de blocos", expanded=False):
        st.write(f"Tipos únicos detectados ({unique_count}):")
        for i, block_type in enumerate(unique_block_types, 1):
            count_this_type = block_dims.count(block_type)
            st.write(f"   • Tipo {i}: {block_type[0]}×{block_type[1]}×{block_type[2]} ({count_this_type} unidades)")
    
    # Cria colunas de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if container.quantidade == 1:
            st.metric(
                "Volume do Container",
                f"{container.volume:,}",
                help="Capacidade total do container"
            )
        else:
            st.metric(
                f"Volume Total ({container.quantidade} containers)",
                f"{container.volume_total:,}",
                help=f"Capacidade total de {container.quantidade} containers"
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
    
    # Resumo detalhado por produto (se orders_df disponível)
    if orders_df is not None:
        st.markdown("### 📋 Resumo por Produto")
        packing_summary = generate_packing_summary(orders_df, placements, total_count)
        
        # Métricas de resumo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Blocos", f"{packing_summary['total_blocks']:,}")
        with col2:
            st.metric("Blocos Empacotados", f"{packing_summary['packed_blocks']:,}")
        with col3:
            st.metric("Eficiência Geral", f"{packing_summary['efficiency']:.1f}%")
        
        # Tabela detalhada por produto
        if packing_summary['products']:
            df_summary = pd.DataFrame(packing_summary['products'])
            st.dataframe(
                df_summary,
                use_container_width=True,
                column_config={
                    "sdk": st.column_config.TextColumn("SDK", width="small"),
                    "produto": st.column_config.TextColumn("Produto", width="medium"),
                    "categoria": st.column_config.TextColumn("Categoria", width="small"),
                    "previsao": st.column_config.NumberColumn("Previsto", width="small"),
                    "empacotado": st.column_config.NumberColumn("Empacotado", width="small"),
                    "pendente": st.column_config.NumberColumn("Pendente", width="small"),
                    "dimensoes": st.column_config.TextColumn("Dimensões", width="small")
                }
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


def run_packing_algorithm(container: ContainerConfig, block_dims: list, pop_size: int, produtos_df=None, algoritmo_tipo="GPU Padrão") -> list:
    """
    Executa o algoritmo de empacotamento com indicação de progresso.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        pop_size: Tamanho da população GPU
        produtos_df: DataFrame com dados dos produtos (opcional)
        algoritmo_tipo: Tipo de algoritmo a ser usado
        
    Retorna:
        Lista de alocações
    """
    if not block_dims:
        st.error("❌ Nenhum bloco válido para empacotar!")
        return []
    
    # Aviso de performance
    if len(block_dims) > MAX_BLOCKS_WARNING:
        st.warning(UI_MESSAGES['warning_performance'].format(len(block_dims)))
    
    # Calcula capacidade - considera múltiplos containers
    max_capacity = calculate_max_capacity(container.volume_total, block_dims)
    st.info(UI_MESSAGES['info_capacity'].format(max_capacity))
    
    # Escolhe algoritmo baseado na seleção do usuário
    if algoritmo_tipo == "Híbrido Inteligente" and produtos_df is not None and not produtos_df.empty:
        spinner_msg = "🎯 Executando algoritmo híbrido inteligente..."
    elif algoritmo_tipo == "Biomecânico (Ergonômico)" and produtos_df is not None and not produtos_df.empty:
        spinner_msg = "🧬 Executando algoritmo biomecânico otimizado..."
    elif algoritmo_tipo == "Chão do Galpão":
        spinner_msg = "🏭 Executando algoritmo de chão do galpão..."
    else:
        spinner_msg = "🚀 Executando algoritmo de otimização GPU..."
    
    # Executa algoritmo com progresso
    with st.spinner(spinner_msg):
        if algoritmo_tipo == "Híbrido Inteligente" and produtos_df is not None and not produtos_df.empty:
            placements = gpu_optimize_packing(container, block_dims, max_capacity, produtos_df, force_floor=True, hybrid_mode=True)
        elif algoritmo_tipo == "Biomecânico (Ergonômico)" and produtos_df is not None and not produtos_df.empty:
            placements = gpu_optimize_packing(container, block_dims, max_capacity, produtos_df, force_floor=False)
        elif algoritmo_tipo == "Chão do Galpão":
            placements = gpu_optimize_packing(container, block_dims, max_capacity, None, force_floor=True)
        else:
            placements = gpu_optimize_packing(container, block_dims, max_capacity, None, force_floor=False)
    
    return placements


def render_visualization(container: ContainerConfig, placements: list, block_dims: list):
    """
    Renderiza a seção de visualização 3D estacionária.
    
    Args:
        container: Configuração do container
        placements: Lista de alocações dos blocos
        block_dims: Lista de dimensões dos blocos
    """
    if not placements:
        st.warning("Nenhum bloco para visualizar.")
        return
    
    st.subheader("🎨 Visualização 3D do Empacotamento")
    
    try:
        # Gera cores usando paleta Viridis
        block_colors = map_block_colors(block_dims)
        
        # Cria e exibe gráfico estacionário
        fig = create_3d_plot(container, placements, block_dims, block_colors)
        
        # Debug: verificar se a figura foi criada
        if fig is None:
            st.error("❌ Figura 3D não foi criada corretamente.")
            return
            
        if len(fig.data) == 0:
            st.error("❌ Figura 3D criada mas sem dados de renderização.")
            return
        
        # Mensagem de debug suprimida para interface mais limpa
        # st.write(f"🔍 Debug: Figura criada com {len(fig.data)} traces")
        
        print(f"[DEBUG] Renderizando visualização com {len(fig.data)} traces")
        
        # Configurações otimizadas com controles visíveis
        config = {
            'displayModeBar': True,   # Mantém controles visíveis
            'staticPlot': False,      # Permite renderização 3D
            'responsive': True,       # Responsivo
            'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],  # Remove botões 2D desnecessários
            'displaylogo': False      # Remove logo Plotly
        }
        
        print(f"[DEBUG] Usando configuração: {config}")
        
        # Renderiza o gráfico
        st.plotly_chart(fig, use_container_width=True, config=config)
        
        print(f"[DEBUG] Gráfico renderizado com sucesso")
        
        # Legenda de cores dos objetos
        st.write("### 🎨 Legenda de Cores")
        
        # Organiza a legenda em colunas para melhor layout
        unique_types = list(set(block_dims))
        unique_types.sort()  # Ordena para consistência
        
        # Calcula número de colunas baseado na quantidade de tipos
        num_types = len(unique_types)
        cols_per_row = min(4, num_types)  # Máximo 4 colunas
        
        # Cria colunas para a legenda
        legend_cols = st.columns(cols_per_row)
        
        for i, block_type in enumerate(unique_types):
            col_idx = i % cols_per_row
            with legend_cols[col_idx]:
                color = block_colors.get(block_type, '#000000')
                # Cria um pequeno quadrado colorido como indicador
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 20px; height: 20px; background-color: {color}; 
                                border: 1px solid #000; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 14px;">{block_type[0]}×{block_type[1]}×{block_type[2]}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Mapeamento de cores individual suprimido para interface mais limpa
        with st.expander("🎨 Ver mapeamento detalhado de cores", expanded=False):
            st.write("Mapeamento de cores Viridis:")
            for dims, color in block_colors.items():
                st.write(f"   • Tipo {dims[0]}×{dims[1]}×{dims[2]}: {color}")
        
        # Estatísticas da visualização
        placed_count = len(placements)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Blocos Visualizados", placed_count)
        with col2:
            st.metric("Tipos de Cores", len(block_colors))
        with col3:
            volume_usado = sum(block_dims[i][0] * block_dims[i][1] * block_dims[i][2] 
                             for i in range(min(placed_count, len(block_dims))))
            st.metric("Volume Ocupado", f"{volume_usado:,}")
            
            
    except Exception as e:
        st.error(f"❌ Erro na visualização: {str(e)}")


def main():
    """Ponto de entrada principal da aplicação."""
    
    # Cabeçalho
    render_header()

    # Parâmetros da heurística GPU (acima do container)
    pop_size, algoritmo_tipo = render_gpu_parameters()

    # Seções principais de configuração
    container = render_container_section()
    orders_df = render_blocks_section()

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
        block_dims = process_block_data(orders_df)
        
        # Remove possíveis valores None ou inválidos
        block_dims = [dims for dims in block_dims if dims is not None and all(d > 0 for d in dims)]
        
        if not block_dims:
            st.error("❌ Erro ao processar pedidos. Verifique os dados gerados.")
            return
            
        # Executa algoritmo de empacotamento
        placements = run_packing_algorithm(container, block_dims, pop_size, orders_df, algoritmo_tipo)
        
        # Armazena resultados no estado da sessão
        st.session_state.update({
            'placements': placements,
            'container': container,
            'block_dims': block_dims,
            'orders_df': orders_df,  # Armazena orders_df para usar na análise
            'last_run': True
        })
        
        # Exibe resultados
        display_analysis_metrics(container, block_dims, placements, orders_df)
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
