// Artigo acadêmico em estilo IEEE conference (A4), implementado em Typst.
// Compilar a partir da raiz: typst compile docs/artigo/artigo_ieee_revisado.typ docs/artigo/artigo_ieee_atualizado.pdf --root docs/artigo
#set document(title: "Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa", author: ("Fátima Araújo", "Rogrigo Gomes"))
#set page(paper: "a4", margin: (top: 19mm, bottom: 25mm, x: 13mm), numbering: none)
#set text(font: "Nimbus Roman", size: 10pt, lang: "pt")
#set par(justify: true, leading: .45em, spacing: .55em, first-line-indent: 1em)
#set heading(numbering: "I.A.")
#set figure(gap: 5pt)
#set math.equation(numbering: "(1)", number-align: right)
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
#grid(
  columns: (1fr, 1fr),
  gutter: 8mm,
  align: center,
  [
    #set par(justify: false, first-line-indent: 0pt, leading: .3em)
    #text(size: 11pt)[Fátima Araújo] \
    #text(size: 10pt, style: "italic")[Centro de Informática] \
    #text(size: 10pt, style: "italic")[Universidade Federal de Pernambuco] \
    #text(size: 10pt)[Recife, Brasil] \
    #text(size: 10pt)[frqal\@cin.ufpe.br]
  ],
  [
    #set par(justify: false, first-line-indent: 0pt, leading: .3em)
    #text(size: 11pt)[Rogrigo Gomes] \
    #text(size: 10pt, style: "italic")[Centro de Informática] \
    #text(size: 10pt, style: "italic")[Universidade Federal de Pernambuco] \
    #text(size: 10pt)[Recife, Brasil] \
    #text(size: 10pt)[rgar\@cin.ufpe.br]
  ],
)
#v(.8em)
]
#columns(2, gutter: 4.22mm)[
#block[
#set par(first-line-indent: 0pt)
#text(size: 9pt, weight: "bold")[Resumo—Este artigo compara sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris padronizada. O protocolo abrange 250 execuções de métodos particionais, uma construção da hierarquia UPGMA e uma execução do DBSCAN. Nos métodos particionais, a função objetivo definiu a melhor execução para cada número de grupos. A silhueta favoreceu a mesma partição de dois grupos em seis métodos, com silhueta de 0,5802 e índice de Rand ajustado (ARI) de 0,5681. O DBSCAN identificou dois grupos e quatro pontos de ruído. A mistura gaussiana com três componentes atingiu ARI de 0,9039, mostrando que a partição favorecida pela silhueta e a de maior concordância com as espécies podem divergir. As duas primeiras componentes da PCA retiveram 95,80% da variância. Na comparação das quatro projeções, o t-SNE obteve o maior valor de #emph[trustworthiness] com dez vizinhos (0,9888).]

#text(size: 9pt, weight: "bold", style: "italic")[Palavras-chave—agrupamento, Iris, silhueta, índice de Rand ajustado, redução de dimensionalidade.]
]
= Introdução
A análise não supervisionada pode revelar estruturas geométricas que não coincidem com classes conhecidas. Este artigo investiga quais partições da base Iris são favorecidas pela silhueta, como elas se relacionam com as três espécies e quais estruturas aparecem nas projeções bidimensionais. São comparados sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade, seguindo o protocolo da Equipe 08 [1].

As projeções incluem PCA, Kernel PCA, t-SNE e UMAP. Após os ajustes, os rótulos das espécies apoiam a interpretação visual e a avaliação externa dos agrupamentos.

= Base de dados e preparação
O estudo utilizou o arquivo `codigo/iris/iris.data`, fornecido na atividade, com 150 observações e quatro atributos em centímetros: comprimento e largura da sépala e da pétala. Cada uma das três espécies (#emph[Iris setosa], #emph[Iris versicolor] e #emph[Iris virginica]) tem 50 observações. Os modelos receberam apenas os quatro atributos numéricos.

Os quatro atributos foram padronizados pelo método z-score com o StandardScaler [2]. Para cada observação i e atributo r, aplicou-se a transformação
$ z_(i r) = (x_(i r)-mu_r)/sigma_r, $
$ mu_r = 1/n sum_(i=1)^n x_(i r), quad
sigma_r = sqrt(1/n sum_(i=1)^n (x_(i r)-mu_r)^2), $
em que $n=150$, $mu_r$ é a média do atributo e $sigma_r$ é seu desvio-padrão populacional. A @estatisticas-iris apresenta os valores usados na padronização.

Os atributos foram padronizados para que diferenças de variância entre eles não determinassem seu peso no cálculo das distâncias. Como o estudo descreve a estrutura da base fornecida, a padronização e os ajustes utilizaram as 150 observações.

As observações 35 e 38 foram mantidas como aparecem no arquivo da atividade. O repositório UCI documenta correções para essas duas linhas [3].

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Médias e desvios-padrão populacionais utilizados no z-score], [
#set text(size: 8pt)
#table(columns: 3, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Atributo*],[*$mu_r$ (cm)*],[*$sigma_r$ (cm)*]),
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
]) <estatisticas-iris>


= Fundamentação dos métodos
Os métodos de agrupamento adotam diferentes critérios para definir uma partição. O K-Means minimiza a soma dos quadrados das distâncias euclidianas entre as observações e os centroides dos respectivos grupos. O algoritmo alterna a atribuição ao centro mais próximo e o recálculo dos centroides, favorecendo grupos compactos. A dependência da inicialização pode levar a diferentes mínimos locais [4].

O Fuzzy C-Means (FCM) representa cada observação por graus de pertinência aos grupos, normalizados. Sua função objetivo pondera as distâncias quadráticas aos centroides pelas pertinências elevadas ao expoente m, que controla o grau de difusividade da partição. Neste estudo, a partição exclusiva é obtida pelo maior grau de pertinência, permitindo o cálculo da silhueta e do ARI [5].

O Kernel FCM utiliza uma distância induzida por kernel. As variantes discutidas por Graves e Pedrycz diferem na representação dos protótipos e na formulação do objetivo [6]. A implementação usada mantém os protótipos no espaço de entrada, como na formulação de Zhang e Chen [7]. O kernel RBF determina a proximidade entre protótipos e observações, com escala controlada por $gamma$.

No K-Medoids, cada grupo é representado por uma observação da própria base, chamada medoide. Neste estudo, o algoritmo busca minimizar a soma das distâncias euclidianas entre as observações e os medoides aos quais estão associadas. Para isso, o procedimento PAM avalia trocas dos medoides por outras observações e mantém aquelas que reduzem o custo [8].

O modelo de mistura gaussiana (GMM) representa a distribuição dos dados por componentes definidos por médias, covariâncias e pesos. O algoritmo de expectativa-maximização (EM) alterna a estimação das probabilidades posteriores de associação e a atualização dos parâmetros, buscando maximizar a verossimilhança [9]. As covariâncias completas permitem representar componentes elípticos com diferentes orientações. A inicialização e o condicionamento das matrizes de covariância afetam a estimação.

Neste estudo, o UPGMA constrói uma hierarquia aglomerativa, unindo a cada etapa os grupos com a menor média das distâncias Manhattan entre seus pares de observações [10]. O DBSCAN identifica agrupamentos por conectividade de regiões densas e classifica como ruído as observações que não pertencem a esses agrupamentos. O parâmetro eps define o raio da vizinhança, enquanto min_samples estabelece a quantidade mínima de observações nessa vizinhança para caracterizar um ponto central [11].

A avaliação combina critérios internos e externos. A silhueta compara a distância média de uma observação ao próprio grupo com a menor distância média a outro grupo, relacionando coesão e separação [12]. O índice de Rand ajustado (ARI) mede a concordância entre a partição estimada e uma partição de referência a partir de pares de observações, com correção para a concordância esperada ao acaso [13]. Neste estudo, as espécies definem a referência externa. Uma partição favorecida pela silhueta pode apresentar concordância limitada com essa referência.

As técnicas de redução de dimensionalidade representam diferentes aspectos da estrutura dos dados. A PCA identifica direções ortogonais que maximizam sucessivamente a variância projetada, formando componentes lineares dos atributos [14]. A Kernel PCA realiza uma decomposição espectral da matriz de kernel centralizada, estendendo a análise a relações não lineares dependentes do kernel escolhido [15].

O t-SNE ajusta uma representação de baixa dimensão pela minimização da divergência KL entre as distribuições de afinidade no espaço original e no espaço projetado. A perplexidade controla a escala de vizinhança considerada, e a inicialização influencia a otimização [16]. O UMAP constrói uma representação das relações de vizinhança e otimiza sua disposição em baixa dimensão. O número de vizinhos controla a escala local, enquanto min_dist influencia a compactação da representação [17]. A interpretação dessas projeções deve considerar possíveis distorções de distâncias globais e densidades.

= Metodologia de agrupamento
== Desenho experimental e recursos utilizados
Para os cinco métodos particionais — K-Means, FCM, Kernel FCM, K-Medoids e GMM/EM —, foram avaliados os valores de $k$ de 1 a 5.

Cada combinação de método e $k$ recebeu dez chamadas com sementes inteiras de 42 a 51, totalizando 50 execuções por método e 250 execuções particionais. No K-Means e no GMM, utilizou-se `n_init=1` em cada chamada. O Kernel FCM começa com um ajuste interno de FCM, executado com a mesma semente, para inicializar as pertinências e os protótipos. Esse ajuste interno faz parte da chamada do Kernel FCM na contagem do protocolo. No K-Medoids com $k = 1$, as dez chamadas repetiram a mesma busca exaustiva pelo medoide, cujo resultado independe da semente.

Do UPGMA foram extraídos os cortes de um a cinco grupos a partir de uma única hierarquia. O DBSCAN também foi executado uma vez, completando as 252 execuções do protocolo de agrupamento. As métricas de agrupamento foram calculadas no espaço dos quatro atributos padronizados.

Os experimentos foram executados em Python 3.14.4, em ambiente virtual. A preparação dos dados utilizou NumPy 2.5.4 e pandas 3.0.6. O scikit-learn 1.9.1 forneceu K-Means, GMM, DBSCAN, PCA, Kernel PCA, t-SNE e as métricas de avaliação, enquanto o SciPy 1.18.1 foi utilizado na construção da hierarquia UPGMA. Os métodos FCM e Kernel FCM foram executados com fuzzy-c-means 2.3.1, o PAM com kmedoids 0.5.5 e o UMAP com umap-learn 0.5.12, em ambiente com Numba 0.68.0.

O ponto de entrada dos experimentos é `codigo/main.py`. Os parâmetros, rótulos dos agrupamentos, métricas e coordenadas projetadas estão nos arquivos CSV e JSON em `resultados/`.

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
  [Distância euclidiana, algoritmo de Lloyd e inicialização aleatória (`n_init=1`).],
  [Menor soma das distâncias quadráticas aos centroides.],
  [FCM],
  [Distância euclidiana quadrática e pertinências iniciais aleatórias. $m = 2$, até 300 iterações e tolerância de 0,00001.],
  [Menor objetivo fuzzy.],
  [Kernel FCM],
  [Kernel RBF com $gamma$ igual a 0,25 e inicialização por FCM. $m = 2$, até 300 iterações e tolerância de 0,00001.],
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

No Kernel FCM, o kernel $K(x,v) = exp(-gamma norm(x-v)^2)$ induz a distância quadrática $2(1-K(x,v))$. Na atualização dos protótipos, o kernel reduz a contribuição das observações mais distantes. O objetivo registrado pondera essa distância pelas pertinências elevadas a $m$. Para os dois métodos fuzzy, adotou-se $m = 2$. O valor 0,25 de $gamma$ é o inverso do número de atributos e coincide com a regra padrão do kernel RBF do scikit-learn.

No DBSCAN, `min_samples` inclui o próprio ponto na contagem da vizinhança. A configuração exploratória adotou `eps` igual a 0,8 e `min_samples` igual a 5. A varredura posterior de `eps` examina a sensibilidade da partição e do ruído ao raio.

== Avaliação
Os agrupamentos foram avaliados pela silhueta, que considera a coesão e a separação dos grupos, e pelo índice de Rand ajustado (ARI), que mede a concordância com as espécies conhecidas. O cálculo das métricas seguiu as convenções do scikit-learn [18].

Para cada observação i, a silhueta é definida por
$ s(i) = (b(i)-a(i))/max(a(i), b(i)), $
em que $a(i)$ é a distância média às demais observações do próprio grupo e $b(i)$ é a menor distância média às observações de outro grupo. Valores próximos de 1 indicam forte separação, valores próximos de zero indicam que as duas distâncias médias são semelhantes e valores negativos indicam que a observação está, em média, mais próxima de outro grupo. A silhueta da partição é a média desses valores. Entre as partições selecionadas pela função objetivo, adotou-se o $k$ com maior silhueta válida [12].

Utilizou-se distância euclidiana no cálculo da silhueta de todos os métodos. No UPGMA, portanto, a avaliação considera uma métrica diferente da distância Manhattan empregada na construção da hierarquia. A silhueta é indefinida quando há apenas um grupo, como em k = 1, ou quando cada observação constitui um grupo. Essas partições foram excluídas da seleção. Em partições válidas, a biblioteca atribui silhueta zero às observações que formam grupos unitários.

O ARI compara pares de observações para verificar a concordância entre a partição estimada e a partição de referência, definida pelas espécies, descontando a concordância esperada ao acaso [13]. O índice assume valor 1 quando as partições são equivalentes, independentemente dos identificadores dos grupos. Valores próximos de zero indicam concordância próxima à esperada ao acaso, e valores negativos indicam concordância inferior a essa referência. O ARI foi utilizado apenas na avaliação externa, após a seleção da partição, sem orientar a escolha de inicializações, hiperparâmetros ou k.

No DBSCAN, a silhueta foi calculada apenas sobre os pontos atribuídos a grupos. O ARI incluiu todas as observações e tratou os pontos de ruído como um único conjunto de rótulo −1 para calcular a concordância.

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
[2 (auto.)],
[0,5963],
[0,5518],
[4]
)
])

Os seis métodos com seleção de $k$ escolheram dois grupos e produziram a mesma partição, salvo permutação dos identificadores. Um grupo contém as 50 observações de #emph[I. setosa]. O outro reúne as 100 observações de #emph[I. versicolor] e #emph[I. virginica]. As métricas coincidem porque avaliam essas mesmas atribuições.

O DBSCAN atribuiu 49 observações de #emph[I. setosa] a um grupo e 50 de #emph[I. versicolor] e 47 de #emph[I. virginica] ao outro. O ruído corresponde a quatro pontos (2,67% da base), sendo um de #emph[I. setosa] e três de #emph[I. virginica]. Sua silhueta de 0,5963 descreve 146 observações, enquanto a silhueta de 0,5802 dos demais métodos abrange as 150. Sobre a base completa, o ARI do DBSCAN foi 0,5518.

== Silhuetas e comparação por k
A @silhuetas-por-k apresenta as silhuetas das melhores execuções particionais e dos cortes do UPGMA. A silhueta é indefinida para $k = 1$.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Silhueta das partições avaliadas por k], [
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
]) <silhuetas-por-k>

#figure(image("figuras/ieee/silhuetas_comparadas.pdf", width: 100%), caption: [Silhueta por $k$ dos seis métodos. A linha tracejada indica a escolha de $k = 2$. A silhueta é indefinida em $k = 1$.])

A silhueta diminuiu de dois para três grupos em todos os métodos avaliados. A @comparacao-k3 examina as partições de três grupos para identificar quanto elas se aproximam das três espécies.
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
]) <comparacao-k3>

Em três grupos, o GMM alcançou o maior ARI (0,9039), seguido por UPGMA (0,7184) e K-Medoids (0,6765). No GMM, a passagem de dois para três componentes reduziu a silhueta de 0,5802 para 0,3728 e elevou o ARI de 0,5681 para 0,9039.

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

As 50 observações de #emph[I. setosa] formam um grupo exclusivo. Outro contém 45 observações de #emph[I. versicolor], e o terceiro reúne as 50 de #emph[I. virginica] e cinco de #emph[I. versicolor].

== Interpretação por algoritmo e diagnósticos complementares
*K-Means.* A preferência por dois grupos expressa a separação compacta das setosas. Em três grupos, a partição recupera parcialmente as espécies e depende da inicialização; a análise de sensibilidade abaixo quantifica essa dependência.

*FCM.* As pertinências permitem descrever transições entre grupos, mas sua conversão pela maior pertinência elimina essa informação na silhueta e no ARI. Em k = 3, a partição exclusiva coincide exatamente com a do Kernel FCM, salvo permutação dos rótulos.

*Kernel FCM.* A comparação direta das partições de FCM e Kernel FCM em $k = 3$ resultou em ARI igual a 1. Com $gamma$ igual a 0,25, as diferenças de objetivo e pertinência não se traduziram em diferenças na atribuição exclusiva.

*K-Medoids.* A representação por observações reais e a soma de distâncias não quadráticas reduzem a influência de pontos extremos em comparação ao objetivo quadrático do K-Means. Essa propriedade não foi testada por contaminação nesta base; o ARI de 0,6765 em três grupos descreve apenas a configuração avaliada.

*GMM/EM.* O melhor ajuste com cinco componentes apresentou silhueta de 0,1503. Os pesos foram (0,1410; 0,3677; 0,2989; 0,1319; 0,0604), com (20; 55; 45; 20; 10) atribuições exclusivas. A componente de menor peso teve um autovalor de covariância de 0,00000381, da mesma ordem de grandeza que a regularização de 0,000001. Isso indica baixa variância em uma direção para essa componente. O critério de informação bayesiano (BIC) combina a qualidade do ajuste com uma penalidade pela complexidade do modelo. Nos melhores ajustes por verossimilhança, os valores foram 1051,2801, 797,6857, 804,5072, 834,8324 e 847,7804 para $k$ de 1 a 5, com mínimo em $k = 2$.

*UPGMA.* A hierarquia permite examinar cortes aninhados sem novas inicializações. O corte em três grupos alcança ARI de 0,7184, mas o corte em dois mantém a maior silhueta tanto euclidiana quanto Manhattan.

*DBSCAN.* Com `min_samples=5`, a varredura complementar produziu dois grupos em cada um dos cinco raios testados.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Sensibilidade do DBSCAN a eps. Silhueta calculada sem ruído.], [
#set text(size: 8pt)
#table(columns: 4, inset: (x: 2pt, y: 3pt), stroke: .3pt,
table.header([*eps*], [*Grupos*], [*Ruído*], [*Silhueta*]),
[0,6], [2], [26], [0,6405],
[0,7], [2], [8], [0,6104],
[0,8], [2], [4], [0,5963],
[0,9], [2], [4], [0,5963],
[1,0], [2], [3], [0,5936],
)
])
Os raios 0,8 e 0,9 produziram as mesmas contagens de grupos e ruído e o mesmo valor de silhueta. Com raio 0,6, a silhueta foi maior e cobriu apenas 124 observações. Lidas em conjunto, as duas medidas mostram como o raio afeta a quantidade de pontos incluídos no cálculo.

== Dependência da inicialização
Para examinar a variação entre as dez sementes, a tabela apresenta o intervalo da função objetivo em k igual a 3. O melhor extremo é o mínimo para K-Means, FCM, Kernel FCM e K-Medoids, e o máximo para GMM/EM. Cada linha deve ser interpretada na escala do próprio algoritmo; objetivos de métodos diferentes não são diretamente comparáveis.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Faixa das funções objetivo em $k = 3$], [
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

K-Means e GMM exibiram variação do objetivo entre sementes. No FCM e no Kernel FCM, os extremos coincidem na precisão exibida. As dez execuções de GMM com três componentes satisfizeram o critério de convergência da biblioteca e alcançaram valores distintos de log-verossimilhança.

Em análise complementar, executou-se K-Means com $k = 3$, inicialização aleatória, semente 42 e 100 inicializações internas. O objetivo passou de 140,9684 para 140,9658, uma redução de 0,0018%. A silhueta passou de 0,4584 para 0,4590 e o ARI de 0,6101 para 0,6201.

== Hierarquia e dendrograma
#figure(image("figuras/ieee/dendrograma_upgma.pdf", width: 100%), caption: [Árvore UPGMA com distância Manhattan e ligação média, truncada em 12 subárvores. As contagens aparecem entre parênteses e as linhas indicam cortes em dois e três grupos.])

No dendrograma, a altura de cada fusão corresponde à distância média entre as observações dos dois grupos na escala padronizada. O corte em dois grupos separa #emph[I. setosa] das demais espécies. Na métrica de construção da hierarquia, as silhuetas Manhattan foram 0,6192, 0,5024, 0,4084 e 0,3770 para $k$ de 2 a 5, respectivamente. O corte em dois grupos também maximiza a silhueta nessa métrica.

= Redução de dimensionalidade
As quatro técnicas receberam a mesma matriz padronizada. Cada técnica foi executada uma vez. A PCA estimou quatro componentes e o gráfico mostra as duas primeiras. As demais técnicas foram ajustadas diretamente para duas dimensões. Os CSV registram as coordenadas das 150 observações por método, com seus identificadores e espécies.

== PCA
As saídas de variância explicada, componentes e valores singulares seguem as definições do estimador PCA do scikit-learn [19].

A PCA utiliza decomposição em valores singulares (SVD) completa. A @espectro-pca mostra os valores singulares, os autovalores da covariância amostral e as proporções de variância explicada.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Espectro e variância explicada da PCA], [
#set text(size: 8pt)
#table(columns: 5, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Comp.*], [*Valor singular*], [*Autovalor*], [*Variância (%)*], [*Acumulada (%)*]),
[PC1],
[20,8955],
[2,9304],
[72,7705],
[72,7705],
[PC2],
[11,7551],
[0,9274],
[23,0305],
[95,8010],
[PC3],
[4,7014],
[0,1483],
[3,6838],
[99,4848],
[PC4],
[1,7582],
[0,0207],
[0,5152],
[100,0000]
)
]) <espectro-pca>

Os valores singulares são as raízes quadradas dos autovalores multiplicados por 149. A média de cada atributo após a padronização é numericamente próxima de zero. As duas primeiras componentes retêm 95,80% da variância, e as duas restantes respondem pelos 4,20% omitidos no gráfico.

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

Cada #emph[loading] é o coeficiente do autovetor multiplicado pela raiz quadrada do autovalor correspondente. Como a padronização utiliza o desvio-padrão populacional e a PCA usa a covariância amostral, a correlação entre atributo e componente corresponde ao #emph[loading] multiplicado por $sqrt(149/150)$.
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

A projeção separa #emph[I. setosa] das demais sobretudo ao longo de PC1, em que as duas medidas de pétala têm os coeficientes de maior magnitude. As regiões de #emph[I. versicolor] e #emph[I. virginica] se sobrepõem.

== Kernel PCA
Foi usado kernel RBF com gamma igual a 0,25 (1/4, correspondente ao padrão 1/número de atributos), matriz de kernel centralizada, duas componentes e decomposição espectral densa. Essa escolha corresponde a uma escala característica de distância igual a 2 nas unidades padronizadas, pois o kernel vale exp(−1) nessa distância. O valor foi fixado, sem busca orientada pelas espécies.
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

O traço da matriz de kernel centralizada é 98,2247. As razões entre os dois autovalores e esse traço são 39,8394% e 18,1140%, com soma de 57,9533% antes do arredondamento. Essas frações descrevem a variância no espaço de características induzido pelo RBF. Na projeção, #emph[I. setosa] permanece separada, e os pontos das duas outras espécies se distribuem em uma faixa curva com sobreposição.

== t-SNE
Os parâmetros e as saídas de otimização são interpretados conforme a documentação de t-SNE [20].

Foram usados perplexidade 30, inicialização por PCA, distância euclidiana, semente 42, exagero inicial 12, método Barnes-Hut com ângulo 0,5 e limite de 1.000 iterações. A taxa de aprendizado automática efetiva foi 50. A perplexidade controla a escala de vizinhança, sem representar um número de grupos.
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Saídas do t-SNE], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Saída*],[*Valor*]),
[Divergência KL final],
[0,1642],
[Índice final (`n_iter_`)],
[999],
[Taxa efetiva],
[50,0000]
)
])
#figure(image("figuras/ieee/tsne.pdf", width: 100%), caption: [Projeção t-SNE com perplexidade 30 e semente 42.])

Na projeção, #emph[I. setosa] aparece isolada à esquerda, enquanto #emph[I. versicolor] e #emph[I. virginica] ocupam regiões próximas e parcialmente sobrepostas. A divergência KL informa o valor final da função objetivo. Nesta versão do scikit-learn, `n_iter_` guarda o índice da última iteração, contado a partir de zero. O valor 999 corresponde às 1.000 iterações previstas no limite configurado.

== UMAP
O papel do número de vizinhos e da distância mínima segue a documentação oficial do UMAP [21].

O UMAP usou 15 vizinhos, `min_dist=0.1`, `spread=1`, duas dimensões, distância euclidiana, inicialização espectral, semente 42 e uma thread. A biblioteca selecionou o número de épocas automaticamente (`n_epochs=None`).
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Saídas do UMAP e parâmetros efetivos da curva], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt,
table.header([*Saída*], [*Valor*]),
[Formato de embedding\_], [150 × 2],
[Intervalo do eixo 1], [−5,8964 a 10,1182],
[Intervalo do eixo 2], [2,2188 a 9,0128],
[a], [1,5769],
[b], [0,8951],
)
])
Os parâmetros $a$ e $b$ foram recalculados com `find_ab_params` a partir de `spread` e `min_dist`. Eles definem a curva de similaridade $1/(1 + a d^(2b))$, em que $d$ é a distância na projeção. Os intervalos correspondem aos extremos das coordenadas registradas.

#figure(image("figuras/ieee/umap.pdf", width: 100%), caption: [Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.])

#emph[I. setosa] forma uma região separada à esquerda. #emph[I. versicolor] e #emph[I. virginica] se distribuem principalmente na direção vertical, com sobreposição na transição entre as duas regiões.

== Comparação complementar das projeções
Para comparar a estrutura local das projeções, calculou-se #emph[trustworthiness] com dez vizinhos, usando distância euclidiana no espaço padronizado e na projeção 2D. A medida penaliza os vizinhos que entram na lista dos dez mais próximos após a projeção. A penalidade aumenta quanto mais abaixo o ponto estava na lista original de vizinhos, ordenada do mais próximo ao mais distante [22].
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Preservação local das projeções], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt, table.header([*Projeção*],[*Trustworthiness (10 vizinhos)*]),
[PCA],
[0,9782],
[Kernel PCA],
[0,9322],
[t-SNE],
[0,9888],
[UMAP],
[0,9783]
)
])

O t-SNE obteve o maior valor nessa configuração (0,9888). UMAP (0,9783) e PCA (0,9782) obtiveram valores próximos entre si, e Kernel PCA obteve 0,9322. A comparação descreve a introdução de vizinhos na escala de dez observações.

= Discussão e limitações
O estudo é descritivo e utiliza uma única base. As repetições dos métodos particionais examinam a influência da inicialização, mantendo fixas as observações. Os diagnósticos complementares variaram o raio do DBSCAN e o número de inicializações do K-Means. A estabilidade das projeções entre sementes e a sensibilidade a $gamma$, à perplexidade e ao número de vizinhos ficaram sem avaliação. No t-SNE e no UMAP, as descrições se limitam à configuração visual observada, pois distâncias entre regiões e densidades podem mudar na projeção.

= Conclusão
A silhueta favoreceu a separação de #emph[I. setosa] das outras duas espécies nos seis métodos com seleção de $k$. A mistura gaussiana com três componentes recuperou melhor a distinção entre #emph[I. versicolor] e #emph[I. virginica], alcançando ARI de 0,9039. O resultado distingue a separação geométrica avaliada pela silhueta da concordância com os rótulos medida pelo ARI.

As quatro projeções reproduziram visualmente a separação de #emph[I. setosa]. A PCA reteve 95,80% da variância em duas componentes, e o t-SNE obteve o maior #emph[trustworthiness] com dez vizinhos entre as configurações avaliadas.

#heading(numbering: none)[Referências]
#block[
#set text(size: 9pt)
#set par(first-line-indent: 0pt, hanging-indent: 1.2em)
[1] F. de A. T. de Carvalho, “Projeto AM-NS 2026-2,” Centro de Informática, Universidade Federal de Pernambuco, Recife, Brasil, enunciado de projeto, 2026, pp. 2–7.

[2] Scikit-learn developers, “StandardScaler,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html")[Online].

[3] R. A. Fisher, “Iris,” UCI Machine Learning Repository, 1936. #link("https://doi.org/10.24432/C56C76")[doi: 10.24432/C56C76].

[4] J. MacQueen, “Some methods for classification and analysis of multivariate observations,” em #emph[Proc. 5th Berkeley Symp. Math. Statist. Probab.], vol. 1, 1967, pp. 281–297. #link("https://digicoll.lib.berkeley.edu/record/113015")[Online].

[5] J. C. Bezdek, #emph[Pattern Recognition with Fuzzy Objective Function Algorithms]. Springer, 1981. doi: 10.1007/978-1-4757-0450-1.

[6] D. Graves e W. Pedrycz, “Kernel-based fuzzy clustering and fuzzy clustering: A comparative experimental study,” #emph[Fuzzy Sets and Systems], vol. 161, no. 4, pp. 522–543, 2010. #link("https://doi.org/10.1016/j.fss.2009.10.021")[doi: 10.1016/j.fss.2009.10.021].

[7] D.-Q. Zhang e S.-C. Chen, “A novel kernelized fuzzy C-means algorithm with application in medical image segmentation,” #emph[Artificial Intelligence in Medicine], vol. 32, no. 1, pp. 37–50, 2004. #link("https://doi.org/10.1016/j.artmed.2004.01.012")[doi: 10.1016/j.artmed.2004.01.012].

[8] L. Kaufman e P. J. Rousseeuw, #emph[Finding Groups in Data: An Introduction to Cluster Analysis]. Wiley, 1990, cap. 2. doi: 10.1002/9780470316801.

[9] A. P. Dempster, N. M. Laird e D. B. Rubin, “Maximum likelihood from incomplete data via the EM algorithm,” #emph[J. Roy. Statist. Soc. B], vol. 39, no. 1, 1977. #link("https://academic.oup.com/jrsssb/article/39/1/1/7027539")[Online].

[10] R. R. Sokal e C. D. Michener, “A statistical method for evaluating systematic relationships,” #emph[Univ. Kansas Sci. Bull.], vol. 38, no. 22, pp. 1409–1438, 1958. #link("https://www.biodiversitylibrary.org/part/385476")[Online].

[11] M. Ester, H.-P. Kriegel, J. Sander e X. Xu, “A density-based algorithm for discovering clusters in large spatial databases with noise,” em #emph[Proc. KDD], 1996, pp. 226–231. #link("https://cdn.aaai.org/KDD/1996/KDD96-037.pdf")[Online].

[12] P. J. Rousseeuw, “Silhouettes: A graphical aid to the interpretation and validation of cluster analysis,” #emph[J. Comput. Appl. Math.], vol. 20, pp. 53–65, 1987. doi: 10.1016/0377-0427(87)90125-7.

[13] L. Hubert e P. Arabie, “Comparing partitions,” #emph[J. Classification], vol. 2, pp. 193–218, 1985. #link("https://link.springer.com/article/10.1007/BF01908075")[Online].

[14] H. Hotelling, “Analysis of a complex of statistical variables into principal components,” #emph[J. Educational Psychology], 1933. #link("https://psycnet.apa.org/record/1934-00490-001")[Online].

[15] B. Schölkopf, A. J. Smola e K.-R. Müller, “Nonlinear component analysis as a kernel eigenvalue problem,” #emph[Neural Computation], vol. 10, no. 5, pp. 1299–1319, 1998. #link("https://doi.org/10.1162/089976698300017467")[doi: 10.1162/089976698300017467].

[16] L. van der Maaten e G. Hinton, “Visualizing data using t-SNE,” #emph[J. Mach. Learn. Res.], vol. 9, pp. 2579–2605, 2008. #link("https://jmlr.org/papers/v9/vandermaaten08a.html")[Online].

[17] L. McInnes, J. Healy e J. Melville, “UMAP: Uniform manifold approximation and projection for dimension reduction,” arXiv:1802.03426, preprint, 2018. #link("https://arxiv.org/abs/1802.03426")[Online].

[18] Scikit-learn developers, “Clustering performance evaluation,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/clustering.html")[Online].

[19] Scikit-learn developers, “PCA,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html")[Online].

[20] Scikit-learn developers, “TSNE,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html")[Online].

[21] UMAP developers, “Basic UMAP parameters,” documentação online. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Online].

[22] J. Venna e S. Kaski, “Neighborhood preservation in nonlinear projection methods: An experimental study,” em #emph[Proc. ICANN], pp. 485–491, 2001. #link("https://research.aalto.fi/en/publications/neighborhood-preservation-in-nonlinear-projection-methods-an-expe/")[Online].
]

]
