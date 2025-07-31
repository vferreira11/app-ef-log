"""
Componentes de loading e feedback visual.
Fornece componentes reutilizáveis para feedback de progresso.
"""

import time
from typing import List, Tuple, Optional
import streamlit as st

class LoadingManager:
    """Gerenciador de componentes de loading."""
    
    def __init__(self):
        self.creative_messages = [
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
    
    def show_loading_screen(self) -> Tuple[st.empty, str]:
        """
        Exibe tela de loading elegante.
        
        Returns:
            Tuple com placeholder e estilo CSS
        """
        placeholder = st.empty()
        
        style = """
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
        
        return placeholder, style
    
    def update_loading_message(self, placeholder: st.empty, style: str, 
                             message: str, dots: int = 3):
        """
        Atualiza mensagem de loading.
        
        Args:
            placeholder: Container Streamlit
            style: CSS da tela
            message: Mensagem atual
            dots: Número de pontos (1-3)
        """
        dots_display = "." * (dots % 4)
        
        html = f"""
        {style}
        <div class="loading-container">
            <div class="loading-title">⏳ AGUARDE</div>
            <div class="loading-spinner"></div>
            <div class="loading-message">{message}</div>
            <div class="loading-dots">{dots_display}</div>
        </div>
        """
        
        placeholder.markdown(html, unsafe_allow_html=True)
    
    def show_completion(self, placeholder: st.empty, style: str, 
                       message: Optional[str] = None):
        """
        Exibe tela de conclusão.
        
        Args:
            placeholder: Container Streamlit
            style: CSS base
            message: Mensagem opcional
        """
        if not message:
            message = "✅ Distribuição de Estoque Finalizada"
            
        html = f"""
        {style}
        <div class="loading-container">
            <div class="loading-title">🎉 CONCLUÍDO!</div>
            <div style="font-size: 1.8rem; margin: 2rem 0; color: #00D4AA;">
                {message}
            </div>
            <div style="font-size: 1.2rem; color: #ccc;">
                Preparando visualização...
            </div>
        </div>
        """
        
        placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(2)
        placeholder.empty()

class ProgressTracker:
    """Gerenciador de barras de progresso."""
    
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
    
    def create(self) -> Tuple[st.progress, st.empty]:
        """
        Cria componentes de progresso.
        
        Returns:
            Tuple com barra e texto de status
        """
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        return self.progress_bar, self.status_text
    
    def update(self, current: int, total: int, message: str):
        """
        Atualiza progresso.
        
        Args:
            current: Valor atual
            total: Valor total
            message: Mensagem de status
        """
        if not (self.progress_bar and self.status_text):
            self.create()
            
        percentage = int((current / total) * 100)
        self.progress_bar.progress(percentage)
        self.status_text.text(f"{message} ({current}/{total}) - {percentage}%")
    
    def clear(self):
        """Limpa componentes de progresso."""
        if self.progress_bar:
            self.progress_bar.empty()
        if self.status_text:
            self.status_text.empty()
            
class ModernLoading:
    """Componente de loading moderno com progress bar."""
    
    def __init__(self):
        self.style = """
        <style>
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
        </style>
        """
    
    def render(self, message: str = "Processando...", progress: int = 0):
        """
        Renderiza loading moderno.
        
        Args:
            message: Mensagem a exibir
            progress: Progresso (0-100)
        """
        html = f"""
        {self.style}
        <div class="modern-loading">
            <div class="loading-spinner-modern"></div>
            <div class="loading-text-modern">{message}</div>
            <div class="loading-progress">
                <div class="loading-progress-bar" style="width: {progress}%;"></div>
            </div>
        </div>
        """
        
        st.markdown(html, unsafe_allow_html=True)

# Instâncias globais
loading = LoadingManager()
progress = ProgressTracker()
modern_loading = ModernLoading()