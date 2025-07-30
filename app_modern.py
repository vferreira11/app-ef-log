# -*- coding: utf-8 -*-
"""
🚀 PARADOXO - Sistema de Empacotamento 3D (Versão Otimizada)
============================================================

Interface Streamlit moderna, responsiva e otimizada para performance.
Arquitetura modular com componentes reutilizáveis.

Uso:
    streamlit run app_modern.py
"""

import os
import sys
import streamlit as st
import pandas as pd
import time
from typing import Dict, List, Any, Optional

# Setup de encoding UTF-8
if sys.platform.startswith('win'):
    try:
        import codecs
        if hasattr(sys.stdout, 'detach'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except Exception:
        os.environ['PYTHONIOENCODING'] = 'utf-8'

# Adiciona paths necessários
current_dir = os.path.dirname(os.path.abspath(__file__))
components_dir = os.path.join(current_dir, 'components')
scripts_dir = os.path.join(current_dir, 'scripts')

for directory in [components_dir, scripts_dir]:
    if directory not in sys.path:
        sys.path.append(directory)

# Importa componentes modernos
try:
    from components.ui_components import ModernUI, LoadingStates
    from components.responsive_layout import ResponsiveLayoutManager, PerformanceOptimizer
except ImportError:
    st.error("❌ Erro: Componentes UI não encontrados. Verifique a estrutura do projeto.")
    st.stop()

# Importa módulos do sistema original
try:
    from scripts.core.models import ContainerConfig, Placement
    from scripts.core.algorithms import hybrid_intelligent_packing
    from scripts.core.gpu_algorithms import gpu_hybrid_ultra_intelligent_packing, check_gpu_availability
    from scripts.core.utils import (
        calculate_efficiency, format_br_number, format_br_percentage,
        generate_random_orders, convert_orders_to_block_dims,
        calculate_sales_analytics
    )
    from scripts.config.settings import (
        DEFAULT_CONTAINER_DIMS, DEFAULT_BLOCK_TYPES, 
        GPU_POPULATION_RANGE, MAX_BLOCKS_WARNING
    )
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos do sistema: {e}")
    st.stop()

# Configuração global do Streamlit
st.set_page_config(
    page_title="🚀 PARADOXO - Empacotamento 3D",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ModernPackingApp:
    """Aplicação moderna de empacotamento 3D"""
    
    def __init__(self):
        self.ui = ModernUI()
        self.layout = ResponsiveLayoutManager()
        self.optimizer = PerformanceOptimizer()
        self.loading = LoadingStates()
        
        # Injeta CSS global
        self.ui.inject_global_css()
        
        # Inicializa estado da sessão
        self._init_session_state()
    
    def _init_session_state(self):
        """Inicializa estado da sessão com valores padrão"""
        defaults = {
            'container_config': None,
            'orders_df': None,
            'placements': None,
            'block_dims': None,
            'last_run': False,
            'processing': False,
            'gpu_status': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render_header(self):
        """Renderiza header moderno"""
        self.ui.header(
            title="PARADOXO - Empacotamento 3D",
            subtitle="Otimização Inteligente com IA e Aceleração GPU",
            emoji="🚀"
        )
    
    def render_gpu_status_section(self) -> Dict[str, Any]:
        """Renderiza seção de status GPU e configurações"""
        st.markdown("### 🖥️ Status do Sistema")
        
        # Verifica status GPU
        try:
            gpu_status = check_gpu_availability()
            st.session_state.gpu_status = gpu_status
        except Exception as e:
            st.warning(f"⚠️ Erro na detecção GPU: {e}")
            gpu_status = {'gpu_available': False, 'cuda_available': False}
        
        # Métricas de sistema
        system_metrics = [
            {
                'title': 'Status GPU',
                'value': '✅ RTX 3070 Ti' if gpu_status.get('gpu_available') else '❌ Não Disponível',
                'icon': '🖥️'
            },
            {
                'title': 'CUDA',
                'value': '✅ Disponível' if gpu_status.get('cuda_available') else '❌ Indisponível',
                'icon': '⚡'
            },
            {
                'title': 'Algoritmo',
                'value': 'GPU Ultra-Inteligente' if gpu_status.get('gpu_available') else 'Híbrido CPU',
                'icon': '🧠'
            }
        ]
        
        # Layout responsivo para métricas
        self.layout.responsive_metrics(system_metrics)
        
        # Configurações avançadas em expander
        with st.expander("⚙️ Configurações Avançadas", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                precision = st.selectbox(
                    "Nível de Precisão",
                    ["Rápido (90-95%)", "Balanceado (95-97%)", "Ultra (97-99%)"],
                    index=1
                )
                
                enable_physics = st.checkbox("Validação Física", value=True)
            
            with col2:
                enable_evolution = st.checkbox("Refinamento Evolutivo", value=True)
                
                batch_processing = st.checkbox("Processamento em Lotes", value=False)
        
        return {
            'gpu_status': gpu_status,
            'precision': precision,
            'enable_physics': enable_physics,
            'enable_evolution': enable_evolution,
            'batch_processing': batch_processing
        }
    
    def render_container_config(self) -> ContainerConfig:
        """Renderiza configuração do container"""
        st.markdown("### 📦 Configuração do Container")
        
        col1, col2 = st.columns(2)
        
        with col1:
            container_length = st.number_input(
                "Comprimento (cm)", 
                min_value=100, max_value=2000, 
                value=DEFAULT_CONTAINER_DIMS[0],
                step=10
            )
            
            container_width = st.number_input(
                "Largura (cm)",
                min_value=100, max_value=2000,
                value=DEFAULT_CONTAINER_DIMS[1], 
                step=10
            )
        
        with col2:
            container_height = st.number_input(
                "Altura (cm)",
                min_value=100, max_value=500,
                value=DEFAULT_CONTAINER_DIMS[2],
                step=10
            )
            
            max_weight = st.number_input(
                "Peso Máximo (kg)",
                min_value=1000, max_value=50000,
                value=25000,
                step=500
            )
        
        # Calcula e exibe volume
        volume = container_length * container_width * container_height
        volume_m3 = volume / 1_000_000
        
        # Métricas do container
        container_metrics = [
            {
                'title': 'Volume Total',
                'value': f"{format_br_number(volume_m3, 2)} m³",
                'delta': f"{format_br_number(volume)} cm³",
                'icon': '📦'
            },
            {
                'title': 'Área Base',
                'value': f"{format_br_number((container_length * container_width) / 10000, 2)} m²",
                'icon': '📐'
            },
            {
                'title': 'Peso Suportado',
                'value': f"{format_br_number(max_weight)} kg",
                'icon': '⚖️'
            }
        ]
        
        self.layout.responsive_metrics(container_metrics)
        
        return ContainerConfig(
            length=container_length,
            width=container_width, 
            height=container_height,
            max_weight=max_weight
        )
    
    def render_data_input_section(self) -> Optional[pd.DataFrame]:
        """Renderiza seção de entrada de dados"""
        st.markdown("### 📊 Dados dos Produtos")
        
        # Opções de entrada de dados
        data_source = st.radio(
            "Fonte dos dados:",
            ["🎲 Gerar dados simulados", "📁 Upload de arquivo", "✏️ Entrada manual"],
            horizontal=True
        )
        
        if data_source == "🎲 Gerar dados simulados":
            return self._render_simulated_data()
        elif data_source == "📁 Upload de arquivo":
            return self._render_file_upload()
        else:
            return self._render_manual_input()
    
    def _render_simulated_data(self) -> pd.DataFrame:
        """Renderiza interface para dados simulados"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            num_products = st.number_input(
                "Número de produtos únicos",
                min_value=5, max_value=100,
                value=20, step=5
            )
        
        with col2:
            forecast_multiplier = st.slider(
                "Multiplicador de previsão",
                min_value=0.5, max_value=3.0,
                value=1.2, step=0.1
            )
        
        with col3:
            seed = st.number_input(
                "Seed (para reproduzir)",
                min_value=1, max_value=9999,
                value=42
            )
        
        if st.button("🎲 Gerar Dados Simulados", type="primary"):
            with st.spinner("Gerando dados simulados..."):
                try:
                    orders_df = generate_random_orders(
                        num_products=num_products,
                        forecast_multiplier=forecast_multiplier,
                        seed=seed
                    )
                    
                    st.session_state.orders_df = orders_df
                    st.success(f"✅ {len(orders_df)} produtos gerados com sucesso!")
                    
                    return orders_df
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar dados: {e}")
                    return None
        
        # Se já existe dados na sessão, mostra
        if st.session_state.orders_df is not None:
            return st.session_state.orders_df
        
        return None
    
    def _render_file_upload(self) -> Optional[pd.DataFrame]:
        """Renderiza interface para upload de arquivo"""
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV",
            type=['csv'],
            help="Arquivo deve conter colunas: Nome Produto, Categoria, Comprimento, Largura, Profundidade, etc."
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.orders_df = df
                st.success(f"✅ Arquivo carregado: {len(df)} registros")
                return df
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivo: {e}")
        
        return st.session_state.get('orders_df')
    
    def _render_manual_input(self) -> Optional[pd.DataFrame]:
        """Renderiza interface para entrada manual"""
        st.info("🔧 Funcionalidade de entrada manual em desenvolvimento")
        return st.session_state.get('orders_df')
    
    def render_data_preview(self, orders_df: pd.DataFrame):
        """Renderiza preview dos dados com analytics"""
        if orders_df is None or orders_df.empty:
            return
        
        st.markdown("### 📋 Preview dos Dados")
        
        # Analytics dos dados
        analytics = calculate_sales_analytics(orders_df)
        if analytics:
            # Métricas principais
            main_metrics = [
                {
                    'title': 'Total Produtos',
                    'value': format_br_number(analytics['total_products']),
                    'icon': '📦'
                },
                {
                    'title': 'Previsão Mensal',
                    'value': format_br_number(analytics['total_forecast']),
                    'icon': '📈'
                },
                {
                    'title': 'Peso Previsto',
                    'value': f"{analytics['total_weight_forecast']:.1f} kg",
                    'icon': '⚖️'
                },
                {
                    'title': 'Receita Prevista',
                    'value': f"R$ {analytics['forecast_revenue']:,.0f}".replace(',', '.'),
                    'icon': '💰'
                }
            ]
            
            self.layout.responsive_metrics(main_metrics)
        
        # Tabela responsiva
        self.layout.mobile_friendly_dataframe(
            orders_df.head(10),
            max_cols_mobile=4,
            priority_cols=['Nome Produto', 'Categoria', 'Previsão Próx. Mês']
        )
        
        if len(orders_df) > 10:
            st.caption(f"Mostrando 10 primeiros de {len(orders_df)} registros")
    
    def run_processing(self, container: ContainerConfig, orders_df: pd.DataFrame, 
                      config: Dict[str, Any]) -> bool:
        """Executa processamento principal"""
        try:
            # Converte dados para dimensões de blocos
            with st.spinner("📊 Processando dados dos produtos..."):
                block_dims = convert_orders_to_block_dims(orders_df)
                
                if not block_dims:
                    st.error("❌ Nenhum bloco válido gerado dos dados")
                    return False
                
                st.session_state.block_dims = block_dims
            
            # Loading com progresso
            progress_container = st.empty()
            
            # Simula etapas do processamento
            stages = [
                "🔍 Analisando dados...",
                "🧠 Inicializando algoritmo...", 
                "⚡ Executando otimização...",
                "🎨 Gerando visualização..."
            ]
            
            for i, stage in enumerate(stages):
                progress = int((i + 1) / len(stages) * 100)
                
                with progress_container.container():
                    self.ui.progress_indicator(i + 1, len(stages), stage)
                
                time.sleep(0.5)  # Simula processamento
            
            # Executa algoritmo real
            if config['gpu_status'].get('gpu_available', False):
                with st.spinner("🚀 Executando algoritmo GPU ultra-inteligente..."):
                    placements = gpu_hybrid_ultra_intelligent_packing(
                        container, block_dims, orders_df
                    )
            else:
                with st.spinner("🔄 Executando algoritmo híbrido CPU..."):
                    placements = hybrid_intelligent_packing(
                        container, block_dims, orders_df
                    )
            
            progress_container.empty()
            
            # Armazena resultados
            st.session_state.placements = placements
            st.session_state.container_config = container
            st.session_state.last_run = True
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro durante processamento: {e}")
            return False
    
    def render_results(self):
        """Renderiza seção de resultados"""
        if not st.session_state.get('last_run', False):
            return
        
        st.markdown("---")
        st.markdown("### 🎯 Resultados do Empacotamento")
        
        placements = st.session_state.placements
        block_dims = st.session_state.block_dims
        
        if not placements:
            st.warning("⚠️ Nenhum bloco foi empacotado")
            return
        
        # Métricas de resultado
        placed_count = len(placements)
        total_count = len(block_dims)
        efficiency = calculate_efficiency(placed_count, total_count)
        
        result_metrics = [
            {
                'title': 'Blocos Empacotados',
                'value': format_br_number(placed_count),
                'delta': f"de {format_br_number(total_count)}",
                'icon': '📦'
            },
            {
                'title': 'Eficiência',
                'value': format_br_percentage(efficiency),
                'icon': '📊'
            },
            {
                'title': 'Status',
                'value': '✅ Concluído',
                'icon': '🎯'
            }
        ]
        
        self.layout.responsive_metrics(result_metrics)
        
        # Botão para visualização (lazy loading)
        self.optimizer.lazy_load_component(
            self._render_3d_visualization,
            "🎨 Carregar Visualização 3D"
        )
    
    def _render_3d_visualization(self):
        """Renderiza visualização 3D (componente pesado)"""
        st.markdown("#### 🎨 Visualização 3D")
        
        try:
            # Importa visualização apenas quando necessário
            from scripts.core.visualization import create_3d_plot
            
            # Prepara dados para visualização
            container = st.session_state.container_config
            placements = st.session_state.placements
            block_dims = st.session_state.block_dims
            
            # Cria gráfico 3D
            with st.spinner("Renderizando visualização 3D..."):
                fig = create_3d_plot(container, placements, block_dims)
                st.plotly_chart(fig, use_container_width=True)
            
            st.success("✅ Visualização 3D carregada com sucesso!")
            
        except Exception as e:
            st.error(f"❌ Erro ao renderizar visualização: {e}")
    
    def render_footer(self):
        """Renderiza rodapé moderno"""
        st.markdown("---")
        
        footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 2])
        
        with footer_col1:
            st.markdown("""
            **🚀 PARADOXO**  
            Sistema de Empacotamento 3D  
            *Versão Otimizada 2.0*
            """)
        
        with footer_col2:
            st.markdown("**Tech Stack:**")
            st.markdown("• Streamlit  \n• GPU Computing  \n• Modern UI")
        
        with footer_col3:
            st.markdown("""
            **Desenvolvido por:**  
            [Vinícius Ferreira](https://linkedin.com/in/viniciusferreira11/)  
            *Made in Brazil* 🇧🇷
            """)
    
    def run(self):
        """Executa aplicação principal"""
        # Header
        self.render_header()
        
        # Configurações do sistema
        config = self.render_gpu_status_section()
        
        st.markdown("---")
        
        # Layout em duas colunas principais
        main_col, sidebar_col = st.columns([3, 1])
        
        with main_col:
            # Configuração do container
            container = self.render_container_config()
            
            st.markdown("---")
            
            # Entrada de dados
            orders_df = self.render_data_input_section()
            
            if orders_df is not None:
                # Preview dos dados
                self.render_data_preview(orders_df)
                
                st.markdown("---")
                
                # Botão de execução
                if st.button("🚀 Executar Otimização", type="primary", use_container_width=True):
                    st.session_state.processing = True
                    
                    success = self.run_processing(container, orders_df, config)
                    
                    if success:
                        st.balloons()
                        st.success("🎉 Otimização concluída com sucesso!")
                    
                    st.session_state.processing = False
                
                # Resultados
                self.render_results()
        
        with sidebar_col:
            # Sidebar contextual
            context = "visualization" if st.session_state.get('last_run') else "data_input"
            sidebar_config = self.layout.contextual_sidebar(context)
        
        # Footer
        self.render_footer()

def main():
    """Função principal da aplicação"""
    app = ModernPackingApp()
    app.run()

if __name__ == "__main__":
    main()