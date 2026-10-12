---
name: nova-aula
description: Cria, passo a passo e com aprovação do usuário a cada etapa, uma nova aula de slides Quarto/revealjs (.qmd) para o curso "Filosofia para o Enem" (projeto filosofia-vc). Use esta skill sempre que o usuário pedir para criar, montar, gerar ou planejar uma nova aula, um novo deck de slides, uma nova aula de filosofia, ou mencionar "/nova-aula" — mesmo que ele não diga explicitamente "crie um arquivo .qmd". Também use quando o usuário disser algo como "quero fazer uma aula sobre X" ou "vamos montar a próxima aula" no contexto deste projeto.
---

# Nova Aula

Produz um novo arquivo `slides/aulaNN_slug.qmd` (revealjs) para o curso, e
registra a aula em `dados/fil_aulas.yaml`. O público-alvo de **toda** aula
deste curso é sempre o mesmo: estudantes de um **cursinho popular
preparatório para o Enem** — escreva com esse leitor em mente (direto,
didático, sem pressupor vocabulário técnico não explicado).

Este é um processo **interativo e iterativo**: nunca gere o arquivo .qmd
final sem antes passar pelas etapas abaixo, cada uma aprovada pelo usuário.
Pular etapas (por exemplo, já entregar o `.qmd` completo depois da primeira
pergunta) é o principal jeito de errar essa skill — o valor dela está
exatamente em checar cada decisão com o usuário antes de seguir para a
próxima.

## Antes de começar: leia o modelo

`slides/aula09_etica_moderna.qmd` é o modelo de referência de estrutura e
estilo. Leia esse arquivo agora (ou o `.qmd` mais recente em `slides/`, se já
existir uma aula mais nova) — as convenções abaixo resumem o que você vai
encontrar nele, mas o arquivo real é a fonte da verdade.

**Padrões de formatação, confirmados por correções reais do usuário ao
longo do projeto — siga-os de propósito, não por acaso:**

- Sem travessões (—) no texto dos slides. O usuário já pediu explicitamente
  para removê-los do projeto inteiro; prefira ponto final ou vírgula.
- Bullets curtos e diretos: ~4 a 6 por slide de conteúdo. Slides com texto
  longo **vazam** da tela no revealjs — se um slide parece denso, é melhor
  dividi-lo em dois (ex.: "Utilitarismo" / "Utilitarismo: objeções") do que
  espremer tudo em um só.
- `**negrito**` para termos-chave; `*itálico*` para palavras estrangeiras,
  títulos de obra e nomes de conceitos em outra língua.
- Citação de autor: dentro de `::: {.no-bullets}`, como
  `- > texto da citação (AUTOR, sobrenome. *Obra*.)`. Se mesmo assim a
  citação ultrapassar o slide, envolva em `::: {style="font-size: 0.6em;"}`.
- Slide de biografia de um(a) filósofo(a) com retrato: layout de duas
  colunas, `::: columns` com `::: {.column width="70%"}` (texto, dentro de
  `::: {.smaller-list}`) e `::: {.column width="30%"}` (`::: {.no-bullets}`
  com `![Legenda da imagem](caminho)`).
- A imagem de fundo (ver Etapa 2) é declarada uma única vez, num bloco
  `<style>` logo abaixo do primeiro heading `#` da aula — ela vale para o
  deck inteiro a partir dali, não só para aquele slide.

## Etapa 1 — Número e título da aula

1. Rode `ls slides/aula*.qmd` para achar o maior número de aula já criado
   como arquivo (hoje, `aula09_etica_moderna.qmd` → próximo seria `10`).
2. Leia `dados/fil_aulas.yaml` também. Às vezes já existe uma entrada
   "planejada" ali para o próximo número (com `titulo` e `questoes`
   definidos) sem o `.qmd` correspondente ainda existir — isso é normal
   neste projeto. Se for o caso, mostre esse planejamento ao usuário e
   pergunte se quer usá-lo como ponto de partida ou prefere outro
   título/número.
3. Pergunte o título da aula, sugerindo o próximo número encontrado no
   passo 1. Deixe o usuário confirmar ou escolher outro número/título.
4. Confirme também o `id_textual` que isso gera (`aulaNN_slug`, no mesmo
   padrão dos arquivos existentes — veja a coluna `id_textual` em
   `dados/fil_aulas.yaml` para exemplos) e o caminho final:
   `slides/aulaNN_slug.qmd`.
5. Pergunte a data planejada para o início dessa aula (campo `date` do
   frontmatter, formato `AAAA-MM-DD`). Rode `grep -h '^date:' slides/aula*.qmd`
   para mostrar as datas já usadas como referência de calendário, mas não
   tente adivinhar a data sozinho — peça explicitamente, já que não há um
   intervalo fixo entre aulas neste curso.

## Etapa 2 — Imagem de fundo

1. Pergunte qual imagem usar como fundo do deck.
2. Se o caminho informado não estiver em `slides/imagens/aulaNN/`, copie o
   arquivo para lá (crie a pasta se não existir), mantendo o nome original.
   Esse é o padrão usado por todas as aulas existentes — mantém os assets de
   cada aula isolados.
3. Proponha um valor de `--bg-opacity` (0 a 1; quanto maior, mais apagada/
   transparente a imagem fica atrás do texto). Aulas anteriores usam
   valores entre 0.5 e 0.9 — como referência rápida, rode
   `grep -h 'bg-opacity' slides/aula*.qmd` para ver os valores já usados e
   proponha algo nessa faixa. Deixe claro para o usuário que essa é só uma
   estimativa inicial: a avaliação de verdade acontece depois de renderizar
   (Etapa 8), olhando a imagem de fato atrás do texto real.
4. Pergunte também a legenda/crédito da imagem (artista, obra, ano) para o
   campo `title-footer` do frontmatter — siga o padrão
   `"Artista, Nome da Obra, ano"` (ex.: `"Kyle T. Webster, O Dilema do
   Trem, 2015"`). Se o usuário não souber, deixe um placeholder e avise que
   precisa ser preenchido.

## Etapa 3 — Questões do Enem

1. Pergunte quais IDs de questão (de `dados/questoes_enem.yaml`) o usuário
   quer incluir na seção final "Questões do Enem".
2. Se o usuário não tiver IDs em mente e quiser ajuda para escolher, use as
   chaves de classificação de cada questão — `fil_filosofos`, `fil_areas`,
   `fil_temas` (os vocabulários controlados correspondentes estão em
   `dados/fil_filosofos.yaml`, `dados/fil_areas.yaml`, `dados/fil_temas.yaml`,
   cada um com comentário de cabeçalho explicando os códigos) — para
   encontrar questões relacionadas ao assunto da aula (Etapa 4). Por
   exemplo, para uma aula sobre Nietzsche, procure questões com
   `fil_filosofos: [nietzsche]` ou tema `contemporanea.nietzsche_critica_valores`.
3. Confira se cada ID existe de fato em `dados/questoes_enem.yaml`
   (`python3 -c "import yaml; ids={q['id'] for q in yaml.safe_load(open('dados/questoes_enem.yaml'))}; print([i for i in IDS if i not in ids])"`
   substituindo `IDS` pela lista escolhida — uma lista vazia impressa confirma
   que todas existem).
4. Verifique também se algum ID já é usado em outra aula (basta olhar as
   listas `questoes` em `dados/fil_aulas.yaml`). Isso **não é proibido**
   (já aconteceu antes no projeto, ex.: a questão 10 aparece em duas aulas),
   mas avise o usuário para que a repetição seja intencional.
5. Guarde a lista final **na ordem exata** que o usuário quer — essa ordem
   vira a numeração "Questão 1", "Questão 2" etc. dentro da aula, e é
   também a ordem salva em `dados/fil_aulas.yaml`.

## Etapa 4 — Assunto da aula

Pergunte, em linhas gerais, do que a aula deve tratar: quais filósofos,
quais conceitos, qual é o fio condutor. Isso, somado às questões escolhidas
na Etapa 3 (que dão pistas concretas do que o Enem cobra sobre o tema), é a
base para o esquema da próxima etapa.

## Etapa 5 — Esquema de tópicos (outline)

Proponha uma lista de slides **só com títulos/tópicos**, sem o texto ainda.
Baseie-se na estrutura típica observada no modelo:

1. Um slide de abertura "gancho" (onde entra o `<style>` da imagem de
   fundo): um dilema, uma pergunta ou um exemplo concreto que introduza a
   tensão ou o problema central da aula, do jeito que "Dilemas éticos" faz
   em `aula09_etica_moderna.qmd`.
2. Para cada bloco temático ou filósofo central: 1-2 slides de conteúdo
   (divida em dois se o assunto for denso — veja a regra de bullets na
   seção "Antes de começar") e, quando fizer sentido (há retrato disponível
   e a pessoa é central o bastante), um slide de biografia em duas colunas.
3. Se a aula contrapõe duas correntes/pensadores (como "Utilitarismo vs.
   Deontologia" em aula09), um slide de síntese comparativa perto do final,
   que retome o gancho de abertura.
4. Seção final fixa: "Questões do Enem" → "Acompanhe pelo celular" → os
   slides de questão (gerados automaticamente na Etapa 8, não precisam
   entrar no esquema individualmente).

Apresente o esquema numerado ao usuário. Ele aprova ou pede mudanças
(adicionar, remover, reordenar, dividir/juntar slides) — itere até ele
aprovar explicitamente antes de seguir.

## Etapa 6 — Ilustrações

Com o esquema aprovado, você já sabe quais slides existem — é a hora certa
de perguntar sobre imagens, antes de escrever o texto de cada slide (a
Etapa 7 já entra sabendo se vai montar um layout de duas colunas ou um
slide só de texto).

1. Para cada slide sobre um(a) filósofo(a) específico(a), pergunte se o
   usuário quer incluir o retrato dele(a) (é o padrão do curso: layout de
   duas colunas com a imagem na coluna estreita, como descrito em "Antes de
   começar"). Pergunte também, de forma mais geral, se há outros slides do
   esquema que ganhariam com alguma ilustração (um mapa, uma pintura, uma
   capa de livro etc.) — não é só para slides de biografia, mas é onde isso
   é mais comum.
2. Antes de pedir um arquivo novo ao usuário, procure se o retrato já existe
   em outra aula — é comum neste projeto reaproveitar a mesma imagem (ex.:
   o retrato de Kant usado em `aula07_epistemologia.qmd` foi reaproveitado
   em `aula09_etica_moderna.qmd`). Rode algo como
   `find slides/imagens -iname '*nome_do_filosofo*'` (tente variações do
   nome/sobrenome) e proponha reaproveitar se achar algo adequado.
3. Se não achar nada reaproveitável, peça ao usuário o caminho do arquivo.
   Copie para `slides/imagens/aulaNN/` como na Etapa 2, e peça também a
   legenda da imagem (autor do retrato/obra, quando o usuário souber) —
   siga o padrão de legendas já usado no modelo, ex.: `"Retrato de Immanuel
   Kant, atribuído a Elisabeth von Stägemann, c. 1790."`.
4. Anote, para cada slide, se ele ficará em layout de duas colunas (com
   imagem) ou de coluna única (sem imagem) — essa decisão molda como o
   texto é escrito na próxima etapa.

## Etapa 7 — Conteúdo de cada slide

Com o esquema aprovado, peça instruções sobre slides específicos (ênfase,
citações a incluir, nível de profundidade) sempre que o usuário quiser
direcionar algum em particular. Preencha o esquema inteiro com o texto real
de cada slide (bullets, citações, legendas de imagem) seguindo as convenções
da seção "Antes de começar", e apresente a proposta completa.

Mostre o conteúdo slide a slide (não precisa ser o `.qmd` bruto ainda —
pode ser a prosa/bullets de cada slide em markdown simples) para facilitar a
leitura e os ajustes. O usuário aprova ou pede mudanças — itere até aprovar.

## Etapa 8 — Gerar, renderizar e abrir

Só depois do conteúdo aprovado:

1. Escreva `slides/aulaNN_slug.qmd` com:
   - Frontmatter idêntico em formato ao do modelo (`title`, `title-footer`,
     `date` com a data da Etapa 1, `date-format: "DD/MM/YYYY"`, bloco
     `format: revealjs:` com `theme: simple`, `slide-number: true`,
     `logo: imagens/logo_vc.png`, `css: styles.css`, `incremental: true`).
   - O esquema de conteúdo aprovado nas Etapas 5-7, convertido para os
     slides reais.
   - Seção final fixa (copie literalmente a estrutura destas linhas do
     modelo, trocando só a lista de IDs):
     ````
     # Questões do Enem

     ## Acompanhe pelo celular

     ::: {style="text-align: center;"}

     ![](imagens/qr_code_bit_ly_filosofia_vc.png){width=40%}

     bit.ly/filosofia-vc

     :::

     ```{python}
     #| echo: false
     #| output: asis

     from scripts.render_questoes import render_questao
     from IPython.display import HTML

     arquivo_yaml = "../dados/questoes_enem.yaml"

     questoes = [IDS_AQUI]

     for i, questao_id in enumerate(questoes, start=1):

       print(f"## Questão {i}")
       html = render_questao(questao_id, arquivo_yaml)
       display(HTML(html))
     ```
     ````
2. Renderize: `cd slides && quarto render aulaNN_slug.qmd`. Leia a saída —
   se houver erro, corrija antes de seguir (não entregue um render quebrado
   como "pronto").
3. Abra o resultado no navegador padrão: `open slides/aulaNN_slug.html`
   (macOS). Diga ao usuário que esse é o melhor momento para reavaliar de
   verdade a transparência do fundo (`--bg-opacity`) e o encaixe do texto
   nos slides — ajustes nesse ponto são esperados e rápidos de aplicar
   (edite o valor no `<style>` e rode `quarto render` de novo).

## Etapa 9 — Registrar em `dados/fil_aulas.yaml`

1. Se já existia uma entrada planejada para esse `id` (ver Etapa 1), edite-a
   para refletir o que foi efetivamente criado (`titulo`, `id_textual`,
   `questoes` na ordem final). Caso contrário, acrescente uma nova entrada
   ao final do arquivo, no mesmo formato das existentes:
   ```yaml
   - id: NN
     id_textual: aulaNN_slug
     titulo: "Título da aula"
     questoes: [id1, id2, id3]
   ```
2. Confira que não há `id` duplicado depois da edição:
   `python3 -c "import yaml; a=yaml.safe_load(open('dados/fil_aulas.yaml')); ids=[x['id'] for x in a]; assert len(ids)==len(set(ids)); print('ok', len(a))"`.

## Etapa 10 (opcional) — `README.md`

O `README.md` da raiz lista as aulas publicadas, uma linha por aula, no
formato `- [DD/MM] [Título](/slides/aulaNN_slug.html)`. Pergunte ao usuário
se quer que essa linha seja adicionada agora (geralmente faz mais sentido
depois que a aula estiver com a data real definida, não no rascunho).
