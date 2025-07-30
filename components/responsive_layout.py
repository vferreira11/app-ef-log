# 📱 Responsive Layout Manager
# ============================
# Sistema de layout adaptativo para diferentes tamanhos de tela

import streamlit as st
import pandas as pd
from typing import Callable, List, Dict, Any, Optional

class ResponsiveLayoutManager:
    """Gerenciador de layout responsivo para Streamlit"""
    
    # Breakpoints responsivos
    BREAKPOINTS = {
        'mobile': 480,
        'tablet': 768,
        'desktop': 1024,
        'large': 1440
    }
    
    def __init__(self):
        self.current_device = self._detect_device()
        self._inject_responsive_css()
    
    def _detect_device(self) -> str:
        """Detecta o tipo de dispositivo baseado no user agent (simulação)"""
        # No Streamlit real, isso seria feito via JavaScript
        # Por enquanto, usamos uma heurística baseada na largura da sidebar
        return "desktop"  # Default para desktop
    
    def _inject_responsive_css(self):
        """Injeta CSS responsivo global"""
        st.markdown("""
        <style>
        /* ======================
           RESPONSIVE UTILITIES
           ====================== */
        
        .responsive-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .responsive-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }
        
        .responsive-grid--dense {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }
        
        .responsive-grid--sparse {
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        }
        
        /* Mobile-first responsive grid */
        @media (max-width: 480px) {
            .responsive-container {
                padding: 0 0.5rem;
            }
            
            .responsive-grid {
                grid-template-columns: 1fr;
                gap: 0.75rem;
            }
            
            .mobile-stack > * {
                margin-bottom: 1rem;
            }
            
            .mobile-hide {
                display: none;
            }
        }
        
        @media (min-width: 481px) and (max-width: 768px) {
            .responsive-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }
            
            .tablet-stack {
                flex-direction: column;
            }
        }
        
        @media (min-width: 769px) {
            .desktop-show {
                display: block;
            }
        }
        
        /* ======================
           ADAPTIVE COMPONENTS
           ====================== */
        
        .adaptive-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .adaptive-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        @media (max-width: 768px) {
            .adaptive-card {
                padding: 1rem;
                border-radius: 8px;
            }
        }
        
        /* ======================
           TOUCH-FRIENDLY ELEMENTS
           ====================== */
        
        .touch-target {
            min-height: 44px;
            min-width: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .touch-button {
            background: linear-gradient(135deg, #FF6B35, #F7931E);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 44px;
        }
        
        .touch-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
        }
        
        .touch-button:active {
            transform: translateY(0);
        }
        
        /* ======================
           COLLAPSIBLE SECTIONS
           ====================== */
        
        .collapsible-section {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        
        .collapsible-header {
            background: #f9fafb;
            padding: 1rem;
            cursor: pointer;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s ease;
        }
        
        .collapsible-header:hover {
            background: #f3f4f6;
        }
        
        .collapsible-content {
            padding: 1rem;
        }
        
        /* ======================
           PERFORMANCE OPTIMIZATIONS
           ====================== */
        
        .gpu-accelerated {
            will-change: transform;
            transform: translateZ(0);
        }
        
        .smooth-scroll {
            scroll-behavior: smooth;
        }
        
        /* Reduce animations for users who prefer reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def adaptive_columns(self, content_items: List[Any], 
                        mobile_cols: int = 1, tablet_cols: int = 2, 
                        desktop_cols: int = 3) -> None:
        """
        Cria layout de colunas adaptativo
        
        Args:
            content_items: Lista de conteúdos para renderizar
            mobile_cols: Número de colunas em mobile
            tablet_cols: Número de colunas em tablet  
            desktop_cols: Número de colunas em desktop
        """
        # Por enquanto, usa a lógica padrão do Streamlit
        # Em uma implementação real, isso seria controlado por JavaScript
        cols = st.columns(desktop_cols)
        
        for i, item in enumerate(content_items):
            with cols[i % desktop_cols]:
                if callable(item):
                    item()
                else:
                    st.markdown(item)
    
    def responsive_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """
        Renderiza métricas de forma responsiva
        
        Args:
            metrics: Lista de métricas com keys: title, value, delta, icon
        """
        # Layout adaptativo baseado no número de métricas
        num_metrics = len(metrics)
        
        if num_metrics <= 2:
            cols = st.columns(num_metrics)
        elif num_metrics <= 4:
            cols = st.columns(2) if self.current_device == 'mobile' else st.columns(num_metrics)
        else:
            # Para muitas métricas, usa grid responsivo
            cols = st.columns(2) if self.current_device == 'mobile' else st.columns(4)
        
        for i, metric in enumerate(metrics):
            with cols[i % len(cols)]:
                st.metric(
                    label=metric.get('title', ''),
                    value=metric.get('value', ''),
                    delta=metric.get('delta', None)
                )
    
    def mobile_friendly_dataframe(self, df: pd.DataFrame, 
                                 max_cols_mobile: int = 3,
                                 priority_cols: Optional[List[str]] = None) -> None:
        """
        Renderiza DataFrame otimizado para mobile
        
        Args:
            df: DataFrame para exibir
            max_cols_mobile: Máximo de colunas em mobile
            priority_cols: Colunas prioritárias para mobile
        """
        if df.empty:
            st.warning("📱 Nenhum dado disponível para exibir")
            return
        
        total_cols = len(df.columns)
        
        # Se há muitas colunas, cria versão mobile
        if total_cols > max_cols_mobile:
            
            # Determina colunas para mobile
            if priority_cols:
                mobile_cols = [col for col in priority_cols if col in df.columns]
                mobile_cols = mobile_cols[:max_cols_mobile]
            else:
                mobile_cols = df.columns[:max_cols_mobile].tolist()
            
            # Cria tabs para mobile vs desktop
            tab1, tab2 = st.tabs(["📱 Resumo", "🖥️ Completo"])
            
            with tab1:
                st.markdown("**Versão mobile otimizada:**")
                mobile_df = df[mobile_cols]
                st.dataframe(mobile_df, use_container_width=True)
                
                # Mostra quais colunas foram ocultadas
                hidden_cols = [col for col in df.columns if col not in mobile_cols]
                if hidden_cols:
                    st.caption(f"Colunas ocultas: {', '.join(hidden_cols)}")
            
            with tab2:
                st.markdown("**Tabela completa:**")
                st.dataframe(df, use_container_width=True)
        else:
            # Se poucas colunas, mostra tudo
            st.dataframe(df, use_container_width=True)
    
    def progressive_disclosure(self, sections: Dict[str, Callable]) -> None:
        """
        Implementa progressive disclosure para interfaces complexas
        
        Args:
            sections: Dict com nome da seção e função de renderização
        """
        for section_name, render_func in sections.items():
            with st.expander(f"📋 {section_name}", expanded=False):
                try:
                    render_func()
                except Exception as e:
                    st.error(f"Erro ao renderizar seção {section_name}: {str(e)}")
    
    def contextual_sidebar(self, context: str = "default") -> None:
        """
        Sidebar contextual que adapta baseado no contexto da página
        
        Args:
            context: Contexto atual da aplicação
        """
        with st.sidebar:
            st.markdown("### ⚙️ Configurações")
            
            if context == "visualization":
                st.markdown("**Controles de Visualização:**")
                show_grid = st.checkbox("Mostrar grade", value=True)
                opacity = st.slider("Opacidade", 0.1, 1.0, 0.8)
                camera_angle = st.selectbox("Ângulo da câmera", 
                                          ["Isométrico", "Frontal", "Superior", "Lateral"])
                
                return {
                    'show_grid': show_grid,
                    'opacity': opacity, 
                    'camera_angle': camera_angle
                }
                
            elif context == "data_input":
                st.markdown("**Configurações de Dados:**")
                auto_refresh = st.checkbox("Auto-refresh", value=False)
                batch_size = st.number_input("Tamanho do lote", 100, 10000, 1000)
                
                return {
                    'auto_refresh': auto_refresh,
                    'batch_size': batch_size
                }
            
            else:
                st.markdown("**Configurações Gerais:**")
                theme = st.selectbox("Tema", ["Claro", "Escuro", "Auto"])
                language = st.selectbox("Idioma", ["Português", "English"])
                
                return {
                    'theme': theme,
                    'language': language
                }

class PerformanceOptimizer:
    """Otimizador de performance para interfaces Streamlit"""
    
    @staticmethod
    def lazy_load_component(component_func: Callable, 
                          trigger_text: str = "Carregar componente") -> None:
        """
        Carregamento lazy de componentes pesados
        
        Args:
            component_func: Função que renderiza o componente
            trigger_text: Texto do botão de trigger
        """
        if st.button(trigger_text):
            with st.spinner("Carregando componente..."):
                try:
                    component_func()
                except Exception as e:
                    st.error(f"Erro ao carregar componente: {str(e)}")
    
    @staticmethod
    def virtual_scroll_table(df: pd.DataFrame, page_size: int = 50) -> None:
        """
        Implementa paginação para grandes DataFrames
        
        Args:
            df: DataFrame para paginar
            page_size: Tamanho da página
        """
        if df.empty:
            st.warning("Nenhum dado para exibir")
            return
        
        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                page = st.selectbox(
                    "Página",
                    range(1, total_pages + 1),
                    format_func=lambda x: f"Página {x} de {total_pages}"
                )
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            
            # Mostra página atual
            st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)
            
            # Informações de paginação
            st.caption(f"Mostrando {start_idx + 1}-{end_idx} de {total_rows} registros")
        else:
            st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def debounced_input(key: str, label: str, delay: float = 0.5) -> str:
        """
        Input com debounce para evitar recálculos excessivos
        
        Args:
            key: Chave única do input
            label: Label do input
            delay: Delay em segundos
            
        Returns:
            Valor do input
        """
        # No Streamlit, implementamos isso usando session_state
        input_value = st.text_input(label, key=key)
        
        # Em uma implementação real, isso teria debounce via JavaScript
        return input_value

# Classe utilitária para analytics
class UIAnalytics:
    """Sistema de analytics para UI Streamlit"""
    
    @staticmethod
    def track_interaction(component: str, action: str, metadata: Dict = None) -> None:
        """
        Rastreia interações do usuário
        
        Args:
            component: Nome do componente
            action: Ação realizada
            metadata: Metadados adicionais
        """
        # Em uma implementação real, isso enviaria dados para analytics
        if 'ui_analytics' not in st.session_state:
            st.session_state.ui_analytics = []
        
        st.session_state.ui_analytics.append({
            'component': component,
            'action': action, 
            'metadata': metadata or {},
            'timestamp': st._get_script_run_ctx().session_id  # Timestamp simulado
        })
    
    @staticmethod
    def get_analytics_summary() -> Dict:
        """Retorna resumo das analytics coletadas"""
        if 'ui_analytics' not in st.session_state:
            return {'total_interactions': 0, 'components': {}}
        
        analytics = st.session_state.ui_analytics
        components = {}
        
        for event in analytics:
            comp = event['component']
            if comp not in components:
                components[comp] = {'total': 0, 'actions': {}}
            
            components[comp]['total'] += 1
            action = event['action']
            
            if action not in components[comp]['actions']:
                components[comp]['actions'][action] = 0
            
            components[comp]['actions'][action] += 1
        
        return {
            'total_interactions': len(analytics),
            'components': components
        }