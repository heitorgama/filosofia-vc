"""Gera slides/questoes_enem_comentadas.qmd: um documento Quarto em formato
PDF com todas as questões de questoes_enem.yaml, mostrando todos os detalhes
de cada uma — textos de apoio, enunciado, alternativas, prova e número da
questão na prova, comentário de cada alternativa e o gabarito.

O documento é organizado em uma seção por aula (na ordem de
aulas_enem.yaml), cada questão exibindo o número que recebeu no slide
daquela aula; ao final, uma seção com as questões que não foram atribuídas a
nenhuma aula (numeradas em ordem crescente a partir de 1), e um índice
indicando, para cada id, a quais aulas (e sob qual número) a questão foi
atribuída.

Diferente de lista01_filosofia_antiga.qmd (uma lista de exercícios sem
respostas, pensada para o aluno resolver), este documento é um banco de
referência comentado, pensado para consulta do professor.

Uso: basta rodar `python3 gerar_lista_comentada.py` (sem argumentos). O
script lê questoes_enem.yaml e aulas_enem.yaml e sobrescreve o arquivo de
saída.
"""

from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml
from render_questoes import formatar_fonte

PASTA_SLIDES = Path(__file__).parent.parent
CAMINHO_QUESTOES = PASTA_SLIDES / "questoes_enem.yaml"
CAMINHO_AULAS = PASTA_SLIDES / "aulas_enem.yaml"


def front_matter(titulo):
    return f"""---
title: "{titulo}"
date: "{date.today().isoformat()}"
lang: pt
number-sections: false
toc: true
format:
  pdf:
    documentclass: article
    pdf-engine: xelatex
    papersize: letter
    geometry: margin=2cm
    fontsize: 11pt
    colorlinks: false
---
"""


def carregar_questoes():
    with open(CAMINHO_QUESTOES, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def carregar_aulas():
    with open(CAMINHO_AULAS, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def validar_ids(aulas, por_id):
    for aula in aulas:
        faltando = [i for i in aula["questoes"] if i not in por_id]
        if faltando:
            raise SystemExit(
                f"Aula {aula['id']} ({aula['titulo']}) referencia id(s) inexistente(s) "
                f"em {CAMINHO_QUESTOES.name}: {faltando}"
            )


def montar_mapa_aulas(aulas):
    """Para cada id de questão, a lista de (id da aula, título da aula,
    número que a questão recebeu no slide dessa aula). Uma questão pode
    aparecer em mais de uma aula."""
    mapa = defaultdict(list)
    for aula in aulas:
        for posicao, questao_id in enumerate(aula["questoes"], start=1):
            mapa[questao_id].append((aula["id"], aula["titulo"], posicao))
    return mapa


def renderizar_elemento(elemento):
    """Renderiza um item de `question_elements` (título, texto e referência)
    como uma citação em Markdown comum (não precisa de LaTeX bruto, pois este
    documento não usa colunas nem minipages)."""
    partes = []

    titulo = elemento.get("question_text_title")
    if titulo:
        partes.append(f"**{titulo.strip()}**\n")

    texto = elemento.get("question_text", "").strip()
    if texto:
        citacao = "\n".join(f"> {linha}" for linha in texto.splitlines())
        partes.append(f"{citacao}\n")

    referencia = elemento.get("question_text_reference", "").strip()
    if referencia:
        partes.append(f"> *{referencia}*\n")

    return "\n".join(partes) + "\n"


def renderizar_questao(questao, numero=None):
    """Renderiza uma questão completa. Se `numero` for informado, é o número
    que a questão recebe no cabeçalho (ex.: o número dela no slide de uma
    aula); o id interno aparece entre parênteses para referência cruzada.
    Sem `numero`, o próprio id é usado como número no cabeçalho."""
    fonte = formatar_fonte(questao.get("test", ""))
    item = questao.get("test_item", "?")

    if numero is not None:
        cabecalho = f"Questão {numero} --- {fonte}, item {item} *(id {questao['id']})*"
    else:
        cabecalho = f"Questão {questao['id']} --- {fonte}, item {item}"

    blocos = [f"## {cabecalho}\n"]

    for elemento in questao.get("question_elements", []):
        blocos.append(renderizar_elemento(elemento))

    statement = questao.get("statement", "").strip()
    if statement:
        blocos.append(f"**{statement}**\n")

    correct_answer = questao.get("correct_answer")
    comments = questao.get("comments", {})
    for letra, texto in questao.get("answers", {}).items():
        if not texto:
            continue
        marca = " **(gabarito)**" if letra == correct_answer else ""
        blocos.append(f"**{letra})** {texto.strip()}{marca}\n")

        comentario = comments.get(letra)
        if comentario:
            blocos.append(f":   {comentario.strip()}\n")

    blocos.append(f"\n**Gabarito: {correct_answer}**\n")
    blocos.append("\n---\n")

    return "\n".join(blocos)


def renderizar_secao_aula(aula, por_id):
    blocos = [f"# {aula['titulo']}\n"]
    for posicao, questao_id in enumerate(aula["questoes"], start=1):
        blocos.append(renderizar_questao(por_id[questao_id], numero=posicao))
    return "\n".join(blocos)


def renderizar_secao_sem_aula(questoes_sem_aula):
    blocos = ["# Questões sem aula atribuída\n"]
    if not questoes_sem_aula:
        blocos.append("Todas as questões do banco já foram atribuídas a alguma aula.\n")
    for posicao, questao in enumerate(questoes_sem_aula, start=1):
        blocos.append(renderizar_questao(questao, numero=posicao))
    return "\n".join(blocos)


def renderizar_indice_aulas(todas_questoes, mapa_aulas):
    linhas = ["# Índice: questão por aula\n", "| id | aula(s) |", "|---|---|"]
    for questao in sorted(todas_questoes, key=lambda q: q["id"]):
        ocorrencias = mapa_aulas.get(questao["id"], [])
        if ocorrencias:
            valor = "; ".join(
                f"Aula {aula_id:02d} (questão {posicao})" for aula_id, _titulo, posicao in ocorrencias
            )
        else:
            valor = "—"
        linhas.append(f"| {questao['id']} | {valor} |")
    return "\n".join(linhas) + "\n"


def gerar_documento(caminho_saida, titulo, corpo, contagem_questoes):
    caminho_saida.write_text(front_matter(titulo) + "\n" + corpo + "\n", encoding="utf-8")
    print(f"Gerado {caminho_saida.relative_to(PASTA_SLIDES.parent)} com {contagem_questoes} questões.")


def main():
    todas_questoes = carregar_questoes()
    por_id = {questao["id"]: questao for questao in todas_questoes}
    aulas = carregar_aulas()
    validar_ids(aulas, por_id)
    mapa_aulas = montar_mapa_aulas(aulas)

    # Documento principal: uma seção por aula, na ordem do slide.
    secoes = [renderizar_secao_aula(aula, por_id) for aula in aulas]

    ids_sem_aula = sorted(questao_id for questao_id in por_id if questao_id not in mapa_aulas)
    questoes_sem_aula = [por_id[questao_id] for questao_id in ids_sem_aula]
    secoes.append(renderizar_secao_sem_aula(questoes_sem_aula))

    secoes.append(renderizar_indice_aulas(todas_questoes, mapa_aulas))

    gerar_documento(
        PASTA_SLIDES / "questoes_enem_comentadas.qmd",
        "Questões do Enem: banco comentado",
        "\n".join(secoes),
        len(todas_questoes),
    )


if __name__ == "__main__":
    main()
