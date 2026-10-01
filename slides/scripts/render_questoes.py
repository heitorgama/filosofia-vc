import markdown
import re
import yaml
import os


def md_filter(text):
    """
    Filtro para renderizar Makdown em HTML, aplicando o estilo definido no CSS
    O estilo deve ser informado no texto markdown com {.class-name} após o elemento, por exemplo:
    # Título da questão {: .question-title}
    """
    return markdown.markdown(text, extensions=['attr_list']) + '\n'

def carregar_questao(questao_id, arquivo_yaml="questoes_enem.yaml"):
    """
    Loads a single ENEM question from a YAML file by its ID.

    Parameters:
    -----------
    questao_id : int
        The ID of the question to load
    arquivo_yaml : str, optional
        Path to the YAML file containing questions (default: "questoes_enem.yaml")

    Returns:
    --------
    dict
        The question data

    Raises:
    -------
    FileNotFoundError: If the YAML file doesn't exist
    ValueError: If the question ID is not found in the YAML file
    """

    # Check if file exists
    if not os.path.exists(arquivo_yaml):
        raise FileNotFoundError(f"File '{arquivo_yaml}' não encontrado.")

    # Load YAML file
    with open(arquivo_yaml, 'r', encoding='utf-8') as f:
        questoes = yaml.safe_load(f)

    # Find the question by ID
    for q in questoes:
        if q.get('id') == questao_id:
            return q

    raise ValueError(f"Questão com ID {questao_id} não encontrada em '{arquivo_yaml}'")


def render_questao(questao_id, arquivo_yaml="questoes_enem.yaml"):
    """
    Renders an ENEM question as HTML from a YAML file.

    Parameters:
    -----------
    questao_id : int
        The ID of the question to render
    arquivo_yaml : str, optional
        Path to the YAML file containing questions (default: "questoes_enem.yaml")

    Returns:
    --------
    str
        HTML string containing the formatted question

    Raises:
    -------
    FileNotFoundError: If the YAML file doesn't exist
    ValueError: If the question ID is not found in the YAML file
    """

    questao = carregar_questao(questao_id, arquivo_yaml)

    # Build HTML
    html = '''
        <div class="container">
        <div class="quiz-card">
    '''
    
    # Renderizar elementos da questão (título, texto, referência)
    question_elements = questao.get("question_elements", [])
    for elemento in question_elements:
        # Renderizar título, se existir
        if elemento.get("question_text_title"):
            titulo = elemento["question_text_title"].strip() + "\n{: .question-title }"
            html += md_filter(titulo)
        
        # Render question text
        texto_questao = elemento.get("question_text", "").strip() + "\n{: .question }"
        if texto_questao:
            html += md_filter(texto_questao)
        
        # Render reference
        referencia = elemento.get("question_text_reference", "").strip() + "\n{: .reference }"
        if referencia:
            html += md_filter(referencia)
    
    # Render statement (enunciado)
    statement = questao.get("statement", "").strip() + "\n{: .statement }"
    if statement:
        html += md_filter(statement)
    
    # Render answers
    answers = questao.get("answers", {})
    if answers:
        html += '  <ul class="answers">\n'
        for answer_key, answer in answers.items():
            if answer:
                answer = f"**{answer_key}** <span style=\"display:inline-block; width:1em;\"></span>" + answer.strip() + "\n{: .answers }"
                answer = md_filter(answer)
                html += f"    <li data-key=\"{answer_key}\" class=\"answers\">{answer}</li>\n"
        html += '  </ul>\n'
    
    html += '''
        </div>
        </div>
    '''

    return html


def formatar_fonte(test):
    """Converte um código de prova (ex.: 'enem_2015_2apl') em um rótulo legível
    (ex.: 'Enem 2015 (2ª aplicação)')."""
    partes = test.split("_")
    ano = partes[1] if len(partes) > 1 else ""
    rotulo = f"Enem {ano}".strip()
    if "2apl" in partes:
        rotulo += " (2ª aplicação)"
    return rotulo


def render_questao_md(questao_id, arquivo_yaml="questoes_enem.yaml", numero=None):
    """
    Renders an ENEM question as plain Markdown, adequado para documentos PDF
    (ex.: listas de exercícios), diferente de `render_questao`, que gera HTML
    voltado para slides revealjs.

    Parameters:
    -----------
    questao_id : int
        The ID of the question to render
    arquivo_yaml : str, optional
        Path to the YAML file containing questions (default: "questoes_enem.yaml")
    numero : int, optional
        Número de exibição da questão na lista (padrão: o próprio `questao_id`)

    Returns:
    --------
    str
        Markdown string containing the formatted question
    """

    questao = carregar_questao(questao_id, arquivo_yaml)

    numero_exibido = numero if numero is not None else questao_id
    fonte = formatar_fonte(questao.get("test", ""))
    elementos = questao.get("question_elements", [])
    primeiro_elemento, *demais_elementos = elementos or [{}]

    # Número da questão, indicação da prova, primeiro texto e sua referência
    # ficam num `minipage`: por ser uma caixa indivisível para o LaTeX, nunca
    # são partidos entre colunas ou páginas. O espaço antes do título é escrito
    # à mão com `\vspace*`, porque o espaçamento automático do `\subsubsection`
    # é descartado por estar no topo da caixa do `minipage`.
    md = _iniciar_minipage()
    md += "\\vspace*{1em}\n"
    md += f"\\subsubsection*{{Questão {numero_exibido}}}\n\n"
    md += f"\\textit{{{_negrito_para_latex(fonte)}}}\n\n"
    md += _render_elemento_md(primeiro_elemento)
    md += "\\end{minipage}\n\n"

    # Textos adicionais (ex.: TEXTO II, TEXTO III) podem quebrar normalmente.
    for elemento in demais_elementos:
        md += _render_elemento_md(elemento)

    # Enunciado e alternativas também ficam num `minipage` à parte.
    md += _iniciar_minipage()

    statement = questao.get("statement", "").strip()
    if statement:
        md += f"{_negrito_para_latex(statement)}\n\n"

    for chave, resposta in questao.get("answers", {}).items():
        if resposta:
            md += f"\\textbf{{{chave})}} {_negrito_para_latex(resposta.strip())}\n\n"

    md += "\\end{minipage}\n\n"

    return md


def _iniciar_minipage():
    """Abre um bloco `minipage` (caixa indivisível do LaTeX, usada para impedir que
    um trecho seja partido entre colunas/páginas) já restaurando o espaçamento
    padrão entre parágrafos, que o LaTeX zera dentro de qualquer `minipage`."""
    return (
        "\\begin{minipage}{\\linewidth}\n"
        "\\setlength{\\parskip}{6pt plus 2pt minus 1pt}\\setlength{\\parindent}{0pt}\n"
    )


def _render_elemento_md(elemento):
    """Renderiza um item de `question_elements` (título, texto e referência) como
    LaTeX bruto, para uso dentro de blocos como `minipage` (onde o pandoc não
    interpreta mais a sintaxe Markdown)."""
    md = ""

    if elemento.get("question_text_title"):
        md += f"\\textbf{{{_negrito_para_latex(elemento['question_text_title'].strip())}}}\n\n"

    texto = elemento.get("question_text", "").strip()
    if texto:
        md += f"\\begin{{quote}}\n{_negrito_para_latex(texto)}\n\\end{{quote}}\n\n"

    referencia = elemento.get("question_text_reference", "").strip()
    if referencia:
        md += f"\\begin{{quote}}\n\\textit{{{_negrito_para_latex(referencia)}}}\n\\end{{quote}}\n\n"

    return md


def _escapar_latex(texto):
    """Escapa caracteres especiais do LaTeX, necessário para textos inseridos em
    blocos de LaTeX bruto (o pandoc deixa de fazer esse escape automaticamente
    dentro de blocos como `minipage`)."""
    texto = texto.replace("\\", r"\textbackslash{}")
    substituicoes = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for caractere, substituto in substituicoes.items():
        texto = texto.replace(caractere, substituto)
    return texto


def _negrito_para_latex(texto):
    """Escapa caracteres especiais do LaTeX e converte negrito em Markdown
    (`**texto**`) para LaTeX (`\\textbf{texto}`)."""
    texto = _escapar_latex(texto)
    return re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", texto)


if __name__ == "__main__":
    # Example usage
    try:
        resultado = render_questao(1, "questoes_enem.yaml")
        print(resultado)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
