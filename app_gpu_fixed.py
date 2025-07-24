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
import time
import random

# Adiciona o diretório scripts ao path para imports
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(scripts_dir)

# Importa componentes modulares
from scripts.core.models import ContainerConfig, Placement
from scripts.core.algorithms import gpu_optimize_packing, hybrid_intelligent_packing
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
    page_title=".: PARADOXO :.", 
    layout="wide",
    initial_sidebar_state="expanded"
)


def format_br_number(value, decimals=0):
    """
    Formata números no padrão brasileiro.
    
    Args:
        value: Número a ser formatado
        decimals: Número de casas decimais (0 para inteiros)
    
    Returns:
        String formatada no padrão brasileiro
    """
    if decimals == 0:
        # Para inteiros: usa ponto como separador de milhares
        return f"{int(value):,}".replace(',', '.')
    else:
        # Para decimais: vírgula decimal e ponto para milhares
        formatted = f"{value:,.{decimals}f}"
        # Troca vírgula por ponto para milhares, depois ponto por vírgula para decimal
        parts = formatted.split('.')
        if len(parts) > 1:
            decimal_part = parts[-1]
            integer_part = '.'.join(parts[:-1]).replace(',', '.')
            return f"{integer_part},{decimal_part}"
        else:
            return formatted.replace(',', '.')


def format_br_currency(value):
    """
    Formata valores monetários no padrão brasileiro.
    
    Args:
        value: Valor a ser formatado
    
    Returns:
        String formatada como moeda brasileira
    """
    return f"R$ {format_br_number(value, 2)}"


def format_br_percentage(value):
    """
    Formata porcentagens no padrão brasileiro.
    
    Args:
        value: Valor da porcentagem
    
    Returns:
        String formatada como porcentagem brasileira
    """
    return f"{format_br_number(value, 1)}%"


def get_creative_loading_messages():
    """
    Retorna lista de mensagens criativas de loading estilo The Sims.
    
    Returns:
        Lista de mensagens de loading temáticas
    """
    return [
        "📦 Organizando produtos no depósito",
        "🎯 Calculando posições otimizadas", 
        "🔧 Ajustando algoritmos híbridos",
        "🧠 Aplicando inteligência biomecânica",
        "🚀 Executando otimização GPU",
        "📏 Medindo espaços disponíveis",
        "🏗️ Construindo layout 3D",
        "⚖️ Balanceando distribuição de peso",
        "🎨 Gerando paleta de cores",
        "📊 Analisando eficiência espacial",
        "🔍 Verificando colisões",
        "✨ Aplicando toque final",
        "🎪 Preparando visualização mágica"
    ]


def show_loading_screen():
    """
    Exibe tela de loading criativa com mensagens dinâmicas.
    
    Returns:
        Container placeholder para controle da tela
    """
    # Cria placeholder que vai ocupar toda a tela
    placeholder = st.empty()
    
    # Estilo CSS para tela de loading
    loading_style = """
    <style>
    .loading-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(26, 28, 36, 0.95);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .loading-title {
        font-size: 2.5rem;
        margin-bottom: 2rem;
        color: #00D4AA;
        font-weight: bold;
    }
    
    .loading-message {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
        min-height: 2rem;
    }
    
    .loading-dots {
        font-size: 2rem;
        color: #00D4AA;
        margin-top: 1rem;
        min-height: 3rem;
    }
    
    .loading-spinner {
        border: 4px solid #333;
        border-top: 4px solid #00D4AA;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 2s linear infinite;
        margin: 2rem 0;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """
    
    return placeholder, loading_style


def update_loading_message(placeholder, style, message, dots):
    """
    Atualiza a mensagem de loading com animação de pontos.
    
    Args:
        placeholder: Container do Streamlit
        style: CSS da tela de loading
        message: Mensagem atual
        dots: Número de pontos (1-3)
    """
    dots_display = "." * dots
    
    html_content = f"""
    {style}
    <div class="loading-container">
        <div class="loading-title">⏳ AGUARDE. VALERÁ A PENA!</div>
        <div class="loading-spinner"></div>
        <div class="loading-message">{message}</div>
        <div class="loading-dots">{dots_display}</div>
    </div>
    """
    
    placeholder.markdown(html_content, unsafe_allow_html=True)


def show_completion_screen(placeholder, style):
    """
    Exibe tela de conclusão com celebração.
    
    Args:
        placeholder: Container do Streamlit  
        style: CSS base
    """
    completion_html = f"""
    {style}
    <div class="loading-container">
        <div class="loading-title">🎉 CONCLUÍDO!</div>
        <div style="font-size: 1.8rem; margin: 2rem 0; color: #00D4AA;">
            ✅ Distribuição de Estoque Finalizada
        </div>
        <div style="font-size: 1.2rem; color: #ccc;">
            Preparando visualização...
        </div>
    </div>
    """
    
    placeholder.markdown(completion_html, unsafe_allow_html=True)
    time.sleep(2)  # Exibe por 2 segundos
    placeholder.empty()  # Remove a tela de loading


def render_header():
    """Renderiza cabeçalho e descrição do aplicativo."""
    st.title("🎯 MAXIMIZAÇÃO DO USO DO ESTOQUE")
    st.markdown("""
    *Otimização avançada de empacotamento 3D com aceleração GPU e algoritmos inteligentes de distribuição e rotação*
    
    📊 **Recursos**: Otimização GPU • Suporte a rotação • Visualização 3D em tempo real • Paleta de cores Viridis
    """)


def render_footer():
    """Renderiza rodapé profissional com informações de copyright."""
    st.markdown("---")
    
    # Layout em colunas para o rodapé
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666;">
            <strong>PARADOXO</strong><br>
            Soluções Inteligentes em Logística
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; font-size: 0.75rem; color: #888;">
            <span style="background: linear-gradient(45deg, #FF6B35, #F7931E); 
                         -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                         font-weight: bold;">VERSÃO BETA</span><br>
            <small>Sujeito a alterações</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: right; font-size: 0.8rem; color: #666;">
            <strong>Vinícius Ferreira</strong><br>
            Desenvolvedor & Arquiteto de Soluções
        </div>
        """, unsafe_allow_html=True)
    
    # Copyright centralizado
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem; padding: 1rem 0; 
                border-top: 1px solid #eee; font-size: 0.75rem; color: #888;">
        © 2025 <strong>PARADOXO</strong>. Todos os direitos reservados. 
        Desenvolvido por <strong>Vinícius Ferreira</strong> no Brasil 🇧🇷<br>
        <small style="color: #aaa;">
            Este software é protegido por direitos autorais. A reprodução não autorizada é proibida por lei.
        </small>
    </div>
    """, unsafe_allow_html=True)


def render_gpu_parameters() -> tuple:
    """
    Renderiza parâmetros do algoritmo híbrido único.
    
    Retorna:
        Tuple: (Tamanho da população, Tipo de algoritmo)
    """
    st.subheader("⚙️ Algoritmo Híbrido Único")
    
    # Informação sobre o algoritmo único
    st.info("""
    🎯 **Algoritmo Híbrido Único - Fusão de 3 Métodos:**
    - 🧬 **Biomecânico**: Zoneamento ergonômico automático por peso/categoria
    - 🏭 **Chão do Galpão**: Empilhamento estável iniciando no Z=0
    - 🚀 **GPU Otimizado**: Compactação inteligente com adjacência
    
    """)
    
    pop_size = st.slider(
        "Precisão da Otimização",
        min_value=GPU_POPULATION_RANGE['min'],
        max_value=GPU_POPULATION_RANGE['max'],
        value=GPU_POPULATION_RANGE['default'],
        step=GPU_POPULATION_RANGE['step'],
        help="Ajusta a precisão vs velocidade da otimização híbrida"
    )
    
    return pop_size, "Híbrido Único"


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
        st.info(f"📦 Container: {format_dimensions(container.dimensions())} | Volume: {format_br_number(container.volume)} unidades")
    else:
        st.info(f"📦 {container.quantidade} Containers: {format_dimensions(container.dimensions())} cada | Volume total: {format_br_number(container.volume_total)} unidades")
    
    return container


def render_blocks_section() -> pd.DataFrame:
    """
    Renderiza a seção de geração de pedidos aleatórios.
    
    Retorna:
        DataFrame com pedidos gerados
    """
    st.subheader("📦 Geração de Pedidos")
    
    # Instruções
    st.markdown("*Configure a quantidade de produtos distintos para geração aleatória*")
        
    # Slider para quantidade de pedidos
    n_orders = st.slider(
        "Número de Pedidos",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        help="Quantidade de pedidos que serão gerados aleatoriamente"
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
            st.metric("Vendas 90 Dias", format_br_number(analytics['total_sales_90d']))
        with col3:
            st.metric("Previsão Mês", format_br_number(analytics['total_forecast']))
        with col4:
            st.metric("Preço Médio", f"R$ {analytics['avg_price']:.2f}")
        
        # Receitas e peso
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Receita 90 Dias", format_br_currency(analytics['total_revenue_90d']))
        with col2:
            st.metric("Receita Prevista", format_br_currency(analytics['forecast_revenue']))
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
                    st.write(f"**Vendas 90d:** {format_br_number(data['sales_90d'])}")
                    st.write(f"**Previsão:** {format_br_number(data['forecast'])}")
                    st.write(f"**Peso Médio:** {data['avg_weight']:.3f} kg")
                with subcol2:
                    st.write(f"**Preço Médio:** R$ {data['avg_price']:.2f}")
                    st.write(f"**Receita 90d:** {format_br_currency(data['revenue_90d'])}")
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
    st.write(f"   • **{unique_products} produtos únicos** gerando **{format_br_number(total_forecast)} blocos totais**")
    st.write(f"   • **{len(unique_types)} tipos de dimensões** diferentes")
    
    # Agrupa por categoria para análise
    category_forecast = orders_data.groupby('Categoria')['Previsão Próx. Mês'].sum()
    st.write("� **Blocos por Categoria:**")
    for category, forecast in category_forecast.items():
        st.write(f"   • {category}: {format_br_number(forecast)} blocos")
    
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
                format_br_number(container.volume),
                help="Capacidade total do container"
            )
        else:
            st.metric(
                f"Volume Total ({container.quantidade} containers)",
                format_br_number(container.volume_total),
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
            format_br_percentage(efficiency),
            help="Percentual de eficiência do empacotamento"
        )
    
    # Resumo detalhado por produto (se orders_df disponível)
    if orders_df is not None:
        st.markdown("### 📋 Resumo por Produto")
        packing_summary = generate_packing_summary(orders_df, placements, total_count)
        
        # Métricas de resumo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Blocos", format_br_number(packing_summary['total_blocks']))
        with col2:
            st.metric("Blocos Empacotados", format_br_number(packing_summary['packed_blocks']))
        with col3:
            st.metric("Eficiência Geral", format_br_percentage(packing_summary['efficiency']))
        
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


def run_packing_algorithm(container: ContainerConfig, block_dims: list, pop_size: int, produtos_df=None, algoritmo_tipo="Híbrido Único") -> list:
    """
    Executa o algoritmo híbrido único de empacotamento com indicação de progresso.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        pop_size: Precisão da otimização (não usado mais, mantido para compatibilidade)
        produtos_df: DataFrame com dados dos produtos (sempre necessário)
        algoritmo_tipo: Sempre "Híbrido Único" (mantido para compatibilidade)
        
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
    
    # Sempre usa o algoritmo híbrido único
    spinner_msg = "🎯 Executando algoritmo híbrido único (3 em 1)..."
    
    # Executa algoritmo híbrido com progresso
    with st.spinner(spinner_msg):
        if produtos_df is not None and not produtos_df.empty:
            placements = hybrid_intelligent_packing(container, block_dims, produtos_df)
        else:
            # Fallback: cria DataFrame básico se não fornecido
            import pandas as pd
            produtos_df_default = pd.DataFrame({
                'peso': [2.0] * len(block_dims),
                'Categoria': ['Utilidades'] * len(block_dims)
            })
            placements = hybrid_intelligent_packing(container, block_dims, produtos_df_default)
    
    return placements


def render_visualization(container: ContainerConfig, placements: list, block_dims: list, orders_df=None):
    """
    Renderiza a seção de visualização 3D estacionária.
    
    Args:
        container: Configuração do container
        placements: Lista de alocações dos blocos
        block_dims: Lista de dimensões dos blocos
        orders_df: DataFrame com informações dos produtos para legenda
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
        
        # Configurações otimizadas com controles visíveis e câmera fixa
        config = {
            'displayModeBar': True,   # Mantém controles visíveis
            'staticPlot': False,      # Permite renderização 3D
            'responsive': True,       # Responsivo
            'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],  # Remove botões 2D desnecessários
            'displaylogo': False,     # Remove logo Plotly
            'doubleClick': 'reset'    # Reset para posição default no duplo clique
        }
        
        print(f"[DEBUG] Usando configuração: {config}")
        
        # Atualiza figura para garantir visualização inicial correta
        fig.update_layout(
            scene=dict(
                camera=dict(
                    projection=dict(type="perspective"),  # Força projeção perspectiva
                    # Força a posição inicial da câmera
                    eye=dict(x=2.5, y=2.5, z=2.0),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1)
                )
            ),
            # Configuração para garantir que a figura seja renderizada corretamente
            autosize=True
        )
        
        # Renderiza o gráfico
        st.plotly_chart(fig, use_container_width=True, config=config)
        
        print(f"[DEBUG] Gráfico renderizado com sucesso")
        
        # Legenda de produtos
        st.write("### 🏷️ Legenda de Produtos")
        
        if orders_df is not None and not orders_df.empty:
            try:
                # Cria mapeamento de dimensões para produtos
                dim_to_product = {}
                
                # Verifica se as colunas necessárias existem
                required_cols = ['Comprimento', 'Largura', 'Profundidade', 'Nome Produto', 'Categoria']
                if all(col in orders_df.columns for col in required_cols):
                    for _, row in orders_df.iterrows():
                        dims = (int(row['Comprimento']), int(row['Largura']), int(row['Profundidade']))
                        product_info = f"{row['Nome Produto']} ({row['Categoria']})"
                        if dims not in dim_to_product:
                            dim_to_product[dims] = []
                        dim_to_product[dims].append(product_info)
                    
                    # Organiza a legenda por produtos únicos
                    unique_products = {}
                    for dims in set(block_dims):
                        if dims in dim_to_product:
                            products = list(set(dim_to_product[dims]))  # Remove duplicatas
                            for product in products:
                                if product not in unique_products:
                                    unique_products[product] = dims
                    
                    if unique_products:
                        # Calcula número de colunas
                        num_products = len(unique_products)
                        cols_per_row = min(3, num_products)  # Máximo 3 colunas para produtos
                        
                        # Cria colunas para a legenda
                        legend_cols = st.columns(cols_per_row)
                        
                        for i, (product, dims) in enumerate(unique_products.items()):
                            col_idx = i % cols_per_row
                            with legend_cols[col_idx]:
                                color = block_colors.get(dims, '#000000')
                                # Cria indicador com nome do produto
                                st.markdown(f"""
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 20px; height: 20px; background-color: {color}; 
                                                border: 1px solid #000; margin-right: 10px; border-radius: 3px;"></div>
                                    <div style="font-size: 13px; line-height: 1.2;">
                                        <strong>{product}</strong><br>
                                        <small style="color: #666;">{dims[0]}×{dims[1]}×{dims[2]} cm</small>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        # Se não conseguiu mapear produtos, usa fallback
                        raise ValueError("Não foi possível mapear produtos para dimensões")
                else:
                    # Se não tem as colunas necessárias, usa fallback
                    raise ValueError(f"Colunas necessárias não encontradas. Disponíveis: {list(orders_df.columns)}")
                    
            except Exception as e:
                st.warning(f"⚠️ Erro ao processar dados de produtos: {str(e)}")
                # Fallback para mostrar apenas dimensões
                orders_df = None
        else:
            # Fallback para dimensões quando não há dados de produto
            st.info("ℹ️ Dados de produtos não disponíveis. Mostrando dimensões:")
            
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
            st.metric("Volume Ocupado", format_br_number(volume_usado))
            
            
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
    if st.button("🚀 DISTRIBUIR ESTOQUE", type="primary", use_container_width=True):
        # Inicia tela de loading
        placeholder, loading_style = show_loading_screen()
        loading_messages = get_creative_loading_messages()
        
        try:
            # FORÇA limpeza completa do estado da sessão
            for key in list(st.session_state.keys()):
                if key.startswith(('placements', 'container', 'block_dims', 'last_run', 'tipo_cores')):
                    del st.session_state[key]
            
            st.session_state['placements'] = []
            st.session_state['container'] = None
            st.session_state['block_dims'] = []
            st.session_state['last_run'] = False

            # Processa dados com loading animado
            for i, message in enumerate(loading_messages[:6]):  # Primeiras 6 mensagens
                for dots in range(1, 4):  # Animação de 1 a 3 pontos
                    update_loading_message(placeholder, loading_style, message, dots)
                    time.sleep(0.4)  # Pausa para animação
            
            # Processa dados de entrada
            block_dims = process_block_data(orders_df)
            
            # Remove possíveis valores None ou inválidos
            block_dims = [dims for dims in block_dims if dims is not None and all(d > 0 for d in dims)]
            
            if not block_dims:
                placeholder.empty()
                st.error("❌ Erro ao processar pedidos. Verifique os dados gerados.")
                return
            
            # Continua loading durante execução do algoritmo
            for i, message in enumerate(loading_messages[6:]):  # Mensagens restantes
                for dots in range(1, 4):
                    update_loading_message(placeholder, loading_style, message, dots)
                    time.sleep(0.3)
            
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
            
            # Mantém loading enquanto prepara a visualização
            update_loading_message(placeholder, loading_style, "🎨 Gerando visualização 3D", 3)
            time.sleep(0.5)
            
            # Exibe resultados
            display_analysis_metrics(container, block_dims, placements, orders_df)
            show_graph = True
            
        except Exception as e:
            placeholder.empty()
            st.error(f"❌ Erro durante processamento: {str(e)}")
            return

    # Seção de visualização (apenas se botão foi pressionado)
    if show_graph and st.session_state.get('last_run', False):
        # Renderiza a visualização primeiro
        render_visualization(
            st.session_state['container'],
            st.session_state['placements'],
            st.session_state['block_dims'],
            st.session_state.get('orders_df')  # Passa orders_df para a legenda
        )
        
        # Remove a tela de loading APENAS depois da visualização
        if 'loading_placeholder' in locals():
            placeholder.empty()
        
        # Pequena pausa para garantir que o gráfico foi renderizado
        time.sleep(1)
        
        # Mostra tela de conclusão APÓS o gráfico estar pronto
        completion_placeholder = st.empty()
        with completion_placeholder.container():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; 
                        color: white; margin: 1rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <h2 style="margin: 0; font-size: 2rem;">🎉 EMPACOTAMENTO CONCLUÍDO!</h2>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                    Sua visualização 3D está pronta! ✨
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Remove a mensagem de conclusão após 4 segundos
        time.sleep(4)
        completion_placeholder.empty()
        
        # 🎉 CELEBRAÇÃO FINAL COM BALÕES!
        st.balloons()
        
        # Informações adicionais de conclusão
        col1, col2, col3 = st.columns(3)
        with col1:
            placed_count = len(st.session_state['placements'])
            st.info(f"📦 **{format_br_number(placed_count)}** blocos processados")
        with col2:
            # Corrige a chamada da função calculate_efficiency
            total_count = len(st.session_state['block_dims'])
            placed_count = len(st.session_state['placements'])
            efficiency = calculate_efficiency(placed_count, total_count)
            st.info(f"📊 **{format_br_percentage(efficiency)}** de eficiência")
        with col3:
            st.info("✅ **Visualização 3D** gerada")
        
        st.markdown("---")
        st.markdown("🎯 **Próximos passos:** Use os controles 3D para explorar o resultado ou ajuste os parâmetros para uma nova simulação.")
    elif st.session_state.get('last_run', False):
        # Se já foi executado anteriormente mas não está mostrando o gráfico
        render_visualization(
            st.session_state['container'],
            st.session_state['placements'],
            st.session_state['block_dims'],
            st.session_state.get('orders_df')
        )
    
    # Rodapé profissional
    render_footer()


if __name__ == "__main__":
    main()
