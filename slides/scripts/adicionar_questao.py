"""Script interativo para adicionar uma nova questão a slides/questoes_enem.yaml
e registrar seu `id` na lista `questoes` do slide de aula escolhido."""

import ast
import re
from pathlib import Path

import yaml

PASTA_SLIDES = Path(__file__).parent.parent
CAMINHO_YAML = PASTA_SLIDES / "questoes_enem.yaml"
PADRAO_QUESTOES = re.compile(r"^questoes\s*=\s*(\[.*?\])", re.MULTILINE | re.DOTALL)

LETRAS = ["A", "B", "C", "D", "E"]


class Texto(str):
    """Marca strings de texto livre, para serem sempre escritas entre aspas
    (ou como bloco literal `|`, se tiverem múltiplas linhas) no YAML gerado.
    Chaves e códigos simples (test, test_type, correct_answer etc.) usam `str`
    normal e seguem o estilo padrão (sem aspas) do PyYAML."""


def representar_texto(dumper, valor):
    estilo = "|" if "\n" in valor else '"'
    return dumper.represent_scalar("tag:yaml.org,2002:str", valor, style=estilo)


yaml.add_representer(Texto, representar_texto, Dumper=yaml.SafeDumper)


def perguntar(mensagem, obrigatorio=False):
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("Esse campo é obrigatório.")


def perguntar_texto(rotulo, obrigatorio=True):
    print(f"{rotulo} (finalize com uma linha vazia):")
    linhas = []
    while True:
        linha = input()
        if linha == "":
            break
        linhas.append(linha)
    texto = "\n".join(linhas).strip()
    if obrigatorio and not texto:
        print("Esse campo é obrigatório.")
        return perguntar_texto(rotulo, obrigatorio)
    return texto


def proximo_id():
    with open(CAMINHO_YAML, encoding="utf-8") as f:
        questoes = yaml.safe_load(f) or []
    return max((questao["id"] for questao in questoes), default=0) + 1


def perguntar_question_elements():
    elementos = []
    while True:
        titulo = perguntar("question_text_title (opcional, Enter para pular): ")
        texto = perguntar_texto("question_text")
        referencia = perguntar_texto("question_text_reference")

        elemento = {}
        if titulo:
            elemento["question_text_title"] = Texto(titulo)
        elemento["question_text"] = Texto(texto)
        elemento["question_text_reference"] = Texto(referencia)
        elementos.append(elemento)

        outro = perguntar("Há outro texto a ser acrescentado (s/n)? ").lower()
        if outro != "s":
            return elementos


def perguntar_answers():
    print("Alternativas (uma por linha, na ordem A, B, C, D, E; finalize com uma linha vazia):")
    linhas = []
    while True:
        linha = input()
        if linha == "":
            break
        linhas.append(linha.strip())

    if len(linhas) != len(LETRAS):
        print(f"Aviso: foram informadas {len(linhas)} alternativas (esperado: {len(LETRAS)}).")

    answers = {letra: Texto(texto) for letra, texto in zip(LETRAS, linhas)}
    print("Alternativas organizadas:")
    for letra, texto in answers.items():
        print(f"  {letra}: {texto}")
    return answers


def perguntar_correct_answer(answers):
    while True:
        correct_answer = perguntar(
            f"correct_answer (letra correta, entre {', '.join(answers)}): ", obrigatorio=True
        ).upper()
        if correct_answer in answers:
            return correct_answer
        print(f"Letra inválida. Escolha entre {', '.join(answers)}.")


def nome_aula(arquivo):
    return arquivo.name.removeprefix("aula").removesuffix(".qmd")


def selecionar_aula():
    aulas = sorted(PASTA_SLIDES.glob("aula*.qmd"))
    print("Aulas disponíveis:")
    for arquivo in aulas:
        print(f"  {nome_aula(arquivo)}")

    numero = perguntar("Número da aula em que a questão será inserida (ex.: 04): ", obrigatorio=True)
    for arquivo in aulas:
        if nome_aula(arquivo)[:2] == numero:
            return arquivo
    raise SystemExit(f"Nenhuma aula encontrada com o número '{numero}'.")


def adicionar_id_na_aula(arquivo, novo_id):
    texto = arquivo.read_text(encoding="utf-8")
    match = PADRAO_QUESTOES.search(texto)
    if not match:
        raise SystemExit(f"Não foi encontrada a variável `questoes` em {arquivo.name}.")

    ids = ast.literal_eval(match.group(1))
    ids.append(novo_id)
    texto_novo = texto[: match.start(1)] + str(ids) + texto[match.end(1) :]
    arquivo.write_text(texto_novo, encoding="utf-8")


def adicionar_questao_no_yaml(novo_item):
    bloco_yaml = yaml.dump(
        [novo_item], Dumper=yaml.SafeDumper, allow_unicode=True, sort_keys=False, default_flow_style=False
    )
    texto_atual = CAMINHO_YAML.read_text(encoding="utf-8")
    CAMINHO_YAML.write_text(texto_atual.rstrip() + "\n\n" + bloco_yaml, encoding="utf-8")


def main():
    novo_id = proximo_id()
    print(f"Nova questão (id={novo_id})\n")

    test = perguntar("test (ex.: enem_2025): ", obrigatorio=True)
    test_type = perguntar("test_type (ex.: azul): ")
    test_part = perguntar("test_part (ex.: ch): ")
    test_item_str = perguntar("test_item (número do item na prova): ")
    test_item = int(test_item_str) if test_item_str.isdigit() else test_item_str

    question_elements = perguntar_question_elements()
    statement = Texto(perguntar_texto("statement"))
    answers = perguntar_answers()
    correct_answer = perguntar_correct_answer(answers)

    novo_item = {
        "id": novo_id,
        "test": test,
        "test_type": test_type,
        "test_part": test_part,
        "test_item": test_item,
        "question_elements": question_elements,
        "statement": statement,
        "answers": answers,
        "correct_answer": correct_answer,
    }
    adicionar_questao_no_yaml(novo_item)
    print(f"\nQuestão {novo_id} adicionada a {CAMINHO_YAML.name}.")

    arquivo_aula = selecionar_aula()
    adicionar_id_na_aula(arquivo_aula, novo_id)
    print(f"id {novo_id} adicionado à lista `questoes` em {arquivo_aula.name}.")


if __name__ == "__main__":
    main()
