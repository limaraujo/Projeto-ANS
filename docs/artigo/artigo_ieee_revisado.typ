// Artigo acadêmico em estilo IEEE conference (A4), implementado em Typst.
// Compilar a partir da raiz: typst compile docs/artigo/artigo_ieee.typ docs/artigo/artigo_ieee.pdf --root docs/artigo
#set document(title: "Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa", author: ("Fátima Araújo", "Rogrigo Gomes"))
#set page(paper: "a4", margin: (top: 19mm, bottom: 43mm, x: 13mm), numbering: none)
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
#text(size: 9pt, weight: "bold")[Resumo—Este artigo compara sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris padronizada. Foram realizados 250 ajustes particionais, uma hierarquia UPGMA e uma execução DBSCAN. A melhor inicialização de cada número de grupos foi selecionada pela função objetivo, e o número de grupos pela silhueta. Os seis métodos com seleção de k escolheram dois grupos, com silhueta de 0,5802 e índice de Rand ajustado (ARI) de 0,5681. O DBSCAN encontrou dois grupos e quatro pontos de ruído. Em análise complementar, a mistura gaussiana com três componentes atingiu ARI de 0,9039, evidenciando a diferença entre separação geométrica e concordância com espécies. As duas primeiras componentes da PCA retiveram 95,80% da variância. Kernel PCA, t-SNE e UMAP complementaram a análise visual; t-SNE apresentou a maior preservação local de vizinhanças na configuração avaliada. Os resultados destacam os limites da seleção interna e a necessidade de interpretar projeções em conjunto com métricas.]

#text(size: 9pt, weight: "bold", style: "italic")[Palavras-chave—agrupamento, Iris, silhueta, índice de Rand ajustado, redução de dimensionalidade.]
]
= Introdução
A análise não supervisionada pode revelar estruturas geométricas que não coincidem com classes conhecidas. Este artigo investiga quais partições da base Iris são favorecidas pela silhueta, como elas se relacionam com as três espécies e quais estruturas aparecem nas projeções bidimensionais. São comparados sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade, seguindo o protocolo da Equipe 08 [1].

Foram realizados 252 ajustes principais: 250 ajustes particionais, uma hierarquia UPGMA e um DBSCAN. As projeções incluem PCA, Kernel PCA, t-SNE e UMAP. As espécies são utilizadas somente após os ajustes, para interpretação e avaliação externa. A comparação combina funções objetivo, silhueta, índice de Rand ajustado e diagnóstico de preservação de vizinhanças.

= Base de dados e preparação
Foi utilizada a base Iris fornecida na atividade, com 150 observações e quatro atributos em centímetros: comprimento e largura de sépala e comprimento e largura de pétala. Há 50 observações por espécie: Iris-setosa, Iris-versicolor e Iris-virginica. Linhas completamente vazias são ignoradas. A matriz numérica é separada dos rótulos antes dos ajustes; os rótulos servem apenas à avaliação externa e às cores e símbolos das figuras.

Os quatro atributos foram padronizados pelo método z-score com o StandardScaler [2]. Para cada observação i e atributo r, aplicou-se a transformação
$ z_(i r) = (x_(i r)-mu_r)/sigma_r, $
$ mu_r = 1/n sum_(i=1)^n x_(i r), quad
sigma_r = sqrt(1/n sum_(i=1)^n (x_(i r)-mu_r)^2), $
em que $n=150$, $mu_r$ é a média do atributo e $sigma_r$ seu desvio-padrão populacional. Os valores de $mu_r$ e $sigma_r$ utilizados na padronização estão na Tabela I.


A padronização equilibra as escalas dos atributos; nos dados brutos, as distâncias, as silhuetas e o número de grupos selecionado podem mudar. Não foi feita divisão treino/teste, pois o objetivo é a análise descritiva não supervisionada da base fornecida, e não a estimação de desempenho preditivo em novos dados.
A descrição da base e de seus atributos está disponível no repositório UCI [3].

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
])


= Fundamentação dos métodos
Os métodos de agrupamento adotam diferentes critérios para definir uma partição. O K-Means minimiza a soma dos quadrados das distâncias euclidianas entre as observações e os centroides dos respectivos grupos. O algoritmo alterna a atribuição ao centro mais próximo e o recálculo dos centroides, favorecendo grupos compactos. A dependência da inicialização pode levar a diferentes mínimos locais [4].

O Fuzzy C-Means (FCM) representa cada observação por graus de pertinência aos grupos, normalizados. Sua função objetivo pondera as distâncias quadráticas aos centroides pelas pertinências elevadas ao expoente m, que controla o grau de difusividade da partição. Neste estudo, a partição exclusiva é obtida pelo maior grau de pertinência, permitindo o cálculo da silhueta e do ARI [5].

O Kernel FCM utiliza uma distância induzida por kernel para representar relações não lineares. As variantes discutidas por Graves e Pedrycz diferem na representação dos protótipos e na formulação do objetivo [6]. Adotou-se a variante de Zhang e Chen com protótipos no espaço de entrada [7], e o kernel RBF determina sua proximidade às observações. O parâmetro gamma controla a escala dessa relação e, portanto, influencia o ajuste.

No K-Medoids, cada grupo é representado por uma observação da própria base, chamada medoide. Neste estudo, o algoritmo busca minimizar a soma das distâncias euclidianas entre as observações e os medoides aos quais estão associadas. Para isso, o procedimento PAM avalia trocas dos medoides por outras observações e mantém aquelas que reduzem o custo [8].

A mistura gaussiana modela a distribuição dos dados por componentes definidos por médias, covariâncias e pesos. O algoritmo de expectativa-maximização (EM) alterna a estimação das probabilidades posteriores de associação e a atualização dos parâmetros, buscando maximizar a verossimilhança [9]. As covariâncias completas permitem representar componentes elípticos com diferentes orientações. A inicialização e o condicionamento das matrizes de covariância afetam a estimação.

Neste estudo, o UPGMA constrói uma hierarquia aglomerativa, unindo a cada etapa os grupos com a menor média das distâncias Manhattan entre seus pares de observações [10]. O DBSCAN identifica agrupamentos por conectividade de regiões densas e classifica como ruído as observações que não pertencem a esses agrupamentos. O parâmetro eps define o raio da vizinhança, enquanto min_samples estabelece a quantidade mínima de observações nessa vizinhança para caracterizar um ponto central [11].

A avaliação combina critérios internos e externos. A silhueta compara a distância média de uma observação ao próprio grupo com a menor distância média a outro grupo, relacionando coesão e separação [12]. O índice de Rand ajustado (ARI) mede a concordância entre a partição estimada e uma partição de referência a partir de pares de observações, com correção para a concordância esperada ao acaso [13]. Neste estudo, as espécies definem a referência externa. Uma partição favorecida pela silhueta pode apresentar concordância limitada com essa referência.

As técnicas de redução de dimensionalidade representam diferentes aspectos da estrutura dos dados. A PCA identifica direções ortogonais que maximizam sucessivamente a variância projetada, formando componentes lineares dos atributos [14]. A Kernel PCA realiza uma decomposição espectral da matriz de kernel centralizada, estendendo a análise a relações não lineares dependentes do kernel escolhido [15].

O t-SNE ajusta uma representação de baixa dimensão pela minimização da divergência KL entre as distribuições de afinidade no espaço original e no espaço projetado. A perplexidade controla a escala de vizinhança considerada, e a inicialização influencia a otimização [16]. O UMAP constrói uma representação das relações de vizinhança e otimiza sua disposição em baixa dimensão. O número de vizinhos controla a escala local, enquanto min_dist influencia a compactação da representação [17]. A interpretação dessas projeções deve considerar possíveis distorções de distâncias globais e densidades.

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

No Kernel FCM, utiliza-se K(x,v) = exp(−0,25‖x−v‖²), com distância quadrática induzida igual a 2(1−K(x,v)). Os protótipos permanecem no espaço de entrada e são atualizados com ponderação pelo kernel, conforme a variante implementada pela biblioteca fcmeans. O objetivo registrado corresponde a essa formulação. Nos dois métodos fuzzy, m = 2 é a escolha convencional de difusividade. O valor gamma = 0,25 coincide com 1/número de atributos, padrão do kernel RBF do scikit-learn, e foi fixado sem consultar as espécies.

No DBSCAN, `min_samples` inclui o próprio ponto na contagem da vizinhança. Adotaram-se eps = 0,8 e min_samples = 5 como configuração exploratória. A varredura complementar de eps apresentada nos resultados examina sua sensibilidade sem utilizar as espécies para seleção; ela não integra os 252 ajustes principais.

== Avaliação
Os agrupamentos foram avaliados pela silhueta, que considera a coesão e a separação dos grupos, e pelo índice de Rand ajustado (ARI), que mede a concordância com as espécies conhecidas. O cálculo das métricas seguiu as convenções do scikit-learn [18].

Para cada observação i, a silhueta é definida por
$ s(i) = (b(i)-a(i))/max(a(i), b(i)) $,
em que a(i) é a distância média às demais observações do próprio grupo e b(i) é a menor distância média às observações de outro grupo. Valores próximos de 1 indicam maior separação em relação aos demais grupos; valores próximos de zero sugerem proximidade entre grupos, e valores negativos indicam que a observação está, em média, mais próxima de outro grupo. A silhueta da partição corresponde à média desses valores e foi utilizada para selecionar k após a escolha da melhor execução pela função objetivo [12].

Utilizou-se distância euclidiana no cálculo da silhueta de todos os métodos. No UPGMA, portanto, a avaliação considera uma métrica diferente da distância Manhattan empregada na construção da hierarquia. A silhueta é indefinida quando há apenas um grupo, como em k = 1, ou quando cada observação constitui um grupo. Essas partições foram excluídas da seleção. Em partições válidas, a biblioteca atribui silhueta zero às observações que formam grupos unitários.

O ARI compara pares de observações para verificar a concordância entre a partição estimada e a partição de referência, definida pelas espécies, descontando a concordância esperada ao acaso [13]. O índice assume valor 1 quando as partições são equivalentes, independentemente dos identificadores dos grupos. Valores próximos de zero indicam concordância próxima à esperada ao acaso, e valores negativos indicam concordância inferior a essa referência. O ARI foi utilizado apenas na avaliação externa, após a seleção da partição, sem orientar a escolha de inicializações, hiperparâmetros ou k.

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
[2 (auto.)],
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

#figure(image("figuras/ieee/silhuetas_comparadas.pdf", width: 100%), caption: [Silhueta por k dos seis métodos. A linha tracejada indica k ótimo = 2 em todos eles; em k = 1, a silhueta é indefinida.])

A silhueta tende a cair quando se subdivide a estrutura que reúne versicolor e virginica em k = 2; os grupos obtidos em k = 3 não correspondem necessariamente às espécies. Isso favorece k igual a 2, apesar das três classes biológicas. O efeito é especialmente claro no GMM: a partição de três componentes tem menor silhueta, embora corresponda muito melhor às espécies. A tabela seguinte usa k igual a 3 apenas para interpretação posterior; ela não substitui a seleção exigida no enunciado.
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

== Interpretação por algoritmo e diagnósticos complementares
*K-Means.* A preferência por dois grupos expressa a separação compacta das setosas. Em três grupos, a partição recupera parcialmente as espécies e depende da inicialização; a análise de sensibilidade abaixo quantifica essa dependência.

*FCM.* As pertinências permitem descrever transições entre grupos, mas sua conversão pela maior pertinência elimina essa informação na silhueta e no ARI. Em k = 3, a partição exclusiva coincide exatamente com a do Kernel FCM, salvo permutação dos rótulos.

*Kernel FCM.* A igualdade das métricas em k = 3 decorre dessa coincidência de partição, verificada por ARI entre as duas soluções igual a 1. Os objetivos e as pertinências são distintos; o kernel não produziu vantagem na partição exclusiva dessa configuração.

*K-Medoids.* A representação por observações reais e a soma de distâncias não quadráticas reduzem a influência de pontos extremos em comparação ao objetivo quadrático do K-Means. Essa propriedade não foi testada por contaminação nesta base; o ARI de 0,6765 em três grupos descreve apenas a configuração avaliada.

*GMM/EM.* A alta concordância em três componentes contrasta com a silhueta de 0,1503 em cinco. No melhor ajuste de cinco componentes, os pesos foram (0,1410; 0,3677; 0,2989; 0,1319; 0,0604), com (20; 55; 45; 20; 10) atribuições exclusivas. A menor componente tem cerca de 6% do peso e covariância quase singular: autovalor mínimo de 0,00000381, próximo à regularização de 0,000001. Isso é compatível com um ajuste muito estreito e fragmentação, embora a silhueta baixa isoladamente não diagnostique degeneração. O BIC, calculado nos melhores ajustes por verossimilhança, foi 1051,2801; 797,6857; 804,5072; 834,8324; 847,7804 para k de 1 a 5. Seu mínimo também ocorre em k = 2, sem substituir a seleção principal pela silhueta.

*UPGMA.* A hierarquia permite examinar cortes aninhados sem novas inicializações. O corte em três grupos alcança ARI de 0,7184, mas o corte em dois mantém a maior silhueta tanto euclidiana quanto Manhattan.

*DBSCAN.* Os quatro pontos de ruído ficam sem atribuição aos dois grupos e não são forçados a integrar uma região densa. Para min_samples = 5, a varredura complementar mostra dois grupos em todo o intervalo examinado:
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Sensibilidade do DBSCAN a eps; silhueta sem ruído], [
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
O valor 0,8 situa-se em uma região localmente estável entre 0,8 e 0,9, com quatro pontos de ruído, e reduz a exclusão observada nos raios menores. A maior silhueta em eps = 0,6 acompanha a exclusão de 26 observações e não é diretamente comparável à avaliação sobre 146 pontos. A varredura oferece justificativa geométrica posterior da configuração exploratória, sem comprovar que seja ótima.

== Dependência da inicialização
Para examinar a variação entre as dez sementes, a tabela apresenta o intervalo da função objetivo em k igual a 3. O melhor extremo é o mínimo para K-Means, FCM, Kernel FCM e K-Medoids, e o máximo para GMM/EM. Cada linha deve ser interpretada na escala do próprio algoritmo; objetivos de métodos diferentes não são diretamente comparáveis.
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

Como análise de sensibilidade separada, executou-se K-Means com k = 3, inicialização aleatória, semente 42 e 100 inicializações internas. O objetivo foi 140,9658, contra 140,9684 no protocolo principal, com ARI de 0,6201 e silhueta de 0,4590. A redução do objetivo foi de apenas 0,0018%, embora a nova partição tenha aumentado o ARI. A diferença de ARI para o FCM diminuiu, mas permaneceu; o resultado principal foi preservado. Essa análise não demonstra otimalidade global.

== Hierarquia e dendrograma
#figure(image("figuras/ieee/dendrograma_upgma.pdf", width: 100%), caption: [Árvore UPGMA com distância Manhattan e ligação média, truncada em 12 subárvores. As contagens aparecem entre parênteses e as linhas indicam cortes em dois e três grupos.])

O dendrograma registra a sequência de fusões; a altura corresponde à distância de ligação média na escala padronizada. O corte em dois grupos separa setosa das demais espécies. Cortes mais finos aumentam a correspondência com as espécies em alguns casos, mas reduzem a silhueta euclidiana. A árvore representa relações de proximidade, e não uma filogenia ou evidência causal. Como verificação na métrica de construção, as silhuetas Manhattan foram 0,6192, 0,5024, 0,4084 e 0,3770 para k de 2 a 5, respectivamente, mantendo a escolha de k = 2.

= Redução de dimensionalidade
As quatro técnicas receberam a mesma matriz padronizada de quatro atributos, sem rótulos de espécie durante o ajuste. As cores foram adicionadas posteriormente. PCA foi ajustada com quatro componentes para apresentar o espectro completo; seu gráfico usa apenas as duas primeiras. Os outros métodos foram ajustados diretamente para duas dimensões. As 150 coordenadas de cada método foram exportadas em CSV, com identificador de observação e espécie.

== PCA
As saídas de variância explicada, componentes e valores singulares seguem as definições do estimador PCA do scikit-learn [19].

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
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Valores singulares da PCA], [
#set text(size: 8pt)
#table(columns: 2, inset: (x: 2pt, y: 3pt), stroke: .3pt,
table.header([*Componente*], [*Valor singular*]),
[PC1], [20,8955],
[PC2], [11,7551],
[PC3], [4,7014],
[PC4], [1,7582],
)
])
Os valores de `singular_values_` correspondem a √(149 × autovalor). A saída `mean_` sobre os atributos padronizados é aproximadamente (0; 0; 0; 0), com resíduos numéricos em módulo inferiores a 7 × 10⁻¹⁶. As médias dos atributos em centímetros constam da Tabela I.

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

Adotou-se como loading o autovetor multiplicado pela raiz do autovalor. A correlação entre atributo e componente é igual ao loading multiplicado por √(149/150).
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

Os autovalores acima pertencem à matriz de kernel centralizada, não à covariância dos quatro atributos originais. O traço da matriz de kernel centralizada é 98,2247, igual à soma de seu espectro completo de 150 autovalores. Dividindo cada autovalor por esse traço, obtêm-se 39,8394% e 18,1140%, ou 57,9533% acumulados, da variância no espaço de características induzido pelo RBF. Essas frações não medem a variância dos atributos originais. A transformação curva a organização dos pontos e evidencia relações não lineares, mas torna a interpretação por pesos dos atributos menos direta. A escolha de gamma altera a noção de proximidade e não foi submetida a análise de sensibilidade.

== t-SNE
Os parâmetros e as saídas de otimização são interpretados conforme a documentação de t-SNE [20].

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
O papel do número de vizinhos e da distância mínima segue a documentação oficial do UMAP [21].

Foram usados 15 vizinhos, `min_dist` igual a 0,1, spread igual a 1, duas dimensões, distância euclidiana, inicialização espectral e semente 42. A execução foi limitada a uma thread para reprodutibilidade. O número de épocas foi deixado no modo automático da biblioteca, registrado como `n_epochs` nulo nos parâmetros; não se declara aqui um contador de épocas observado.
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
Os parâmetros a e b foram recuperados pela função de ajuste da biblioteca a partir de spread = 1 e min_dist = 0,1; definem a curva de similaridade $1/(1 + a d^(2b))$. Os intervalos foram calculados sobre o embedding registrado. O tempo desse ajuste não foi medido, portanto não se compara seu custo computacional.

#figure(image("figuras/ieee/umap.pdf", width: 100%), caption: [Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.])

Setosa forma uma região separada à esquerda. Versicolor e virginica aparecem à direita, com tendência de organização vertical e pontos misturados na transição. Os 15 vizinhos definem a escala da estrutura local; `min_dist` controla a compactação permitida na projeção. Distâncias entre regiões desconectadas e a orientação dos eixos não têm interpretação física direta. A presença de subestruturas visuais não demonstra novas classes biológicas.

== Comparação complementar das projeções
Como diagnóstico adicional, calculou-se trustworthiness com dez vizinhos e distância euclidiana entre a matriz padronizada e cada representação 2D. Essa medida penaliza vizinhos artificiais introduzidos pela projeção; valores mais próximos de 1 são melhores nesse critério [22]. Ela não utiliza espécies e não mede toda a estrutura global, nem equivale a acurácia.
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

Nesta execução, t-SNE apresentou o maior valor local (0,9888), seguido de UMAP (0,9783) e PCA (0,9782), muito próximos entre si. Kernel PCA obteve 0,9322. Essa ordenação é específica dos hiperparâmetros, da semente e da vizinhança escolhida; não constitui superioridade universal. PCA oferece interpretação direta e alta retenção de variância, enquanto t-SNE e UMAP enfatizam relações locais. Não foram executados agrupamentos sobre as projeções: as métricas da Questão 1 pertencem ao espaço original padronizado.

= Discussão e limitações
Os resultados se referem ao arquivo local Iris, a uma padronização e a um conjunto fixo de hiperparâmetros. Dez reinicializações reduzem a dependência da inicialização dos agrupamentos, mas não asseguram ótimo global. Houve uma execução de cada projeção; não foram estimados intervalos de confiança ou estabilidade entre sementes. A análise complementar abrangeu eps e o orçamento de inicializações do K-Means; a sensibilidade de gamma, perplexidade e número de vizinhos permanece fora do escopo.

= Conclusão
A principal conclusão dos agrupamentos é a distinção entre estrutura geométrica e classes conhecidas. Todos os métodos com escolha de k favoreceram dois grupos, separando setosa das demais espécies. Entretanto, GMM com três componentes teve concordância muito maior com os rótulos. O resultado não justifica substituir a seleção pela silhueta: ele esclarece o alcance da métrica exigida.

As quatro projeções permitem visualizar a separação de setosa e a proximidade entre as outras espécies. PCA concentra 95,80% da variância nas duas primeiras componentes; t-SNE tem a maior preservação local pelo diagnóstico adotado. As figuras complementam os índices, sem provar que a estrutura visual corresponda a classes discretas perfeitamente recuperáveis.

#heading(numbering: none)[Referências]
#block[
#set par(first-line-indent: 0pt, hanging-indent: 1.2em)
[1] F. de A. T. de Carvalho, “Projeto AM-NS 2026-2,” Centro de Informática, Universidade Federal de Pernambuco, Recife, Brasil, enunciado de projeto, 2026, pp. 2–7.

[2] Scikit-learn developers, “StandardScaler,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html")[Online].

[3] R. A. Fisher, “Iris,” UCI Machine Learning Repository, 1936. doi: 10.24432/C56C76.

[4] J. MacQueen, “Some methods for classification and analysis of multivariate observations,” em Proc. 5th Berkeley Symp. Math. Statist. Probab., vol. 1, 1967. #link("https://digicoll.lib.berkeley.edu/record/113015")[Online].

[5] J. C. Bezdek, #emph[Pattern Recognition with Fuzzy Objective Function Algorithms]. Springer, 1981. doi: 10.1007/978-1-4757-0450-1.

[6] D. Graves e W. Pedrycz, “Kernel-based fuzzy clustering and fuzzy clustering: A comparative experimental study,” #emph[Fuzzy Sets and Systems], 2010. #link("https://www.sciencedirect.com/science/article/pii/S016501140900459X")[Online].

[7] D.-Q. Zhang e S.-C. Chen, “A novel kernelized fuzzy C-means algorithm with application in medical image segmentation,” #emph[Artificial Intelligence in Medicine], vol. 32, no. 1, pp. 37–50, 2004. #link("https://www.sciencedirect.com/science/article/pii/S0933365704000351")[Online].

[8] L. Kaufman e P. J. Rousseeuw, #emph[Finding Groups in Data: An Introduction to Cluster Analysis]. Wiley, 1990, cap. 2. doi: 10.1002/9780470316801.

[9] A. P. Dempster, N. M. Laird e D. B. Rubin, “Maximum likelihood from incomplete data via the EM algorithm,” #emph[J. Roy. Statist. Soc. B], vol. 39, no. 1, 1977. #link("https://academic.oup.com/jrsssb/article/39/1/1/7027539")[Online].

[10] R. R. Sokal e C. D. Michener, “A statistical method for evaluating systematic relationships,” #emph[Univ. Kansas Sci. Bull.], 1958. #link("https://www.biodiversitylibrary.org/part/385476")[Online].

[11] M. Ester, H.-P. Kriegel, J. Sander e X. Xu, “A density-based algorithm for discovering clusters in large spatial databases with noise,” em #emph[Proc. KDD], 1996. #link("https://cdn.aaai.org/KDD/1996/KDD96-037.pdf")[Online].

[12] P. J. Rousseeuw, “Silhouettes: A graphical aid to the interpretation and validation of cluster analysis,” #emph[J. Comput. Appl. Math.], vol. 20, pp. 53–65, 1987. doi: 10.1016/0377-0427(87)90125-7.

[13] L. Hubert e P. Arabie, “Comparing partitions,” #emph[J. Classification], vol. 2, pp. 193–218, 1985. #link("https://link.springer.com/article/10.1007/BF01908075")[Online].

[14] H. Hotelling, “Analysis of a complex of statistical variables into principal components,” #emph[J. Educational Psychology], 1933. #link("https://psycnet.apa.org/record/1934-00490-001")[Online].

[15] B. Schölkopf, A. Smola e K.-R. Müller, “Nonlinear component analysis as a kernel eigenvalue problem,” #emph[Neural Computation], vol. 10, pp. 1299–1319, 1998. #link("https://is.mpg.de/ei/publications/730")[Online].

[16] L. van der Maaten e G. Hinton, “Visualizing data using t-SNE,” #emph[J. Mach. Learn. Res.], vol. 9, pp. 2579–2605, 2008. #link("https://jmlr.org/papers/v9/vandermaaten08a.html")[Online].

[17] L. McInnes, J. Healy e J. Melville, “UMAP: Uniform manifold approximation and projection for dimension reduction,” arXiv:1802.03426, preprint, 2018. #link("https://arxiv.org/abs/1802.03426")[Online].

[18] Scikit-learn developers, “Clustering performance evaluation,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/clustering.html")[Online].

[19] Scikit-learn developers, “PCA,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html")[Online].

[20] Scikit-learn developers, “TSNE,” documentação v. 1.9.1. #link("https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html")[Online].

[21] UMAP developers, “Basic UMAP parameters,” documentação online. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Online].

[22] J. Venna e S. Kaski, “Neighborhood preservation in nonlinear projection methods: An experimental study,” em #emph[Proc. ICANN], pp. 485–491, 2001. #link("https://research.aalto.fi/en/publications/neighborhood-preservation-in-nonlinear-projection-methods-an-expe/")[Online].
]

]
