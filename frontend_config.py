# ⚡ Performance & UX Configuration
# Configurações otimizadas para melhor performance e experiência do usuário

# ========================================
# CACHE SETTINGS
# ========================================
ENABLE_CACHE = True
CACHE_TTL = 3600  # 1 hora
MAX_CACHE_ENTRIES = 50

# ========================================
# UI PERFORMANCE
# ========================================
# Lazy loading thresholds
LAZY_LOAD_THRESHOLD = 1000  # Elementos para ativar lazy loading
BATCH_SIZE = 100  # Tamanho do batch para renderização
PROGRESS_UPDATE_INTERVAL = 5  # Intervalo para updates de progresso (%)

# Animation settings
ANIMATION_DURATION = 300  # ms
ENABLE_ANIMATIONS = True
REDUCE_MOTION_RESPECT = True  # Respeita prefers-reduced-motion

# ========================================
# VISUALIZATION SETTINGS
# ========================================
# Plotly performance configs
PLOTLY_CONFIG = {
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

# 3D Rendering limits
MAX_BLOCKS_3D = 2000  # Máximo de blocos para rendering 3D
FALLBACK_TO_2D = True  # Fallback para 2D se exceder limite
WEBGL_ENABLED = True  # Use WebGL para performance

# ========================================
# RESPONSIVE BREAKPOINTS
# ========================================
BREAKPOINTS = {
    'mobile': 480,
    'tablet': 768,
    'desktop': 1024,
    'large': 1440
}

# ========================================
# ACCESSIBILITY
# ========================================
# WCAG 2.1 compliance settings
MIN_CONTRAST_RATIO = 4.5
FOCUS_OUTLINE_WIDTH = 2
TOUCH_TARGET_MIN_SIZE = 44  # px

# Screen reader support
ARIA_LABELS_ENABLED = True
SEMANTIC_HTML = True

# ========================================
# LOADING & FEEDBACK
# ========================================
# Loading messages for different operations
LOADING_MESSAGES = {
    'processing': 'Processando dados...',
    'optimizing': 'Otimizando algoritmo...',
    'rendering': 'Gerando visualização...',
    'finalizing': 'Finalizando resultado...'
}

# Progress bar colors
PROGRESS_COLORS = {
    'primary': '#00D4AA',
    'secondary': '#FF6B35',
    'success': '#28a745',
    'warning': '#ffc107',
    'error': '#dc3545'
}

# ========================================
# THEME SETTINGS
# ========================================
# Color palette otimizada
COLORS = {
    'primary': '#00D4AA',
    'secondary': '#FF6B35',
    'accent': '#F7931E',
    'background': '#f8f9fb',
    'surface': '#ffffff',
    'text_primary': '#1A1C24',
    'text_secondary': '#5A6474',
    'text_muted': '#8A94A6',
    'border': '#E6EAF1',
    'shadow': 'rgba(0,0,0,0.04)'
}

# Gradient definitions
GRADIENTS = {
    'primary': 'linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #00D4AA 100%)',
    'success': 'linear-gradient(90deg, #28a745 0%, #20c997 100%)',
    'warning': 'linear-gradient(90deg, #ffc107 0%, #fd7e14 100%)'
}

# ========================================
# PERFORMANCE MONITORING
# ========================================
# Enable performance tracking
ENABLE_PERFORMANCE_TRACKING = True
LOG_RENDER_TIMES = True
SHOW_DEBUG_INFO = False  # Set to True for development

# Performance thresholds (milliseconds)
PERFORMANCE_THRESHOLDS = {
    'fast': 1000,
    'acceptable': 3000,
    'slow': 5000
}

# ========================================
# FEATURE FLAGS
# ========================================
# Progressive enhancement features
FEATURES = {
    'advanced_caching': True,
    'lazy_loading': True,
    'progressive_rendering': True,
    'performance_monitoring': True,
    'accessibility_enhancements': True,
    'mobile_optimizations': True,
    'offline_support': False,  # Future feature
    'pwa_features': False      # Future feature
}
