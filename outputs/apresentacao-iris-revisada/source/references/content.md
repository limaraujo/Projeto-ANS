# Análise e escrita científica

Para cada fonte, registre caminho/URL, autoria/data quando conhecidos, se foi consultada e páginas/seções relevantes. Preserve o original. Extração textual de PDF pode perder tabelas, fórmulas, colunas e figuras: compare páginas renderizadas quando esses elementos forem essenciais. `pdftoppm -f N -l N -png artigo.pdf pagina` permite inspecioná-las sem GUI.

Escreva em `plan.analysis`: tema central, conceitos indispensáveis, argumentos, resultados realmente apresentados, oportunidades visuais. Separe evidência publicada de dedução, hipótese, interpretação e exemplo didático. Se faltar informação na fonte, assinale a ausência; não preencha lacunas com números plausíveis.

Escolha uma pergunta orientadora e uma conclusão sustentada. Uma apresentação de artigo pode reorganizar introdução, fundamentos, método, resultados, validade e discussão para o público; a ordem do artigo não é obrigatória. Não faça um slide para cada parágrafo. Use títulos informativos, relações explícitas e exemplos que esclareçam condições, unidades e limitações.

Use `citations: ["id"]` nas afirmações provenientes de fontes e um layout `references` com as entradas citadas. Dados e figuras precisam de origem; exemplos sintéticos devem ser rotulados também no slide. Uma URL bem formada não é verificação bibliográfica: abra a fonte quando a rede permitir e registre o que foi consultado. Preferir artigo original, documentação oficial ou dados publicados. Não afirmar resultados experimentais próprios sem experimentos e dados reais.

Equações em Unicode são texto editável; notação complexa pode usar SVG acompanhado de expressão-fonte nas notas. Informe que SVG é editável como objeto, não como equação Office Math. Pseudocódigo deve preservar o fluxo lógico e condições de parada. Inclua explicações longas nas notas, sem retirar qualificações científicas essenciais dos slides.
