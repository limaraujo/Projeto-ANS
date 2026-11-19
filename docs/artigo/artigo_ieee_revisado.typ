// Artigo acadêmico em estilo IEEE conference (A4), implementado em Typst.
// Compilar a partir da raiz: typst compile docs/artigo/artigo_ieee_revisado.typ docs/artigo/artigo_ieee_revisado.pdf --root docs/artigo
#set document(title: "Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa", author: ("Fátima Araújo", "Rodrigo Gomes"))
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
#let etapas = json("resumo_etapas.json")
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
    #text(size: 11pt)[Rodrigo Gomes] \
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
#text(size: 9pt, weight: "bold")[Resumo—Este artigo compara sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris padronizada. Na tunagem, os hiperparâmetros dos métodos particionais foram escolhidos pela média das silhuetas para $k$ de 2 a 5, sem selecionar um $k$ final. Com esses perfis fixados, o experimento usou dez chamadas por $k$, com novas sementes, e a silhueta favoreceu dois grupos nos cinco métodos particionais e no UPGMA. O índice de Rand ajustado (ARI) mediu a concordância com as espécies. O DBSCAN encontrou #db.grupos grupos, com #db.cobertura% de cobertura, silhueta de #db.silhueta e ARI de #db.ari sobre #db.n observações. Em três grupos, #experimentos.maior_ari_k3.nome alcançou ARI de #experimentos.maior_ari_k3.ari. As duas primeiras componentes da PCA retiveram 95,80% da variância. O t-SNE obteve o maior #emph[trustworthiness] com dez vizinhos (0,9888).]

#text(size: 9pt, weight: "bold", style: "italic")[Palavras-chave—agrupamento, Iris, silhueta, índice de Rand ajustado, redução de dimensionalidade.]
]
= Introdução
A análise não supervisionada pode revelar estruturas geométricas que não coincidem com classes conhecidas. Este artigo investiga quais partições da base Iris são favorecidas pela silhueta, como elas se relacionam com as três espécies e quais estruturas aparecem nas projeções bidimensionais. São comparados sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade, seguindo o protocolo da Equipe 08 [1].

As projeções incluem PCA, Kernel PCA, t-SNE e UMAP. Após os ajustes, os rótulos das espécies apoiam a interpretação visual e a avaliação externa dos agrupamentos.

= Base de dados e preparação
O estudo utilizou a base Iris fornecida na atividade, com 150 observações e quatro atributos em centímetros: comprimento e largura da sépala e da pétala. Cada uma das três espécies (#emph[Iris setosa], #emph[Iris versicolor] e #emph[Iris virginica]) tem 50 observações. Os modelos receberam apenas os quatro atributos numéricos.

Para evitar que diferenças de variância atribuíssem pesos distintos aos atributos no cálculo das distâncias, aplicou-se a padronização z-score com o StandardScaler [2]:
$ z_(i r) = (x_(i r)-mu_r)/sigma_r, $
$ mu_r = 1/n sum_(i=1)^n x_(i r), quad
sigma_r = sqrt(1/n sum_(i=1)^n (x_(i r)-mu_r)^2), $
em que $n=150$, $mu_r$ é a média do atributo e $sigma_r$ é seu desvio-padrão populacional. A @estatisticas-iris apresenta os valores calculados.

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

#block(breakable: false)[
A avaliação combina critérios internos e externos. A silhueta mede a coesão e a separação dos grupos [12]. O índice de Rand ajustado (ARI) mede a concordância entre a partição estimada e as espécies, corrigida pela concordância esperada ao acaso [13]:
$ "ARI" = (A-B C/N)/(1/2 (B+C)-B C/N), $
em que $A=sum_(i,j) binom(n_(i j),2)$, $B=sum_i binom(a_i,2)$, $C=sum_j binom(b_j,2)$ e $N=binom(n,2)$. Os termos $n_(i j)$ são as frequências conjuntas das duas partições, e $a_i$ e $b_j$ são seus totais marginais. Uma partição com boa silhueta pode apresentar ARI limitado.
]

As técnicas de redução de dimensionalidade representam diferentes aspectos da estrutura dos dados. A PCA identifica direções ortogonais que maximizam sucessivamente a variância projetada, formando componentes lineares dos atributos [14]. A Kernel PCA realiza uma decomposição espectral da matriz de kernel centralizada, estendendo a análise a relações não lineares dependentes do kernel escolhido [15].

O t-SNE ajusta uma representação de baixa dimensão pela minimização da divergência KL entre as distribuições de afinidade no espaço original e no espaço projetado. A perplexidade controla a escala de vizinhança considerada, e a inicialização influencia a otimização [16]. O UMAP constrói uma representação das relações de vizinhança e otimiza sua disposição em baixa dimensão. O número de vizinhos controla a escala local, enquanto min_dist influencia a compactação da representação [17]. A interpretação dessas projeções deve considerar possíveis distorções de distâncias globais e densidades.

A silhueta euclidiana foi calculada no espaço dos quatro atributos padronizados. Para cada observação $i$,
$ s(i) = (b(i)-a(i))/max(a(i),b(i)), $
em que $a(i)$ é a distância média no próprio grupo e $b(i)$ é a menor distância média a outro grupo [12]. A métrica é indefinida em $k=1$ e em partições degeneradas. Nos cortes do UPGMA, a métrica de avaliação euclidiana é distinta da distância Manhattan usada nas fusões.

As métricas usam as implementações do scikit-learn [18]. O ARI foi calculado após a seleção e usado para comentar as alternativas da grade. Para o DBSCAN, ambas as métricas excluem as observações de rótulo −1, aplicando a mesma máscara às espécies no ARI. A cobertura é a fração de observações mantidas após aplicar essa máscara.


= Metodologia e rodada piloto de hiperparâmetros
== Protocolo em duas etapas
O protocolo separou a escolha dos hiperparâmetros da escolha final do número de grupos:
+ *Rodada piloto ou tunagem (sementes 42 a 51):* comparou-se a grade dos cinco métodos particionais em $k in {2,3,4,5}$, escolhendo um único perfil de hiperparâmetros por método pela média das quatro silhuetas. Para o DBSCAN, foram avaliados 24 pares de parâmetros com cobertura mínima de 95%.
+ *Rodada final (sementes 52 a 61):* os perfis escolhidos foram fixados, e cada método particional recebeu dez chamadas para cada $k in {1,2,3,4,5}$. A melhor execução por objetivo de cada $k$ foi avaliada pela silhueta para selecionar $k^*$. Também foram avaliados os cortes de uma árvore UPGMA e um ajuste DBSCAN.

As duas etapas usaram a mesma matriz padronizada das 150 flores, sem empregar os rótulos das espécies na seleção. A troca das sementes examina novas inicializações sobre essa base, sem constituir uma avaliação em dados novos. As quatro projeções usaram configurações fixas, sem tunagem.

== Critérios de seleção na rodada piloto
Em cada par de configuração $c$ e número de grupos $k$, foram feitas dez chamadas. Escolheu-se a de menor objetivo no K-Means, FCM, Kernel FCM e K-Medoids, ou de maior log-verossimilhança total no GMM. Empates seguiram a ordem crescente das sementes. Os objetivos comparam execuções do mesmo método, configuração e $k$; não são diretamente comparados entre métodos.

No FCM e no Kernel FCM, a atribuição exclusiva correspondeu à maior pertinência; no GMM, à maior probabilidade posterior. Nos métodos fuzzy, o objetivo pondera as distâncias quadráticas pelas pertinências elevadas a $m$. No Kernel FCM, a distância quadrática induzida pelo RBF é $2 (1-exp(-gamma norm(x-v)^2))$, com protótipo $v$ no espaço de entrada [7].

Se $S(c,k)$ é a silhueta da execução escolhida por objetivo, o perfil de cada método particional foi selecionado pela maior média
$ S_("piloto") (c) = (S(c,2)+S(c,3)+S(c,4)+S(c,5))/4. $
Só concorreram perfis com quatro silhuetas definidas. A comparação usou valores sem arredondamento; empates favoreceram o perfil de referência e depois a ordem da grade. As referências foram K-Means `random`, FCM com $m=2$, Kernel FCM com $m=2$ e $gamma=0,25$, PAM `random` e GMM `full` com regularização $10^(-6)$.

*Papel de k na tunagem:* os valores de 2 a 5 receberam o mesmo peso na média para escolher os demais hiperparâmetros. Não se selecionou um $k^*$ nesta etapa, nem um perfil diferente para cada $k$. O caso $k=1$ ficou fora da média por ter silhueta indefinida. As sementes identificaram as dez execuções candidatas; não foram hiperparâmetros da grade.

No DBSCAN, os raios relativos foram obtidos multiplicando a mediana da distância ao quinto vizinho (0,462862, contando o próprio ponto) pelos fatores da grade. Entre os pares com silhueta definida e cobertura mínima de 95%, venceu o de maior silhueta sem ruído; empates favoreceram maior cobertura e a ordem da grade. O perfil de referência foi $epsilon=0,8$ com `min_samples=5`. *O DBSCAN não recebe k:* o número de grupos resulta de cada par de parâmetros, excluindo o ruído.

== Grade explorada e hiperparâmetros fixados
A @grade-piloto reúne a busca e suas escolhas. No UPGMA, a distância Manhattan e a ligação média foram fixadas pelo enunciado; a árvore foi construída somente na rodada final. A tunagem somou 1.120 ajustes particionais (28 perfis × 4 valores de $k$ × 10 sementes) e 24 ajustes DBSCAN, totalizando 1.144 ajustes.

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Grade piloto (sementes 42–51) e perfis fixados para a rodada final. As médias de silhueta dos métodos particionais usam $k=2$ a $5$.], tabela-dados(
  ("Método", "Grade explorada", "Perfil escolhido"),
  (
    ([K-Means], [`init`: `random`, `k-means++` (2 perfis)], [`k-means++` #linebreak() Média: 0,4443]),
    ([FCM], [$m$: 1,5; 2; 2,5 (3 perfis)], [$m=2$ #linebreak() Média: 0,4431]),
    ([Kernel FCM], [$m$: 1,5; 2; 2,5 × $gamma$: 0,05; 0,25; 1 (9 perfis)], [$m=2$; $gamma=0,05$ #linebreak() Média: 0,4419]),
    ([K-Medoids], [PAM euclidiano: `random`, `build` (2 perfis)], [`build` #linebreak() Média: 0,4514]),
    ([GMM/EM], [`full`, `tied`, `diag`, `spherical` × reg.: $10^(-6)$; $10^(-4)$; $10^(-2)$ (12 perfis)], [`spherical`; reg. $10^(-2)$ #linebreak() Média: 0,4503]),
    ([UPGMA], [Sem tunagem: Manhattan e ligação média fixadas], [Uma árvore na rodada final; cortes $k=1$ a $5$]),
    ([DBSCAN], [$epsilon$: 0,4; 0,6; 0,8; 1 ou mediana × 0,75; 1; 1,5; 2, cruzados com `min_samples`: 3; 5; 10 (24 pares)], [$epsilon=0,694293$; mínimo 3 #linebreak() Sil.: 0,6035; cob.: 96%]),
  ),
  columns: (20%, 47%, 33%),
)) <grade-piloto>

K-Means, FCM, Kernel FCM e GMM usaram `n_init=1`, com as dez chamadas controladas pelo protocolo externo. FCM e Kernel FCM tiveram limite de 300 iterações e tolerância de $10^(-5)$; o PAM teve limite de 300 iterações para $k>1$. O GMM usou `init_params="random_from_data"` e tolerância de $10^(-5)$.

Os experimentos foram conduzidos em Python com as bibliotecas scikit-learn, SciPy, fuzzy-c-means, kmedoids e umap-learn.

== Comportamento paramétrico na rodada piloto
As figuras a seguir resumem a sensibilidade na grade piloto. As médias usam a melhor execução por objetivo em cada $k$; os ARIs são descritivos e não participaram das escolhas.

#figure(image("figuras/ieee/tunagem_k_means.pdf", width: 100%), caption: [K-Means na rodada piloto: silhueta média para $k=2$ a $5$ e ARI em $k=3$, por inicialização.])
#figure(image("figuras/ieee/tunagem_fuzzy_k_means.pdf", width: 100%), caption: [FCM na rodada piloto: efeito do expoente $m$ na silhueta média e no ARI em $k=3$.])
#figure(image("figuras/ieee/tunagem_kernel_fuzzy_k_means.pdf", width: 100%), caption: [Kernel FCM na rodada piloto: silhueta média por $(m,gamma)$ e efeito de $gamma$ com $m=2$ para cada $k$.])
#figure(image("figuras/ieee/tunagem_k_medoids.pdf", width: 100%), caption: [K-Medoids na rodada piloto: comparação das inicializações `random` e `build`.])
#figure(image("figuras/ieee/tunagem_gaussian_mixture.pdf", width: 100%), caption: [GMM na rodada piloto: efeito da covariância e da regularização na silhueta média e no ARI em $k=3$.])
#figure(image("figuras/ieee/tunagem_dbscan.pdf", width: 100%), caption: [DBSCAN na rodada piloto: silhueta, ARI e cobertura em função do raio e de `min_samples`. Círculos vermelhos destacam o par escolhido; a linha tracejada indica cobertura de 95%.])

A análise da grade mostra os seguintes comportamentos:
- *K-Means e K-Medoids:* a silhueta média favoreceu `k-means++` no primeiro e `build` no segundo. No recorte em $k=3$, K-Means `random` e `k-means++` tiveram ARIs de 0,6101 e 0,6201. No PAM, `build` elevou a silhueta de 0,4497 para 0,4555, mas reduziu o ARI de 0,6765 para 0,6416. A melhora no critério interno não implica melhora no externo.
- *FCM e Kernel FCM:* ambos selecionaram $m=2$. No Kernel FCM, a configuração com $gamma=0,05$ obteve média de 0,4419, ante 0,4401 com $gamma=0,25$ e o mesmo $m$. Em $k=4$ e $m=2$, aumentar $gamma$ de 0,05 para 0,25 e 1 reduziu a silhueta de 0,3985 para 0,3941 e 0,3872.
- *GMM/EM:* a média das silhuetas favoreceu covariância esférica e regularização de 0,01. Na grade piloto em $k=3$, covariância completa com a mesma regularização alcançou ARI de 0,9222, com silhueta de 0,3685, enquanto a esférica obteve ARI de 0,6199 e silhueta de 0,4568. Essa alternativa com maior ARI não definiu o perfil final, pois o critério de seleção foi a silhueta média.
- *DBSCAN:* a maior silhueta bruta foi 0,6482, com $epsilon=0,6$ e `min_samples=10`, mas a cobertura de 76,67% tornou o par inelegível. No raio selecionado, subir o mínimo de 3 para 5 elevou a silhueta de 0,6035 para 0,6104 e reduziu a cobertura de 96% para 94,67%, abaixo do piso. A referência $epsilon=0,8$ e mínimo 5 reteve 97,33%, com silhueta de 0,5963.

= Experimento final e resultados de agrupamento (Questão 1)
== Execução com hiperparâmetros fixados
Os perfis escolhidos na tunagem foram mantidos para todos os valores de $k$. Para cada um dos cinco métodos particionais, fizeram-se dez novas chamadas para cada $k in {1,2,3,4,5}$, com sementes 52 a 61. Para cada $k$, a melhor execução foi novamente selecionada pela função objetivo do método, sem reutilizar a execução vencedora da tunagem. Assim, as métricas do experimento final podem diferir das métricas da tunagem, mesmo quando o perfil e o número de grupos são iguais.

No PAM com inicialização `build`, as chamadas podem repetir a mesma solução apesar da troca da semente. Em $k=1$, o K-Medoids repete a busca exaustiva pelo único medoide. As contagens representam chamadas de ajuste, não necessariamente soluções distintas.

O UPGMA construiu uma única árvore com distância Manhattan e ligação média, da qual foram extraídos os cinco cortes de um a cinco grupos. O DBSCAN foi executado uma vez com o par escolhido na tunagem. O experimento final somou 252 ajustes: 250 particionais, uma árvore UPGMA e um DBSCAN. Somadas as duas etapas, foram #experimentos.contagens.ajustes_totais ajustes de agrupamento; os cortes da mesma árvore não foram contados como novos ajustes.

== Escolha final do número de grupos
Nos cinco métodos particionais, calculou-se a silhueta da melhor execução por objetivo de cada $k$. No UPGMA, calculou-se a silhueta de cada corte. Em ambos os casos, a escolha final foi
$ k^* = arg max_(k in K_"válido") S_"final"(k), $
em que $K_"válido"$ reúne os valores de $k in {2,3,4,5}$ com silhueta definida e $S_"final"(k)$ é a silhueta euclidiana da partição no experimento final. Empates favoreceram o menor $k$. O caso $k=1$ foi executado e registrado, mas não concorreu à seleção por silhueta. O conhecimento de que existem três espécies não foi usado para impor $k=3$.

No DBSCAN, não houve nova escolha de $k$ nem nova busca de parâmetros no experimento final: o número de grupos foi determinado pelo ajuste com o par fixado na tunagem. O ARI foi usado para avaliar a concordância com as espécies depois das seleções; ele não escolheu a execução, os hiperparâmetros ou o número de grupos.

== Partições selecionadas
#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Resultados do experimento final com os hiperparâmetros fixados pela tunagem. Para o DBSCAN, $k$ é o número de grupos encontrados e $n$ é o número de flores avaliadas.], tabela-dados(
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

== Silhueta e ARI por k no experimento final
#figure(image("figuras/ieee/silhuetas_comparadas.pdf", width: 100%), caption: [Silhueta no experimento final para cada $k$, com os perfis fixados pela tunagem. Em $k=1$, a silhueta é indefinida.])

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Silhueta e ARI, nessa ordem, no experimento final: cada corte do UPGMA ou melhor execução por objetivo dos métodos particionais.], tabela-dados(
  ("Método", "k = 2", "k = 3", "k = 4", "k = 5"),
  experimentos.por_k,
  columns: (20%, 20%, 20%, 20%, 20%),
))

Em $k=3$, o maior ARI entre os perfis selecionados foi #experimentos.maior_ari_k3.ari, obtido por #experimentos.maior_ari_k3.nome. O GMM alcançou silhueta de #experimentos.em_k3.silhueta e ARI de #experimentos.em_k3.ari com três componentes. Comparar as duas métricas ajuda a identificar partições geometricamente favorecidas e partições que recuperam melhor a distinção entre as espécies.

== Recuperação das espécies em k = 3
A @comparacao-k3 apresenta uma análise complementar com três grupos. Ela avalia a concordância com as espécies, mantendo os hiperparâmetros escolhidos na rodada piloto, sem substituir o $k^*=2$ selecionado pela silhueta. Os valores vêm exclusivamente da rodada final, com sementes 52 a 61.

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Comparação das partições com três grupos na rodada final, ordenada por ARI.], tabela-dados(
  ("Método", "Silhueta em k = 3", "ARI em k = 3"),
  etapas.k3,
)) <comparacao-k3>

O maior ARI entre esses perfis foi o do UPGMA, seguido pelo K-Medoids. O GMM esférico da rodada final difere da alternativa com covariância completa discutida na tunagem: os parâmetros foram fixados pelo critério interno, e não pelo ARI.

== Variação entre sementes na rodada final
A @objetivos-sementes apresenta o intervalo das funções objetivo nas dez chamadas de cada método em $k=3$. A comparação é interna a cada linha, pois os objetivos têm escalas e definições distintas. A última coluna identifica a execução selecionada pelo melhor objetivo, não pela maior silhueta.

#figure(kind: table, supplement: [TABELA], numbering: "I", caption: [Objetivos das dez chamadas com sementes 52–61 em $k=3$.], tabela-dados(
  ("Método", "Mínimo", "Máximo", "Semente escolhida"),
  etapas.objetivos_k3,
  columns: (27%, 24%, 24%, 25%),
)) <objetivos-sementes>

A proximidade de valores após arredondamento não demonstra um ótimo global. No PAM com `build`, a repetição decorre da estratégia de inicialização; as dez chamadas não representam necessariamente dez soluções distintas.

== Hierarquia e dendrograma
#figure(image("figuras/ieee/dendrograma_upgma.pdf", width: 100%), caption: [Árvore UPGMA com distância Manhattan e ligação média, truncada em 12 subárvores. Os cortes indicados produzem dois e três grupos.])

No UPGMA, a distância Manhattan e a ligação média são exigidas pelo enunciado. A comparação varia o número de grupos por meio dos cortes da mesma árvore. O corte em dois grupos separa #emph[I. setosa] das demais espécies. De dois a cinco grupos, as silhuetas Manhattan foram 0,6192, 0,5024, 0,4084 e 0,3770. A silhueta euclidiana da avaliação principal também favoreceu dois grupos.

= Redução de dimensionalidade
As quatro técnicas receberam a mesma matriz padronizada. Cada técnica foi executada uma vez. A PCA estimou quatro componentes e o gráfico mostra as duas primeiras. As demais técnicas foram ajustadas diretamente para duas dimensões. Cada projeção bidimensional representa as 150 observações, identificadas visualmente por espécie.

== PCA
As saídas de variância explicada, componentes e valores singulares seguem as definições do estimador PCA do scikit-learn [19].

A PCA utiliza decomposição em valores singulares (SVD) completa. Para a componente $j$, a variância e sua proporção explicada são
$ lambda_j = 1/(n-1) sum_(i=1)^n (z_(i j)-overline(z)_j)^2, quad
"VE"_j = lambda_j/(sum_(l=1)^p lambda_l), $
em que $z_(i j)$ é a projeção da observação $i$, $lambda_j$ é o autovalor correspondente e $p=4$. A @espectro-pca apresenta os resultados.
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
O estudo descreve uma única base com atributos padronizados. A separação entre as sementes da tunagem e do experimento examina novas inicializações sobre as mesmas flores, quando a inicialização depende da semente. Não há avaliação em observações novas. As grades delimitam as configurações comparadas, e a média das silhuetas na tunagem atribui o mesmo peso a $k$ de 2 a 5. A interpretação do DBSCAN depende da cobertura mínima e da comparação na amostra comum. Cada projeção foi ajustada uma vez, com uma configuração registrada. As distâncias entre regiões e as densidades podem mudar na projeção.

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
