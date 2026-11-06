"""Gera slides/questoes_enem_comentadas.qmd: um documento Quarto em formato
PDF com todas as questões de dados/questoes_enem.yaml, mostrando todos os
detalhes de cada uma — textos de apoio, enunciado, alternativas, prova e
número da questão na prova, comentário de cada alternativa e o gabarito.

O documento é organizado em uma seção por aula (na ordem de
dados/aulas.yaml), cada questão exibindo o número que recebeu no slide
daquela aula; ao final, uma seção com as questões que não foram atribuídas a
nenhuma aula (numeradas em ordem crescente a partir de 1), e um índice
indicando, para cada id, a quais aulas (e sob qual número) a questão foi
atribuída. Por fim, uma seção lista, para cada prova (em ordem cronológica),
os temas e autores cobrados com o número de questões, seguida de um panorama
dos últimos cinco anos com os temas e correntes mais e menos cobrados; depois,
uma seção com as aulas (e os autores e temas das questões de cada uma) e outra
com a taxonomia completa, indicando quantas questões recebem cada nó.

Diferente de lista01_filosofia_antiga.qmd (uma lista de exercícios sem
respostas, pensada para o aluno resolver), este documento é um banco de
referência comentado, pensado para consulta do professor.

Uso: basta rodar `python3 gerar_lista_comentada.py` (sem argumentos). O
script lê dados/questoes_enem.yaml, dados/aulas.yaml, dados/provas.yaml
e dados/fil_taxonomia.yaml e sobrescreve o arquivo de saída.
"""

from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import re

import yaml
from render_questoes import _negrito_para_latex, formatar_fonte

PASTA_SLIDES = Path(__file__).parent.parent
PASTA_DADOS = PASTA_SLIDES.parent / "dados"
CAMINHO_QUESTOES = PASTA_DADOS / "questoes_enem.yaml"
CAMINHO_AULAS = PASTA_DADOS / "aulas.yaml"
MATERIA = "fil"  # seção de dados/aulas.yaml com as aulas do curso
CAMINHO_PROVAS = PASTA_DADOS / "provas.yaml"
CAMINHO_TAXONOMIA = PASTA_DADOS / "fil_taxonomia.yaml"

# Raízes do eixo A (fil_areas); as demais raízes da taxonomia são do eixo P.
AREAS = {
    "etica", "politica", "conhecimento", "ciencia", "metafisica", "antropologia",
    "logica", "estetica", "linguagem", "cultura", "educacao", "filosofia",
}
# Quantos anos (contando o mais recente do banco) entram no panorama final.
ANOS_PANORAMA = 5


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
    include-in-header:
      text: |
        \\usepackage{{multicol}}
        \\raggedcolumns
        \\setlength{{\\columnsep}}{{0.8cm}}
        \\usepackage{{fancyhdr}}
        \\pagestyle{{fancy}}
        \\fancyhf{{}}
        \\renewcommand{{\\sectionmark}}[1]{{\\markright{{#1}}}}
        \\makeatletter
        \\let\\subsectionmark\\@gobble
        \\makeatother
        \\fancyhead[R]{{\\rightmark}}
        \\fancyfoot[C]{{\\thepage}}
        \\renewcommand{{\\headrulewidth}}{{0.4pt}}
---
"""


def carregar_questoes():
    with open(CAMINHO_QUESTOES, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def carregar_aulas():
    with open(CAMINHO_AULAS, encoding="utf-8") as f:
        return (yaml.safe_load(f) or {}).get(MATERIA) or []


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


def latex(codigo):
    """Bloco de LaTeX bruto: o pandoc o repassa intacto ao PDF e continua
    interpretando normalmente o Markdown antes e depois dele."""
    return f"```{{=latex}}\n{codigo}\n```\n"


def bloco_indivisivel(conteudo):
    """Envolve um trecho de Markdown num `minipage`, caixa que o LaTeX nunca
    parte entre colunas ou páginas. Como as marcações de abertura e
    fechamento são blocos de LaTeX bruto separados, o Markdown de dentro
    continua sendo convertido pelo pandoc. O `minipage` zera o espaçamento
    entre parágrafos, que é restaurado logo na abertura."""
    abertura = latex(
        "\\par\\noindent\\begin{minipage}{\\linewidth}\n"
        "\\setlength{\\parskip}{6pt plus 2pt minus 1pt}\\setlength{\\parindent}{0pt}"
    )
    fechamento = latex("\\end{minipage}")
    return f"{abertura}\n{conteudo}\n{fechamento}\n"


def abrir_colunas(titulo):
    """Abre o bloco de duas colunas de uma seção de questões. O título da
    seção vai no argumento opcional do `multicols`, que o escreve em largura
    total acima das colunas. Cada seção começa numa página nova: no meio de
    uma página, o primeiro bloco indivisível (cabeçalho da questão e primeiro
    texto) pode não caber no espaço que resta abaixo do título e, como não
    pode ser partido, vazaria pela margem inferior."""
    titulo = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\textit{\1}", _negrito_para_latex(titulo))
    return latex(f"\\clearpage\n\\begin{{multicols}}{{2}}[\\section{{{titulo}}}]")


def fechar_colunas():
    return latex("\\end{multicols}")


def renderizar_elemento(elemento):
    """Renderiza um item de `question_elements` (título, texto e referência)
    como uma citação em Markdown comum."""
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


def renderizar_classificacao(questao, nos):
    """Lista a classificação taxonômica da questão (eixos P, A e H), pelos
    nomes dos nós. Um código ausente da taxonomia aparece como está."""
    classificacao = questao.get("classificacao", {})

    def nomes(eixo, rotulo):
        codigos = classificacao.get(eixo, [])
        return "; ".join(rotulo(c, nos) if c in nos else c for c in codigos) or "—"

    linhas = [
        "**Classificação**\n",
        f"- *Período e autor:* {nomes('fil_periodos', lambda c, n: n[c]['nome'])}",
        f"- *Área e tema:* {nomes('fil_areas', nome_tema)}",
        f"- *Habilidade:* {nomes('fil_habilidades', lambda c, n: n[c]['nome'])}",
    ]
    return "\n".join(linhas) + "\n"


def renderizar_questao(questao, nos, numero=None):
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

    # Cada bloco indivisível fica inteiro numa só coluna: o cabeçalho da
    # questão vai junto com o primeiro texto (para não ficar sozinho no pé de
    # uma coluna); cada texto seguinte forma um bloco próprio; e o enunciado
    # vai junto com as alternativas. Os comentários podem quebrar livremente.
    elementos = questao.get("question_elements", []) or [{}]
    blocos = [bloco_indivisivel(f"## {cabecalho}\n\n" + renderizar_elemento(elementos[0]))]
    for elemento in elementos[1:]:
        blocos.append(bloco_indivisivel(renderizar_elemento(elemento)))

    correct_answer = questao.get("correct_answer")
    alternativas = []
    statement = questao.get("statement", "").strip()
    if statement:
        alternativas.append(f"**{statement}**\n")
    for letra, texto in questao.get("answers", {}).items():
        if texto:
            marca = " **(gabarito)**" if letra == correct_answer else ""
            alternativas.append(f"**{letra})** {texto.strip()}{marca}\n")
    blocos.append(bloco_indivisivel("\n".join(alternativas)))

    comments = questao.get("comments", {})
    comentarios = [f"- **{letra})** {texto.strip()}" for letra, texto in comments.items() if texto]
    if comentarios:
        blocos.append("**Comentários**\n\n" + "\n".join(comentarios) + "\n")

    blocos.append(f"**Gabarito: {correct_answer}**\n")
    blocos.append(renderizar_classificacao(questao, nos))
    blocos.append("---\n")

    return "\n".join(blocos)


def renderizar_secao_aula(aula, por_id, nos):
    blocos = [abrir_colunas(aula["titulo"])]
    for posicao, questao_id in enumerate(aula["questoes"], start=1):
        blocos.append(renderizar_questao(por_id[questao_id], nos, numero=posicao))
    blocos.append(fechar_colunas())
    return "\n".join(blocos)


def renderizar_secao_sem_aula(questoes_sem_aula, nos):
    blocos = [abrir_colunas("Questões sem aula atribuída")]
    if not questoes_sem_aula:
        blocos.append("Todas as questões do banco já foram atribuídas a alguma aula.\n")
    for posicao, questao in enumerate(questoes_sem_aula, start=1):
        blocos.append(renderizar_questao(questao, nos, numero=posicao))
    blocos.append(fechar_colunas())
    return "\n".join(blocos)


def renderizar_indice_aulas(todas_questoes, mapa_aulas):
    total = len(todas_questoes)
    associadas = sum(1 for q in todas_questoes if q["id"] in mapa_aulas)
    em_mais_de_uma_aula = sum(1 for ocorrencias in mapa_aulas.values() if len(ocorrencias) > 1)
    avulsas = total - associadas

    linhas = [
        "# Índice: questão por aula\n",
        f"- **Questões no banco**: {total}",
        f"- **Questões associadas a aulas**: {associadas}",
        f"- **Questões associadas a mais de uma aula**: {em_mais_de_uma_aula}",
        f"- **Questões avulsas (sem aula)**: {avulsas}\n",
        "| id | aula(s) |",
        "|---|---|",
    ]
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


def carregar_provas():
    with open(CAMINHO_PROVAS, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def carregar_taxonomia():
    with open(CAMINHO_TAXONOMIA, encoding="utf-8") as f:
        return yaml.safe_load(f)


def carregar_nomes_taxonomia(taxonomia):
    """Mapeia cada código dos eixos `fil_periodos`, `fil_areas` e
    `fil_habilidades` ao seu nó (com `nome` e `ordem`), percorrendo a árvore
    inteira. Os códigos dos três eixos nunca coincidem."""
    nos = {}

    def visitar(lista):
        for no in lista or []:
            nos[no["codigo"]] = no
            visitar(no.get("temas"))

    visitar(taxonomia["fil_periodos"])
    visitar(taxonomia["fil_areas"])
    visitar(taxonomia["fil_habilidades"])
    return nos


def prefixo(codigo, niveis):
    """Trunca um código da taxonomia aos `niveis` primeiros níveis
    (ex.: prefixo('moderna.kant.etica', 2) == 'moderna.kant')."""
    return ".".join(codigo.split(".")[:niveis])


def contar_codigos(questoes, eixo, niveis):
    """Conta, em quantas questões, aparece cada código do `eixo` truncado a
    `niveis` níveis. Cada questão conta no máximo uma vez por código."""
    contagem = Counter()
    for questao in questoes:
        codigos = questao.get("classificacao", {}).get(eixo, [])
        contagem.update({prefixo(codigo, niveis) for codigo in codigos})
    return contagem


def nome_tema(codigo, nos):
    """Rótulo de um subtema do eixo A, precedido pelo nome da área
    (ex.: 'Filosofia política › Justiça e igualdade')."""
    area = nos[prefixo(codigo, 1)]["nome"]
    return f"{area} › {nos[codigo]['nome']}" if "." in codigo else area


def nome_corrente(codigo, nos):
    """Rótulo de uma corrente do eixo P, precedido pelo período, sem o
    intervalo de datas que o nome do período traz entre parênteses."""
    periodo = nos[prefixo(codigo, 1)]["nome"].split(" (")[0]
    return f"{periodo} › {nos[codigo]['nome']}" if "." in codigo else periodo


def ordenar_contagem(contagem, nos):
    """Ordena por número de questões (decrescente) e, no empate, pela ordem
    da taxonomia."""
    return sorted(contagem.items(), key=lambda par: (-par[1], nos[par[0]]["ordem"]))


def tabela_contagem(contagem, nos, rotulo, cabecalho="Tema"):
    linhas = [f"| {cabecalho} | Questões |", "|" + "-" * 60 + "|:" + "-" * 6 + ":|"]
    for codigo, quantidade in ordenar_contagem(contagem, nos):
        linhas.append(f"| {rotulo(codigo, nos)} | {quantidade} |")
    return "\n".join(linhas) + "\n"


def lista_rotulos(codigos, nos, rotulo):
    return "; ".join(rotulo(codigo, nos) for codigo in sorted(codigos, key=lambda c: nos[c]["ordem"]))


def renderizar_temas_por_prova(todas_questoes, provas, nos):
    """Seção final: para cada prova, em ordem cronológica, os temas (eixo A,
    no nível de subtema) e os autores e correntes (eixo P, no nível mais
    específico) cobrados, com o número de questões; depois, um panorama dos
    últimos cinco anos com os temas mais e menos cobrados."""
    por_prova = defaultdict(list)
    for questao in todas_questoes:
        por_prova[questao["test"]].append(questao)

    provas = [prova for prova in provas if prova["test"] in por_prova]
    ordem_prova = {prova["test"]: i for i, prova in enumerate(provas)}
    provas.sort(key=lambda prova: (prova["test_year"], ordem_prova[prova["test"]]))

    blocos = [
        "# Temas cobrados por prova\n",
        "As contagens abaixo refletem apenas as questões cadastradas neste banco, "
        "e não necessariamente todas as questões de Filosofia de cada prova. Uma "
        "questão pode receber mais de um tema (ou autor), por isso a soma de uma "
        "tabela pode passar do número de questões da prova.\n",
    ]

    for prova in provas:
        questoes = por_prova[prova["test"]]
        n = len(questoes)
        blocos.append(f"## {prova['test_full_name']} --- {n} {'questão' if n == 1 else 'questões'}\n")
        blocos.append(tabela_contagem(contar_codigos(questoes, "fil_areas", 2), nos, nome_tema))

        autores = contar_codigos(questoes, "fil_periodos", 3)
        if autores:
            itens = "; ".join(
                f"{nos[codigo]['nome']} ({quantidade})" for codigo, quantidade in ordenar_contagem(autores, nos)
            )
            blocos.append(f"**Autores e correntes:** {itens}.\n")

    blocos.append(renderizar_panorama_recente(todas_questoes, provas, por_prova, nos))
    return "\n".join(blocos)


def renderizar_panorama_recente(todas_questoes, provas, por_prova, nos):
    ano_final = max(prova["test_year"] for prova in provas)
    ano_inicial = ano_final - ANOS_PANORAMA + 1
    provas_recentes = [prova for prova in provas if prova["test_year"] >= ano_inicial]
    recentes = [questao for prova in provas_recentes for questao in por_prova[prova["test"]]]
    ids_recentes = {questao["id"] for questao in recentes}
    anteriores = [questao for questao in todas_questoes if questao["id"] not in ids_recentes]

    areas = contar_codigos(recentes, "fil_areas", 1)
    temas = contar_codigos(recentes, "fil_areas", 2)
    correntes = contar_codigos(recentes, "fil_periodos", 2)

    subtemas = [codigo for codigo in nos if codigo.count(".") == 1 and prefixo(codigo, 1) in AREAS]
    todas_correntes = [codigo for codigo in nos if codigo.count(".") == 1 and prefixo(codigo, 1) not in AREAS]
    temas_anteriores = contar_codigos(anteriores, "fil_areas", 2)
    correntes_anteriores = contar_codigos(anteriores, "fil_periodos", 2)

    blocos = [
        f"## Panorama dos últimos {ANOS_PANORAMA} anos ({ano_inicial}–{ano_final})\n",
        f"{len(recentes)} questões de {len(provas_recentes)} provas "
        f"({', '.join(prova['test_full_name'] for prova in provas_recentes)}).\n",
        "### Áreas da filosofia\n",
        tabela_contagem(areas, nos, nome_tema, cabecalho="Área"),
        "### Temas mais cobrados\n",
        tabela_contagem(Counter({c: q for c, q in temas.items() if q >= 2}), nos, nome_tema),
        "### Temas menos cobrados\n",
        "**Cobrados uma única vez:** "
        + lista_rotulos([c for c, q in temas.items() if q == 1], nos, nome_tema)
        + ".\n",
    ]

    so_antes = [c for c in subtemas if c not in temas and c in temas_anteriores]
    if so_antes:
        blocos.append(
            f"**Cobrados só antes de {ano_inicial}:** " + lista_rotulos(so_antes, nos, nome_tema) + ".\n"
        )
    nunca = [c for c in subtemas if c not in temas and c not in temas_anteriores]
    if nunca:
        blocos.append("**Nunca cobrados no banco:** " + lista_rotulos(nunca, nos, nome_tema) + ".\n")

    blocos += [
        "### Períodos e correntes mais cobrados\n",
        tabela_contagem(
            Counter({c: q for c, q in correntes.items() if q >= 2}), nos, nome_corrente, cabecalho="Corrente"
        ),
        "### Períodos e correntes menos cobrados\n",
        "**Cobrados uma única vez:** "
        + lista_rotulos([c for c, q in correntes.items() if q == 1], nos, nome_corrente)
        + ".\n",
    ]

    so_antes = [c for c in todas_correntes if c not in correntes and c in correntes_anteriores]
    if so_antes:
        blocos.append(
            f"**Cobrados só antes de {ano_inicial}:** " + lista_rotulos(so_antes, nos, nome_corrente) + ".\n"
        )
    nunca = [c for c in todas_correntes if c not in correntes and c not in correntes_anteriores]
    if nunca:
        blocos.append("**Nunca cobrados no banco:** " + lista_rotulos(nunca, nos, nome_corrente) + ".\n")

    return "\n".join(blocos)


def resumo_contagem(contagem, nos, rotulo):
    """Lista em uma linha os códigos de uma contagem, com o número de
    questões entre parênteses (ex.: 'Platão: política (2); Hobbes (1)')."""
    return "; ".join(f"{rotulo(codigo, nos)} ({quantidade})" for codigo, quantidade in ordenar_contagem(contagem, nos))


def renderizar_secao_aulas(aulas, por_id, nos):
    """Seção com as aulas do curso (dados/aulas.yaml): uma tabela-resumo
    e, para cada aula, os autores e temas das questões usadas nela."""
    blocos = [
        "# Aulas\n",
        "As aulas seguem a ordem de `dados/aulas.yaml`. Os autores e temas de "
        "cada aula são os das questões usadas no slide, com o número de questões "
        "entre parênteses.\n",
        "| Aula | Título | Arquivo | Questões |",
        "|:" + "-" * 4 + ":|" + "-" * 38 + "|" + "-" * 38 + "|:" + "-" * 8 + ":|",
    ]
    for aula in aulas:
        blocos.append(
            f"| {aula['id']:02d} | {aula['titulo']} | `{aula['id_textual']}` | {len(aula['questoes'])} |"
        )
    blocos.append("")

    for aula in aulas:
        questoes = [por_id[questao_id] for questao_id in aula["questoes"]]
        autores = contar_codigos(questoes, "fil_periodos", 3)
        temas = contar_codigos(questoes, "fil_areas", 2)
        blocos += [
            f"## Aula {aula['id']:02d} --- {aula['titulo']}\n",
            f"**Questões (ids, na ordem do slide):** {', '.join(str(i) for i in aula['questoes'])}.\n",
            f"**Autores e correntes:** {resumo_contagem(autores, nos, lambda c, n: n[c]['nome'])}.\n",
            f"**Temas:** {resumo_contagem(temas, nos, nome_tema)}.\n",
        ]
    return "\n".join(blocos)


def contar_por_no(questoes, eixo):
    """Conta em quantas questões cada nó do `eixo` aparece, contando também as
    etiquetas dos seus descendentes (ex.: uma questão etiquetada com
    'moderna.kant.etica' conta para 'moderna', 'moderna.kant' e o próprio nó)."""
    contagem = Counter()
    for questao in questoes:
        codigos = questao.get("classificacao", {}).get(eixo, [])
        contagem.update({prefixo(codigo, n) for codigo in codigos for n in range(1, codigo.count(".") + 2)})
    return contagem


def renderizar_no_taxonomia(no, contagem, nivel):
    """Renderiza um nó da taxonomia (e, recursivamente, seus filhos) como item
    de lista aninhada, com código, número de questões e campos opcionais."""
    recuo = "    " * nivel
    nome = f"**{no['nome']}**" if no.get("temas") else no["nome"]
    item = f"{recuo}- {nome} `{no['codigo']}` ({contagem.get(no['codigo'], 0)})"
    if no.get("aprofundamento"):
        item += " --- *aprofundamento*"
    if no.get("conceitos"):
        item += f": *{no['conceitos']}*"
    linhas = [item]
    for filho in no.get("temas") or []:
        linhas.append(renderizar_no_taxonomia(filho, contagem, nivel + 1))
    return "\n".join(linhas)


def renderizar_secao_taxonomia(taxonomia, todas_questoes):
    """Seção com a taxonomia completa de dados/fil_taxonomia.yaml, eixo por
    eixo, mostrando em cada nó quantas questões do banco o recebem."""
    blocos = [
        "# Taxonomia de Filosofia\n",
        "Taxonomia de `dados/fil_taxonomia.yaml`, usada para classificar as "
        "questões. Ao lado de cada nó aparecem o código e, entre parênteses, "
        "quantas questões do banco recebem esse nó ou algum de seus "
        "descendentes. Nós marcados como *aprofundamento* são autores ou temas "
        "de baixa incidência no Enem.\n",
    ]

    for eixo, titulo in [
        ("fil_periodos", "Eixo P: períodos, correntes e autores"),
        ("fil_areas", "Eixo A: áreas e temas"),
    ]:
        contagem = contar_por_no(todas_questoes, eixo)
        blocos.append(f"## {titulo}\n")
        for raiz in taxonomia[eixo]:
            blocos.append(f"### {raiz['nome']} `{raiz['codigo']}` ({contagem.get(raiz['codigo'], 0)})\n")
            blocos.append("\n".join(renderizar_no_taxonomia(no, contagem, 0) for no in raiz.get("temas") or []))
            blocos.append("")

    contagem = contar_por_no(todas_questoes, "fil_habilidades")
    blocos += [
        "## Eixo H: habilidades\n",
        "| Habilidade | Código | Descrição | Questões |",
        "|" + "-" * 20 + "|" + "-" * 16 + "|" + "-" * 42 + "|:" + "-" * 8 + ":|",
    ]
    for habilidade in taxonomia["fil_habilidades"]:
        blocos.append(
            f"| {habilidade['nome']} | `{habilidade['codigo']}` | {habilidade.get('descricao', '')} "
            f"| {contagem.get(habilidade['codigo'], 0)} |"
        )
    return "\n".join(blocos) + "\n"


def gerar_documento(caminho_saida, titulo, corpo, contagem_questoes):
    caminho_saida.write_text(front_matter(titulo) + "\n" + corpo + "\n", encoding="utf-8")
    print(f"Gerado {caminho_saida.relative_to(PASTA_SLIDES.parent)} com {contagem_questoes} questões.")


def main():
    todas_questoes = carregar_questoes()
    por_id = {questao["id"]: questao for questao in todas_questoes}
    aulas = carregar_aulas()
    validar_ids(aulas, por_id)
    mapa_aulas = montar_mapa_aulas(aulas)
    taxonomia = carregar_taxonomia()
    nos = carregar_nomes_taxonomia(taxonomia)

    # Documento principal: uma seção por aula, na ordem do slide.
    secoes = [renderizar_secao_aula(aula, por_id, nos) for aula in aulas]

    ids_sem_aula = sorted(questao_id for questao_id in por_id if questao_id not in mapa_aulas)
    questoes_sem_aula = [por_id[questao_id] for questao_id in ids_sem_aula]
    secoes.append(renderizar_secao_sem_aula(questoes_sem_aula, nos))

    secoes.append(renderizar_indice_aulas(todas_questoes, mapa_aulas))

    secoes.append(renderizar_temas_por_prova(todas_questoes, carregar_provas(), nos))
    secoes.append(renderizar_secao_aulas(aulas, por_id, nos))
    secoes.append(renderizar_secao_taxonomia(taxonomia, todas_questoes))

    gerar_documento(
        PASTA_SLIDES / "questoes_enem_comentadas.qmd",
        "Questões do Enem: banco comentado",
        "\n".join(secoes),
        len(todas_questoes),
    )


if __name__ == "__main__":
    main()
