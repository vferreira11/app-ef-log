# App EF Log - V1 Clean

Sistema de otimização 3D para empacotamento inteligente com algoritmos híbridos e visualização em tempo real.

## 🎯 Arquitetura V1 - Essenciais

### Aplicação Principal
- **`app_gpu_fixed.py`** - Interface Streamlit com algoritmos híbridos (GPU + biomecânico + floor-level)

### Módulos Core
- **`scripts/core/algorithms.py`** - Algoritmos de empacotamento (GPU, biomecânico, híbrido)
- **`scripts/core/models.py`** - Modelos de dados (ContainerConfig, Item, etc.)
- **`scripts/core/utils.py`** - Utilitários e funções auxiliares
- **`scripts/core/visualization.py`** - Visualização 3D com Plotly

### Configuração
- **`scripts/config/settings.py`** - Configurações centralizadas do sistema

### Dependencies Legacy
- **`scripts/distribuir_milp.py`** - Algoritmo MILP original
- **`scripts/run_packing_gpu.py`** - Algoritmo GPU standalone

### Dados & Config
- **`data/produtos_simulados.csv`** - Dataset de produtos para testes
- **`streamlit/config.toml`** - Configuração do Streamlit
- **`.gitignore`** - Controle de versão

## 🚀 Como Executar

```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Executar aplicação
streamlit run app_gpu_fixed.py
```

## 📊 Funcionalidades

- ✅ Algoritmos híbridos de empacotamento 3D
- ✅ Otimização GPU com CuPy/Numba
- ✅ Análise biomecânica de estabilidade
- ✅ Visualização 3D interativa
- ✅ Interface Streamlit responsiva
- ✅ Relatórios detalhados de alocação

## 🏗️ Branch Strategy

- **`v1-clean`** - Versão mínima funcional (14 arquivos essenciais)
- **`copilot_v0`** - Versão base com histórico completo

---
*Sistema desenvolvido para otimização logística e análise espacial 3D*
