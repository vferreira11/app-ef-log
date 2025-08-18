# 🎨 Streamlit UI Components
# ===========================
# Componentes reutilizáveis para interface moderna e responsiva

import streamlit as st
from typing import Optional, Dict, Any

class ModernUI:
    """Sistema de design moderno para Streamlit"""
    
    # Design Tokens
    COLORS = {
        'primary': '#FF6B35',
        'secondary': '#00D4AA', 
        'accent': '#F7931E',
        'neutral': '#1A1C24',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6'
    }
    
    SPACING = {
        'xs': '4px', 'sm': '8px', 'md': '16px', 
        'lg': '24px', 'xl': '32px', 'xxl': '48px'
    }
    
    @staticmethod
    def inject_global_css():
        """Injeta CSS global otimizado"""
        st.markdown("""
        <style>
        /* ======================
           PERFORMANCE & ACCESSIBILITY
           ====================== */
        
        :root {
            --primary: #FF6B35;
            --secondary: #00D4AA;
            --accent: #F7931E;
            --neutral: #1A1C24;
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
        }
        
        /* Hardware acceleration for smooth animations */
        .modern-card, .modern-header, .modern-button {
            will-change: transform;
            transform: translateZ(0);
        }
        
        /* Reduced motion for accessibility */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        /* ======================
           MODERN CARD SYSTEM
           ====================== */
        
        .modern-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .modern-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        .modern-card--primary {
            border-left: 4px solid var(--primary);
        }
        
        .modern-card--success {
            border-left: 4px solid var(--success);
        }
        
        .modern-card--warning {
            border-left: 4px solid var(--warning);
        }
        
        .modern-card--error {
            border-left: 4px solid var(--error);
        }
        
        /* ======================
           RESPONSIVE TYPOGRAPHY
           ====================== */
        
        .text-display {
            font-size: clamp(1.5rem, 4vw, 2.5rem);
            font-weight: 800;
            line-height: 1.2;
        }
        
        .text-title {
            font-size: clamp(1.25rem, 3vw, 2rem);
            font-weight: 700;
            line-height: 1.3;
        }
        
        .text-body {
            font-size: clamp(0.875rem, 2vw, 1rem);
            line-height: 1.6;
        }
        
        /* ======================
           MODERN HEADER
           ====================== */
        
        .modern-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 50%, var(--secondary) 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 40px rgba(255, 107, 53, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .modern-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%);
            pointer-events: none;
        }
        
        .modern-header h1 {
            color: white;
            margin: 0;
            font-size: clamp(1.8rem, 5vw, 3rem);
            font-weight: 800;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .modern-header p {
            color: rgba(255,255,255,0.95);
            margin: 0.5rem 0 0 0;
            font-size: clamp(1rem, 2.5vw, 1.25rem);
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        /* ======================
           MOBILE OPTIMIZATIONS
           ====================== */
        
        @media (max-width: 768px) {
            .modern-card {
                padding: 1rem;
                margin-bottom: 0.75rem;
            }
            
            .modern-header {
                padding: 1.5rem 1rem;
                margin-bottom: 1.5rem;
            }
        }
        
        @media (max-width: 480px) {
            .modern-card {
                padding: 0.75rem;
                border-radius: 8px;
            }
            
            .modern-header {
                padding: 1rem;
                border-radius: 12px;
            }
        }
        
        /* ======================
           UTILITY CLASSES
           ====================== */
        
        .flex { display: flex; }
        .flex-col { flex-direction: column; }
        .items-center { align-items: center; }
        .justify-center { justify-content: center; }
        .text-center { text-align: center; }
        .mb-0 { margin-bottom: 0; }
        .mb-1 { margin-bottom: 0.5rem; }
        .mb-2 { margin-bottom: 1rem; }
        .mt-2 { margin-top: 1rem; }
        
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def card(content: str, variant: str = "default", icon: str = "", title: str = "") -> None:
        """
        Renderiza um card moderno
        
        Args:
            content: Conteúdo do card
            variant: Tipo do card (default, primary, success, warning, error)
            icon: Emoji/ícone opcional
            title: Título opcional
        """
        card_class = f"modern-card modern-card--{variant}" if variant != "default" else "modern-card"
        
        title_html = f"<h3 class='text-title mb-1'>{icon} {title}</h3>" if title else ""
        
        st.markdown(f"""
        <div class="{card_class}">
            {title_html}
            <div class="text-body">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def metric_card(title: str, value: str, delta: Optional[str] = None, 
                   icon: str = "📊", color: str = "primary") -> None:
        """
        Card de métrica moderno
        
        Args:
            title: Título da métrica
            value: Valor principal
            delta: Variação (opcional)
            icon: Ícone da métrica
            color: Cor do tema
        """
        delta_html = f"""
        <div style="color: var(--{color}); font-size: 0.875rem; font-weight: 600; margin-top: 0.25rem;">
            ↗ {delta}
        </div>
        """ if delta else ""
        
        st.markdown(f"""
        <div class="modern-card modern-card--{color}">
            <div class="flex items-center mb-1">
                <span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>
                <h3 style="color: #6b7280; font-size: 0.875rem; font-weight: 600; margin: 0;">
                    {title}
                </h3>
            </div>
            <div class="text-display" style="color: var(--{color}); margin-bottom: 0;">
                {value}
            </div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def header(title: str, subtitle: str = "", emoji: str = "🚀") -> None:
        """
        Header moderno com gradiente
        
        Args:
            title: Título principal
            subtitle: Subtítulo opcional
            emoji: Emoji decorativo
        """
        subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
        
        st.markdown(f"""
        <div class="modern-header">
            <h1>{emoji} {title}</h1>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def progress_indicator(current: int, total: int, label: str = "Progresso") -> None:
        """
        Indicador de progresso moderno
        
        Args:
            current: Valor atual
            total: Valor total
            label: Label do progresso
        """
        percentage = int((current / total) * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div class="modern-card">
            <div class="flex justify-between items-center mb-1">
                <span class="text-body" style="font-weight: 600;">{label}</span>
                <span class="text-body" style="color: var(--primary); font-weight: 600;">
                    {percentage}%
                </span>
            </div>
            <div style="background: #e5e7eb; border-radius: 8px; height: 8px; overflow: hidden;">
                <div style="
                    background: linear-gradient(90deg, var(--primary), var(--secondary));
                    height: 100%;
                    width: {percentage}%;
                    border-radius: 8px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <div class="text-body mt-1" style="color: #6b7280; font-size: 0.75rem;">
                {current:,} de {total:,} concluídos
            </div>
        </div>
        """, unsafe_allow_html=True)

# Classe para loading states modernos
class LoadingStates:
    """Estados de loading modernos e acessíveis"""
    
    @staticmethod
    def spinner_overlay(message: str = "Carregando...", progress: int = 0) -> None:
        """
        Overlay de loading com spinner moderno
        
        Args:
            message: Mensagem do loading
            progress: Progresso de 0-100
        """
        st.markdown(f"""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(26, 28, 36, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(10px);
        ">
            <div style="
                width: 60px;
                height: 60px;
                border: 3px solid rgba(0, 212, 170, 0.1);
                border-top: 3px solid #00D4AA;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 2rem;
            "></div>
            
            <h2 style="
                color: white;
                font-size: 1.5rem;
                margin-bottom: 1rem;
                text-align: center;
            ">{message}</h2>
            
            <div style="
                width: 300px;
                height: 6px;
                background: rgba(255,255,255,0.2);
                border-radius: 3px;
                overflow: hidden;
            ">
                <div style="
                    height: 100%;
                    background: linear-gradient(90deg, #00D4AA, #FF6B35);
                    width: {progress}%;
                    border-radius: 3px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            
            <p style="
                color: rgba(255,255,255,0.8);
                margin-top: 1rem;
                font-size: 0.875rem;
            ">{progress}% concluído</p>
        </div>
        
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)

# Utilitários de responsividade
class ResponsiveLayout:
    """Sistema de layout responsivo"""
    
    @staticmethod
    def auto_columns(items: list, min_width: int = 300) -> None:
        """
        Cria colunas automáticas baseadas no conteúdo
        
        Args:
            items: Lista de conteúdos para colunas
            min_width: Largura mínima de cada coluna
        """
        # Calcula número ideal de colunas baseado na tela
        num_cols = max(1, min(len(items), 4))  # Máximo 4 colunas
        
        cols = st.columns(num_cols)
        
        for i, item in enumerate(items):
            with cols[i % num_cols]:
                if callable(item):
                    item()
                else:
                    st.markdown(item)

    @staticmethod
    def mobile_friendly_table(df, max_cols_mobile: int = 3) -> None:
        """
        Tabela otimizada para mobile
        
        Args:
            df: DataFrame para exibir
            max_cols_mobile: Máximo de colunas em mobile
        """
        # Em mobile, mostra versão simplificada
        if len(df.columns) > max_cols_mobile:
            with st.expander("📱 Ver tabela completa"):
                st.dataframe(df, use_container_width=True)
            
            # Versão mobile simplificada
            mobile_df = df.iloc[:, :max_cols_mobile]
            st.dataframe(mobile_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)