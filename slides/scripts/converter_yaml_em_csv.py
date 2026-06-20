import yaml
import csv

# Arquivos
INPUT_YAML = "slides/questoes_enem.yaml"
OUTPUT_CSV = "slides/questoes_enem.csv"

# Ler YAML
with open(INPUT_YAML, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# Espera-se que o YAML seja uma lista de registros (lista de dicts)
# Exemplo:
# - nome: Ana
#   idade: 30
# - nome: João
#   idade: 25

if not isinstance(data, list):
    raise ValueError("O YAML precisa ser uma lista de registros (lista de dicionários).")

# Descobrir colunas automaticamente
fieldnames = set()
for item in data:
    if isinstance(item, dict):
        fieldnames.update(item.keys())

ordered_fieldnames = [
    'id',
    'test',
    'test_part',
    'test_type',
    'test_item',
    'question_elements',
    'statement',
    'answers',
    'correct_answer',
]

if set(ordered_fieldnames) == fieldnames:
    fieldnames = ordered_fieldnames
else:
    fieldnames = list(fieldnames)

# Escrever CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

print(f"CSV gerado com sucesso: {OUTPUT_CSV}")