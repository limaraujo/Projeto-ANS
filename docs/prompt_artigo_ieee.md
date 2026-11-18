# Especificação para produção do artigo — Projeto AM-NS, Equipe 08

## 1. Análise dos requisitos

Esta especificação foi construída a partir do enunciado `docs/Projeto-AMG-NS-2026-2.pdf`, do código, dos dados e dos artefatos disponíveis no repositório. O nome efetivamente encontrado difere da grafia inicialmente informada. Não foi redigido um novo artigo nesta etapa.

| Aspecto | Decisão e fundamento |
|---|---|
| Tema | Comparação de sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris. |
| Área | Aprendizado de máquina não supervisionado, análise exploratória e avaliação de agrupamentos. |
| Natureza | Artigo de disciplina com estudo computacional empírico, exploratório e comparativo. |
| Equipe | Equipe 08, identificada no README e nos metadados; sua seleção de algoritmos corresponde à página 6 do PDF. |
| Problema | Como a seleção interna por silhueta se relaciona com as espécies conhecidas da Iris, e que aspectos dessa estrutura são representados pelas quatro projeções? |
| Objetivo geral | Avaliar e interpretar os agrupamentos e as representações de baixa dimensionalidade, respeitando o protocolo do projeto e as limitações das métricas. |
| Objetivos específicos | Conferir dados e protocolo; comparar os sete métodos; selecionar execuções e números de grupos; avaliar concordância externa; interpretar quatro projeções; discutir limites e reprodutibilidade. |
| Público | Docente e estudantes da disciplina; pressupõem-se conhecimentos básicos de álgebra linear, estatística e aprendizado de máquina. |
| Profundidade | Explicar fundamentos necessários, funções objetivo, parâmetros e interpretação das evidências, sem demonstrações extensas ou revisão enciclopédica. |
| Idioma | Português brasileiro, conforme a resposta do usuário. |
| Formato | Estilo IEEE por solicitação do usuário. O enunciado permite formato livre; portanto, IEEE é uma escolha de apresentação, não uma exigência atribuível ao professor. |
| Extensão | Sem limite de páginas informado. Cobrir integralmente as duas questões, com concisão, preservando a legibilidade das figuras e tabelas. |
| Evidências | Código e dados locais, execuções persistidas, métricas, figuras e metadados. Existe auditoria registrada; ela não foi reexecutada durante a preparação deste prompt. |
| Fontes obrigatórias | Enunciado e fonte UCI da Iris. Não foi indicada lista obrigatória de autores; a literatura metodológica será selecionada e verificada pelo agente redator. |
| Uso de IA | Permitido pelo usuário. Isso não dispensa verificação das referências, autoria correta ou rastreabilidade dos resultados. |

O PDF exige decisões explicadas, comentários sobre os resultados, seis curvas de silhueta, análise hierárquica, avaliação do DBSCAN e quatro projeções. Também solicita slides para a entrega da disciplina; a produção desses slides não integra esta tarefa de elaboração de prompt nem o artigo a ser gerado por ele.

**Abordagem recomendada.** O estudo empírico aproveita a implementação e os resultados já existentes e atende diretamente às duas questões. Uma revisão narrativa pode fundamentar a análise, mas, isoladamente, não responde ao trabalho. Uma revisão sistemática exigiria outra pergunta, protocolo de busca e seleção de estudos, sem substituir os experimentos solicitados. Não há fundamento para apresentar esta atividade como descoberta de uma lacuna inédita da literatura.

**Cuidados identificados.** O artigo anterior menciona um complemento e 840 ajustes adicionais, cujos artefatos não apareceram no inventário consultado. Essas alegações dependem de confirmação. A existência de `codigo/tunagem.py` não comprova sua execução. Também há versões distintas da Iris no diretório de dados: o agente deve identificar o arquivo realmente usado, sem substituí-lo silenciosamente. A própria [página da UCI](https://archive.ics.uci.edu/dataset/53/iris) documenta diferenças em registros da base.

## 2. Estrutura recomendada

| Seção | Finalidade, conteúdo e ligação argumentativa |
|---|---|
| Título, resumo e palavras-chave | Identificar o recorte; sintetizar problema, protocolo, resultados confirmados e conclusão. Redigir o resumo depois do corpo. |
| I. Introdução | Formular problema, perguntas e objetivos; explicar o interesse didático da comparação e delimitar o alcance das conclusões. |
| II. Fundamentação e trabalhos relacionados | Explicar famílias de agrupamento, silhueta, ARI, PCA e métodos não lineares. Relacionar seus objetivos às perguntas, preparando a interpretação dos resultados. |
| III. Dados e metodologia | Descrever a versão da Iris, padronização, implementação, parâmetros, reinicializações, seleção e avaliação. Tornar verificável o caminho entre perguntas e evidências. |
| IV. Resultados de agrupamento | Apresentar tabela dos sete métodos, seis curvas Sil × k, dendrograma e análise do ruído. Responder sobre seleção interna e concordância externa. |
| V. Resultados de redução de dimensionalidade | Apresentar quatro projeções e saídas pertinentes. Relacionar o que cada método representa aos agrupamentos, sem transferir métricas entre espaços. |
| VI. Discussão e limitações | Integrar as duas questões, confrontar interpretações, discutir escolhas e restringir generalizações. |
| VII. Conclusão | Responder às perguntas com base nos resultados apresentados; registrar limites e possíveis extensões ainda não executadas. |
| Referências | Listar somente fontes reais, verificadas, citadas e pertinentes, em estilo IEEE. |
| Material suplementar, se necessário | Preservar parâmetros extensos e saídas detalhadas, com remissão explícita; manter as respostas centrais e figuras exigidas no corpo. |

A fundamentação pode ser incorporada à introdução e à metodologia se isso melhorar a concisão. Resultados e discussão têm funções distintas: os primeiros mostram as evidências; a segunda examina seu significado e alcance.

## 3. Prompt definitivo

Copie o conteúdo entre os delimitadores abaixo. O agente executor precisa ter acesso ao repositório descrito; nenhuma informação da conversa anterior é necessária.

--- INÍCIO DO PROMPT ---

### A. Papel e tarefa

Atue como pesquisador em aprendizado de máquina não supervisionado, avaliação de agrupamentos, análise exploratória e redação científica. Produza um artigo de disciplina em português brasileiro, em estilo IEEE, fundamentado no enunciado, na implementação e nos resultados de um repositório fornecido.

Trata-se do Projeto AM-NS 2026-2, Equipe 08. O tema é a comparação de sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris. O trabalho é empírico, exploratório e comparativo; sua contribuição é a análise crítica e reproduzível deste estudo delimitado. Não reivindique novidade algorítmica ou uma lacuna inédita sem evidências.

Seu produto é o artigo completo, acompanhado de um registro conciso de verificação. Não produza slides. Não altere código, dados, resultados principais ou documentos anteriores apenas para ajustar a narrativa.

### B. Contexto, fontes locais e precedência

Leia inicialmente:

- `docs/Projeto-AMG-NS-2026-2.pdf`: enunciado oficial; Questão 1 nas páginas 2–3, Questão 2 na página 4, algoritmos da Equipe 08 na página 6 e observações na página 7, considerando a capa como página 1.
- `README.md` e `docs/requisitos.md`: orientação e interpretação auxiliares, subordinadas ao PDF.
- `codigo/main.py`, `codigo/questoes.py`, `codigo/algoritmos.py`, `codigo/algoritmos.json` e `codigo/requirements.txt`: implementação, orquestração, parâmetros e dependências.
- `codigo/iris/iris.data`, `codigo/iris/bezdekIris.data` e `codigo/iris/iris.names`: dados e documentação. Identifique qual arquivo fundamentou os resultados.
- `resultados/execucoes_questao_1.json`, `resultados/execucoes_questao_2.json`, `resultados/metadados_questao_1.json` e `resultados/metadados_questao_2.json`: execuções e contexto experimental.
- `resultados/metricas_por_k.csv`, `resultados/resumo_agrupamentos.csv`, `resultados/contingencias.json`, `resultados/pca_componentes.csv`, `resultados/pca_loadings.csv`, arquivos `resultados/coordenadas_*.csv` e `resultados/figuras/`: métricas e visualizações.
- `codigo/validar_resultados.py` e `resultados/validacao.json`: implementação e registro da auditoria.

Podem existir textos anteriores em `docs/relatorio.typ`, `docs/relatorio.pdf`, `docs/artigo/artigo_ieee.typ`, `docs/artigo/artigo_ieee.pdf` e geradores associados. Use-os como material a revisar. Eles não validam seus próprios resultados nem suas referências.

Se os caminhos mudaram, localize os equivalentes e registre a correspondência. Se não houver acesso ao repositório, solicite os materiais necessários antes de afirmar resultados específicos.

Separe três planos: o PDF determina o que era exigido; o código e os registros permitem estabelecer o que foi implementado e executado; a literatura fundamenta conceitos e interpretações. Não confunda intenção no código com prova de execução. Divergências entre registros, código atual e textos anteriores devem ser investigadas, não resolvidas por preferência narrativa. Diferencie o protocolo pretendido daquele efetivamente comprovado.

### C. Problema, perguntas e objetivos

Problema central: em que medida a estrutura geométrica privilegiada pelos métodos e pela seleção por silhueta coincide com as espécies conhecidas da Iris, e como essa estrutura aparece em representações bidimensionais?

Responda:

1. Quais partições e valores de k são favorecidos pelo protocolo de seleção exigido, e qual sua concordância com as espécies pelo ARI?
2. Como as famílias de algoritmos, as distâncias e o tratamento de ruído condicionam a comparação?
3. Que características são representadas por PCA, Kernel PCA, t-SNE e UMAP, e quais interpretações seus objetivos e saídas permitem sustentar?

Objetivo geral: avaliar comparativamente e interpretar os sete agrupadores e as quatro reduções de dimensionalidade, com rastreabilidade e respeito às limitações das evidências.

Objetivos específicos: conferir a base e o pré-processamento; verificar o protocolo; selecionar execuções e k; interpretar silhueta, ARI e contingências; examinar as quatro projeções; discutir limitações e reprodutibilidade.

Não imponha hipóteses direcionais depois de observar os resultados. Não interprete o número de espécies como obrigação de obter três grupos.

### D. Escopo e protocolo obrigatório de agrupamento

Inclua os sete métodos da Equipe 08: K-Means; Fuzzy K-Means/Fuzzy C-Means; Kernel Fuzzy K-Means; K-Medoids com distância euclidiana; mistura gaussiana ajustada por EM; UPGMA com ligação média e distância Manhattan/city-block; DBSCAN.

Para os cinco métodos particionais, o protocolo exige dez ajustes para cada k em {1, 2, 3, 4, 5}: 250 ajustes. Acrescentam-se uma hierarquia UPGMA e uma execução DBSCAN: 252 ajustes principais. Cinco cortes de uma árvore não equivalem a cinco ajustes hierárquicos. Confira contagens e inicializações internas; dez chamadas com `n_init=10` não equivalem ao orçamento de dez inicializações.

Para cada método particional e cada k:

1. Selecione a execução pela própria função objetivo: minimizar inércia no K-Means, objetivo fuzzy no FCM, objetivo da variante kernel implementada no Kernel FCM e soma das distâncias aos medoides no K-Medoids; maximizar log-verossimilhança no GMM/EM.
2. Converta pertinências fuzzy em rótulos por argmax; no GMM, use argmax das probabilidades posteriores.
3. Calcule a silhueta da partição selecionada.
4. Escolha k* pela maior silhueta válida.
5. Calcule e interprete o ARI da partição escolhida em relação às espécies.

Não selecione inicializações pela silhueta em substituição à função objetivo. Não compare numericamente funções objetivo distintas como se tivessem a mesma escala. Não use ARI ou espécies para selecionar k ou hiperparâmetros do protocolo principal.

Para UPGMA, descreva a construção de uma única árvore, os cortes, o dendrograma, a seleção por silhueta e o ARI. Para DBSCAN, documente parâmetros, número de grupos, quantidade e percentual de ruído e convenções de avaliação.

A silhueta é indefinida com um único rótulo global. Registre ausência/NaN em k=1, nunca zero. Verifique também partições degeneradas nos demais k: a validade depende do número de rótulos efetivos. Diferencie esse caso da convenção da biblioteca para um grupo unitário em uma partição válida.

O repositório registra silhueta euclidiana comum, inclusive para avaliar a árvore construída com Manhattan. No DBSCAN, registra silhueta sem ruído e ARI com todos os pontos, mantendo -1. Confira essas escolhas nos registros e no código e explique que a silhueta do DBSCAN considera outro subconjunto; seu maior valor isolado não demonstra superioridade geral.

### E. Dados, parâmetros e redução de dimensionalidade

Confira dimensões, atributos, unidades, espécies, balanceamento e valores ausentes na base local. Os registros existentes indicam `codigo/iris/iris.data`, 150 observações, quatro atributos e padronização por `StandardScaler`. Não substitua esse arquivo por outra versão da Iris sem registrar a mudança e seu efeito.

Os rótulos das espécies devem ser usados apenas na avaliação externa e identificação visual, sem participação no ajuste dos agrupamentos ou projeções. Os agrupamentos principais utilizam os quatro atributos padronizados; não atribua a eles métricas de um experimento sobre projeções 2D.

Verifique sementes, limites de iteração, tolerâncias, inicialização, convergência, versões e hiperparâmetros. O código consultado registra sementes 42–51 nos métodos particionais, gamma=0,25 no Kernel FCM, expoente fuzzy m=2, covariâncias completas no GMM e DBSCAN principal com eps=0,8 e min_samples=5. Trate esses valores como pontos de conferência, não como prova automática de uma execução. Inspecione a variante Kernel FCM efetivamente implementada; não lhe atribua uma função objetivo de outra formulação encontrada na literatura.

Para a Questão 2, apresente:

- PCA: componentes, autovalores, variância explicada e acumulada, convenção de loadings, interpretação dos atributos e gráfico PC1 × PC2. O código prevê quatro componentes no ajuste e duas na visualização. Distinga coeficientes dos autovetores, loadings e correlações.
- Kernel PCA: kernel e parâmetros, centralização, autovalores disponíveis e projeção 2D. O código prevê RBF e gamma=0,25. Não interprete a normalização de apenas dois autovalores como porcentagem da variância dos quatro atributos originais.
- t-SNE: projeção 2D, perplexidade, inicialização, taxa de aprendizado, orçamento de iterações, semente e divergência KL quando registrada. O código prevê perplexidade 30, inicialização PCA, taxa automática, até 1.000 iterações e semente 42.
- UMAP: projeção 2D, número de vizinhos, min_dist, métrica, inicialização, semente e outros parâmetros relevantes registrados. O código prevê 15 vizinhos, min_dist=0,1, distância euclidiana e semente 42.

Explique o que cada representação preserva e perde. Não interprete automaticamente distâncias entre ilhas, áreas, densidades ou orientação dos eixos de t-SNE e UMAP como medidas fiéis do espaço original. Variância explicada de PCA não é acurácia; divergência KL não é erro de classificação.

Se utilizar `trustworthiness_10`, já previsto nos registros, identifique-o como diagnóstico complementar de vizinhança, com definição e configuração verificadas. Não o apresente como exigência do PDF, medida completa de qualidade ou prova de superioridade universal.

### F. Pesquisa bibliográfica e fundamentação

Construa uma fundamentação seletiva: famílias de agrupamento e suas funções objetivo; distâncias e padronização; pertinência fuzzy e posterior probabilística; avaliação interna e externa; projeção linear e não linear. Explique relações entre esses conceitos e as perguntas do estudo, evitando uma sucessão de definições desconectadas.

Priorize publicações originais, livros acadêmicos pertinentes, periódicos e anais reconhecidos. Use documentação oficial para comportamento de APIs e parâmetros da implementação. Identifique preprints como tais. Não confunda documentação de biblioteca com evidência de validade geral de um método.

Exija cobertura bibliográfica explícita para cada um dos onze métodos: K-Means, Fuzzy C-Means, Kernel Fuzzy C-Means, K-Medoids/PAM, GMM/EM, UPGMA, DBSCAN, PCA, Kernel PCA, t-SNE e UMAP. Para cada método, apresente uma explicação concisa e citada de seu princípio de funcionamento, objetivo ou critério de construção, hipóteses relevantes, principais parâmetros e limitações que ajudem a interpretar este experimento. Posicione a citação junto à explicação correspondente; uma referência apenas na lista final não atende a esse requisito.

A referência deve corresponder à variante descrita: diferencie a formulação geral de K-Medoids do procedimento PAM, o algoritmo EM do modelo de mistura gaussiana e as diferentes formulações de Kernel FCM. Quando necessário, combine uma fonte teórica com documentação ou código da versão utilizada para esclarecer particularidades da implementação. Uma mesma fonte pode fundamentar mais de um método se efetivamente os abordar; não imponha onze referências distintas nem presuma que uma fonte genérica cobre todos eles.

Organize essa cobertura em uma matriz de apoio “método → fonte teórica verificada → fonte da implementação, quando necessária → conceito sustentado → seção do artigo”. Inclua também fontes para silhueta e ARI e, se utilizado, trustworthiness. Use essa matriz na verificação, sem obrigatoriamente reproduzi-la no corpo do artigo. Evite uma exposição de manual: retenha apenas os fundamentos necessários para compreender o protocolo, as diferenças entre métodos e os resultados.

Pontos de partida, cujas informações e pertinência devem ser conferidas na execução:

- Iris, UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/53/iris
- L. van der Maaten e G. Hinton, “Visualizing Data using t-SNE”, JMLR, 2008: https://jmlr.org/papers/v9/vandermaaten08a.html
- L. McInnes, J. Healy e J. Melville, “UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction”, preprint arXiv:1802.03426; confira a versão citada: https://arxiv.org/abs/1802.03426
- Documentação oficial das versões pertinentes de scikit-learn, SciPy, fuzzy-c-means, kmedoids e umap-learn.
- Modelos e orientações IEEE: https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/

Localize e confira também literatura apropriada para os demais agrupadores, silhueta, ARI, PCA e Kernel PCA. A seleção deve cobrir os fundamentos efetivamente utilizados, sem uma quota arbitrária de referências.

Para cada fonte, registre título, autoria, ano, veículo ou repositório, identificador ou URL estável, versão quando relevante, conteúdo consultado e afirmações que ela sustenta. Confirme metadados na editora, periódico, DOI ou repositório institucional. Uma página bibliográfica confirma existência e metadados; não autoriza afirmar que todo o texto foi lido. Não baseie alegações detalhadas apenas em trechos de buscadores.

É proibido inventar autores, títulos, anos, páginas, DOI, veículos, resultados ou referências. Não complete dados bibliográficos por plausibilidade. DOI não é obrigatório quando inexistente; URL oficial estável pode ser suficiente. Use a data real de consulta, sem copiar datas de acesso de textos anteriores.

Se uma fonte não puder ser verificada, registre a limitação fora do artigo e procure alternativa verificável. Não a apresente como confirmada. Se faltar acesso ao conteúdo necessário a uma afirmação, restrinja ou retire essa afirmação. Se a lacuna for essencial à resposta, identifique o manuscrito como incompleto.

Diferencie resultados próprios, evidências da literatura e interpretações. Procure limitações e resultados divergentes pertinentes; avalie se protocolos, dados e parâmetros permitem comparação. Não invente controvérsias nem declare consenso a partir de poucos textos.

### G. Estrutura e escrita

Adote a estrutura: título; resumo; palavras-chave; I. Introdução; II. Fundamentação e trabalhos relacionados; III. Dados e metodologia; IV. Resultados de agrupamento; V. Resultados de redução de dimensionalidade; VI. Discussão e limitações; VII. Conclusão; Referências. Integre a fundamentação a outras seções se isso reduzir repetição sem perder clareza.

Em cada seção, mantenha uma finalidade definida e uma ligação explícita com as perguntas. A introdução delimita o problema; a teoria prepara a interpretação; a metodologia explica a obtenção das evidências; os resultados apresentam achados; a discussão examina seu significado e limites; a conclusão responde às perguntas.

Utilize linguagem formal, clara, precisa e natural em português brasileiro. Defina siglas na primeira ocorrência e mantenha terminologia e notação consistentes. Inclua equações apenas quando ajudarem a explicar objetivos, métricas ou seleção; defina seus símbolos. Evite generalizações, elogios vagos a algoritmos e repetições entre resumo, introdução e conclusão.

Apresente tabela dos sete agrupadores com k* ou número de grupos, silhueta, ARI e ruído pertinente; seis curvas Sil × k; um dendrograma; quatro projeções 2D; saídas relevantes das quatro técnicas. Figuras podem ser organizadas em painéis legíveis, preservando a identificação individual. Use legendas informativas, remissões no texto e precisão numérica consistente. Preserve valores completos nos artefatos e arredonde apenas na apresentação.

Discuta se a seleção interna coincide com as espécies. Uma análise adicional em k=3 pode usar os resultados já existentes, se verificados, mas deve ser identificada como interpretação posterior, sem substituir k*. Não interprete ARI como percentual de acertos. Métricas iguais não provam partições iguais: para afirmar equivalência, verifique rótulos de maneira invariável à permutação.

Restrinja conclusões ao conjunto, parâmetros e execuções analisados. Reinicializações não são amostras independentes de flores. Não invente significância estatística, intervalos de confiança, hardware, duração, convergência ou robustez não medidos. A análise descritiva da base completa não exige artificialmente uma divisão treino/teste; tampouco autoriza inferências sobre desempenho preditivo fora da amostra.

O PDF não fixa páginas e solicita equilíbrio entre concisão e cobertura. Não imponha um limite fictício. Evite despejar matrizes de coordenadas no corpo: apresente sínteses e remeta aos artefatos completos.

Use citações numéricas por ordem de primeira ocorrência e correspondência completa com as referências em estilo IEEE. Caso produza PDF, confira o modelo oficial apropriado, duas colunas e legibilidade. O projeto existente usa Typst com aparência IEEE; isso não comprova conformidade estrita com um modelo oficial. Distinga estilo de citações de conformidade de diagramação. Não invente nomes de autores, afiliações ou identificadores de publicação; use “Equipe 08” quando não houver identificação confirmada.

### H. Processo de execução

**Fase 1 — Planejamento e auditoria inicial.** Leia os materiais, extraia exigências e apresente a estrutura. Produza uma matriz “requisito → artefato → seção → situação” e identifique lacunas. A estrutura acima é a orientação inicial autorizada: avance sem pedir aprovações rotineiras. Faça perguntas apenas se uma decisão relevante não puder ser resolvida por evidências ou por esta especificação.

**Fase 2 — Pesquisa e organização das evidências.** Verifique referências e monte uma matriz “afirmação → fonte ou arquivo → localização/campo → limitação”. Confira a consistência dos registros de execução e resumos. Recalcule métricas a partir dos rótulos e dados quando necessário e viável. Se executar o validador, inspecione antes seu alcance e suas gravações. Preserve os registros anteriores e não apresente uma auditoria parcial como certificação de todo o trabalho.

**Fase 3 — Redação.** Redija o corpo a partir das evidências, depois resumo e título final. Use os textos anteriores criticamente, eliminando repetições e afirmações sem suporte. Não transfira automaticamente sua bibliografia ou conclusões.

**Fase 4 — Revisão crítica.** Confira a ligação entre perguntas, método, resultados e conclusões; a adequação das métricas; o tratamento de ruído; a fidelidade da descrição ao que foi executado; a relevância da literatura e os limites das projeções. Reduza afirmações mais fortes que suas evidências.

**Fase 5 — Verificação final.** Confira valores no texto, resumo, tabelas e figuras; contagens; parâmetros; referências cruzadas; bibliografia; atendimento ao PDF e estilo IEEE. Se houver compilação, inspecione o PDF e reporte o que efetivamente foi validado. Diferencie verificações executadas, registros preexistentes consultados e verificações não realizadas.

Não há necessidade de executar novamente todo o experimento se os artefatos forem suficientes e consistentes. Antes de comandos que sobrescrevam resultados, escolha um diretório separado ou preserve os anteriores. Novas análises devem ser claramente identificadas e não podem modificar silenciosamente o protocolo principal.

Se resultados essenciais estiverem ausentes ou inconsistentes, não preencha a lacuna com números plausíveis nem apresente o artigo como finalizado. Redija as partes sustentadas, registre precisamente a pendência e indique o que seria necessário para resolvê-la. Diferencie sempre procedimento planejado, código disponível e execução comprovada.

Atenção especial: uma versão anterior menciona `complemento_experimentos.pdf` e 840 ajustes adicionais. Só inclua essa informação se localizar e verificar os artefatos correspondentes. A existência de `codigo/tunagem.py` ou uma menção em prosa não comprova a execução.

### I. Entregáveis e critérios de aceitação

Entregue o artigo completo, suas referências e um registro curto, separado do texto acadêmico, contendo fontes locais utilizadas, verificações realizadas, divergências resolvidas e limitações pendentes. Se houver geração de arquivos, forneça o texto-fonte e o PDF quando a compilação for possível; informe honestamente se produziu apenas texto ou se a diagramação não foi validada.

Avalie o trabalho pelos seguintes critérios:

1. **Rigor científico:** toda afirmação quantitativa é rastreável; nenhuma evidência ou referência é fabricada.
2. **Qualidade das fontes:** metadados e conteúdo usado foram conferidos; os fundamentos centrais têm referências pertinentes e confiáveis.
3. **Adequação metodológica:** protocolo, seleção, distâncias, conversões crisp, métricas indefinidas e ruído são descritos corretamente; desvios são explicitados.
4. **Profundidade:** cada bloco de resultados traz interpretação e limites, indo além da descrição de números e figuras.
5. **Coerência:** todas as perguntas recebem resposta apoiada nos resultados; a conclusão não introduz dados novos.
6. **Originalidade da síntese:** a discussão integra evidências e contrapõe critérios de avaliação, sem paráfrase mecânica ou alegações injustificadas de novidade.
7. **Clareza:** termos consistentes, símbolos definidos, parágrafos articulados, figuras legíveis e ausência de redundância evitável.
8. **Conformidade acadêmica:** duas questões cobertas, citações e referências correspondentes, formato IEEE atendido no nível efetivamente produzido.

Antes de concluir, procure ativamente instruções conflitantes, lacunas, evidências circulares e frases que excedam os resultados. Corrija-as. Nenhum critério estético compensa fabricação de dados, referência inexistente ou omissão de uma falha metodológica essencial.

--- FIM DO PROMPT ---

## 4. Justificativa técnica

O prompt separa exigência, implementação e evidência para evitar que um texto anterior ou um script ainda não executado sejam tratados como comprovação. A seleção em duas etapas foi explicitada porque trocar função objetivo por silhueta altera o protocolo do projeto. Os cuidados com ruído, ARI e projeções impedem comparações e interpretações indevidas.

As cinco fases têm saídas observáveis, mas dispensam aprovações intermediárias sem necessidade. A matriz de rastreabilidade e a verificação bibliográfica transformam exigências genéricas de rigor em ações verificáveis. O tratamento de lacunas permite progredir sem fabricar resultados ou declarar um manuscrito incompleto como finalizado.

A revisão do prompt eliminou a exigência de um número arbitrário de páginas, de revisão sistemática e de novos experimentos. Também distinguiu estilo IEEE de conformidade estrita com um modelo oficial. Os pontos de partida bibliográficos foram conferidos nas páginas da [UCI](https://archive.ics.uci.edu/dataset/53/iris), do [JMLR](https://jmlr.org/papers/v9/vandermaaten08a.html), do [arXiv](https://arxiv.org/abs/1802.03426) e do [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/); a conferência de páginas bibliográficas não equivale à leitura integral dessas publicações.

## 5. Checklist de validação do artigo

- [ ] O trabalho está em português brasileiro e apresenta estilo IEEE, com o nível de conformidade informado.
- [ ] Tema, perguntas, objetivos e escopo estão explícitos e coerentes.
- [ ] As duas questões e os algoritmos da Equipe 08 foram integralmente contemplados.
- [ ] A versão da Iris e a separação entre atributos e espécies foram verificadas.
- [ ] Pré-processamento, parâmetros, sementes, versões e contagens são rastreáveis.
- [ ] Os 252 ajustes principais foram confirmados ou suas divergências foram declaradas.
- [ ] A melhor execução foi selecionada pela função objetivo antes da escolha de k por silhueta.
- [ ] As conversões fuzzy/probabilística para crisp estão corretas.
- [ ] k=1 e outras partições inválidas não receberam silhueta zero indevidamente.
- [ ] UPGMA utiliza ligação média e Manhattan; a métrica usada para avaliar a silhueta está explícita.
- [ ] O tratamento do ruído no DBSCAN e seu efeito na comparação estão descritos.
- [ ] Há tabela dos sete agrupadores, seis curvas Sil × k e dendrograma.
- [ ] PCA, Kernel PCA, t-SNE e UMAP têm projeções, parâmetros, saídas pertinentes e comentários.
- [ ] ARI, variância explicada, KL e trustworthiness foram interpretados de acordo com suas definições.
- [ ] Resultados principais e análises complementares estão identificados e sustentados por registros.
- [ ] Não foram incluídas alegações sobre os 840 ajustes adicionais sem confirmação dos artefatos.
- [ ] Valores coincidem entre arquivos, figuras, tabelas, resumo e conclusão.
- [ ] Fontes existem, foram verificadas e sustentam as afirmações associadas.
- [ ] Cada um dos onze métodos tem explicação concisa com citação teórica pertinente e compatível com a variante implementada.
- [ ] Silhueta, ARI e, quando utilizado, trustworthiness têm fundamentação bibliográfica; fontes de implementação complementam as fontes teóricas quando necessário.
- [ ] Todas as citações correspondem a referências e vice-versa.
- [ ] Discussão e conclusão respondem às perguntas sem extrapolar o estudo.
- [ ] Limitações e verificações não realizadas estão declaradas.
- [ ] O PDF, se produzido, foi inspecionado quanto a legibilidade e diagramação.
