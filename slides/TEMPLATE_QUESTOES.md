# Como usar o template de questões

O arquivo `render_questoes.py` fornece uma função reutilizável para renderizar questões ENEM em slides Quarto/RevealJS.

## Uso Básico

Em qualquer arquivo `.qmd`, adicione um bloco de código Python:

```{python}
#| echo: false
#| results: asis

from render_questoes import render_questao

# Renderizar questão ID 1 do arquivo "questoes_enem.yaml"
html = render_questao(1, "questoes_enem.yaml")
print(html)
```

## Parâmetros

- `questao_id` (int): ID da questão que você quer renderizar
- `arquivo_yaml` (str): Caminho do arquivo YAML com as questões (padrão: "questoes_enem.yaml")

## Exemplos

### Exemplo 1: Questão 1
```{python}
#| echo: false
#| results: asis

from render_questoes import render_questao
print(render_questao(1))
```

### Exemplo 2: Questão 2 de outro arquivo
```{python}
#| echo: false
#| results: asis

from render_questoes import render_questao
print(render_questao(2, "questoes_enem.yaml"))
```

### Exemplo 3: Loop para múltiplas questões
```{python}
#| echo: false
#| results: asis

from render_questoes import render_questao

for questao_id in [1, 2, 3]:
    html = render_questao(questao_id)
    print(html)
```

## Estrutura do YAML

O arquivo YAML deve ter a seguinte estrutura:

```yaml
- id: 1
  test: enem_2024
  test_type: azul
  test_part: ch
  test_item: 55
  question_elements:
    - question_text: "Texto da pergunta"
      question_text_reference: "Referência bibliográfica"
  statement: "Enunciado da questão"
  answers:
    A: "Opção A"
    B: "Opção B"
    C: "Opção C"
    D: "Opção D"
    E: "Opção E"
  correct_answer: B
```

## Personalização

Se você quiser customizar o estilo HTML, edite a função `render_questao()` no arquivo `render_questoes.py`.
