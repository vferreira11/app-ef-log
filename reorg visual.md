# Plano de Reestruturação Visual para App Streamlit (Paleta Viridis)

## 1. Paleta de Cores

- **Viridis**: Utilize exclusivamente a paleta Viridis (roxo ao amarelo-esverdeado), garantindo acessibilidade e sofisticação.
    - Exemplos:  
      - Roxo escuro: `#440154`
      - Azul: `#31688e`
      - Verde: `#35b779`
      - Amarelo-esverdeado: `#fde725`
- **Fundo:** Branco ou cinza muito claro para destacar os tons Viridis.
- **Acentos e destaques:** Sempre tons da paleta Viridis.

---

## 2. Layout Geral

- **Header fixo:** Com logo, nome do app e menu minimalista, usando Viridis para títulos e detalhes.
- **Sidebar:** Opcional, para filtros ou navegação, com fundo branco e ícones/textos em tons Viridis.
- **Área principal:** Cards/painéis com bordas suaves, sombra leve e detalhes em Viridis.
- **Footer discreto:** Texto em cinza claro, detalhes em Viridis.

---

## 3. Componentes Visuais

- **Cards:** Use `st.container` ou `st.columns`, com títulos e ícones em tons Viridis.
- **Tabelas:** `st.dataframe` com cabeçalhos e linhas selecionadas em Viridis.
- **Gráficos:** Sempre com colormap Viridis (ex: `color_continuous_scale="viridis"` no Plotly).
- **Botões:** Fundo branco, borda e texto em Viridis, hover com gradiente Viridis.
- **Inputs:** Labels em Viridis, campos claros.

---

## 4. Tipografia

- **Fonte:** Sans-serif moderna.
- **Títulos:** Negrito, cor Viridis escura.
- **Textos:** Cinza escuro, links e destaques em Viridis.

---

## 5. Espaçamento e Hierarquia

- **Espaçamento generoso** entre seções.
- **Divisores** em tons suaves da paleta Viridis.
- **Hierarquia visual clara:** Títulos, subtítulos, corpo do texto.

---

## 6. Experiência do Usuário

- **Feedback visual:** Mensagens de sucesso/erro em tons Viridis.
- **Spinners/loaders:** Use animações ou ícones em Viridis.
- **Responsividade:** Layout adaptável.

---

## 7. Exemplo de Estrutura de Código

```python
import streamlit as st
import plotly.express as px
import numpy as np

# Paleta Viridis via CSS
st.markdown("""
    <style>
        body { background-color: #F8F9FA; }
        .main { background-color: #FFF; border-radius: 12px; box-shadow: 0 2px 8px #E0E0E0; }
        h1, h2, h3 { color: #440154; }
        .stButton>button { color: #FFF; background: linear-gradient(90deg, #440154, #31688e, #35b779, #fde725); border-radius: 8px; }
        .stDataFrame thead { background-color: #31688e !important; color: #FFF; }
    </style>
""", unsafe_allow_html=True)

st.markdown("# Nome do App")
st.markdown("Descrição curta e objetiva.")

with st.sidebar:
    st.header("Navegação")
    st.button("Página 1")
    st.button("Página 2")

st.subheader("Dashboard")
col1, col2 = st.columns(2)
with col1:
    st.metric("Indicador 1", "123")
with col2:
    st.metric("Indicador 2", "456")

st.divider()

st.subheader("Gráfico Viridis")
x = np.linspace(0, 10, 100)
y = np.sin(x)
fig = px.line(x=x, y=y, color_discrete_sequence=px.colors.sequential.Viridis)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr><center><small>© 2025 Sua Empresa</small></center>", unsafe_allow_html=True)
```

---

## 8. Inspirações

- [Streamlit Gallery](https://streamlit.io/gallery)
- [Material Design](https://material.io/design)
- [Viridis colormap](https://matplotlib.org/stable/users/explain/colors/colormaps.html#viridis)

---

**Resumo:**  
O design deve ser clean, profissional e elegante, com **uso estrito da paleta Viridis** em todos os elementos visuais e gráficos, garantindo identidade visual forte, acessibilidade e sofisticação.