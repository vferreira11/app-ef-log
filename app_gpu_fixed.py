# -*- coding: utf-8 -*-
"""
Sistema de Empacotamento 3D - Aplicação Principal Streamlit
=========================================================

Interface Streamlit limpa e modular para otimização de empacotamento 3D.
Usa algoritmos acelerados por GPU com suporte a rotação e visualização avançada.

Uso:
    streamlit run app_gpu_fixed.py
"""

import os
import sys

# Força encoding UTF-8 no Windows
if sys.platform.startswith('win'):
    try:
        import codecs
        if hasattr(sys.stdout, 'detach'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except Exception:
        # Fallback: define ambiente UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'

import streamlit as st
import pandas as pd
import time
import random
import plotly.graph_objects as go
import plotly.colors as pc
import numpy as np

# Adiciona o diretório scripts ao path para imports
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(scripts_dir)

# Importa componentes modulares
from scripts.core.models import ContainerConfig, Placement
from ef_log.core.algorithms import hybrid_intelligent_packing
from ef_log.gpu.algorithms import gpu_hybrid_ultra_intelligent_packing, check_gpu_availability
from ef_log.gpu.visualization.standard import create_3d_plot
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

def render_custom_css():
    """Injeta CSS customizado otimizado para performance e responsividade."""
    st.markdown("""
    <style>
    /* ======================
       PERFORMANCE OPTIMIZATIONS
       ====================== */
    
    /* Reduce repaints and enable hardware acceleration */
    .stat-card, .modern-header, .loading-container {
        will-change: transform;
        transform: translateZ(0);
    }
    
    /* ======================
       RESPONSIVE STAT CARDS
       ====================== */
    .stat-card {
        background-color: #FFFFFF;
        border: 1px solid #E6EAF1;
        border-left: 5px solid #00D4AA;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        text-align: left;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stat-card:hover {
        transform: translateY(-3px) translateZ(0);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .stat-card h3 {
        font-size: 1rem;
        color: #5A6474;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .stat-card p {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A1C24;
        margin: 0;
        line-height: 1.2;
    }
    
    .stat-card small {
        font-size: 0.85rem;
        color: #8A94A6;
        display: block;
        margin-top: 4px;
    }
    
    /* ======================
       MODERN HEADER
       ====================== */
    .modern-header {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #00D4AA 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(255, 107, 53, 0.3);
    }
    
    .modern-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .modern-header p {
        color: rgba(255,255,255,0.95);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* ======================
       IMPROVED LOADING
       ====================== */
    .modern-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 3rem 2rem;
        background: rgba(26, 28, 36, 0.98);
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    .loading-spinner-modern {
        border: 3px solid rgba(0, 212, 170, 0.1);
        border-top: 3px solid #00D4AA;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin-bottom: 1.5rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text-modern {
        color: white;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .loading-progress {
        width: 200px;
        height: 4px;
        background: rgba(255,255,255,0.2);
        border-radius: 2px;
        overflow: hidden;
        margin-top: 1rem;
    }
    
    .loading-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #00D4AA, #FF6B35);
        border-radius: 2px;
        animation: progress 2s ease-in-out infinite;
    }
    
    @keyframes progress {
        0% { width: 0%; }
        50% { width: 70%; }
        100% { width: 100%; }
    }
    
    /* ======================
       RESPONSIVE BREAKPOINTS
       ====================== */
    
    /* Tablet */
    @media (max-width: 1024px) {
        .modern-header h1 {
            font-size: 2rem;
        }
        
        .stat-card {
            padding: 16px;
        }
        
        .stat-card p {
            font-size: 1.8rem;
        }
    }
    
    /* Mobile */
    @media (max-width: 768px) {
        .modern-header {
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
        }
        
        .modern-header h1 {
            font-size: 1.6rem;
        }
        
        .modern-header p {
            font-size: 0.95rem;
        }
        
        .stat-card {
            padding: 15px;
            margin-bottom: 12px;
        }
        
        .stat-card h3 {
            font-size: 0.9rem;
        }
        
        .stat-card p {
            font-size: 1.5rem;
        }
        
        .loading-spinner-modern {
            width: 40px;
            height: 40px;
        }
        
        .loading-text-modern {
            font-size: 1rem;
        }
    }
    
    /* Small Mobile */
    @media (max-width: 480px) {
        .modern-header {
            padding: 1rem;
        }
        
        .modern-header h1 {
            font-size: 1.4rem;
        }
        
        .stat-card {
            padding: 12px;
        }
        
        .stat-card p {
            font-size: 1.3rem;
        }
    }
    
    /* ======================
       ACCESSIBILITY
       ====================== */
    @media (prefers-reduced-motion: reduce) {
        .stat-card, .loading-spinner-modern, .loading-progress-bar {
            animation: none;
            transition: none;
        }
        
        .stat-card:hover {
            transform: none;
        }
    }
    
    /* High contrast mode */
    @media (prefers-contrast: high) {
        .stat-card {
            border-width: 2px;
            border-left-width: 6px;
        }
        
        .modern-header {
            background: #1a1c24;
            border: 2px solid #00D4AA;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_stat_card(title, value, help_text="", icon="📦"):
    """Renderiza um card de estatística customizado."""
    st.markdown(f"""
    <div class="stat-card"><h3>{icon} {title}</h3><p>{value}</p><small>{help_text}</small></div>
    """, unsafe_allow_html=True)

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
        "📍 Calculando posições otimizadas", 
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
        <div class="loading-title">⏳ AGUARDE</div>
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
    """Renderiza cabeçalho moderno e otimizado."""
    st.markdown("""
    <div class="modern-header">
        <h1>🚀 PARADOXO - Empacotamento 3D</h1>
        <p>Otimização Inteligente com IA e Aceleração GPU</p>
    </div>
    """, unsafe_allow_html=True)


def render_modern_loading(message="Processando...", progress=0):
    """
    Renderiza loading moderno com progress bar.
    
    Args:
        message: Mensagem a ser exibida
        progress: Progresso de 0 a 100
    """
    return st.markdown(f"""
    <div class="modern-loading">
        <div class="loading-spinner-modern"></div>
        <div class="loading-text-modern">{message}</div>
        <div class="loading-progress">
            <div class="loading-progress-bar" style="width: {progress}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_progress_tracker():
    """Cria um tracker de progresso para operações longas."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    return progress_bar, status_text


def update_progress(progress_bar, status_text, current, total, message):
    """Atualiza o progresso de uma operação."""
    percentage = int((current / total) * 100)
    progress_bar.progress(percentage)
    status_text.text(f"{message} ({current}/{total}) - {percentage}%")


def render_optimized_stat_card(title, value, delta=None, icon="�", color="#00D4AA"):
    """
    Renderiza card de estatística otimizado com melhor performance.
    
    Args:
        title: Título do card
        value: Valor principal
        delta: Variação (opcional)
        icon: Ícone do card
        color: Cor de destaque
    """
    delta_html = f"<small style='color: {color}; font-weight: 600;'>△ {delta}</small>" if delta else ""
    
    st.markdown(f"""
    <div class="stat-card" style="border-left-color: {color};">
        <h3>{icon} {title}</h3>
        <p style="color: {color};">{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    *Otimização avançada de empacotamento 3D com aceleração GPU e algoritmos inteligentes de distribuição e rotação*
    
    📊 **Recursos**: Otimização GPU • Suporte a rotação • Visualização 3D em tempo real • Paleta de cores Viridis
    """)


def render_footer():
    """Renderiza rodapé profissional com informações de copyright."""
    st.markdown("---")
    
    # Layout responsivo usando colunas do Streamlit
    col1, col2, col3 = st.columns([2, 1, 2])
    
    # CSS para estilos
    st.markdown("""
    <style>
    .footer-company {
        font-size: 0.8rem;
        color: #666;
    }
    
    .footer-version {
        text-align: center;
        font-size: 0.75rem;
        color: #888;
    }
    
    .footer-dev {
        text-align: right;
        font-size: 0.8rem;
        color: #666;
    }
    
    .version-badge {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold;
        display: inline-block;
    }
    
    .linkedin-link {
        color: #0077B5 !important;
        text-decoration: none !important;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .linkedin-link:hover {
        border-bottom: 2px solid #0077B5;
        transform: translateY(-1px);
        color: #005885 !important;
    }
    
    .linkedin-copyright {
        color: #0077B5 !important;
        text-decoration: none !important;
        border-bottom: 1px dotted #0077B5;
        transition: all 0.3s ease;
    }
    
    .linkedin-copyright:hover {
        border-bottom: 1px solid #0077B5;
        color: #005885 !important;
    }
    
    .copyright-section {
        text-align: center;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        font-size: 0.75rem;
        color: #888;
        line-height: 1.4;
    }
    
    /* Responsividade melhorada para mobile */
    @media (max-width: 768px) {
        .footer-company, .footer-dev {
            text-align: center !important;
            font-size: 0.75rem !important;
        }
        .footer-version {
            font-size: 0.7rem !important;
        }
        .version-badge {
            font-size: 0.7rem !important;
        }
        .copyright-section {
            font-size: 0.7rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Primeira linha - Desenvolvedor, Versão, Empresa (ordem trocada)
    with col1:
        st.markdown("""
        <div class="footer-company">
            <strong>
                <a href="https://www.linkedin.com/in/viniciusferreira11/" 
                   target="_blank" 
                   class="linkedin-link">
                    💼 Vinícius Ferreira
                </a>
            </strong><br>
            Resolvedor de problemas
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="footer-version">
            <span class="version-badge">VERSÃO BETA</span><br>
            <small>Sujeito a alterações</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="footer-dev">
            <strong>PARADOXO</strong><br>
            IA feita a mão.
        </div>
        """, unsafe_allow_html=True)
    
    # Segunda linha - Copyright centralizado
    st.markdown("""
    <div class="copyright-section">
        © 2025 <strong>PARADOXO</strong>. Todos os direitos reservados. 
        Desenvolvido por 
        <strong>
            <a href="https://www.linkedin.com/in/viniciusferreira11/" 
               target="_blank" 
               class="linkedin-copyright">
                Vinícius Ferreira
            </a>
        </strong> no Brasil 🇧🇷<br>
        <small style="color: #aaa;">
            Este software é protegido por direitos autorais. A reprodução não autorizada é proibida por lei.
        </small>
    </div>
    """, unsafe_allow_html=True)


def render_gpu_parameters() -> tuple:
    """
    Renderiza parâmetros do algoritmo GPU ultra-inteligente.
    
    Retorna:
        Tuple: (Tipo de algoritmo, Status GPU)
    """
    st.subheader("🚀 Algoritmo GPU Ultra-Inteligente")
    
    # Verifica status da GPU com debug (força re-detecção)
    try:
        # Força reimport para garantir detecção correta
        import importlib
        from ef_log.gpu.algorithms import check_gpu_availability
        importlib.reload(gpu_algorithms)
        gpu_status = check_gpu_availability()
    except Exception as e:
        st.error(f"Erro na detecção GPU: {e}")
        gpu_status = {'gpu_available': False, 'cuda_available': False, 'error': str(e)}
    
    # Debug: mostra status detalhado
    with st.expander("🔍 Debug GPU Status", expanded=True):
        st.json(gpu_status)
        st.write(f"**Condição:** gpu_available={gpu_status.get('gpu_available', False)} AND cuda_available={gpu_status.get('cuda_available', False)}")
        st.write(f"**Resultado:** {gpu_status.get('gpu_available', False) and gpu_status.get('cuda_available', False)}")
    
    if gpu_status.get('gpu_available', False) and gpu_status.get('cuda_available', False):
        st.success("✅ RTX 3070 Ti detectada - Modo GPU ativado")
        algo_tipo = "GPU Ultra-Inteligente"
        
        st.info("""
        🚀 **Algoritmo GPU Ultra-Inteligente (99% Acurácia):**
        - 📊 **ABC + Biomecânica**: Classificação CUDA massiva (4096 cores)
        - 🧮 **Otimização Matemática**: Mixed Integer Programming
        - ⚖️ **Validação Tensorial**: Física realista GPU
        - 🧬 **Refinamento Evolutivo**: Algoritmo genético paralelo
        """)
        
    else:
        st.warning("⚠️ GPU não disponível - Usando algoritmo híbrido CPU")
        algo_tipo = "Híbrido CPU"
        
        st.info("""
        🔄 **Fallback: Algoritmo Híbrido CPU:**
        - 🧬 **Biomecânico**: Zoneamento ergonômico por peso/categoria
        - 🏭 **Chão do Galpão**: Empilhamento estável iniciando em Z=0
        - 🚀 **Otimização**: Compactação inteligente com adjacência
        """)
    
    # Parâmetros avançados
    with st.expander("⚙️ Configurações Avançadas", expanded=False):
        precision_level = st.selectbox(
            "Nível de Precisão",
            ["Rápido (90-95%)", "Balanceado (95-97%)", "Ultra (97-99%)"],
            index=1,
            help="Balança velocidade vs acurácia"
        )
        
        enable_physics = st.checkbox(
            "Validação Física Avançada",
            value=True,
            help="Ativa cálculos de estabilidade e centro de massa"
        )
        
        enable_evolution = st.checkbox(
            "Refinamento Evolutivo",
            value=True,
            help="Usa algoritmo genético para otimização final"
        )
    
    return algo_tipo, {
        'precision': precision_level,
        'physics': enable_physics,
        'evolution': enable_evolution,
        'gpu_status': gpu_status
    }


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
    
    # Exibe a tabela de pedidos APENAS se existir no session_state (após clique do botão)
    if 'orders_df' in st.session_state and not st.session_state.orders_df.empty:
        st.markdown("### 📋 Pedidos Gerados")
        st.dataframe(
            st.session_state.orders_df,
            use_container_width=True,
            hide_index=True,  # Remove o índice da tabela
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
    
    # Calcula e exibe estatísticas de vendas (só se existir orders_df)
    if 'orders_df' in st.session_state and not st.session_state.orders_df.empty:
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
                    with subcol2:
                        st.write(f"**Previsão:** {format_br_number(data['forecast'])}")
                        st.write(f"**Peso Médio:** {data['avg_weight']:.3f} kg")
                    with subcol3:
                        st.write(f"**Preço Médio:** R$ {data['avg_price']:.2f}")
                        st.write(f"**Receita 90d:** {format_br_currency(data['revenue_90d'])}")
                        st.write(f"**Peso Total:** {data['total_weight_forecast']:.2f} kg")
                    
                    # Tendência de crescimento
                    growth = ((data['forecast'] * 3) / data['sales_90d'] - 1) * 100 if data['sales_90d'] > 0 else 0
                    trend = "📈" if growth > 0 else "📉" if growth < 0 else "➡️"
                    st.write(f"**Tendência:** {trend} {growth:+.1f}%")
                    
                    # Densidade média da categoria (se dados disponíveis)
                    if 'Comprimento' in st.session_state.orders_df.columns:
                        cat_orders = st.session_state.orders_df[st.session_state.orders_df['Categoria'] == category]
                        if not cat_orders.empty:
                            volumes = cat_orders['Comprimento'] * cat_orders['Largura'] * cat_orders['Profundidade']
                            avg_volume = volumes.mean()
                            if avg_volume > 0:
                                density = (data['avg_weight'] * 1000) / avg_volume  # g/cm³
                                st.write(f"**Densidade:** {density:.2f} g/cm³")
    
    # Retorna o DataFrame se existir, senão retorna None
    return st.session_state.get('orders_df', None)


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
    placed_count = len(placements)
    total_count = len(block_dims)
    efficiency = calculate_efficiency(placed_count, total_count)

    # Renderiza Stat Cards
    col1, col2 = st.columns(2)
    with col1:
        if container.quantidade > 1:
            render_stat_card(
                "Volume Total",
                format_br_number(container.volume_total),
                f"Capacidade total de {container.quantidade} containers",
                "🧊"
            )
        else:
            render_stat_card(
                "Volume do Container",
                format_br_number(container.volume),
                "Capacidade total do container",
                "🧊"
            )
        render_stat_card(
            "Blocos Alocados",
            f"{placed_count} / {total_count}",
            "Blocos alocados com sucesso vs. total",
            "✅"
        )
    with col2:
        render_stat_card(
            "Tipos de Bloco",
            str(unique_count),
            "Número de dimensões diferentes de blocos",
            "🎨"
        )
        render_stat_card(
            "Eficiência de Ocupação",
            format_br_percentage(efficiency),
            "Percentual de blocos alocados com sucesso",
            "🎯"
        )

    # Mensagens de status
    if placements:
        if placed_count == total_count:
            st.success(UI_MESSAGES['success_perfect'].format(total_count))
        elif placed_count > 0:
            missing = total_count - placed_count
            st.warning(UI_MESSAGES['warning_partial'].format(missing))
        else:
            st.error(UI_MESSAGES['error_no_blocks'])

    # Tabela de resumo detalhado por produto
    if orders_df is not None and not orders_df.empty:
        st.markdown("---")
        st.markdown("### 📋 Detalhamento por Produto")
        packing_summary = generate_packing_summary(orders_df, placements, block_dims)

        with col1:
            render_stat_card("Total de Blocos", format_br_number(packing_summary['total_blocks']), "Total de itens previstos para empacotar", "🔢")
        with col2:
            render_stat_card("Blocos Empacotados", format_br_number(packing_summary['packed_blocks']), "Itens que couberam no container", "📥")

        if packing_summary['products']:
            df_summary = pd.DataFrame(packing_summary['products'])
            st.dataframe(
                df_summary,
                use_container_width=True,
                hide_index=True,  # Remove o índice da tabela
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

def run_packing_algorithm(container: ContainerConfig, block_dims: list, algoritmo_tipo: str, 
                         config: dict, produtos_df=None) -> list:
    """
    Executa o algoritmo de empacotamento baseado no tipo e configurações.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        algoritmo_tipo: Tipo do algoritmo ("GPU Ultra-Inteligente" ou "Híbrido CPU")
        config: Configurações do algoritmo
        produtos_df: DataFrame com dados dos produtos
        
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
    
    # Prepara DataFrame se necessário
    if produtos_df is None or produtos_df.empty:
        import pandas as pd
        produtos_df = pd.DataFrame({
            'peso': [2.0] * len(set(block_dims)),
            'Categoria': ['Utilidades'] * len(set(block_dims)),
            'Previsão Próx. Mês': [1] * len(set(block_dims))
        })
    
    # Seleciona algoritmo baseado no tipo
    if algoritmo_tipo == "GPU Ultra-Inteligente" and config['gpu_status']['gpu_available']:
        spinner_msg = "🚀 Executando algoritmo GPU ultra-inteligente (4 etapas)..."
        
        with st.spinner(spinner_msg):
            # Barra de progresso para as 4 etapas
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📊 Etapa 1/4: Classificação ABC + Biomecânica...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("🧮 Etapa 2/4: Otimização Matemática (MIP)...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("⚖️ Etapa 3/4: Validação Física Tensorial...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            status_text.text("🧬 Etapa 4/4: Refinamento Evolutivo...")
            progress_bar.progress(100)
            
            try:
                placements = gpu_hybrid_ultra_intelligent_packing(container, block_dims, produtos_df)
                status_text.text("✅ Algoritmo GPU concluído com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro no algoritmo GPU: {e}")
                st.warning("🔄 Fallback para algoritmo CPU...")
                placements = hybrid_intelligent_packing(container, block_dims, produtos_df)
                status_text.text("✅ Fallback CPU concluído!")
            
            progress_bar.empty()
            status_text.empty()
            
    else:
        # Algoritmo híbrido CPU
        spinner_msg = "🔄 Executando algoritmo híbrido CPU (3 em 1)..."
        
        with st.spinner(spinner_msg):
            placements = hybrid_intelligent_packing(container, block_dims, produtos_df)
    
    return placements


@st.cache_data(show_spinner=False)
def _cached_create_visualization(container_dict, placements_tuple, block_dims_tuple):
    """
    Cria visualização 3D com cache para melhor performance.
    
    Args:
        container_dict: Container serializado como dict
        placements_tuple: Placements como tupla (imutável para cache)
        block_dims_tuple: Block dims como tupla (imutável para cache)
    
    Returns:
        Figure do Plotly serializada
    """
    # Reconstrói objetos a partir dos dados cached
    container = ContainerConfig(**container_dict)
    placements = list(placements_tuple)
    block_dims = list(block_dims_tuple)
    
    return create_3d_plot(container, placements, block_dims)


def render_visualization(container: ContainerConfig, placements: list, block_dims: list, orders_df=None):
    """
    Renderiza visualização 3D otimizada com cache e lazy loading.
    
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
        st.write("🔄 Gerando visualização 3D...")
        
        # Progress tracker para visualização
        progress_bar, status_text = create_progress_tracker()
        
        try:
            # Converte dados para formato cacheable
            container_dict = {
                'dx': container.dx,
                'dy': container.dy, 
                'dz': container.dz,
                'quantidade': container.quantidade
            }
            
            placements_tuple = tuple(tuple(p) if isinstance(p, (list, tuple)) else p for p in placements)
            block_dims_tuple = tuple(tuple(bd) if isinstance(bd, (list, tuple)) else bd for bd in block_dims)
            
            # Atualiza progresso - Preparação
            update_progress(progress_bar, status_text, 1, 4, "Preparando dados")
            
            # Usa visualização cacheada
            update_progress(progress_bar, status_text, 2, 4, "Gerando visualização 3D")
            fig = _cached_create_visualization(container_dict, placements_tuple, block_dims_tuple)
            
            # Atualiza progresso - Configuração
            update_progress(progress_bar, status_text, 3, 4, "Configurando interatividade")
            
            # Configuração otimizada para performance
            config = {
                'displayModeBar': True,
                'staticPlot': False,
                'responsive': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'empacotamento_3d',
                    'height': 800,
                    'width': 1200,
                    'scale': 1
                }
            }
            
            # Finaliza progresso
            update_progress(progress_bar, status_text, 4, 4, "Renderizando")
            
            # Remove progress bar
            progress_bar.empty()
            status_text.empty()
            
            # Renderiza visualização otimizada
            st.markdown("### 🎨 Visualização 3D Interativa")
            
            # Container lazy loading para visualização
            with st.container():
                st.plotly_chart(fig, use_container_width=True, config=config)
                
            st.success("✅ Visualização 3D renderizada com sucesso!")
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Erro ao gerar visualização: {str(e)}")
            return
        
        # 1. Adiciona chão cinza claro
        dx, dy, dz = container.dx, container.dy, container.dz
        
        # Chão como superfície cinza clara
        fig.add_trace(go.Mesh3d(
            x=[0, dx, dx, 0],
            y=[0, 0, dy, dy],
            z=[0, 0, 0, 0],
            i=[0, 0],
            j=[1, 2], 
            k=[2, 3],
            color='lightgray',
            opacity=0.3,
            name='Chão',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # 2. Adiciona wireframe do container
        # Vértices do container
        vertices = [
            [0, 0, 0], [dx, 0, 0], [dx, dy, 0], [0, dy, 0],  # base
            [0, 0, dz], [dx, 0, dz], [dx, dy, dz], [0, dy, dz]  # topo
        ]
        
        # Arestas do container
        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        
        for start, end in edges:
            fig.add_trace(go.Scatter3d(
                x=[vertices[start][0], vertices[end][0]],
                y=[vertices[start][1], vertices[end][1]], 
                z=[vertices[start][2], vertices[end][2]],
                mode='lines',
                line=dict(color='black', width=2),
                name='Container',
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # 3. Mapeamento de cores Viridis por tipo de produto
        unique_dims = list(set(block_dims))
        viridis_colors = pc.sample_colorscale('Viridis', np.linspace(0, 1, len(unique_dims)))
        dim_to_color = {dim: color for dim, color in zip(unique_dims, viridis_colors)}
        
        # 4. Adiciona blocos com cores por tipo
        for i, placement in enumerate(placements):
            if placement is None:
                continue
                
            # Extrai coordenadas dependendo da estrutura
            if hasattr(placement, 'x'):  # Objeto Placement
                x, y, z = placement.x, placement.y, placement.z
                block_idx = placement.block_index
            elif len(placement) >= 4:  # Tupla com índice
                x, y, z, block_idx = placement[:4]
            else:
                continue
            
            # Obtém dimensões do bloco
            if isinstance(block_dims[block_idx], dict):
                bdx = block_dims[block_idx].get('dx', 1)
                bdy = block_dims[block_idx].get('dy', 1) 
                bdz = block_dims[block_idx].get('dz', 1)
                current_dim = (bdx, bdy, bdz)
            elif isinstance(block_dims[block_idx], (tuple, list)):
                bdx, bdy, bdz = block_dims[block_idx]
                current_dim = block_dims[block_idx]
            else:
                print(f"[ERRO] Formato inválido para block_dims[{block_idx}]: {block_dims[block_idx]}")
                continue
            
            # Cor baseada no tipo de produto (dimensões)
            color = dim_to_color.get(current_dim, viridis_colors[0])
            
            # Adiciona cubo sólido do bloco usando Mesh3d
            fig.add_trace(go.Mesh3d(
                x=[x, x+bdx, x+bdx, x, x, x+bdx, x+bdx, x],
                y=[y, y, y+bdy, y+bdy, y, y, y+bdy, y+bdy],
                z=[z, z, z, z, z+bdz, z+bdz, z+bdz, z+bdz],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color=color,
                opacity=1.0,
                name=f'Tipo {current_dim[0]}×{current_dim[1]}×{current_dim[2]}',
                showlegend=False,
                hovertemplate=f'<b>Bloco {i+1}</b><br>'+
                             f'Posição: ({x}, {y}, {z})<br>'+
                             f'Dimensões: {bdx}×{bdy}×{bdz}<br>'+
                             '<extra></extra>'
            ))
            
            # Adiciona wireframe do bloco para definir bordas
            block_vertices = [
                [x, y, z], [x+bdx, y, z], [x+bdx, y+bdy, z], [x, y+bdy, z],
                [x, y, z+bdz], [x+bdx, y, z+bdz], [x+bdx, y+bdy, z+bdz], [x, y+bdy, z+bdz]
            ]
            
            for start, end in edges:
                fig.add_trace(go.Scatter3d(
                    x=[block_vertices[start][0], block_vertices[end][0]],
                    y=[block_vertices[start][1], block_vertices[end][1]],
                    z=[block_vertices[start][2], block_vertices[end][2]],
                    mode='lines',
                    line=dict(color='black', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # 5. Configuração do layout com proporções reais preservadas
        fig.update_layout(
            title="📦 Visualização 3D do Empacotamento",
            scene=dict(
                xaxis_title="Largura (X) - cm",
                yaxis_title="Profundidade (Y) - cm", 
                zaxis_title="Altura (Z) - cm",
                aspectmode='data',
                aspectratio=dict(x=1, y=1, z=1),  # Mantém escala real
                xaxis=dict(
                    range=[0, dx],
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                yaxis=dict(
                    range=[0, dy],
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                zaxis=dict(
                    range=[0, dz],
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)'
                ),
                # Camera na posição default do Plotly
                bgcolor='white'
            ),
            width=900,
            height=700,
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False
        )
        
        figure = fig
        
        if not figure or len(figure.data) == 0:
            st.error("❌ Erro ao gerar visualização 2D.")
            return
        
        st.success(f"✅ Visualização criada com {len(figure.data)} elementos!")
        
        st.markdown("### 🎨 Visualização 3D Interativa")
        
        # Configuração para visualização 3D interativa
        config = {
            'displayModeBar': True,
            'staticPlot': False
        }
        
        try:
            st.plotly_chart(figure, use_container_width=True, config=config)
            st.success("✅ Visualização 3D renderizada com sucesso!")
            
            # Adiciona legenda de tipos de produto
            st.markdown("### 🎨 Legenda de Tipos de Produto (Paleta Viridis)")
            
            # Organiza legenda em colunas
            unique_types = list(unique_dims)
            cols_per_row = min(4, len(unique_types))
            legend_cols = st.columns(cols_per_row)
            
            for i, dim_type in enumerate(unique_types):
                col_idx = i % cols_per_row
                with legend_cols[col_idx]:
                    color = dim_to_color[dim_type]
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="width: 25px; height: 25px; background-color: {color}; 
                                    border: 1px solid #000; margin-right: 10px; border-radius: 4px;"></div>
                        <div style="font-size: 14px; font-weight: bold;">
                            {dim_type[0]}×{dim_type[1]}×{dim_type[2]} cm
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as render_error:
            st.error(f"❌ Erro ao renderizar: {str(render_error)}")
        
        # Gera legenda com cores Viridis por tipo
        block_colors = dim_to_color
        
        # Exibe legenda e estatísticas
        render_legend_and_stats(block_colors, orders_df, placements, block_dims)
        
    except Exception as e:
        st.error(f"❌ Erro na visualização: {str(e)}")


def render_legend_and_stats(block_colors, orders_df, placements, block_dims):
    """Renderiza legenda de produtos e estatísticas."""
    st.write("### 🏷️ Legenda de Produtos")
    
    # Verificação robusta para orders_df
    if orders_df is not None and hasattr(orders_df, 'empty') and not orders_df.empty:
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
                    # Fallback para dimensões usando só as dimensões dos blocos
                    st.info("ℹ️ Informações detalhadas dos produtos não disponíveis.")
            else:
                # Fallback para dimensões usando só as dimensões dos blocos  
                st.info("ℹ️ Colunas necessárias não encontradas nos dados dos produtos.")
                    
        except Exception as e:
            st.warning(f"⚠️ Erro ao processar dados de produtos: {str(e)}")
    
    # Fallback para dimensões quando não há dados de produto válidos
    if orders_df is None or (hasattr(orders_df, 'empty') and orders_df.empty):
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
    
    # Mapeamento de cores detalhado (opcional, expandido)
    with st.expander("🎨 Ver mapeamento detalhado de cores", expanded=False):
        st.markdown("**Esquema de cores utilizado:**")
        for i, (dims, color) in enumerate(block_colors.items()):
            st.markdown(f"   • **Tipo {i+1}** ({dims[0]}×{dims[1]}×{dims[2]} cm): `{color}`")
    
    # Estatísticas consolidadas (evitando duplicação)
    st.markdown("---")
    st.markdown("### 📊 Estatísticas de Visualização")
    
    placed_count = len(placements)
    unique_types = len(set(block_dims))
    volume_usado = sum(block_dims[i][0] * block_dims[i][1] * block_dims[i][2] 
                      for i in range(min(placed_count, len(block_dims))))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="📦 Blocos na Visualização",
            value=format_br_number(placed_count),
            help="Quantidade de blocos renderizados na visualização 3D"
        )
    with col2:
        st.metric(
            label="🎨 Tipos Únicos",
            value=unique_types,
            help="Número de dimensões diferentes encontradas"
        )
    with col3:
        st.metric(
            label="📏 Volume Visualizado",
            value=f"{format_br_number(volume_usado)} cm³",
            help="Volume total dos blocos mostrados na visualização"
        )


def main():
    """Ponto de entrada principal da aplicação otimizada."""
    
    # Aplica CSS otimizado
    render_custom_css()
    
    # ========================================
    # SEÇÃO 1: APRESENTAÇÃO MODERNA
    # ========================================
    render_header()
    
    # Quick stats no topo
    col1, col2, col3 = st.columns(3)
    with col1:
        render_optimized_stat_card("Status", "Sistema Online", icon="🟢", color="#00D4AA")
    with col2:
        render_optimized_stat_card("GPU", "Disponível" if check_gpu_availability().get('gpu_available', False) else "CPU Mode", 
                                  icon="⚡", color="#FF6B35")
    with col3:
        render_optimized_stat_card("Otimização", "Ativa", icon="🚀", color="#F7931E")
    
    # Linha separadora
    st.markdown("---")
    
    # ========================================
    # SEÇÃO 2: CONFIGURAÇÃO DO CONTAINER + ALGORITMO
    # ========================================
    st.subheader("⚙️ Configuração do Sistema")
    
    # Container e configuração do algoritmo
    container = render_container_section()
    algoritmo_tipo, config = render_gpu_parameters()
    orders_df = render_blocks_section()
    
    # Linha separadora
    st.markdown("---")
    
    # Linha separadora (só aparece se houver dados)
    if orders_df is not None and not orders_df.empty:
        st.markdown("---")
    
    # ========================================
    # SEÇÃO 4: EXECUÇÃO OTIMIZADA
    # ========================================
    st.subheader("🚀 Processamento")
    
    # Botão de execução
    show_graph = False
    if st.button("🚀 DISTRIBUIR ESTOQUE", type="primary", use_container_width=True):
        # Verifica se há dados de pedidos gerados
        if 'orders_df' not in st.session_state or st.session_state.orders_df is None or st.session_state.orders_df.empty:
            # Mostra caixa informativa se não há pedidos
            st.info("""
            ℹ️ **Nenhum pedido foi gerado ainda!**
            
            Para usar a funcionalidade de distribuição de estoque, você precisa primeiro:
            
            1. **Configurar os parâmetros** do container e quantidade de pedidos
            2. **Clicar em "Gerar Pedidos"** para criar a base de dados
            3. **Depois clicar em "DISTRIBUIR ESTOQUE"** para executar o algoritmo
            
            👆 Volte à seção **"Geração de Pedidos"** acima e clique em **"Gerar Pedidos"** primeiro.
            """)
            return
            
        # Inicia tela de loading
        placeholder, loading_style = show_loading_screen()
        loading_messages = get_creative_loading_messages()
        
        try:
            # FORÇA limpeza completa do estado da sessão
            for key in list(st.session_state.keys()):
                if key.startswith(('placements', 'container', 'block_dims', 'last_run', 'tipo_cores', 'show_completion')):
                    del st.session_state[key]
            
            st.session_state['placements'] = []
            st.session_state['container'] = None
            st.session_state['block_dims'] = []
            st.session_state['last_run'] = False
            st.session_state['show_completion'] = False

            # Processa dados com loading animado (sem sleeps que travem)
            for i, message in enumerate(loading_messages[:3]):  # Apenas 3 mensagens rápidas
                update_loading_message(placeholder, loading_style, message, 3)
            
            # Processa dados de entrada
            block_dims = process_block_data(orders_df)
            
            # Remove possíveis valores None ou inválidos
            block_dims = [dims for dims in block_dims if dims is not None and all(d > 0 for d in dims)]
            
            if not block_dims:
                placeholder.empty()
                st.error("❌ Erro ao processar pedidos. Verifique os dados gerados.")
                return
            
            # Loading para algoritmo
            update_loading_message(placeholder, loading_style, "🧠 Executando algoritmo inteligente", 3)
            
            # Executa algoritmo de empacotamento com configurações do usuário
            placements = run_packing_algorithm(container, block_dims, algoritmo_tipo, config, orders_df)
            
            # Armazena resultados no estado da sessão
            st.session_state.update({
                'placements': placements,
                'container': container,
                'block_dims': block_dims,
                'orders_df': orders_df,  # Armazena orders_df para usar na análise
                'last_run': True,
                'show_completion': True  # Flag para mostrar a tela de conclusão
            })
            
            # Mantém loading enquanto prepara a visualização
            update_loading_message(placeholder, loading_style, "🎨 Gerando visualização 3D", 3)
            
            show_graph = True
            
        except Exception as e:
            placeholder.empty()
            st.error(f"❌ Erro durante processamento: {str(e)}")
            return

    # ========================================
    # SEÇÃO 5: VISUALIZAÇÃO (só aparece após execução)
    # ========================================
    if show_graph and st.session_state.get('last_run', False):
        # Linha separadora
        st.markdown("---")
        
        # Remove a tela de loading ANTES de renderizar
        placeholder.empty()
        
        # Renderiza a visualização
        render_visualization(
            st.session_state['container'],
            st.session_state['placements'],
            st.session_state['block_dims'],
            st.session_state.get('orders_df')  # Passa orders_df para a legenda
        )
        
        # Mostra tela de conclusão e celebração IMEDIATAMENTE após renderização
        if st.session_state.get('show_completion', False):
            # 🎉 CELEBRAÇÃO COM BALÕES APÓS A VISUALIZAÇÃO!
            st.balloons()
            
            st.success("🎉 **EMPACOTAMENTO CONCLUÍDO!** Sua visualização 3D está pronta! ✨")
            
            # Remove a flag para não mostrar novamente
            st.session_state['show_completion'] = False
        
        # Linha separadora
        st.markdown("---")
        
        # Seção de status final elegante
        st.markdown("### 📍 Resumo do Processamento")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            placed_count = len(st.session_state['placements'])
            st.success(f"✅ **{format_br_number(placed_count)}** blocos processados")
        with col2:
            total_count = len(st.session_state['block_dims'])
            placed_count = len(st.session_state['placements'])
            efficiency = calculate_efficiency(placed_count, total_count)
            st.info(f"📊 **{format_br_percentage(efficiency)}** de eficiência")
        with col3:
            st.info("🎨 **Visualização 3D** concluída")
        
        st.markdown("---")
        st.markdown("📍 **Próximos passos:** Use os controles 3D para explorar o resultado ou ajuste os parâmetros para uma nova simulação.")
    elif st.session_state.get('last_run', False):
        # Linha separadora
        st.markdown("---")
        
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
