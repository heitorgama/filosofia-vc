import pandas as pd
import yaml
import os

ARQUIVO_YAML = "questoes_enem.yaml"

# Check if file exists
if not os.path.exists(ARQUIVO_YAML):
    raise FileNotFoundError(f"File '{ARQUIVO_YAML}' não encontrado.")

# Load YAML file
with open(ARQUIVO_YAML, 'r', encoding='utf-8') as f:
    questoes = yaml.safe_load(f)

# Convert YAML to DataFrame
df = pd.DataFrame(questoes)

# Exibir as primeiras linhas do DataFrame
print(df.head())