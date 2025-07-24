# 📐 Especificações Técnicas do Container

## 🏗️ Container Padrão - Representação Técnica

### 📏 Dimensões Físicas
```
CONTAINER PADRÃO
├── Largura (X): 30cm (300mm)
├── Profundidade (Y): 40cm (400mm)  
└── Altura (Z): 50cm (500mm)

Volume Total: 60.000 cm³ (60 litros)
Escala Representação: 1:10 (1cm = 10cm real)
```

## 🎯 Mapeamento 3D Completo

### 📐 Vista Lateral (Perfil Z)
```
200cm ┌─────────────────────────────────┐ ZONA V - Ε (CRÍTICA)
      │  ⚠️ Acesso apenas c/ escada     │ Rom: V
180cm ├─────────────────────────────────┤ ZONA IV - Δ (DIFÍCIL)  
      │  🤏 Braços totalmente estendidos │ Rom: IV
160cm ├─────────────────────────────────┤ ZONA III - Α (PREMIUM)
      │  👁️ ALTURA DOS OLHOS - IDEAL    │ Rom: III
100cm │  🎯 Acesso perfeito sem esforço │
      │  💪 ALTURA DO PEITO - BOA       │
70cm  ├─────────────────────────────────┤ ZONA II - Γ (ACEITÁVEL)
      │  🤏 Flexão leve do tronco       │ Rom: II  
30cm  ├─────────────────────────────────┤ ZONA I - Ε (CRÍTICA)
      │  🔻 Agachamento necessário       │ Rom: I
0cm   └─────────────────────────────────┘ CHÃO
```

### 📐 Vista Superior (Planta XY)
```
      ←─── 40cm (Profundidade) ───→
    ┌─────────────────────────────┐ ↑
    │  A1   A2   A3   A4   A5   │ │
    ├─────────────────────────────┤ │
    │  B1   B2   B3   B4   B5   │ │
    ├─────────────────────────────┤ │ 30cm
    │  C1   C2   C3   C4   C5   │ │ (Largura)
    ├─────────────────────────────┤ │
    │  D1   D2   D3   D4   D5   │ │
    └─────────────────────────────┘ ↓
    
Grade: 20 posições por nível (4x5)
Níveis: 5 zonas verticais
Total: 100 posições possíveis
```

## 🎯 Sistema de Coordenadas

### 📍 Origem e Eixos
```
ORIGEM: (0, 0, 0) = Canto inferior esquerdo frontal

EIXO X: 0 → 30cm (Largura)
EIXO Y: 0 → 40cm (Profundidade) 
EIXO Z: 0 → 50cm (Altura)

Exemplo de Posição:
├── (15, 20, 25) = Centro do container
├── (0, 0, 0) = Canto inferior esquerdo
└── (30, 40, 50) = Canto superior direito
```

### 🗺️ Mapeamento Zona → Coordenadas

| Zona | Altura Real | Z Container | Classificação | Adequação |
|------|-------------|-------------|---------------|-----------|
| I    | 0-30cm      | 0-6cm       | Ε (Epsilon)   | ⚠️ Crítica |
| II   | 30-70cm     | 6-14cm      | Γ (Gamma)     | 📦 Aceitável |
| III  | 70-160cm    | 14-32cm     | Α/Β (Alpha/Beta) | 👑 Premium |
| IV   | 160-180cm   | 32-36cm     | Δ (Delta)     | ⚠️ Difícil |
| V    | >180cm      | 36-50cm     | Ε (Epsilon)   | ❌ Crítica |

## 🧍 Referência Ergonômica

### 👤 Operador Padrão (170cm)
```
MEDIDAS ANTROPOMÉTRICAS:
├── Altura Total: 170cm
├── Altura dos Olhos: 160cm (👁️ IDEAL)
├── Altura dos Ombros: 145cm
├── Altura do Peito: 100cm (💪 BOM)
├── Altura da Cintura: 70cm
└── Alcance Máximo: 200cm (⚠️ CRÍTICO)

CAPACIDADES:
├── Peso Máximo: 20kg (💪 Seguro)
├── Alcance Confortável: 60cm
├── Flexão Segura: 30cm abaixo cintura
└── Extensão Segura: 30cm acima ombros
```

### 🔄 Mapeamento Ergonômico
```
PRODUTO + CARACTERÍSTICAS → ZONA RECOMENDADA

Curva A + Leve (0-2kg) → Α (Alpha) → III (100-160cm)
Curva A + Médio (2-5kg) → Β (Beta) → III (70-100cm)  
Curva A + Pesado (5-20kg) → Γ (Gamma) → II (30-70cm)

Curva B + Leve → Β (Beta) → III/IV
Curva B + Médio → Γ (Gamma) → II/III
Curva B + Pesado → Γ (Gamma) → II

Curva C + Qualquer → Δ/Ε → IV/V (aproveitamento)
```

## 🎯 Algoritmo de Posicionamento

### 📊 Sequência de Decisão
```
1️⃣ CLASSIFICAÇÃO ABC
   ├── Giro ≥50/mês → A (🔥 Alta Prioridade)
   ├── Giro 15-49/mês → B (📊 Média Prioridade)
   └── Giro <15/mês → C (📉 Baixa Prioridade)

2️⃣ ZONA BIOMECÂNICA
   ├── A + Leve → Α (Premium)
   ├── A + Pesado → Β (Boa)
   ├── B → Γ (Aceitável)
   └── C → Δ/Ε (Flexível)

3️⃣ VALIDAÇÃO FÍSICA
   ├── ✅ Base ≥60% apoiada
   ├── ✅ Centro massa dentro base
   └── ✅ Peso superior ≤ inferior

4️⃣ RECUPERAÇÃO GREEDY
   └── 🤖 Produtos rejeitados → Melhor espaço disponível
```

## 📈 Métricas de Performance

### 🎯 Indicadores Principais
```
TAXA DE ALOCAÇÃO:
├── Curva A: 100% (prioridade absoluta)
├── Curva B: 98% (alta prioridade)
├── Curva C: 95% (recuperação Greedy)
└── Total: 97%+ (excelente)

DISTRIBUIÇÃO ERGONÔMICA:
├── Zona Α: 85% produtos A
├── Zona Β: 70% produtos A+B
├── Zona Γ: 50% produtos B+C
└── Zona Δ/Ε: 90% produtos C
```

### ⚡ Otimizações Aplicadas
```
BONIFICAÇÕES ABC:
├── Curva A: +1000 pontos (máxima prioridade)
├── Curva B: +100 pontos (boa prioridade)
└── Curva C: +10 pontos (básica)

PENALIZAÇÕES ERGONÔMICAS:
├── Zona inadequada: -500 pontos
├── Peso excessivo: -200 pontos
└── Altura crítica: -100 pontos

ALGORITMO HÍBRIDO:
├── 60% Algoritmo Principal (ABC+Bio+Física)
└── 40% Recuperação Greedy (aproveitamento)
```

## 🔧 Parâmetros Configuráveis

### ⚙️ Configuração Container
```python
CONTAINER_CONFIG = {
    'largura': 30,      # cm
    'profundidade': 40, # cm  
    'altura': 50,       # cm
    'resolucao': 1,     # cm (precisão grid)
    'margem_seguranca': 0.5  # cm
}
```

### 🎯 Configuração ABC
```python
ABC_CONFIG = {
    'limite_a': 50,     # vendas/mês para Curva A
    'limite_b': 15,     # vendas/mês para Curva B
    'bonus_a': 1000,    # pontos Curva A
    'bonus_b': 100,     # pontos Curva B
    'bonus_c': 10       # pontos Curva C
}
```

### 🧬 Configuração Biomecânica
```python
BIOMEC_CONFIG = {
    'altura_operador': 170,    # cm
    'peso_max_operador': 20,   # kg
    'zona_alpha': [100, 160],  # cm (ideal)
    'zona_beta': [70, 100],    # cm (boa)
    'zona_gamma': [30, 70],    # cm (aceitável)
    'zona_delta': [160, 180],  # cm (difícil)
    'zona_epsilon': [0, 30, 180, 200]  # cm (crítica)
}
```

---

*📐 Especificações técnicas para implementação e manutenção do sistema de empacotamento 3D.*
