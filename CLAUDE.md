# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application

#### Método Recomendado (Windows):

**Opção 1 - Script Batch:**
```bash
# Execute o script batch (duplo clique ou via CMD)
run_app.bat
```

**Opção 2 - Script PowerShell:**
```powershell
# Execute via PowerShell
.\run_app.ps1
```

#### Método Manual:
```bash
# Configure o encoding antes de executar
chcp 65001
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Run the main Streamlit application
streamlit run app_gpu_fixed.py
```

#### Resolução de Problemas de Encoding:
- **Erro 'charmap' codec**: Use os scripts automatizados acima
- **Emojis não aparecem**: Verifique se o terminal suporta UTF-8
- **Caracteres estranhos**: Execute `chcp 65001` antes do comando

### Dependencies
```bash
# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

### Main Application
- **`app_gpu_fixed.py`** - Primary Streamlit interface that orchestrates the 3D packing optimization system
- Entry point that combines all core modules and provides the web interface

### Visualização 3D Padrão
A visualização 3D do empacotamento segue estas configurações exatas:

1. **Container**
   - Dimensões padrão: 15x30x20 cm (largura x profundidade x altura)
   - Wireframe em preto com espessura 2
   - Plano do chão em cinza claro (opacity: 0.3)

2. **Blocos**
   - Cores: Paleta Viridis por tipo de bloco
   - Opacidade: 1.0 (totalmente sólidos)
   - Bordas: Pretas com espessura 2
   - Dimensões: Escala real 1:1 com o container

3. **Layout**
   - aspectmode: 'data'
   - aspectratio: x=1, y=1, z=1
   - Camera: Posição default do Plotly (sem configuração manual)
   - Dimensões: width=900, height=700

4. **Interação**
   - Hover com informações do bloco (posição e dimensões)
   - displayModeBar: true
   - staticPlot: false

### Core Modules Structure
The application follows a modular architecture under `scripts/core/`:

- **`algorithms.py`** - Contains hybrid intelligent packing algorithms combining:
  - ABC classification for demand-based prioritization
  - Biomechanical zoning for ergonomic placement (operator height-based zones)
  - GPU-accelerated optimization using CuPy/Numba
  - Greedy algorithms for gap filling

- **`models.py`** - Data models and classes:
  - `ContainerConfig` - Container dimensions and properties
  - `Placement` - Block positioning with orientations
  - `BlockType` - Block specifications and volume calculations

- **`visualization.py`** - 3D visualization using Plotly:
  - Interactive 3D plotting with container wireframes
  - Block placement visualization with color mapping
  - Multi-container support with spatial separation

- **`utils.py`** - Utility functions for:
  - Capacity calculations and efficiency metrics
  - Color mapping using Viridis palette
  - Block validation and dimension formatting
  - Analytics and reporting functions

### Configuration
- **`scripts/config/settings.py`** - Centralized configuration including:
  - Default container dimensions and block types
  - GPU population parameters
  - Biomechanical zones (ZONA_PREMIUM, ZONA_BOA, etc.)
  - UI messages and visualization settings

### Algorithm Intelligence System
The core algorithm (`hybrid_intelligent_packing`) implements a 4-stage optimization:

1. **ABC Classification** - Demand-based product prioritization
2. **Biomechanical Zoning** - Ergonomic placement based on operator height (170cm reference)
3. **Physical Validation** - Floor-level stability and weight distribution
4. **Greedy Optimization** - Gap filling and compaction

### Ergonomic Zones (Height-based)
- ZONA_PREMIUM (100-160cm): Optimal reach zone
- ZONA_BOA (160-180cm): Minimal effort zone
- ZONA_ACEITAVEL (70-100cm): Low effort zone
- ZONA_RUIM (30-70cm): High effort zone
- ZONA_CRITICA (0-30cm): Critical zone (avoid heavy items)

### Data Flow
1. User configures containers and blocks via Streamlit interface
2. Data validation through `utils.py` functions
3. Algorithm selection (GPU, hybrid, or biomechanical)
4. Processing through `algorithms.py` with ABC classification
5. 3D visualization via `visualization.py`
6. Results display with efficiency metrics

### Key Dependencies
- **Streamlit** - Web interface framework
- **Plotly** - 3D visualization
- **NumPy/Pandas** - Data processing
- **Numba** - GPU acceleration
- **PuLP** - Linear programming (legacy MILP support)

### Legacy Components
- `scripts/distribuir_milp.py` - Original MILP algorithm (kept for reference)
- `scripts/run_packing_gpu.py` - Standalone GPU algorithm
- Multiple visualization variants in `scripts/core/visualization_*.py` - Different 3D rendering approaches

### Data Files
- `data/produtos_simulados.csv` - Sample product dataset for testing
- `streamlit/config.toml` - Streamlit-specific configuration

## Branch Strategy
- `v1-clean` - Current minimal functional version (14 essential files)
- `main` - Primary development branch
- `copilot_v0` - Historical version with full development history