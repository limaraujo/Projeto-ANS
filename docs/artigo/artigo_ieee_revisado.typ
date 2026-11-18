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

Cada atributo foi padronizado em z-score, subtraindo-se a média e dividindo-se pelo desvio-padrão populacional, conforme o StandardScaler. Não foi feita divisão treino/teste, pois o objetivo é a análise descritiva não supervisionada da base fornecida, e não a estimação de desempenho preditivo em novos dados.
A descrição da base e de seus atributos está disponível no repositório UCI [2].

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


= Fundamentação dos métodos
Os métodos de agrupamento adotam diferentes critérios para definir uma partição. O K-Means minimiza a soma dos quadrados das distâncias euclidianas entre as observações e os centroides dos respectivos grupos. O algoritmo alterna a atribuição ao centro mais próximo e o recálculo dos centroides, favorecendo grupos compactos. A dependência da inicialização pode levar a diferentes mínimos locais [3].

O Fuzzy C-Means (FCM) representa cada observação por graus de pertinência aos grupos, normalizados. Sua função objetivo pondera as distâncias quadráticas aos centroides pelas pertinências elevadas ao expoente m, que controla o grau de difusividade da partição. Neste estudo, a partição exclusiva é obtida pelo maior grau de pertinência, permitindo o cálculo da silhueta e do ARI [4].

O Kernel FCM utiliza uma distância induzida por kernel para representar relações não lineares. As variantes discutidas por Graves e Pedrycz diferem na representação dos protótipos e na formulação do objetivo [5]. Na implementação adotada, os protótipos permanecem no espaço de entrada, e o kernel RBF determina sua proximidade às observações. O parâmetro gamma controla a escala dessa relação e, portanto, influencia o ajuste.

No K-Medoids, cada grupo é representado por uma observação da própria base, chamada medoide. Neste estudo, o algoritmo busca minimizar a soma das distâncias euclidianas entre as observações e os medoides aos quais estão associadas. Para isso, o procedimento PAM avalia trocas dos medoides por outras observações e mantém aquelas que reduzem o custo [6].

A mistura gaussiana modela a distribuição dos dados por componentes definidos por médias, covariâncias e pesos. O algoritmo de expectativa-maximização (EM) alterna a estimação das probabilidades posteriores de associação e a atualização dos parâmetros, buscando maximizar a verossimilhança [7]. As covariâncias completas permitem representar componentes elípticos com diferentes orientações. A inicialização e o condicionamento das matrizes de covariância afetam a estimação.

Neste estudo, o UPGMA constrói uma hierarquia aglomerativa, unindo a cada etapa os grupos com a menor média das distâncias Manhattan entre seus pares de observações [8]. O DBSCAN identifica agrupamentos por conectividade de regiões densas e classifica como ruído as observações que não pertencem a esses agrupamentos. O parâmetro eps define o raio da vizinhança, enquanto min_samples estabelece a quantidade mínima de observações nessa vizinhança para caracterizar um ponto central [9].

A avaliação combina critérios internos e externos. A silhueta compara a distância média de uma observação ao próprio grupo com a menor distância média a outro grupo, relacionando coesão e separação [10]. O índice de Rand ajustado (ARI) mede a concordância entre a partição estimada e uma partição de referência a partir de pares de observações, com correção para a concordância esperada ao acaso [11]. Neste estudo, as espécies definem a referência externa. Uma partição favorecida pela silhueta pode apresentar concordância limitada com essa referência.

As técnicas de redução de dimensionalidade representam diferentes aspectos da estrutura dos dados. A PCA identifica direções ortogonais que maximizam sucessivamente a variância projetada, formando componentes lineares dos atributos [12]. A Kernel PCA realiza uma decomposição espectral da matriz de kernel centralizada, estendendo a análise a relações não lineares dependentes do kernel escolhido [13].

O t-SNE ajusta uma representação de baixa dimensão pela minimização da divergência KL entre as distribuições de afinidade no espaço original e no espaço projetado. A perplexidade controla a escala de vizinhança considerada, e a inicialização influencia a otimização [14]. O UMAP constrói uma representação das relações de vizinhança e otimiza sua disposição em baixa dimensão. O número de vizinhos controla a escala local, enquanto min_dist influencia a compactação da representação [15]. A interpretação dessas projeções deve considerar possíveis distorções de distâncias globais e densidades.

= Metodologia de agrupamento
== Desenho experimental e recursos utilizados
O estudo compara os métodos na base completa, com os quatro atributos padronizados em z-score. Os rótulos das espécies foram utilizados na avaliação externa e na identificação visual dos resultados. Para os cinco métodos particionais — K-Means, FCM, Kernel FCM, K-Medoids e GMM/EM —, foram avaliados os valores de k em {1, 2, 3, 4, 5}.

Para cada método e cada valor de k, foram realizadas dez execuções, uma para cada semente inteira entre 42 e 51, inclusive. Cada combinação de método, k e semente correspondeu a um único ajuste, totalizando 50 ajustes por método e 250 ajustes particionais. No K-Means e no GMM, utilizou-se `n_init=1` em cada chamada. No K-Medoids com k igual a 1, as dez chamadas utilizaram a mesma busca exaustiva pelo medoide, cujo resultado independe da semente. As repetições permitem examinar a influência da inicialização na mesma base; não representam novas amostras dos dados.

O UPGMA foi executado uma vez, e os cinco cortes, de um a cinco grupos, foram extraídos da mesma hierarquia. O DBSCAN também teve uma única execução, completando os 252 ajustes principais. Para cada k dos métodos particionais, selecionou-se a execução com o melhor valor da função objetivo. Em seguida, a maior silhueta válida definiu o número de grupos, e o ARI mediu a concordância da partição selecionada com as espécies. As quatro técnicas de redução de dimensionalidade foram ajustadas separadamente sobre os mesmos atributos padronizados, uma vez cada. No t-SNE e no UMAP, utilizou-se a semente 42. As métricas de agrupamento foram calculadas no espaço de quatro atributos.

Os experimentos foram executados em Python 3.14.4, em ambiente virtual. A preparação dos dados utilizou NumPy 2.5.4 e pandas 3.0.6. O scikit-learn 1.9.1 forneceu K-Means, GMM, DBSCAN, PCA, Kernel PCA, t-SNE e as métricas de avaliação, enquanto o SciPy 1.18.1 foi utilizado na construção da hierarquia UPGMA. Os métodos FCM e Kernel FCM foram executados com fuzzy-c-means 2.3.1, o PAM com kmedoids 0.5.5 e o UMAP com umap-learn 0.5.12, em ambiente com Numba 0.68.0.

== Parâmetros e seleção das execuções
A @parametros-agrupamento reúne as configurações utilizadas e os critérios de seleção das execuções dos sete agrupadores indicados para a Equipe 08 no enunciado [1].

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Configurações dos agrupadores e critérios de seleção por k], [
#set text(size: 8pt)
#set par(justify: false, first-line-indent: 0pt)
#table(
  columns: (20%, 49%, 31%),
  inset: (x: 3pt, y: 4pt),
  stroke: .3pt,
  table.header([*Método*], [*Configuração*], [*Critério de seleção*]),
  [K-Means],
  [Distância euclidiana; inicialização aleatória; `n_init=1`.],
  [Menor soma das distâncias quadráticas aos centroides.],
  [FCM],
  [Distância euclidiana quadrática; m = 2; até 300 iterações; tolerância de 0,00001.],
  [Menor objetivo fuzzy.],
  [Kernel FCM],
  [Kernel RBF; gamma = 0,25; m = 2; até 300 iterações; tolerância de 0,00001.],
  [Menor objetivo fuzzy com distância induzida pelo kernel.],
  [K-Medoids],
  [PAM; distância euclidiana; inicialização aleatória; até 300 iterações para k > 1. Busca exaustiva para k = 1.],
  [Menor soma das distâncias aos medoides.],
  [GMM/EM],
  [Covariâncias completas; inicialização `random_from_data`; `n_init=1`; tolerância de 0,00001; regularização de 0,000001.],
  [Maior log-verossimilhança total no modelo final.],
  [UPGMA],
  [Distância Manhattan; ligação média; uma hierarquia e cortes de 1 a 5 grupos.],
  [Sem reinicializações; corte escolhido pela silhueta.],
  [DBSCAN],
  [Distância euclidiana; eps = 0,8; `min_samples=5`; uma execução.],
  [Sem seleção entre execuções.],
)
]) <parametros-agrupamento>

A melhor execução de cada k foi selecionada pela função objetivo antes do cálculo da silhueta. Em caso de empate, o código retém a primeira execução na ordem das sementes. Nos métodos fuzzy, os rótulos exclusivos são obtidos pela maior pertinência; no GMM, pela maior probabilidade posterior. As funções objetivo têm escalas e significados próprios e são comparadas apenas entre execuções do mesmo método e do mesmo k.

No Kernel FCM, utiliza-se K(x,v) = exp(−0,25‖x−v‖²), com distância quadrática induzida igual a 2(1−K(x,v)). Os protótipos permanecem no espaço de entrada e são atualizados com ponderação pelo kernel, conforme a variante implementada pela biblioteca fcmeans. O objetivo registrado corresponde a essa formulação.

No DBSCAN, `min_samples` inclui o próprio ponto na contagem da vizinhança. Os parâmetros foram mantidos da configuração experimental existente, sem otimização orientada pelos rótulos das espécies.

== Avaliação
Os agrupamentos foram avaliados pela silhueta, que considera a coesão e a separação dos grupos, e pelo índice de Rand ajustado (ARI), que mede a concordância com as espécies conhecidas. O cálculo das métricas seguiu as convenções do scikit-learn [17].

Para cada observação i, a silhueta é definida por
$ s(i) = (b(i)-a(i))/max(a(i), b(i)) $,
em que a(i) é a distância média às demais observações do próprio grupo e b(i) é a menor distância média às observações de outro grupo. Valores próximos de 1 indicam maior separação em relação aos demais grupos; valores próximos de zero sugerem proximidade entre grupos, e valores negativos indicam que a observação está, em média, mais próxima de outro grupo. A silhueta da partição corresponde à média desses valores e foi utilizada para selecionar k após a escolha da melhor execução pela função objetivo [10].

Utilizou-se distância euclidiana no cálculo da silhueta de todos os métodos. No UPGMA, portanto, a avaliação considera uma métrica diferente da distância Manhattan empregada na construção da hierarquia. A silhueta é indefinida quando há apenas um grupo, como em k = 1, ou quando cada observação constitui um grupo. Essas partições foram excluídas da seleção. Em partições válidas, a biblioteca atribui silhueta zero às observações que formam grupos unitários.

O ARI compara pares de observações para verificar a concordância entre a partição estimada e a partição de referência, definida pelas espécies, descontando a concordância esperada ao acaso [11]. O índice assume valor 1 quando as partições são equivalentes, independentemente dos identificadores dos grupos. Valores próximos de zero indicam concordância próxima à esperada ao acaso, e valores negativos indicam concordância inferior a essa referência. O ARI foi utilizado apenas na avaliação externa, após a seleção da partição, sem orientar a escolha de inicializações, hiperparâmetros ou k.

No DBSCAN, a silhueta foi calculada apenas sobre as observações não classificadas como ruído, desde que a partição restante fosse válida para essa métrica. O ARI incluiu todas as observações, mantendo o rótulo −1 atribuído ao ruído. Assim, a silhueta do DBSCAN descreve um subconjunto da base, o que deve ser considerado ao compará-la aos valores dos demais métodos.

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
As saídas de variância explicada, componentes e valores singulares seguem as definições do estimador PCA do scikit-learn [18].

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
Os parâmetros e as saídas de otimização são interpretados conforme a documentação de t-SNE [19].

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
O papel do número de vizinhos e da distância mínima segue a documentação oficial do UMAP [20].

Foram usados 15 vizinhos, `min_dist` igual a 0,1, spread igual a 1, duas dimensões, distância euclidiana, inicialização espectral e semente 42. A execução foi limitada a uma thread para reprodutibilidade. O número de épocas foi deixado no modo automático da biblioteca, registrado como `n_epochs` nulo nos parâmetros; não se declara aqui um contador de épocas observado.
#figure(image("figuras/ieee/umap.pdf", width: 100%), caption: [Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.])

Setosa forma uma região separada à esquerda. Versicolor e virginica aparecem à direita, com tendência de organização vertical e pontos misturados na transição. Os 15 vizinhos definem a escala da estrutura local; `min_dist` controla a compactação permitida na projeção. Distâncias entre regiões desconectadas e a orientação dos eixos não têm interpretação física direta. A presença de subestruturas visuais não demonstra novas classes biológicas.

== Comparação complementar das projeções
Como diagnóstico adicional, calculou-se trustworthiness com dez vizinhos e distância euclidiana entre a matriz padronizada e cada representação 2D. Essa medida penaliza vizinhos artificiais introduzidos pela projeção; valores mais próximos de 1 são melhores nesse critério [16]. Ela não utiliza espécies e não mede toda a estrutura global, nem equivale a acurácia.
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

Não foram localizados os artefatos do complemento e das 840 execuções adicionais mencionadas no artigo anterior. Essas análises não integram as conclusões desta versão. A auditoria registrada cobre a consistência de parte dos resultados principais; não certifica a execução histórica de cada comando nem a correção de toda a metodologia.

= Conclusão
A principal conclusão dos agrupamentos é a distinção entre estrutura geométrica e classes conhecidas. Todos os métodos com escolha de k favoreceram dois grupos, separando setosa das demais espécies. Entretanto, GMM com três componentes teve concordância muito maior com os rótulos. O resultado não justifica substituir a seleção pela silhueta: ele esclarece o alcance da métrica exigida.

As quatro projeções permitem visualizar a separação de setosa e a proximidade entre as outras espécies. PCA concentra 95,80% da variância nas duas primeiras componentes; t-SNE tem a maior preservação local pelo diagnóstico adotado. As figuras complementam os índices, sem provar que a estrutura visual corresponda a classes discretas perfeitamente recuperáveis.

#heading(numbering: none)[Referências]
#block[
#set par(first-line-indent: 0pt, hanging-indent: 1.2em)
[1] F. de A. T. de Carvalho, “Projeto AM-NS 2026-2,” Centro de Informática, Universidade Federal de Pernambuco, Recife, Brasil, enunciado de projeto, 2026, pp. 2–7.

[2] R. A. Fisher, “Iris,” UCI Machine Learning Repository, 1936. doi: 10.24432/C56C76.

[3] J. MacQueen, “Some methods for classification and analysis of multivariate observations,” em Proc. 5th Berkeley Symp. Math. Statist. Probab., vol. 1, 1967. #link("https://digicoll.lib.berkeley.edu/record/113015")[Online].

[4] J. C. Bezdek, #emph[Pattern Recognition with Fuzzy Objective Function Algorithms]. Springer, 1981. doi: 10.1007/978-1-4757-0450-1.

[5] D. Graves e W. Pedrycz, “Kernel-based fuzzy clustering and fuzzy clustering: A comparative experimental study,” #emph[Fuzzy Sets and Systems], 2010. #link("https://www.sciencedirect.com/science/article/pii/S016501140900459X")[Online].

[6] L. Kaufman e P. J. Rousseeuw, #emph[Finding Groups in Data: An Introduction to Cluster Analysis]. Wiley, 1990, cap. 2. doi: 10.1002/9780470316801.

[7] A. P. Dempster, N. M. Laird e D. B. Rubin, “Maximum likelihood from incomplete data via the EM algorithm,” #emph[J. Roy. Statist. Soc. B], vol. 39, no. 1, 1977. #link("https://academic.oup.com/jrsssb/article/39/1/1/7027539")[Online].

[8] R. R. Sokal e C. D. Michener, “A statistical method for evaluating systematic relationships,” #emph[Univ. Kansas Sci. Bull.], 1958. #link("https://www.biodiversitylibrary.org/part/385476")[Online].

[9] M. Ester, H.-P. Kriegel, J. Sander e X. Xu, “A density-based algorithm for discovering clusters in large spatial databases with noise,” em #emph[Proc. KDD], 1996. #link("https://cdn.aaai.org/KDD/1996/KDD96-037.pdf")[Online].

[10] P. J. Rousseeuw, “Silhouettes: A graphical aid to the interpretation and validation of cluster analysis,” #emph[J. Comput. Appl. Math.], vol. 20, pp. 53–65, 1987. doi: 10.1016/0377-0427(87)90125-7.

[11] L. Hubert e P. Arabie, “Comparing partitions,” #emph[J. Classification], vol. 2, pp. 193–218, 1985. #link("https://link.springer.com/article/10.1007/BF01908075")[Online].

[12] H. Hotelling, “Analysis of a complex of statistical variables into principal components,” #emph[J. Educational Psychology], 1933. #link("https://psycnet.apa.org/record/1934-00490-001")[Online].

[13] B. Schölkopf, A. Smola e K.-R. Müller, “Nonlinear component analysis as a kernel eigenvalue problem,” #emph[Neural Computation], vol. 10, pp. 1299–1319, 1998. #link("https://is.mpg.de/ei/publications/730")[Online].

[14] L. van der Maaten e G. Hinton, “Visualizing data using t-SNE,” #emph[J. Mach. Learn. Res.], vol. 9, pp. 2579–2605, 2008. #link("https://jmlr.org/papers/v9/vandermaaten08a.html")[Online].

[15] L. McInnes, J. Healy e J. Melville, “UMAP: Uniform manifold approximation and projection for dimension reduction,” arXiv:1802.03426, preprint, 2018. #link("https://arxiv.org/abs/1802.03426")[Online].

[16] J. Venna e S. Kaski, “Neighborhood preservation in nonlinear projection methods: An experimental study,” em #emph[Proc. ICANN], pp. 485–491, 2001. #link("https://research.aalto.fi/en/publications/neighborhood-preservation-in-nonlinear-projection-methods-an-expe/")[Online].

[17] Scikit-learn developers, “Clustering performance evaluation,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/clustering.html")[Online].

[18] Scikit-learn developers, “PCA,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html")[Online].

[19] Scikit-learn developers, “TSNE,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html")[Online].

[20] UMAP developers, “Basic UMAP parameters,” documentação online. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Online].
]

]
