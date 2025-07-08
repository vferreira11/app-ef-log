
import pandas as pd
import sqlite3
import os

# Caminho do CSV de entrada
caminho_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "produtos_simulados.csv"))

# Leitura da base simulada
df = pd.read_csv(caminho_csv)

# Caminho do banco SQLite de saída
caminho_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "produtos.db"))

# Conexão com SQLite
conn = sqlite3.connect(caminho_db)

# Exporta os dados para a tabela 'produtos'
df.to_sql("produtos", conn, if_exists="replace", index=False)

# Fecha a conexão
conn.close()

print(f"Dados carregados com sucesso para o banco SQLite: {caminho_db}")
