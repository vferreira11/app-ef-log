# CLAUDE.md

Instruções para Claude Code (claude.ai/code) para este repositório.

## Execução da Aplicação

### Configuração Recomendada
```bash
# Configure o encoding (Windows)
chcp 65001
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

# Ative o ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### Executar a Aplicação
```bash
streamlit run app_gpu_fixed.py
```

### Resolução de Problemas
- **Erro 'charmap' codec**: Configure UTF-8 antes de executar
- **Emojis quebrados**: Terminal deve suportar UTF-8
- **Caracteres estranhos**: Execute `chcp 65001` (Windows)

## Arquitetura

### Interface Principal
- **`app_gpu_fixed.py`** - Interface Streamlit principal
  - Configuração do container
  - Geração de pedidos aleatórios
  - Visualização 3D interativa
  - Análise de resultados

### Visualização 3D
Especificações exatas da visualização:

1. **Container**
   - Dimensões: 15x30x20 cm (largura x profundidade x altura)
   - Wireframe: Preto, espessura 2px
   - Chão: Cinza claro (opacity: 0.3)

2. **Blocos**
   - Cores: Paleta Viridis por tipo
   - Opacidade: 1.0
   - Bordas: Pretas, espessura 2px
   - Escala: 1:1 com container

3. **Layout**
   - aspectmode: 'data'
   - aspectratio: 1:1:1
   - Camera: Default Plotly
   - Dimensões: 900x700px

4. **Interatividade**
   - Hover: Info do bloco
   - displayModeBar: true
   - staticPlot: false

### Módulos Core
Estrutura sob `scripts/core/`:

- **`algorithms.py`**
  - Algoritmo híbrido único com 3 inteligências:
    1. Biomecânico: Zoneamento ergonômico por peso
    2. Chão do Galpão: Empilhamento estável Z=0
    3. GPU Otimizado: Compactação com adjacência

- **`models.py`**
  - ContainerConfig: Dimensões e quantidade
  - Placement: Posicionamento 3D

- **`visualization.py`**
  - Renderização 3D via Plotly
  - Suporte multi-container
  - Mapeamento de cores Viridis

- **`utils.py`**
  - Cálculos de capacidade
  - Validação de dimensões
  - Análise de eficiência

### Configurações
- **`scripts/config/settings.py`**
  - Container padrão: 15x30x20 cm
  - Tipos de bloco default
  - Configurações de GPU
  - Mensagens da UI

### Zonas Ergonômicas
- ZONA_PREMIUM (100-160cm): Alcance ótimo
- ZONA_BOA (160-180cm): Esforço mínimo
- ZONA_ACEITAVEL (70-100cm): Baixo esforço
- ZONA_RUIM (30-70cm): Alto esforço
- ZONA_CRITICA (0-30cm): Zona crítica

### Fluxo de Dados
1. Configuração via interface
2. Geração/validação de pedidos
3. Algoritmo híbrido único
4. Visualização 3D
5. Análise de eficiência

### Dependências
- Streamlit: Interface web
- Plotly: Visualização 3D
- NumPy/Pandas: Processamento
- Numba: Aceleração GPU

### Dados
- `data/produtos_simulados.csv`: Dataset de teste
- `.streamlit/config.toml`: Configuração Streamlit

## Branches
- `v1-clean`: Versão limpa atual
- `main`: Branch principal