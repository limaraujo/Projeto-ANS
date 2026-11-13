// Artigo acadêmico em estilo IEEE conference (A4), implementado em Typst.
// Compilar a partir da raiz: typst compile docs/artigo/artigo_ieee.typ docs/artigo/artigo_ieee.pdf --root docs/artigo
#set document(title: "Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa", author: "Equipe 08")
#set page(paper: "a4", margin: (top: 19mm, bottom: 43mm, x: 13mm), numbering: none)
#set text(font: "Nimbus Roman", size: 10pt, lang: "pt")
#set par(justify: true, leading: .45em, spacing: .55em, first-line-indent: 1em)
#set heading(numbering: "I.A.")
#set figure(gap: 5pt)
#show figure.caption: set text(size: 8pt)
#show figure.caption.where(kind: image): set figure.caption(separator: [. ])
#show figure.caption.where(kind: table): set figure.caption(separator: linebreak())
#show figure.where(kind: table): set figure.caption(position: top)
#show heading.where(level: 1): it => block(width: 100%, above: 1em, below: .6em)[
#set par(justify: false, first-line-indent: 0pt)
#align(center)[#text(weight: "regular", size: 10pt)[#if it.numbering != none {counter(heading).display("I."); h(.4em)}#upper(it.body)]]
]
#show heading.where(level: 2): it => block(above: .8em, below: .4em)[
#text(size: 10pt, weight: "regular", style: "italic")[#context numbering("A.", counter(heading).get().at(1)) #it.body]
]
#show figure.where(kind: image): set figure(supplement: [Fig.])
#align(center)[
#text(size: 24pt)[Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa]
#v(.7em)
#text(size: 11pt)[Equipe 08]
#linebreak()
#text(size: 10pt, style: "italic")[Centro de Informática — Universidade Federal de Pernambuco \ Recife, Brasil]
#v(.8em)
]
#columns(2, gutter: 4.22mm)[
#block[
#set par(first-line-indent: 0pt)
#text(size: 9pt, weight: "bold")[Resumo—Este artigo compara sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris padronizada. Foram realizados 250 ajustes particionais, uma hierarquia UPGMA e uma execução DBSCAN. A melhor inicialização de cada número de grupos foi selecionada pela função objetivo, e o número de grupos pela silhueta. Os seis métodos com seleção de k escolheram dois grupos, com silhueta de 0,5802 e índice de Rand ajustado (ARI) de 0,5681. O DBSCAN encontrou dois grupos e quatro pontos de ruído. Em análise complementar, a mistura gaussiana com três componentes atingiu ARI de 0,9039, evidenciando a diferença entre separação geométrica e concordância com espécies. As duas primeiras componentes da PCA retiveram 95,80% da variância. Kernel PCA, t-SNE e UMAP complementaram a análise visual; t-SNE apresentou a maior preservação local de vizinhanças na configuração avaliada. Os resultados destacam os limites da seleção interna e a necessidade de interpretar projeções em conjunto com métricas.]

#text(size: 9pt, weight: "bold", style: "italic")[Palavras-chave—agrupamento, Iris, silhueta, índice de Rand ajustado, redução de dimensionalidade.]
]
= Introdução
O objetivo é investigar quais estruturas emergem das medidas das flores quando as espécies não são utilizadas no ajuste. A análise procura responder duas perguntas: qual número de grupos é favorecido pela geometria dos dados e quanto dessa organização pode ser representado em duas dimensões? As espécies conhecidas permitem uma avaliação posterior, sem determinar os agrupamentos.

A análise não supervisionada pode revelar estruturas geométricas que não coincidem com classes conhecidas. Na base Iris, essa distinção permite comparar a seleção interna de agrupamentos com sua concordância externa com espécies botânicas. Este artigo avalia sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade, seguindo o protocolo atribuído à Equipe 08 no enunciado do projeto [1].

O objetivo é investigar quais partições são favorecidas pela silhueta, como elas se relacionam com as três espécies e quais estruturas são evidenciadas nas projeções bidimensionais. Foram realizados 252 ajustes principais: 250 ajustes particionais, uma hierarquia UPGMA e um DBSCAN. As projeções incluem PCA, Kernel PCA, t-SNE e UMAP. Os rótulos das espécies são utilizados apenas após os ajustes, para interpretação e avaliação externa.

As contribuições deste estudo são a comparação sob um protocolo comum, o registro completo das execuções e a interpretação conjunta de silhueta, índice de Rand ajustado e projeções. Padronização, sementes e hiperparâmetros são escolhas metodológicas; os requisitos experimentais decorrem exclusivamente de [1].

= Base de dados e preparação
Foi utilizado o arquivo local `codigo/iris/iris.data`, com 150 observações e quatro atributos em centímetros: comprimento e largura de sépala e comprimento e largura de pétala. Há 50 observações por espécie: Iris-setosa, Iris-versicolor e Iris-virginica. Linhas completamente vazias são ignoradas. A matriz numérica é separada dos rótulos antes dos ajustes; os rótulos servem apenas à avaliação externa e às cores e símbolos das figuras.

Cada atributo foi transformado pela subtração da média e divisão pelo desvio-padrão populacional, usando StandardScaler. Isso confere escala unitária às variáveis. Essa opção altera a geometria em relação aos dados em centímetros e influencia as conclusões. Não foi feita divisão treino/teste, pois o objetivo é a análise descritiva não supervisionada da base fornecida, e não a estimação de desempenho preditivo em novos dados.
A descrição da base e de seus atributos está disponível no repositório UCI [2]. Foi mantida a versão local fornecida na atividade; resultados de outras versões da Iris não são automaticamente intercambiáveis.

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Estatísticas dos atributos antes da padronização], [
#set text(size: 8pt)
#table(columns: 3, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Atributo*],[*Média (cm)*],[*Escala (cm)*]),
[Comp. sépala],
[5,8433],
[0,8253],
[Larg. sépala],
[3,0540],
[0,4321],
[Comp. pétala],
[3,7587],
[1,7585],
[Larg. pétala],
[1,1987],
[0,7606]
)
])

= Metodologia de agrupamento
== Desenho experimental e recursos utilizados
Trata-se de um estudo exploratório e comparativo sobre a base completa, sem estimativa de desempenho preditivo em dados novos. A unidade experimental dos métodos particionais é um ajuste para um par (k, semente). As dez inicializações avaliam dependência do otimizador; não constituem dez amostras independentes da população de flores. Não foram aplicados testes de significância entre algoritmos.

O fluxo adotado consiste em carregar e padronizar os quatro atributos, executar os métodos sem acesso às espécies, selecionar inicializações pelo objetivo, selecionar k pela silhueta e avaliar externamente pelo ARI. As projeções constituem um experimento separado, ajustado sobre os mesmos atributos padronizados. Essa separação evita atribuir às projeções as métricas obtidas no espaço de quatro dimensões.

Os meios computacionais utilizados foram Python em ambiente virtual, NumPy e pandas para manipulação dos dados, scikit-learn para estimadores e métricas, SciPy para a hierarquia, fuzzy-c-means para FCM e Kernel FCM, kmedoids para PAM e umap-learn para UMAP. Matplotlib produziu as figuras, CSV e JSON armazenaram os artefatos e Typst compôs o artigo em duas colunas. Não há registro de hardware ou tempos de execução que permita comparar custo computacional.

== Reinicializações e seleção
Os sete algoritmos exigidos para a Equipe 08 estão contemplados: K-Means, Fuzzy K-Means, misturas gaussianas via EM e DBSCAN são comuns às equipes; Kernel Fuzzy K-Means, K-Medoids euclidiano e UPGMA city-block são os métodos adicionais indicados na página 6 do enunciado [1]. A Questão 2 inclui as quatro técnicas solicitadas na página 4.

Para cada algoritmo particional e cada k, foram usadas as sementes 42 a 51, com uma inicialização por chamada. Primeiro selecionou-se a execução de melhor função objetivo dentro de cada k; somente então se calculou a silhueta da partição crisp escolhida. O melhor k foi definido pela maior silhueta válida. Em caso de empate na função objetivo, o código retém a primeira execução na ordem das sementes.

K-Means minimiza a soma de quadrados das distâncias aos centroides. Utilizou-se inicialização aleatória, uma inicialização por chamada e os demais controles registrados no código e nas bibliotecas fixadas.

Fuzzy K-Means minimiza a soma das distâncias euclidianas quadráticas ponderadas pelas pertinências elevadas ao expoente m. Foram usados m igual a 2, limite de 300 iterações e tolerância de 0,00001. O grupo crisp de cada ponto é o de maior pertinência.

Kernel Fuzzy K-Means usa kernel RBF, K(x,v) = exp(−0,25‖x−v‖²), m igual a 2 e os mesmos limites do FCM. A distância quadrática no espaço induzido é 2(1−K(x,v)). Os protótipos permanecem no espaço de entrada e são atualizados com ponderação pelo kernel; essa é a variante implementada pela biblioteca fcmeans instalada. A função objetivo registrada corresponde a essa variante, e não a uma formulação com protótipos irrestritos no espaço de características.

K-Medoids utiliza PAM e minimiza a soma das distâncias euclidianas aos medoides, que são observações reais. Para k maior que 1, a inicialização é aleatória e o limite é 300 iterações; para k igual a 1, seleciona-se diretamente a observação de menor soma de distâncias.

GMM/EM ajusta componentes com covariâncias completas. Foram usados tolerância de 0,00001, regularização de covariância de 0,000001, uma inicialização e inicialização `random_from_data`. A seleção maximiza a log-verossimilhança total calculada no modelo final, somando as log-densidades dos 150 pontos. O grupo crisp é o componente de maior probabilidade posterior. As funções objetivo dos diferentes algoritmos têm escalas e significados distintos; seus valores não são comparados entre métodos.

UPGMA constrói uma única árvore usando distância Manhattan (city-block) e ligação média não ponderada. A distância entre grupos é a média das distâncias entre todos os pares de observações dos grupos. Os cortes com 1 a 5 grupos são extraídos da árvore.

DBSCAN utiliza distância euclidiana, eps igual a 0,8 e `min_samples` igual a 5, incluindo o próprio ponto na contagem da vizinhança. Esses valores foram mantidos da configuração experimental existente e não foram otimizados com os rótulos das espécies. Representam uma configuração exploratória única; não se afirma que sejam ótimos.

== Avaliação
As definições e convenções das métricas seguem a documentação de avaliação de agrupamentos do scikit-learn [3].

Para cada ponto i, a silhueta é
$ s(i) = (b(i)-a(i))/max(a(i), b(i)) $,
em que a(i) é a distância média intragrupo e b(i) é a menor distância média a outro grupo. A avaliação utiliza distância euclidiana em todos os métodos, inclusive UPGMA, cuja construção usa Manhattan. Essa convenção facilita a comparação geométrica, mas não coincide com o critério de construção da árvore. Grupos unitários recebem a convenção de silhueta zero da biblioteca. Para uma única partição global, a silhueta é indefinida e não participa da seleção.

O ARI compara pares de observações nas partições predita e verdadeira, descontando a concordância esperada ao acaso. Vale 1 para partições idênticas, sem depender dos números atribuídos aos grupos; valores próximos de zero indicam concordância próxima à referência de acaso. O ARI não foi utilizado para escolher execuções, hiperparâmetros ou k.

No DBSCAN, a silhueta é calculada nos pontos não classificados como ruído, desde que haja ao menos dois grupos válidos. O ARI inclui todos os pontos e mantém −1 como rótulo do ruído. Assim, a silhueta do DBSCAN avalia um subconjunto diferente dos demais métodos.

= Resultados de agrupamento
== Comparação das partições selecionadas
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Resultados das partições selecionadas], [
#set text(size: 8pt)
#table(columns: 5, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Método*],[*k escolhido*],[*Silhueta*],[*ARI*],[*Ruído*]),
[K-Means],
[2],
[0,5802],
[0,5681],
[0],
[FCM],
[2],
[0,5802],
[0,5681],
[0],
[Kernel FCM],
[2],
[0,5802],
[0,5681],
[0],
[K-Medoids],
[2],
[0,5802],
[0,5681],
[0],
[GMM/EM],
[2],
[0,5802],
[0,5681],
[0],
[UPGMA],
[2],
[0,5802],
[0,5681],
[0],
[DBSCAN],
[auto.],
[0,5963],
[0,5518],
[4]
)
])

Todos os seis métodos com seleção de k escolheram dois grupos e produziram a mesma partição, salvo permutação dos identificadores: um grupo contém as 50 setosas e o outro reúne as 50 versicolors e as 50 virginicas. Isso explica a igualdade das métricas, sem implicar igualdade dos centros, pertinências ou funções objetivo.

O DBSCAN reteve 49 setosas em um grupo e 50 versicolors mais 47 virginicas no outro. O ruído contém uma setosa e três virginicas: quatro pontos, ou 2,67% da base. Sua silhueta de 0,5963 supera numericamente 0,5802, mas exclui esses quatro pontos; portanto, não demonstra superioridade global. O ARI de 0,5518 é inferior ao dos demais resultados selecionados.

== Silhuetas e comparação por k
A tabela apresenta as silhuetas após a seleção pela função objetivo. Para todos os métodos, k igual a 1 é indefinido.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Silhueta das melhores execuções por k], [
#set text(size: 8pt)
#table(columns: 5, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Método*],[*k = 2*],[*k = 3*],[*k = 4*],[*k = 5*]),
[K-Means],
[0,5802],
[0,4584],
[0,3883],
[0,3477],
[FCM],
[0,5802],
[0,4574],
[0,4006],
[0,3342],
[Kernel FCM],
[0,5802],
[0,4574],
[0,3941],
[0,3285],
[K-Medoids],
[0,5802],
[0,4497],
[0,4080],
[0,3421],
[GMM/EM],
[0,5802],
[0,3728],
[0,3455],
[0,1503],
[UPGMA],
[0,5802],
[0,4517],
[0,3991],
[0,3824]
)
])
#figure(image("figuras/ieee/silhueta_k_means.pdf", width: 100%), caption: [Silhueta após seleção da execução por função objetivo: K-Means.])
#figure(image("figuras/ieee/silhueta_fuzzy_k_means.pdf", width: 100%), caption: [Silhueta após seleção da execução por função objetivo: Fuzzy K-Means.])
#figure(image("figuras/ieee/silhueta_kernel_fuzzy_k_means.pdf", width: 100%), caption: [Silhueta após seleção da execução por função objetivo: Kernel Fuzzy K-Means.])
#figure(image("figuras/ieee/silhueta_k_medoids.pdf", width: 100%), caption: [Silhueta após seleção da execução por função objetivo: K-Medoids.])
#figure(image("figuras/ieee/silhueta_gaussian_mixture.pdf", width: 100%), caption: [Silhueta após seleção da execução por função objetivo: GMM/EM.])
#figure(image("figuras/ieee/silhueta_upgma.pdf", width: 100%), caption: [Silhueta dos cinco cortes de uma única hierarquia UPGMA.])

A silhueta cai ao subdividir o bloco formado por versicolor e virginica. Isso favorece k igual a 2, apesar das três classes biológicas. O efeito é especialmente claro no GMM: a partição de três componentes tem menor silhueta, embora corresponda muito melhor às espécies. A tabela seguinte usa k igual a 3 apenas para interpretação posterior; ela não substitui a seleção exigida no enunciado.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Avaliação complementar com três grupos], [
#set text(size: 8pt)
#table(columns: 3, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Método*],[*Silhueta em k = 3*],[*ARI em k = 3*]),
[K-Means],
[0,4584],
[0,6101],
[FCM],
[0,4574],
[0,6303],
[Kernel FCM],
[0,4574],
[0,6303],
[K-Medoids],
[0,4497],
[0,6765],
[GMM/EM],
[0,3728],
[0,9039],
[UPGMA],
[0,4517],
[0,7184]
)
])

O GMM obtém ARI de 0,9039 em k igual a 3, contra 0,5681 na solução escolhida pela silhueta. A modelagem por covariâncias completas permite grupos com formas distintas, enquanto a silhueta euclidiana favorece separação compacta. UPGMA alcança ARI de 0,7184 e K-Medoids 0,6765 em três grupos. Esses valores mostram que a avaliação interna e a recuperação das espécies respondem a perguntas diferentes. Não houve escolha retroativa pelo melhor ARI.

A tabela de contingência da execução selecionada do GMM em k igual a 3 torna essa diferença explícita. Os identificadores dos grupos são arbitrários.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Contingência da mistura gaussiana com três grupos], [
#set text(size: 8pt)
#table(columns: 4, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Espécie*],[*Grupo 0*],[*Grupo 1*],[*Grupo 2*]),
[Iris-setosa],
[50],
[0],
[0],
[Iris-versicolor],
[0],
[45],
[5],
[Iris-virginica],
[0],
[0],
[50]
)
])

As 50 setosas formam um grupo exclusivo. Outro contém 45 versicolors, e o terceiro contém as 50 virginicas e cinco versicolors. Essa correspondência é observada após o ajuste e não representa acurácia preditiva em novas amostras. Em particular, ARI igual a 0,9039 não significa que 90,39% das flores foram classificadas corretamente.

== Dependência da inicialização
Para examinar a variação entre as dez sementes, a tabela apresenta o intervalo da função objetivo em k igual a 3. Cada linha deve ser interpretada na escala do próprio algoritmo; objetivos de métodos diferentes não são diretamente comparáveis.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Faixa das funções objetivo], [
#set text(size: 8pt)
#table(columns: 3, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Método*],[*Mínimo*],[*Máximo*]),
[K-Means],
[140,9684],
[192,0372],
[FCM],
[101,2222],
[101,2222],
[Kernel FCM],
[32,7858],
[32,7858],
[K-Medoids],
[131,2703],
[132,3408],
[GMM/EM],
[-318,3884],
[-292,0196]
)
])

K-Means e GMM exibem diferenças entre as soluções encontradas. Fuzzy K-Means e Kernel Fuzzy K-Means apresentam objetivos praticamente iguais entre sementes na precisão exibida. Essa concordância numérica não prova ótimo global. No GMM, as dez execuções com três componentes registraram convergência pelo critério da biblioteca, embora tenham alcançado valores distintos de log-verossimilhança. Convergir e atingir a melhor solução possível são propriedades diferentes.

As explorações posteriores de hiperparâmetros discutidas durante o desenvolvimento não foram incorporadas ao protocolo principal. Aumentar `n_init` para 10 dentro de cada uma das dez chamadas, por exemplo, representa cem inicializações internas por configuração. Portanto, não se deve descrever esse experimento como tendo o mesmo orçamento de dez inicializações utilizado nesta entrega.

== Hierarquia e dendrograma
#figure(image("figuras/ieee/dendrograma_upgma.pdf", width: 100%), caption: [Uma única árvore UPGMA, construída com distância Manhattan e ligação média.])

O dendrograma registra a sequência de fusões; a altura corresponde à distância de ligação média na escala padronizada. O corte em dois grupos separa setosa das demais espécies. Cortes mais finos aumentam a correspondência com as espécies em alguns casos, mas reduzem a silhueta euclidiana. A árvore representa relações de proximidade, e não uma filogenia ou evidência causal.

= Redução de dimensionalidade
As quatro técnicas receberam a mesma matriz padronizada de quatro atributos, sem rótulos de espécie durante o ajuste. As cores foram adicionadas posteriormente. PCA foi ajustada com quatro componentes para apresentar o espectro completo; seu gráfico usa apenas as duas primeiras. Os outros métodos foram ajustados diretamente para duas dimensões. As 150 coordenadas de cada método foram exportadas em CSV, com identificador de observação e espécie.

== PCA
As saídas de variância explicada, componentes e valores singulares seguem as definições do estimador PCA do scikit-learn [4].

A PCA utiliza decomposição SVD completa. As componentes são combinações lineares ortogonais dos atributos padronizados. A tabela mostra os autovalores da covariância amostral, as proporções explicadas e a soma acumulada.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Espectro e variância explicada da PCA], [
#set text(size: 8pt)
#table(columns: 4, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Componente*],[*Autovalor*],[*Variância (%)*],[*Acumulada (%)*]),
[PC1],
[2,9304],
[72,7705],
[72,7705],
[PC2],
[0,9274],
[23,0305],
[95,8010],
[PC3],
[0,1483],
[3,6838],
[99,4848],
[PC4],
[0,0207],
[0,5152],
[100,0000]
)
])
As duas primeiras componentes retêm 95,80% da variância da matriz padronizada. As duas omitidas representam 4,20%; portanto, o gráfico bidimensional preserva a maior parte da variabilidade linear, mas não toda a informação.

Coeficientes das componentes (autovetores):
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Coeficientes das componentes principais], [
#set text(size: 8pt)
#table(columns: 5, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Atributo*],[*PC1*],[*PC2*],[*PC3*],[*PC4*]),
[Comp. sépala],
[0,5224],
[0,3723],
[0,7210],
[-0,2620],
[Larg. sépala],
[-0,2634],
[0,9256],
[-0,2420],
[0,1241],
[Comp. pétala],
[0,5813],
[0,0211],
[-0,1409],
[0,8012],
[Larg. pétala],
[0,5656],
[0,0654],
[-0,6338],
[-0,5235]
)
])

PC1 atribui pesos positivos ao comprimento de sépala e às duas medidas de pétala, com peso negativo para largura de sépala. PC2 é dominada pela largura de sépala (coeficiente 0,9256). O sinal de um autovetor pode ser invertido sem alterar a solução; a interpretação depende dos pesos relativos.

Adotou-se como convenção de loadings o autovetor multiplicado pela raiz do autovalor. Esses valores não são exatamente os coeficientes acima nem, sem ajuste de escala amostral, as correlações com os atributos, pois StandardScaler usa variância populacional e a PCA reporta covariância amostral.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Loadings da PCA], [
#set text(size: 8pt)
#table(columns: 5, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Atributo*],[*Loading 1*],[*Loading 2*],[*Loading 3*],[*Loading 4*]),
[Comp. sépala],
[0,8942],
[0,3585],
[0,2777],
[-0,0377],
[Larg. sépala],
[-0,4508],
[0,8913],
[-0,0932],
[0,0179],
[Comp. pétala],
[0,9950],
[0,0203],
[-0,0543],
[0,1154],
[Larg. pétala],
[0,9682],
[0,0630],
[-0,2441],
[-0,0754]
)
])
#figure(image("figuras/ieee/pca.pdf", width: 100%), caption: [Projeção linear nas duas primeiras componentes principais.])

A projeção destaca a separação de setosa e a maior proximidade entre versicolor e virginica. A interpretação dos eixos pelos atributos é uma vantagem da PCA neste conjunto pequeno. A elevada variância retida não garante separação perfeita entre as espécies, pois variância e discriminação de classes não são o mesmo objetivo.

== Kernel PCA
Foi usado kernel RBF com gamma igual a 0,25, matriz de kernel centralizada, duas componentes e decomposição espectral densa. Essa escolha corresponde a uma escala característica de distância igual a 2 nas unidades padronizadas, pois o kernel vale exp(−1) nessa distância. O valor foi fixado, sem busca orientada pelas espécies.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Autovalores da Kernel PCA], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Componente*],[*Autovalor do kernel centralizado*]),
[1],
[39,1321],
[2],
[17,7924]
)
])
#figure(image("figuras/ieee/kernel_pca.pdf", width: 100%), caption: [Duas primeiras componentes da Kernel PCA com kernel RBF.])

Os autovalores acima pertencem à matriz de kernel centralizada, não à covariância dos quatro atributos originais. Como foram retidas apenas duas componentes, não se divide sua soma para declarar uma porcentagem de variância original explicada. A transformação curva a organização dos pontos e evidencia relações não lineares, mas torna a interpretação por pesos dos atributos menos direta. A escolha de gamma altera a noção de proximidade e não foi submetida a análise de sensibilidade.

== t-SNE
Os parâmetros e as saídas de otimização são interpretados conforme a documentação de t-SNE [5].

Foram usados perplexidade 30, inicialização por PCA, distância euclidiana, semente 42, exagero inicial 12, método Barnes-Hut com ângulo 0,5 e limite de 1.000 iterações. A taxa de aprendizado automática efetiva foi 50. A perplexidade controla a escala de vizinhança, sem representar um número de grupos.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Saídas do t-SNE], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Saída*],[*Valor*]),
[Divergência KL final],
[0,1642],
[n\_iter\_ reportado],
[999],
[Taxa efetiva],
[50,0000]
)
])
#figure(image("figuras/ieee/tsne.pdf", width: 100%), caption: [Projeção t-SNE com perplexidade 30 e semente 42.])

Setosa aparece isolada à esquerda, enquanto versicolor e virginica ocupam regiões próximas e parcialmente misturadas à direita. A divergência KL final quantifica o objetivo de preservação de afinidades desse ajuste, não uma taxa de erro de classificação. O atributo `n_iter_` reporta 999; não se toma o esgotamento do orçamento como prova de ótimo global. Distâncias entre ilhas, tamanhos e áreas não devem ser interpretados como distâncias e densidades fiéis do espaço original. Os eixos não têm o significado de componentes lineares nem proporção de variância explicada.

== UMAP
O papel do número de vizinhos e da distância mínima segue a documentação oficial do UMAP [6].

Foram usados 15 vizinhos, `min_dist` igual a 0,1, spread igual a 1, duas dimensões, distância euclidiana, inicialização espectral e semente 42. A execução foi limitada a uma thread para reprodutibilidade. O número de épocas foi deixado no modo automático da biblioteca, registrado como `n_epochs` nulo nos parâmetros; não se declara aqui um contador de épocas observado.
#figure(image("figuras/ieee/umap.pdf", width: 100%), caption: [Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.])

Setosa forma uma região separada à esquerda. Versicolor e virginica aparecem à direita, com tendência de organização vertical e pontos misturados na transição. Os 15 vizinhos definem a escala da estrutura local; `min_dist` controla a compactação permitida na projeção. Distâncias entre regiões desconectadas e a orientação dos eixos não têm interpretação física direta. A presença de subestruturas visuais não demonstra novas classes biológicas.

== Comparação complementar das projeções
Como diagnóstico adicional, calculou-se trustworthiness com dez vizinhos e distância euclidiana entre a matriz padronizada e cada representação 2D. Essa medida penaliza vizinhos artificiais introduzidos pela projeção; valores mais próximos de 1 são melhores nesse critério. Ela não utiliza espécies e não mede toda a estrutura global, nem equivale a acurácia.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Preservação local das projeções], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Projeção*],[*Trustworthiness (10 vizinhos)*]),
[PCA],
[0,9782],
[KERNEL PCA],
[0,9322],
[TSNE],
[0,9888],
[UMAP],
[0,9783]
)
])

Nesta execução, t-SNE apresentou o maior valor local (0,9888), seguido de UMAP (0,9783) e PCA (0,9782), muito próximos entre si. Kernel PCA obteve 0,9322. Essa ordenação é específica dos hiperparâmetros, da semente e da vizinhança escolhida; não constitui superioridade universal. PCA oferece interpretação direta e alta retenção de variância, enquanto t-SNE e UMAP enfatizam relações locais. Não foram executados agrupamentos sobre as projeções: as métricas da Questão 1 pertencem ao espaço original padronizado.

= Discussão e limitações
Os resultados se referem ao arquivo local Iris, a uma padronização e a um conjunto fixo de hiperparâmetros. Dez reinicializações reduzem a dependência da inicialização dos agrupamentos, mas não asseguram ótimo global. Houve uma execução de cada projeção; não foram estimados intervalos de confiança ou estabilidade entre sementes. A sensibilidade de gamma, perplexidade, vizinhos e eps permanece fora desta análise.

== Experimentos complementares realizados
As análises de estabilidade, sensibilidade e escala foram executadas posteriormente e estão documentadas no complemento `complemento_experimentos.pdf`. Foram comparados 1.125 pares de inicializações e realizados 840 ajustes adicionais: 252 sobre atributos originais, 48 DBSCAN, 400 Kernel FCM e 140 projeções. Os seis métodos com escolha de k mantiveram dois grupos nas duas escalas. Os resultados principais deste artigo permanecem separados dessas análises. A estabilidade por subamostragem continua como trabalho futuro.

= Conclusão
A principal conclusão dos agrupamentos é a distinção entre estrutura geométrica e classes conhecidas. Todos os métodos com escolha de k favoreceram dois grupos, separando setosa das demais espécies. Entretanto, GMM com três componentes teve concordância muito maior com os rótulos. O resultado não justifica substituir a seleção pela silhueta: ele esclarece o alcance da métrica exigida.

As quatro projeções permitem visualizar a separação de setosa e a proximidade entre as outras espécies. PCA concentra 95,80% da variância nas duas primeiras componentes; t-SNE tem a maior preservação local pelo diagnóstico adotado. As figuras complementam os índices, sem provar que a estrutura visual corresponda a classes discretas perfeitamente recuperáveis.

= Reprodutibilidade
O código em Python separa os algoritmos (`codigo/algoritmos.py`), a execução das questões (`codigo/questoes.py`) e a interface (`codigo/main.py`). As versões utilizadas incluem NumPy 2.5.4, SciPy 1.18.1, scikit-learn 1.9.1, fuzzy-c-means 2.3.1, kmedoids 0.5.5 e umap-learn 0.5.12. As dependências completas são fixadas em `codigo/requirements.txt`.

Os artefatos incluem rótulos por execução, objetivos, parâmetros, sementes, pertinências e probabilidades posteriores. As métricas por k, contingências, coordenadas das projeções, componentes e loadings foram exportados em CSV ou JSON. A auditoria verificou as 252 execuções principais, a seleção por objetivo, silhuetas e ARI recalculados, normalização e conversão crisp, além da finitude das quatro projeções. O hash dos dados e as versões foram registrados para rastreabilidade. A auditoria verifica consistência dos resultados, sem garantir otimalidade global.

#heading(numbering: none)[Referências]
#block[
#set par(first-line-indent: 0pt, hanging-indent: 1.2em)
[1] F. de A. T. de Carvalho, “Projeto AM-NS 2026-2,” Centro de Informática, Universidade Federal de Pernambuco, Recife, Brasil, enunciado de projeto, 2026, pp. 2–7. Arquivo fornecido: `Projeto-AMG-NS-2026-2.pdf`.
]

#block[
#set par(first-line-indent: 0pt, hanging-indent: 1.2em)
[2] R. A. Fisher, “Iris,” UCI Machine Learning Repository, 1936. doi: 10.24432/C56C76. #link("https://archive.ics.uci.edu/dataset/53/iris")[Disponível online].

[3] Scikit-learn developers, “Clustering: clustering performance evaluation.” #link("https://scikit-learn.org/stable/modules/clustering.html")[Documentação online]. Acesso: 13 nov. 2026.

[4] Scikit-learn developers, “PCA.” #link("https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html")[Documentação online]. Acesso: 13 nov. 2026.

[5] Scikit-learn developers, “TSNE.” #link("https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html")[Documentação online]. Acesso: 13 nov. 2026.

[6] UMAP developers, “Basic UMAP Parameters.” #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Documentação online]. Acesso: 13 nov. 2026.
]

]
