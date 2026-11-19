// Artigo acadêmico em estilo IEEE conference (A4), implementado em Typst.
// Compilar a partir da raiz: typst compile docs/artigo/artigo_ieee_revisado.typ docs/artigo/artigo_ieee_revisado.pdf --root docs/artigo
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
#let experimentos = json("diagnosticos_revisao.json").agrupamento
#let db = experimentos.dbscan
#let tabela-dados(cabecalho, linhas, columns: auto) = {
  set text(size: 8pt)
  set par(justify: false, first-line-indent: 0pt)
  table(
    columns: if columns == auto { cabecalho.len() } else { columns },
    inset: (x: 2pt, y: 3pt),
    stroke: .3pt,
    table.header(..cabecalho.map(x => strong(x))),
    ..linhas.flatten(),
  )
}
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
#text(size: 9pt, weight: "bold")[Resumo—Este artigo compara sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris padronizada. Nos métodos particionais, a busca variou os hiperparâmetros e o número de grupos. A melhor execução por função objetivo de cada configuração foi avaliada pela silhueta euclidiana. O índice de Rand ajustado (ARI) mediu a concordância com as espécies. O DBSCAN encontrou #db.grupos grupos, com #db.cobertura% de cobertura, silhueta de #db.silhueta e ARI de #db.ari sobre #db.n observações. Em três grupos, #experimentos.maior_ari_k3.nome alcançou ARI de #experimentos.maior_ari_k3.ari. As duas primeiras componentes da PCA retiveram 95,80% da variância. Na comparação das projeções, o t-SNE obteve o maior #emph[trustworthiness] com dez vizinhos (0,9888).]

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
== Desenho experimental
A busca avaliou configurações para os cinco métodos particionais em $k in {2, 3, 4, 5}$. Cada combinação recebeu dez chamadas com sementes de 42 a 51. O K-Means e o GMM usaram `n_init=1` por chamada. O objetivo foi minimizado no K-Means, no FCM, no Kernel FCM e no K-Medoids. No GMM, foi maximizada a log-verossimilhança total. Empates de objetivo seguiram a ordem das sementes. A partição exclusiva foi obtida pela maior pertinência nos métodos fuzzy e pela maior probabilidade posterior no GMM.

Foram comparadas as silhuetas das melhores execuções por objetivo, escolhendo o maior valor. Empates de silhueta favoreceram menor $k$ e a ordem da grade, com a configuração de referência primeiro. Para cada método particional, os quatro conjuntos de ajustes do perfil escolhido foram reaproveitados e somados a dez chamadas em $k=1$. Em $k=1$, o K-Medoids repete a busca exaustiva pelo único medoide. O ajuste interno de FCM que inicializa o Kernel FCM integra a chamada do método.

A hierarquia UPGMA foi construída uma vez com Manhattan e ligação média, com extração de cinco cortes. No DBSCAN, foram testados #experimentos.contagens.ajustes_dbscan pares de parâmetros, incluindo raios fixos e raios relativos à mediana da distância ao quinto vizinho, contando o próprio ponto. Selecionou-se a maior silhueta válida entre as configurações com cobertura de pelo menos #experimentos.contagens.cobertura_minima_dbscan_pct%. Empates favoreceram maior cobertura e a ordem da grade.

A busca fez #experimentos.contagens.ajustes_particionais ajustes particionais para $k$ de 2 a 5. Incluindo o DBSCAN, as 50 chamadas em $k=1$ e a árvore, foram #experimentos.contagens.ajustes_totais ajustes. O protocolo final conserva 252 resultados, correspondentes aos 250 ajustes dos perfis escolhidos, à árvore e à configuração escolhida de DBSCAN.

== Grade de hiperparâmetros
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Parâmetros variados no experimento], tabela-dados(
  ("Método", "Variação"),
  (
    ("K-Means", [Inicialização `random` e `k-means++`]),
    ("FCM", [$m$: 1,5, 2 e 2,5]),
    ("Kernel FCM", [RBF com $m$ de 1,5, 2 e 2,5, cruzado com $gamma$ de 0,05, 0,25 e 1]),
    ("K-Medoids", [PAM euclidiano com inicialização `random` e `build`]),
    ("GMM/EM", [Covariância `full`, `tied`, `diag` e `spherical`, cruzada com regularização de $10^(-6)$, $10^(-4)$ e $10^(-2)$]),
    ("UPGMA", [Cortes $k$ de 1 a 5 na mesma árvore]),
    ("DBSCAN", [Raios $epsilon$ fixos (0,4, 0,6, 0,8 e 1,0) e relativos (fatores de 0,75, 1, 1,5 e 2), cruzados com `min_samples` de 3, 5 e 10]),
  ),
  columns: (25%, 75%),
))

Nos métodos fuzzy, o objetivo pondera a distância quadrática pela pertinência elevada ao $m$ de cada configuração. No Kernel FCM, a distância quadrática induzida pelo RBF é $2 (1 - exp(-gamma norm(x - v)^2))$, em que $v$ é o protótipo no espaço de entrada [7]. O objetivo serve para escolher a semente dentro da configuração e do $k$.

Os experimentos usam Python e as bibliotecas scikit-learn, SciPy, fuzzy-c-means, kmedoids e umap-learn. O ponto de entrada é `codigo/main.py`. Sementes, parâmetros, versões, métricas e partições estão em `resultados/`. As grades e figuras de sensibilidade estão em `resultados/tunagem/`.

== Métricas
A silhueta euclidiana foi calculada no espaço dos quatro atributos padronizados. Para cada observação $i$,
$ s(i) = (b(i)-a(i))/max(a(i),b(i)), $
em que $a(i)$ é a distância média no próprio grupo e $b(i)$ é a menor distância média a outro grupo [12]. A métrica é indefinida em $k=1$ e em partições degeneradas. Nos cortes do UPGMA, a métrica de avaliação euclidiana é distinta da distância Manhattan usada nas fusões.

O ARI compara a partição estimada com as espécies, descontando a concordância esperada ao acaso [13]. As métricas usam as implementações do scikit-learn [18]. O ARI foi calculado após a seleção e usado para comentar as alternativas da grade. Para o DBSCAN, ambas as métricas excluem as observações de rótulo −1, aplicando a mesma máscara às espécies no ARI. A cobertura é a fração de observações mantidas após aplicar essa máscara.

= Resultados de agrupamento
== Partições selecionadas
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Resultados dos sete métodos. Para o DBSCAN, $k$ é o número de grupos encontrados e $n$ é o número de flores avaliadas.], tabela-dados(
  ("Método", "Parâmetros", "k", "Sil.", "ARI", "n"),
  experimentos.resumo,
  columns: (19%, 40%, 6%, 13%, 13%, 9%),
))

#if experimentos.particao_comum and experimentos.estrutura_setosa [
  Os seis métodos com escolha de $k$ chegaram à mesma partição de dois grupos. Um reúne as 50 setosas, o outro reúne as 50 versicolors e as 50 virginicas. A concordância das partições explica as silhuetas e os ARIs iguais na base completa.
]
O DBSCAN reteve #db.n observações e marcou #db.ruido como ruído. Sua silhueta e seu ARI descrevem apenas as flores atribuídas a grupos. Para controlar a diferença de cobertura na comparação, também foram reavaliadas as outras partições selecionadas nas mesmas #db.n flores.

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Comparação sobre a amostra retida pelo DBSCAN. A última coluna mede a concordância direta com a partição do DBSCAN.], tabela-dados(
  ("Método", "Silhueta", "ARI com espécies", "ARI com DBSCAN"),
  experimentos.mesma_amostra,
))

#if experimentos.amostra_igual [
  Na amostra comum, os sete métodos concordaram integralmente, salvo os identificadores dos grupos. As diferenças numéricas na base completa acompanham a mudança de amostra.
] else [
  Na amostra comum, valores de ARI entre partições abaixo de 1 indicam diferenças nas atribuições de grupos que persistem mesmo após igualar a cobertura.
]

== Silhueta e ARI por número de grupos
#figure(image("figuras/ieee/silhuetas_comparadas.pdf", width: 100%), caption: [Silhueta dos perfis selecionados para cada $k$. Em $k=1$, a silhueta é indefinida.])

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Silhueta e ARI, nessa ordem, para cada corte ou melhor execução dos perfis selecionados.], tabela-dados(
  ("Método", "k = 2", "k = 3", "k = 4", "k = 5"),
  experimentos.por_k,
  columns: (20%, 20%, 20%, 20%, 20%),
))

Em $k=3$, o maior ARI entre os perfis selecionados foi #experimentos.maior_ari_k3.ari, obtido por #experimentos.maior_ari_k3.nome. O GMM alcançou silhueta de #experimentos.em_k3.silhueta e ARI de #experimentos.em_k3.ari com três componentes. Comparar as duas métricas ajuda a identificar partições geometricamente favorecidas e partições que recuperam melhor a distinção entre as espécies.

== Sensibilidade dos métodos particionais
A tabela de sensibilidade examina as configurações em $k=3$, mantendo fixo o número de grupos. As curvas completas para $k$ de 2 a 5 e os mapas das configurações cruzadas encontram-se em `resultados/tunagem/figuras/`. Cada célula descreve a execução de melhor objetivo da respectiva configuração.

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Perfis com menor e maior silhueta válida em $k=3$ e intervalo de ARI entre os perfis.], tabela-dados(
  ("Método", "Menor Sil.", "Maior Sil.", "Faixa de ARI"),
  experimentos.sensibilidade_k3,
  columns: (19%, 27%, 27%, 27%),
))

Em $k=3$, `k-means++` elevou ligeiramente a silhueta e o ARI em relação à inicialização aleatória. No PAM, `build` elevou a silhueta e reduziu o ARI. As configurações fuzzy produziram silhuetas próximas entre si, mesmo com diferenças de ARI. O GMM apresentou a maior faixa de variação das duas métricas, compatível com a flexibilidade de formas e orientações admitidas para os componentes em cada configuração. Os cinco métodos particionais retiveram a configuração de referência após os empates na maior silhueta em $k=2$.

== Cobertura no DBSCAN
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Configuração selecionada, referência e maior silhueta observada na grade do DBSCAN. As duas métricas usam os pontos retidos de cada configuração.], tabela-dados(
  ("Perfil", [$epsilon$], "Mín.", "Gr.", "Cob. %", "Sil.", "ARI"),
  experimentos.dbscan.tabela,
  columns: (20%, 14%, 9%, 9%, 16%, 16%, 16%),
))

Um raio que retém poucas flores pode produzir silhueta elevada ao remover pontos de regiões de transição. A escolha por silhueta com cobertura mínima mantém a avaliação próxima do conjunto original. Os mapas completos apresentam como o raio e a densidade mínima afetam o número de grupos, as duas métricas e a cobertura.

== Hierarquia e dendrograma
#figure(image("figuras/ieee/dendrograma_upgma.pdf", width: 100%), caption: [Árvore UPGMA com distância Manhattan e ligação média, truncada em 12 subárvores. Os cortes indicados produzem dois e três grupos.])

No dendrograma, a altura de fusão corresponde à distância média entre as observações dos grupos. O corte em dois grupos separa #emph[I. setosa] das demais espécies. Nos cortes de dois a cinco grupos, as silhuetas Manhattan foram 0,6192, 0,5024, 0,4084 e 0,3770. A distância euclidiana usada na avaliação principal e a Manhattan favorecem o corte em dois grupos.

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
O estudo descreve uma única base com atributos padronizados. As dez sementes examinam a influência da inicialização para as mesmas flores. As grades delimitam as configurações comparadas. A interpretação do DBSCAN depende da cobertura mínima e da comparação na amostra comum. Cada projeção foi ajustada uma vez, com uma configuração registrada. As distâncias entre regiões e as densidades podem mudar na projeção.

= Conclusão
A comparação separa a coesão geométrica, medida pela silhueta, da concordância com as espécies, medida pelo ARI. Em três grupos, #experimentos.maior_ari_k3.nome alcançou o maior ARI entre os perfis selecionados (#experimentos.maior_ari_k3.ari). Para o DBSCAN, a cobertura de #db.cobertura% especifica a amostra a que se referem as duas métricas.

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
