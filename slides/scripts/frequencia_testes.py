"""Lista a frequência de itens por valor da chave `test` em questoes_enem.yaml,
e quantas dessas questões já apareceram nos slides de aula (slides/aula*.qmd)."""

import ast
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

PASTA_SLIDES = Path(__file__).parent.parent
CAMINHO_YAML = PASTA_SLIDES / "questoes_enem.yaml"
PADRAO_QUESTOES = re.compile(r"^questoes\s*=\s*(\[.*?\])", re.MULTILINE | re.DOTALL)

CIANO = "\033[36m"
VERDE = "\033[32m"
AMARELO = "\033[33m"
VERMELHO = "\033[31m"
MAGENTA = "\033[35m"
NEGRITO = "\033[1m"
RESET = "\033[0m"


def nome_aula(arquivo):
    """Remove o prefixo `aula` e o sufixo `.qmd` do nome do arquivo, mantendo só a parte central."""
    return arquivo.name.removeprefix("aula").removesuffix(".qmd")


def arquivos_por_id_questao():
    """Lê os slides de aula (slides/aula*.qmd) e mapeia cada `id` de questão
    do Enem aos nomes (abreviados) das aulas em que ele aparece."""
    arquivos_por_id = defaultdict(list)
    for arquivo in sorted(PASTA_SLIDES.glob("aula*.qmd")):
        texto = arquivo.read_text(encoding="utf-8")
        match = PADRAO_QUESTOES.search(texto)
        if not match:
            continue
        for id_questao in ast.literal_eval(match.group(1)):
            arquivos_por_id[id_questao].append(nome_aula(arquivo))
    return arquivos_por_id


def main():
    with open(CAMINHO_YAML, encoding="utf-8") as f:
        questoes = yaml.safe_load(f)

    arquivos_por_id = arquivos_por_id_questao()

    ids_por_test = defaultdict(list)
    for questao in questoes:
        ids_por_test[questao["test"]].append(questao["id"])

    contagem = Counter(questao["test"] for questao in questoes)
    itens = sorted(contagem.items())

    largura_barra = max(contagem.values())

    colunas = ["test", "qtd", "barra", "em aulas", "ids em aulas", "ids fora de aulas", "aulas"]
    cores = [CIANO, VERDE, VERDE, AMARELO, AMARELO, VERMELHO, MAGENTA]

    linhas = []
    for test, quantidade in itens:
        ids_test = sorted(ids_por_test[test])
        apareceram = [i for i in ids_test if i in arquivos_por_id]
        nao_apareceram = [i for i in ids_test if i not in arquivos_por_id]
        aulas = sorted({aula for i in apareceram for aula in arquivos_por_id[i]})

        linhas.append(
            [
                test,
                str(quantidade),
                "█" * quantidade,
                f"{len(apareceram)}/{len(ids_test)}",
                str(apareceram),
                str(nao_apareceram),
                ", ".join(aulas),
            ]
        )

    larguras = [
        max(len(coluna), len("█" * largura_barra) if coluna == "barra" else 0, *(len(linha[i]) for linha in linhas))
        for i, coluna in enumerate(colunas)
    ]

    cabecalho = "  ".join(f"{coluna:<{larguras[i]}}" for i, coluna in enumerate(colunas))
    print(f"{NEGRITO}{cabecalho}{RESET}")
    for linha in linhas:
        print(
            "  ".join(
                f"{cores[i]}{valor:<{larguras[i]}}{RESET}" for i, valor in enumerate(linha)
            )
        )


if __name__ == "__main__":
    main()
