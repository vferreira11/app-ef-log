# 🎯 Algoritmos de Empacotamento 3D - Guia Visual

## 📚 Índice
- [Visão Geral](#-visão-geral)
- [As 4 Inteligências](#-as-4-inteligências)
- [Fluxo Completo](#-fluxo-completo)
- [Nomenclatura e Zoneamento](#-nomenclatura-e-zoneamento)
- [Container Padrão](#-container-padrão)
- [Exemplos Práticos](#-exemplos-práticos)

## 🎭 Visão Geral

Este sistema implementa **4 inteligências integradas** para otimização de empacotamento 3D, combinando **eficiência operacional**, **ergonomia biomecânica**, **estabilidade física** e **aproveitamento máximo do espaço**.

### 🧠 Analogia Visual (Para TDAH)

Imagine que você está organizando uma **farmácia**:

```
🏪 FARMÁCIA = CONTAINER
💊 REMÉDIOS = PRODUTOS
👨‍⚕️ FARMACÊUTICO = OPERADOR
📊 RECEITAS POR MÊS = DEMANDA ABC
```

## 🎭 As 4 Inteligências

### 1️⃣ 📊 GERENTE COMERCIAL (Curva ABC)
```
"Quais remédios saem mais?"
- Aspirina: 100 vendas/mês = CURVA A (alta rotatividade)
- Vitamina C: 30 vendas/mês = CURVA B (média rotatividade)  
- Pomada rara: 2 vendas/mês = CURVA C (baixa rotatividade)

DECISÃO: Aspirina vai para altura dos olhos! 👀
```

### 2️⃣ 🧬 FISIOTERAPEUTA (Biomecânico)
```
"Onde o farmacêutico consegue pegar sem se machucar?"
- Altura dos olhos = Zona Α (Alpha) - PERFEITA
- Altura do peito = Zona Β (Beta) - BOA
- No chão = Zona Γ (Gamma) - RUIM para as costas

DECISÃO: Pesados embaixo, leves em cima! 💪
```

### 3️⃣ 🏗️ ENGENHEIRO (Física)
```
"Isso vai cair?"
- Caixa pesada em cima de leve = ❌ CAI
- Base sólida com 60% apoio = ✅ ESTÁVEL

DECISÃO: Verifica se não vai desabar! 🏗️
```

### 4️⃣ 🤖 FAXINEIRO (Greedy)
```
"Sobrou espaço? Vou aproveitar!"
- Pega produtos rejeitados pelos outros
- Encaixa em qualquer buraquinho
- Salva produtos importantes

DECISÃO: Aproveita cada cantinho! 🧹
```

## 🎬 Fluxo Completo

```
📦 CHEGARAM 100 PRODUTOS NA FARMÁCIA

1️⃣ GERENTE COMERCIAL classifica:
   🔥 20 produtos CURVA A (alta venda)
   📊 30 produtos CURVA B (média venda)  
   📉 50 produtos CURVA C (baixa venda)

2️⃣ FISIOTERAPEUTA define zonas:
   👑 CURVA A → Zona Α (altura dos olhos)
   🎯 CURVA B → Zona Β (altura do peito)
   📦 CURVA C → Zona Γ (qualquer lugar)

3️⃣ ENGENHEIRO valida:
   ✅ "Este arranjo é estável?"
   ✅ "Tem apoio suficiente?"
   ✅ "Não vai cair?"

4️⃣ FAXINEIRO limpa:
   🤖 "Opa, sobrou 5 produtos importantes!"
   🤖 "Vou encaixar eles em algum lugar!"
   🤖 "Melhor mal colocado que perdido!"
```

## 🏷️ Nomenclatura e Zoneamento

### 📈 CURVA ABC (Giro/Demanda)
- **A**: Alta rotatividade (≥50 vendas/mês)
- **B**: Média rotatividade (15-49 vendas/mês)  
- **C**: Baixa rotatividade (<15 vendas/mês)

### 🏛️ CLASSIFICAÇÃO POR ZONAS (Letras Gregas)
- **Α (Alpha)**: Zona Premium - altura ideal
- **Β (Beta)**: Zona Boa - fácil alcance
- **Γ (Gamma)**: Zona Aceitável - alcance médio
- **Δ (Delta)**: Zona Ruim - alcance difícil
- **Ε (Epsilon)**: Zona Crítica - muito difícil

### 🏗️ ZONEAMENTO FÍSICO (Números Romanos)
- **I**: Chão (0-30cm)
- **II**: Baixa (30-70cm)
- **III**: Ideal (70-160cm) 
- **IV**: Alta (160-180cm)
- **V**: Crítica (>180cm)

### 🔗 RELAÇÃO ENTRE OS SISTEMAS

```
CURVA ABC → CLASSIFICAÇÃO → ZONEAMENTO FÍSICO

Produto CURVA A + Peso 2kg → Zona Α → Região III (ideal)
Produto CURVA B + Peso 5kg → Zona Β → Região II (baixa)  
Produto CURVA C + Peso 1kg → Zona Γ → Região V (crítica)
```

## 📐 Container Padrão

### 🏗️ Representação 3D do Container

```
                    ┌─────────────────────────────────┐
                   /│                                 │
                  / │          ZONA V (CRÍTICA)       │ 200cm
                 /  │         >180cm - Ε (Epsilon)    │
                /   │                                 │
               /    ├─────────────────────────────────┤
              /     │          ZONA IV (ALTA)        │ 180cm
             /      │       160-180cm - Δ (Delta)     │
            /       ├─────────────────────────────────┤
           /        │                                 │
          /         │          ZONA III (IDEAL)      │ 160cm
         /          │       70-160cm - Α,Β (Alpha/Beta)│
        /           │                                 │
       /            │      👁️ ALTURA DOS OLHOS       │ 100cm
      /             │                                 │
     /              ├─────────────────────────────────┤
    /               │          ZONA II (BAIXA)       │ 70cm
   /                │       30-70cm - Γ (Gamma)      │
  /                 ├─────────────────────────────────┤
 /                  │          ZONA I (CHÃO)         │ 30cm
└───────────────────┴─────────────────────────────────┘ 0cm
│←────── 40cm ─────→│
│←────────── 30cm ──────────→│

Dimensões Padrão: 30cm (L) × 40cm (P) × 50cm (A)
Escala 1:10 (1cm = 10cm real)
```

### 🎯 Mapeamento de Zonas por Altura

| Altura Real | Zona Física | Classificação | Adequação | Uso Recomendado |
|-------------|-------------|---------------|-----------|-----------------|
| 0-30cm      | I (Chão)    | Ε (Epsilon)   | ⚠️ Crítica | Produtos C pesados |
| 30-70cm     | II (Baixa)  | Γ (Gamma)     | 📦 Aceitável | Produtos B/C médios |
| 70-100cm    | III (Ideal) | Β (Beta)      | 🎯 Boa | Produtos B leves |
| 100-160cm   | III (Ideal) | Α (Alpha)     | 👑 Premium | Produtos A todos |
| 160-180cm   | IV (Alta)   | Δ (Delta)     | ⚠️ Difícil | Produtos C leves |
| >180cm      | V (Crítica) | Ε (Epsilon)   | ❌ Crítica | Apenas emergência |

### 🧍 Referência Ergonômica (Operador 170cm)

```
     👤 OPERADOR 170cm
     
🆘 >200cm ─ Ε ─ ZONA V  ─ ❌ Impossível
⚠️  180cm ─ Δ ─ ZONA IV ─ 🔻 Braços estendidos
👑  160cm ─ Α ─ ZONA III ─ 👁️ ALTURA DOS OLHOS
🎯  100cm ─ Β ─ ZONA III ─ 💪 Altura do peito  
📦   70cm ─ Γ ─ ZONA II  ─ 🤏 Flexão leve
⚠️   30cm ─ Ε ─ ZONA I   ─ 🔻 Agachamento
🆘    0cm ─ Ε ─ ZONA I   ─ ❌ Chão
```

## 🎯 Exemplos Práticos

### Exemplo 1: Aspirina (Produto Ideal)
```
💊 ASPIRINA:
- Demanda: 100/mês → CURVA A
- Peso: 0.5kg → Leve
- Categoria: Medicamento → Frágil
- Resultado: Zona Α → Região III (100-160cm)
- Posição Final: (5, 10, 12) - Altura dos olhos ✅
```

### Exemplo 2: Xarope Pesado (Produto Especial)
```
🏺 XAROPE PESADO:
- Demanda: 80/mês → CURVA A  
- Peso: 3kg → Pesado
- Categoria: Líquido → Cuidado especial
- Resultado: Zona Α → Região II (30-70cm)
- Posição Final: (2, 5, 6) - Altura do peito ✅
```

### Exemplo 3: Vacina Rara (Produto Flexível)
```
💉 VACINA RARA:
- Demanda: 2/mês → CURVA C
- Peso: 0.2kg → Muito leve  
- Categoria: Especialidade → Pouco uso
- Resultado: Zona Ε → Região V (>180cm)
- Posição Final: (15, 20, 45) - Lá em cima ✅
```

### Exemplo 4: Produto Recuperado pelo Greedy
```
🔧 BAND-AID IMPORTANTE:
- Demanda: 60/mês → CURVA A
- Rejeitado pelas outras inteligências (espaço ocupado)
- Greedy encontra espaço em: (8, 12, 25)
- Não é ideal, mas está alocado! 🤖
```

## 🧠 Resumo para TDAH

### 🎯 REGRA DE OURO
```
QUEM VENDE MAIS = MAIS FÁCIL DE PEGAR
QUEM PESA MAIS = MAIS EMBAIXO
QUEM É INSTÁVEL = NÃO PODE FICAR
QUEM SOBROU = GREEDY SALVA
```

### 🏆 RESULTADO FINAL
- **97%+** dos produtos alocados
- **Produtos importantes** sempre acessíveis  
- **Farmacêutico feliz** (sem dor nas costas)
- **Cliente satisfeito** (atendimento rápido)

---

## 📚 Referências Técnicas

- **Arquivo Principal**: `scripts/core/algorithms.py`
- **Função Principal**: `hybrid_intelligent_packing()`
- **Configuração**: `scripts/core/models.py` - `ContainerConfig`
- **Visualização**: `scripts/core/visualization.py`

### 🔧 Funções Auxiliares

1. **`classificar_abc_por_giro()`** - Determina curva ABC
2. **`determinar_zona_biomecanica()`** - Mapeia zona ergonômica
3. **`get_zona_abc_biomecanica()`** - Valida adequação altura/peso
4. **`aplicar_greedy_inteligente()`** - Recupera produtos rejeitados

---

*📝 Documentação criada para facilitar compreensão e manutenção dos algoritmos de empacotamento 3D.*
