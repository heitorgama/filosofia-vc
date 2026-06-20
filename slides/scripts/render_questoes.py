import markdown
import yaml
import os


def md_filter(text):
    """
    Filtro para renderizar Makdown em HTML, aplicando o estilo definido no CSS
    O estilo deve ser informado no texto markdown com {.class-name} após o elemento, por exemplo:
    # Título da questão {: .question-title}
    """
    return markdown.markdown(text, extensions=['attr_list']) + '\n'

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
    
    # Check if file exists
    if not os.path.exists(arquivo_yaml):
        raise FileNotFoundError(f"File '{arquivo_yaml}' não encontrado.")
    
    # Load YAML file
    with open(arquivo_yaml, 'r', encoding='utf-8') as f:
        questoes = yaml.safe_load(f)
    
    # Find the question by ID
    questao = None
    for q in questoes:
        if q.get('id') == questao_id:
            questao = q
            break
    
    if questao is None:
        raise ValueError(f"Questão com ID {questao_id} não encontrada em '{arquivo_yaml}'")
    
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


if __name__ == "__main__":
    # Example usage
    try:
        resultado = render_questao(1, "questoes_enem.yaml")
        print(resultado)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
