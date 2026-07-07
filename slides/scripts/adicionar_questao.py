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

CIANO = "\033[36m"   # cor do prompt
VERDE = "\033[32m"   # cor da resposta do usuário
AMARELO = "\033[33m"
NEGRITO = "\033[1m"
RESET = "\033[0m"


class Texto(str):
    """Marca strings de texto livre, para serem sempre escritas entre aspas
    (ou como bloco literal `|`, se tiverem múltiplas linhas) no YAML gerado.
    Chaves e códigos simples (test, test_type, correct_answer etc.) usam `str`
    normal e seguem o estilo padrão (sem aspas) do PyYAML."""


def representar_texto(dumper, valor):
    estilo = "|" if "\n" in valor else '"'
    return dumper.represent_scalar("tag:yaml.org,2002:str", valor, style=estilo)


yaml.add_representer(Texto, representar_texto, Dumper=yaml.SafeDumper)


def perguntar(mensagem, obrigatorio=False, padrao=None):
    if padrao:
        mensagem = f"{mensagem}[{padrao}] "
    while True:
        valor = input(f"{CIANO}{mensagem}{RESET}{VERDE}")
        print(RESET, end="", flush=True)
        valor = valor.strip()
        if not valor and padrao:
            return padrao
        if valor or not obrigatorio:
            return valor
        print("Esse campo é obrigatório.")


def perguntar_texto(rotulo, obrigatorio=True):
    print(f"{CIANO}{rotulo} (finalize com uma linha vazia):{RESET}")
    print(VERDE, end="", flush=True)
    linhas = []
    while True:
        linha = input()
        if linha == "":
            break
        linhas.append(linha)
    print(RESET, end="", flush=True)
    texto = "\n".join(linhas).strip()
    if obrigatorio and not texto:
        print("Esse campo é obrigatório.")
        return perguntar_texto(rotulo, obrigatorio)
    return texto


def carregar_questoes():
    with open(CAMINHO_YAML, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def proximo_id(questoes):
    return max((questao["id"] for questao in questoes), default=0) + 1


def buscar_questao_existente(questoes, test, test_type, test_part, test_item):
    for questao in questoes:
        if (
            questao.get("test") == test
            and questao.get("test_type") == test_type
            and questao.get("test_part") == test_part
            and questao.get("test_item") == test_item
        ):
            return questao
    return None


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
    print(f"{CIANO}Alternativas (uma por linha, na ordem A, B, C, D, E; finalize com uma linha vazia):{RESET}")
    print(VERDE, end="", flush=True)
    linhas = []
    while True:
        linha = input()
        if linha == "":
            break
        linhas.append(linha.strip())
    print(RESET, end="", flush=True)

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

    numero = perguntar(
        "Número da aula em que a questão será inserida (ex.: 04; opcional, Enter para pular): "
    )
    if not numero:
        return None
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
    questoes_existentes = carregar_questoes()
    novo_id = proximo_id(questoes_existentes)
    print(f"\n{NEGRITO}{AMARELO}{'═' * 50}")
    print(f"📝  NOVA QUESTÃO (id={novo_id})")
    print(f"{'═' * 50}{RESET}\n")

    ultima_questao = max(questoes_existentes, key=lambda q: q["id"], default={})

    test = perguntar("Código da prova - Parâmetro `test` (ex.: enem_2025, enem_2025_2_apl). Enter para usar o da última questão adicionada: ", obrigatorio=True, padrao=ultima_questao.get("test"))
    test_type = perguntar("Cor da prova - Parâmetro `test_type` (ex.: azul, branca). Enter para usar o da última questão adicionada: ", padrao=ultima_questao.get("test_type"))
    test_part = perguntar("Tema da prova - Parâmetro `test_part` (ex.: ch, cn). Enter para usar o da última questão adicionada: ", padrao=ultima_questao.get("test_part"))
    test_item_str = perguntar("test_item (número do item na prova): ")
    test_item = int(test_item_str) if test_item_str.isdigit() else test_item_str

    questao_existente = buscar_questao_existente(questoes_existentes, test, test_type, test_part, test_item)
    if questao_existente:
        print(
            f"\nJá existe a questão id={questao_existente['id']} com "
            f"test={test}, test_type={test_type}, test_part={test_part}, test_item={test_item}."
        )
        continuar = perguntar("Adicionar mesmo assim (s/n)? ").lower()
        if continuar != "s":
            raise SystemExit("Cadastro cancelado.")

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
    if arquivo_aula:
        adicionar_id_na_aula(arquivo_aula, novo_id)
        print(f"id {novo_id} adicionado à lista `questoes` em {arquivo_aula.name}.")


if __name__ == "__main__":
    main()
