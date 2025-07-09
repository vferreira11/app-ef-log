import pandas as pd

# 1. Carrega o CSV
df = pd.read_csv('produtos_simulados.csv')

# 2. Sorteia 2 linhas aleatórias
amostra = df.sample(n=2, random_state=42)  # retire random_state ou ajuste conforme necessidade

# 3. Armazena em novo CSV
amostra.to_csv('amostra_produtos.csv', index=False)

# (Opcional) exibe na tela
print(amostra)
