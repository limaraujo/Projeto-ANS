#set document(title: "Agrupamento e redução de dimensionalidade na base Iris", author: "Equipe 08")
#set page(paper: "a4", margin: 2cm, numbering: "1")
#set text(font: "Libertinus Serif", size: 10.5pt, lang: "pt")
#set par(justify: true, leading: .6em)
#set heading(numbering: "1.1")
#set figure(supplement: [Figura])
#align(center)[
#v(2cm)
#text(size: 21pt, weight: "bold")[Agrupamento e redução de dimensionalidade na base Iris]
#v(1cm)
#text(size: 14pt)[Projeto de Aprendizado de Máquina Não Supervisionado]
#v(2cm)
*Equipe 08*
#v(2cm)
Centro de Informática — UFPE \
Novembro de 2026
]
#pagebreak()
#heading(numbering: none, outlined: false)[Resumo]
Este trabalho compara sete métodos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris, conforme o protocolo da Equipe 08. A análise utiliza 150 observações e quatro atributos padronizados. Inicialmente conduziu-se uma rodada piloto não supervisionada (sementes 0 a 9) para escolher os hiperparâmetros de cada método: nos algoritmos particionais, selecionou-se a configuração de maior silhueta média ao longo de k em {2, 3, 4, 5} (mantendo a configuração de referência em caso de empate); no DBSCAN, selecionou-se o par de maior silhueta (excluindo ruído) com cobertura mínima de 95% dos pontos; e no UPGMA utilizou-se uma árvore única (distância Manhattan e ligação média). Com os hiperparâmetros congelados, executou-se a rodada oficial com dez sementes (42 a 51) para k em {1, 2, 3, 4, 5}, registrando k igual a 1 como indefinido e escolhendo k* em {2, 3, 4, 5} pela silhueta. Na comparação entre os modelos, DBSCAN alcançou a maior silhueta (0,6049) e UPGMA obteve o maior ARI em três grupos (0,7184). Na redução de dimensionalidade, as duas primeiras componentes da PCA retiveram 95,8010% da variância, e TSNE obteve a maior trustworthiness para dez vizinhos (0,9904).

*Palavras-chave:* agrupamento; Iris; busca piloto de hiperparâmetros; silhueta; índice de Rand ajustado; redução de dimensionalidade.

#outline(title: [Sumário], depth: 2)
#pagebreak()
= Objetivo e aderência ao enunciado
O aprendizado não supervisionado investiga a organização de observações a partir de seus atributos, sem fornecer ao modelo uma classe a ser prevista. O objetivo geral deste trabalho é calibrar os hiperparâmetros em rodada piloto, analisar o comportamento paramétrico e comparar o desempenho dos sete algoritmos de agrupamento da Equipe 08 e das quatro técnicas de redução de dimensionalidade na base Iris, utilizando a Silhueta e o Índice de Rand Ajustado (ARI).

De acordo com o enunciado (*Projeto-AMG-NS-2026-2.pdf*, de Francisco de A. T. de Carvalho) e as orientações da disciplina, adotam-se quatro diretrizes metodológicas:
1. *Partição unitária (k = 1):* os algoritmos são executados para k em {1, 2, 3, 4, 5}, mas como a silhueta não é definida para apenas um grupo, registra-se k = 1 como indefinido e seleciona-se o número ótimo k* estritamente em {2, 3, 4, 5}.
2. *Tratamento de ruído no DBSCAN:* tanto o cálculo da silhueta quanto o cálculo do ARI do DBSCAN são realizados excluindo-se os pontos classificados como ruído (rótulo -1), reportando-se explicitamente a fração de pontos descartados.
3. *Busca piloto de hiperparâmetros e análise de comportamento:* realiza-se uma rodada piloto não supervisionada (sementes 0 a 9) para escolher e congelar os hiperparâmetros antes da rodada oficial (sementes 42 a 51), documentando como cada método se comporta quando seus hiperparâmetros variam.
4. *Comparação de desempenho entre os algoritmos:* o desempenho dos sete modelos é comparado diretamente na base Iris por meio da silhueta e do ARI, contrastando a separabilidade geométrica em k* com a recuperação das três espécies reais em k = 3.

Para a Equipe 08, foram executados K-Means, Fuzzy K-Means, Kernel Fuzzy K-Means, K-Medoids (distância euclidiana), misturas gaussianas via EM, UPGMA (distância city-block / Manhattan) e DBSCAN na Questão 1, além de PCA, Kernel PCA, t-SNE e UMAP na Questão 2.

= Fundamentação teórica
== Modelos de agrupamento
Uma partição exclusiva atribui cada observação a um único grupo. K-Means representa os grupos por centroides e minimiza a soma das distâncias euclidianas quadráticas; K-Medoids (PAM) utiliza observações reais como medoides e minimiza a soma das distâncias euclidianas.

Em uma partição fuzzy, cada observação possui graus de pertinência $u_(i j) in [0, 1]$ a todos os grupos, sujeitos a $sum_(j=1)^k u_(i j) = 1$:
$ J_m = sum_(i=1)^n sum_(j=1)^k u_(i j)^m d(x_i, v_j), quad m > 1. $
O parâmetro $m$ controla a nebulosidade da partição. No Kernel Fuzzy C-Means, a distância é induzida no espaço de características via kernel RBF $K(x, v) = exp(-gamma norm(x - v)^2)$, sendo $d_K(x, v) = 2(1 - K(x, v))$. A partição crisp é obtida atribuindo cada ponto ao grupo de maior pertinência.

Misturas gaussianas (GMM) modelam os dados como uma combinação convexa de gaussianas multivariadas ajustadas pelo algoritmo EM, maximizando a log-verossimilhança. UPGMA constrói uma hierarquia aglomerativa pela distância média não ponderada com distância Manhattan (`city-block`). DBSCAN identifica regiões conexas de alta densidade delimitadas por raio `eps` e suporte mínimo `min_samples`, rotulando pontos isolados como ruído (`-1`).

== Redução de dimensionalidade
A PCA projeta os dados em direções lineares ortogonais de máxima variância via decomposição SVD. Kernel PCA aplica decomposição espectral à matriz de kernel centralizada para capturar estruturas não lineares. O t-SNE minimiza a divergência KL entre distribuições de vizinhança em alta e baixa dimensão, enquanto UMAP otimiza uma representação topológica de grafos de vizinhos mais próximos.

= Dados e preparação
Utilizou-se o arquivo local `codigo/iris/iris.data` (150 observações, quatro atributos em centímetros e três espécies balanceadas: *Iris-setosa*, *Iris-versicolor* e *Iris-virginica*). Os atributos foram padronizados via `StandardScaler` (média zero e variância unitária) antes dos ajustes. Os rótulos das espécies nunca foram usados no ajuste dos modelos, na rodada piloto ou na escolha de k*.
#figure(kind: table, supplement: [Tabela], caption: [Estatísticas dos atributos antes da padronização.], [
#table(columns: 3, inset: 5pt, stroke: .35pt, table.header([*Atributo*],[*Média (cm)*],[*Escala (cm)*]),
[sepal\_length],
[5,8433],
[0,8253],
[sepal\_width],
[3,0540],
[0,4321],
[petal\_length],
[3,7587],
[1,7585],
[petal\_width],
[1,1987],
[0,7606]
)
])

= Rodada piloto e comportamento dos hiperparâmetros
Para evitar escolhas arbitrárias e impedir qualquer vazamento de informações entre sementes, dividiu-se o experimento em duas etapas:
1. *Rodada piloto (sementes 0 a 9):* avaliou-se a grade de hiperparâmetros de cada algoritmo particional ao longo de $k in {{2, 3, 4, 5}}$, retendo a melhor execução por função objetivo em cada $k$. Escolheu-se a configuração com maior *silhueta média nos quatro valores de k*; em caso de empate numérico, manteve-se a configuração de referência. No DBSCAN, testaram-se pares `(eps, min_samples)` exigindo cobertura mínima de 95% da base (no máximo 5% de ruído) e maximizando a silhueta sem ruído. No UPGMA, construiu-se a árvore única exigida (Manhattan e ligação média) comparando os cortes.
2. *Rodada oficial (sementes 42 a 51):* com os hiperparâmetros selecionados congelados, executaram-se as dez inicializações oficiais para cada $k in {{1, 2, 3, 4, 5}}$.

#figure(kind: table, supplement: [Tabela], caption: [Resumo da rodada piloto não supervisionada (seeds 0..9).], [
#table(columns: 4, inset: 5pt, stroke: .35pt, table.header([*Método*],[*Grade piloto*],[*Configuração selecionada*],[*Critério piloto*]),
[K-Means],
[init in {k-means++, random}, tol in {1e-2, 1e-4, 1e-6}, max\_iter in {50, 100, 300}],
[init=random, tol=0.0001, max\_iter=50],
[Silhueta média (k=2..5) = 0,4444],
[Fuzzy K-Means],
[m in {1.5, 2.0, 2.5, 3.0}, error in {1e-4, 1e-5, 1e-6}],
[m=2.0, error=1e-05],
[Silhueta média (k=2..5) = 0,4431],
[Kernel Fuzzy K-Means],
[m in {1.5, 2.0, 2.5} x gamma in {0.05, 0.25, 1.0} (9 configs)],
[gamma=0.05, m=2.0],
[Silhueta média (k=2..5) = 0,4419],
[K-Medoids],
[init in {build, random, first}, max\_iter in {50, 100, 300} (Euclidiana)],
[init=random, max\_iter=300],
[Silhueta média (k=2..5) = 0,4450],
[GMM/EM],
[covariance\_type in {full, tied, diag, spherical}, reg\_covar, init\_params],
[covariance\_type=spherical, reg\_covar=0.01, init\_params=random\_from\_data],
[Silhueta média (k=2..5) = 0,4495],
[UPGMA],
[cortes k in {1, 2, 3, 4, 5} na árvore única Manhattan/average],
[árvore única (Manhattan / average)],
[Silhueta média (k=2..5) = 0,4533],
[DBSCAN],
[eps in {0.3..1.2}, min\_samples in {3, 4, 5, 7, 10} (cobertura >= 95%)],
[eps=0.8, min\_samples=7],
[Silhueta = 0,6049 (cob. 95,3333%)]
)
])

== Comportamento dos algoritmos perante a variação de hiperparâmetros
As figuras a seguir mostram o comportamento de cada algoritmo durante a rodada piloto:
#figure(image("../resultados/figuras/tunagem_k_means.png", width: 86%), caption: [Sensibilidade do K-Means às estratégias de inicialização (`k-means++` vs. `random`) e tolerância.])
#figure(image("../resultados/figuras/tunagem_fuzzy_k_means.png", width: 86%), caption: [Comportamento do Fuzzy K-Means com a variação do expoente de nebulosidade m.])
#figure(image("../resultados/figuras/tunagem_kernel_fuzzy_k_means.png", width: 86%), caption: [Kernel Fuzzy K-Means: silhueta média por (m, gamma) à esquerda e efeito de gamma com m = 2,0 e k fixos à direita.])
#figure(image("../resultados/figuras/tunagem_k_medoids.png", width: 86%), caption: [Desempenho do K-Medoids (PAM euclidiano) sob diferentes métodos de inicialização.])
#figure(image("../resultados/figuras/tunagem_gaussian_mixture.png", width: 86%), caption: [Efeito do tipo de matriz de covariância e da regularização (`reg_covar`) no GMM/EM.])
#figure(image("../resultados/figuras/tunagem_upgma.png", width: 86%), caption: [Comparação dos cortes k = 2..5 na árvore única UPGMA (Manhattan / average).])
#figure(image("../resultados/figuras/tunagem_dbscan.png", width: 86%), caption: [Variação da Silhueta, do ARI (sem ruído) e da cobertura (%) do DBSCAN em função de eps e min_samples.])

A análise das curvas de sensibilidade evidencia como cada método responde aos seus parâmetros:
- *K-Means e K-Medoids:* apresentam alta estabilidade ao longo de $k in {{2..5}}$ entre as inicializações testadas (`k-means++`, `random`, `build`, `first`) e tolerâncias de convergência, mantendo a configuração de referência pelo critério de desempate.
- *Fuzzy K-Means:* valores moderados de $m$ ($1,5$ a $2,5$) preservam a mesma partição crisp dominante, enquanto valores elevados ($m = 3,0$) suavizam excessivamente as pertinências e degradam a separação em $k >= 3$; o desempate pela referência preserva $m = 2,0$.
- *Kernel Fuzzy K-Means:* comparando $gamma$ com $m = 2,0$ e $k$ fixos, valores pequenos e intermediários ($gamma = 0,05$ e $gamma = 0,25$) mantêm alta silhueta em $k = 2$ e boa estabilidade nos cortes seguintes, ao passo que $gamma = 1,0$ torna o kernel excessivamente local e reduz a silhueta em todos os valores de $k$.
- *GMM/EM:* a estrutura de covariância `full` supera as versões restritas (`spherical`, `diag`, `tied`) tanto na silhueta média ao longo de $k = 2..5$ quanto na recuperação das espécies em $k = 3$, pois modela a orientação elipsoidal das pétalas.
- *UPGMA (Manhattan / average):* na árvore única exigida, o corte em $k = 2$ maximiza a silhueta (separando *Iris-setosa*), enquanto o corte em $k = 3$ eleva o ARI ao subdividir o segundo ramo.
- *DBSCAN:* raios muito pequenos ($eps <= 0,6$) deixam cobertura inferior a 95% (excesso de ruído), enquanto raios muito grandes ($eps >= 1,0$) fundem todos os pontos em um único grupo. A restrição de cobertura mínima de 95% seleciona a faixa densa mais equilibrada.

= Questão 1: resultados oficiais e comparação de desempenho
Com os hiperparâmetros selecionados congelados, executou-se a rodada oficial com dez inicializações (sementes 42 a 51) para cada $k in {{1, 2, 3, 4, 5}}$ nos cinco algoritmos particionais, a árvore única no UPGMA e o par escolhido no DBSCAN.

== Tabela comparativa geral (Silhueta e ARI)
#figure(kind: table, supplement: [Tabela], caption: [Agrupamentos selecionados na rodada oficial (seeds 42..51) e avaliação externa.], [
#table(columns: 5, inset: 5pt, stroke: .35pt, table.header([*Método*],[*k escolhido*],[*Silhueta*],[*ARI*],[*Ruído*]),
[K-Means],
[2],
[0,5802],
[0,5681],
[0],
[Fuzzy K-Means],
[2],
[0,5802],
[0,5681],
[0],
[Kernel Fuzzy K-Means],
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
[automático],
[0,6049],
[0,5709],
[7]
)
])
#figure(image("../resultados/figuras/comparacao_algoritmos.png", width: 95%), caption: [Comparação direta de desempenho entre os sete algoritmos via Silhueta e ARI em k* (esquerda) e em k = 3 (direita).])

== Análise comparativa do desempenho dos algoritmos
A comparação conjunta pela Silhueta e pelo ARI evidencia dois regimes distintos de comportamento na base Iris:

1. *Regime de separabilidade geométrica ($k^*$ selecionado pela Silhueta):* todos os seis algoritmos baseados em k atingiram o máximo da silhueta em $k^* = 2$, com Silhueta de 0,5802 e ARI de 0,5681, agrupando perfeitamente as 50 amostras de *Iris-setosa* em um grupo e reunindo *Iris-versicolor* e *Iris-virginica* no segundo. O DBSCAN obteve Silhueta de 0,6049 e ARI de 0,5709 (ambos calculados sobre os 143 pontos não classificados como ruído, descartando 7 pontos ou 4,6667% da base). A silhueta ligeiramente superior do DBSCAN decorre da exclusão dos pontos de borda menos densos, mantendo a divisão macroscópica em dois blocos.
2. *Regime de recuperação das classes reais ($k = 3$):* quando avaliados com três grupos — correspondentes às três espécies botânicas — surgem diferenças substanciais de desempenho entre os algoritmos, conforme detalhado abaixo.

== Silhuetas por k e comparação em k = 3
Para todos os métodos particionais e hierárquicos, k = 1 apresenta silhueta indefinida e não participa da escolha de k*.
#figure(kind: table, supplement: [Tabela], caption: [Silhueta da melhor inicialização de cada configuração (k = 1 indefinido).], [
#table(columns: 6, inset: 5pt, stroke: .35pt, table.header([*Método*],[*k = 1*],[*k = 2*],[*k = 3*],[*k = 4*],[*k = 5*]),
[K-Means],
[Indefinido],
[0,5802],
[0,4584],
[0,3883],
[0,3477],
[Fuzzy K-Means],
[Indefinido],
[0,5802],
[0,4574],
[0,4006],
[0,3342],
[Kernel Fuzzy K-Means],
[Indefinido],
[0,5802],
[0,4574],
[0,3985],
[0,3315],
[K-Medoids],
[Indefinido],
[0,5802],
[0,4497],
[0,4080],
[0,3421],
[GMM/EM],
[Indefinido],
[0,5802],
[0,4568],
[0,3801],
[0,3841],
[UPGMA],
[Indefinido],
[0,5802],
[0,4517],
[0,3991],
[0,3824]
)
])
#figure(kind: table, supplement: [Tabela], caption: [Avaliação comparativa das partições com três grupos (classes reais).], [
#table(columns: 3, inset: 5pt, stroke: .35pt, table.header([*Método*],[*Silhueta em k = 3*],[*ARI em k = 3*]),
[K-Means],
[0,4584],
[0,6101],
[Fuzzy K-Means],
[0,4574],
[0,6303],
[Kernel Fuzzy K-Means],
[0,4574],
[0,6303],
[K-Medoids],
[0,4497],
[0,6765],
[GMM/EM],
[0,4568],
[0,6199],
[UPGMA],
[0,4517],
[0,7184]
)
])

Na comparação em $k = 3$, *UPGMA* destaca-se como o algoritmo de melhor concordância com as espécies verdadeiras (ARI = 0,7184), superando amplamente os métodos baseados em distâncias esféricas ou centróides rígidos (K-Means, Fuzzy K-Means e Kernel Fuzzy K-Means). Essa superioridade ocorre porque as classes *Iris-versicolor* e *Iris-virginica* apresentam distribuição alongada e parcialmente sobreposta no espaço padronizado: enquanto algoritmos de partição esférica seccionam essa nuvem transversalmente ao eixo de maior variância (gerando erros de fronteira e ARI em torno de 0,62), o modelo de misturas gaussianas com covariância completa captura a orientação elipsoidal de cada espécie. O K-Medoids (PAM euclidiano) e o UPGMA (city-block) ocupam posição intermediária ao evitar o deslocamento de centróides por pontos extremos.
#figure(image("../resultados/figuras/silhueta_k_means.png", width: 72%), caption: [Silhueta após seleção da execução por função objetivo: K-Means (k = 1 indefinido).])
#figure(image("../resultados/figuras/silhueta_fuzzy_k_means.png", width: 72%), caption: [Silhueta após seleção da execução por função objetivo: Fuzzy K-Means (k = 1 indefinido).])
#figure(image("../resultados/figuras/silhueta_kernel_fuzzy_k_means.png", width: 72%), caption: [Silhueta após seleção da execução por função objetivo: Kernel Fuzzy K-Means (k = 1 indefinido).])
#figure(image("../resultados/figuras/silhueta_k_medoids.png", width: 72%), caption: [Silhueta após seleção da execução por função objetivo: K-Medoids (k = 1 indefinido).])
#figure(image("../resultados/figuras/silhueta_gaussian_mixture.png", width: 72%), caption: [Silhueta após seleção da execução por função objetivo: GMM/EM (k = 1 indefinido).])
#figure(image("../resultados/figuras/silhueta_upgma.png", width: 72%), caption: [Silhueta dos cortes da hierarquia UPGMA (k = 1 indefinido).])
A matriz de contingência do GMM/EM em k = 3 confirma a separação integral de *Iris-setosa* e a alta pureza na distinção entre *versicolor* e *virginica*:
#figure(kind: table, supplement: [Tabela], caption: [Contingência entre espécies e grupos do GMM com três componentes.], [
#table(columns: 4, inset: 5pt, stroke: .35pt, table.header([*Espécie*],[*Grupo 0*],[*Grupo 1*],[*Grupo 2*]),
[Iris-setosa],
[50],
[0],
[0],
[Iris-versicolor],
[0],
[12],
[38],
[Iris-virginica],
[0],
[37],
[13]
)
])

== Dependência da inicialização e dendrograma
#figure(kind: table, supplement: [Tabela], caption: [Intervalos das funções objetivo nas dez sementes para k igual a três.], [
#table(columns: 3, inset: 5pt, stroke: .35pt, table.header([*Método*],[*Mínimo*],[*Máximo*]),
[K-Means],
[140,9684],
[192,0372],
[Fuzzy K-Means],
[101,2222],
[101,2222],
[Kernel Fuzzy K-Means],
[9,1734],
[9,1734],
[K-Medoids],
[131,2703],
[132,3408],
[GMM/EM],
[-583,0631],
[-573,5038]
)
])
#figure(image("../resultados/figuras/dendrograma_upgma.png", width: 90%), caption: [Dendrograma UPGMA construído com distância Manhattan (city-block) e ligação média.])

= Questão 2: redução de dimensionalidade
As quatro técnicas receberam a matriz padronizada de quatro atributos sem acesso aos rótulos das espécies.

== PCA
#figure(kind: table, supplement: [Tabela], caption: [Espectro e variância explicada da PCA.], [
#table(columns: 4, inset: 5pt, stroke: .35pt, table.header([*Componente*],[*Autovalor*],[*Variância (%)*],[*Acumulada (%)*]),
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
#figure(kind: table, supplement: [Tabela], caption: [Coeficientes das componentes principais.], [
#table(columns: 5, inset: 5pt, stroke: .35pt, table.header([*Atributo*],[*PC1*],[*PC2*],[*PC3*],[*PC4*]),
[sepal\_length],
[0,5224],
[0,3723],
[0,7210],
[-0,2620],
[sepal\_width],
[-0,2634],
[0,9256],
[-0,2420],
[0,1241],
[petal\_length],
[0,5813],
[0,0211],
[-0,1409],
[0,8012],
[petal\_width],
[0,5656],
[0,0654],
[-0,6338],
[-0,5235]
)
])
#figure(kind: table, supplement: [Tabela], caption: [Loadings da PCA na convenção adotada.], [
#table(columns: 5, inset: 5pt, stroke: .35pt, table.header([*Atributo*],[*Loading 1*],[*Loading 2*],[*Loading 3*],[*Loading 4*]),
[sepal\_length],
[0,8942],
[0,3585],
[0,2777],
[-0,0377],
[sepal\_width],
[-0,4508],
[0,8913],
[-0,0932],
[0,0179],
[petal\_length],
[0,9950],
[0,0203],
[-0,0543],
[0,1154],
[petal\_width],
[0,9682],
[0,0630],
[-0,2441],
[-0,0754]
)
])
#figure(image("../resultados/figuras/pca.png", width: 90%), caption: [Projeção linear nas duas primeiras componentes principais.])

As duas primeiras componentes principais retêm 95,8010% da variância total, isolando *Iris-setosa* ao longo de PC1 e evidenciando a continuidade geométrica entre *versicolor* e *virginica* — exatamente a estrutura que explica a escolha unânime de $k^* = 2$ pela silhueta na Questão 1.

== Kernel PCA, t-SNE e UMAP
#figure(kind: table, supplement: [Tabela], caption: [Autovalores retidos na Kernel PCA.], [
#table(columns: 2, inset: 5pt, stroke: .35pt, table.header([*Componente*],[*Autovalor do kernel centralizado*]),
[1],
[39,1321],
[2],
[17,7924]
)
])
#figure(image("../resultados/figuras/kernel_pca.png", width: 90%), caption: [Duas primeiras componentes da Kernel PCA com kernel RBF.])
#figure(kind: table, supplement: [Tabela], caption: [Saídas do ajuste de t-SNE.], [
#table(columns: 2, inset: 5pt, stroke: .35pt, table.header([*Saída*],[*Valor*]),
[Divergência KL final],
[0,1462],
[n\_iter\_ reportado],
[999],
[Taxa efetiva],
[50,0000]
)
])
#figure(image("../resultados/figuras/tsne.png", width: 90%), caption: [Projeção t-SNE com perplexidade 30 e semente 42.])
#figure(image("../resultados/figuras/umap.png", width: 90%), caption: [Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.])
#figure(kind: table, supplement: [Tabela], caption: [Preservação de vizinhanças nas quatro projeções.], [
#table(columns: 2, inset: 5pt, stroke: .35pt, table.header([*Projeção*],[*Trustworthiness (10 vizinhos)*]),
[PCA],
[0,9782],
[KERNEL PCA],
[0,9323],
[TSNE],
[0,9904],
[UMAP],
[0,9783]
)
])

As projeções não lineares (t-SNE e UMAP) ampliam a visualização das vizinhanças locais entre *versicolor* e *virginica*, alcançando trustworthiness superior a 0,97 (com destaque para TSNE, em 0,9904), enquanto a PCA preserva a interpretabilidade linear direta dos atributos originais.

= Conclusão
A adoção de uma rodada piloto não supervisionada (sementes 0 a 9) seguida da rodada oficial com hiperparâmetros congelados (sementes 42 a 51), combinada à definição de k = 1 como indefinido e ao cálculo do ARI sem ruído no DBSCAN, permite avaliar com rigor os sete algoritmos da Equipe 08. Sob o critério interno da silhueta, todos os algoritmos baseados em k convergem para $k^* = 2$ (Silhueta = 0,5802), refletindo a forte separabilidade linear de *Iris-setosa*. Quando avaliados em $k = 3$ frente às espécies botânicas, UPGMA apresenta o melhor desempenho (ARI = 0,7184) graças à modelagem de covariâncias elipsoidais, superando algoritmos de partição esférica.

= Reprodutibilidade e artefatos
Para reproduzir integralmente a rodada piloto, os experimentos oficiais das Questões 1 e 2, a auditoria automática e o PDF final:
```sh
python codigo/main.py
python codigo/validar_resultados.py
python codigo/gerar_relatorio.py
typst compile docs/relatorio.typ docs/relatorio.pdf --root .
```
== Versões utilizadas
#figure(kind: table, supplement: [Tabela], caption: [Versões registradas na execução dos experimentos.], [
#table(columns: 2, inset: 5pt, stroke: .35pt, table.header([*Pacote*],[*Versão*]),
[numpy],
[1.26.4],
[pandas],
[2.3.3],
[scikit-learn],
[1.9.1],
[scipy],
[1.16.3],
[matplotlib],
[3.11.2],
[seaborn],
[0.13.2],
[pydantic],
[2.14.1],
[fuzzy-c-means],
[2.3.1],
[kmedoids],
[0.5.5],
[umap-learn],
[0.5.12],
[numba],
[0.68.0]
)
])

= Fonte dos requisitos
Francisco de A. T. de Carvalho. *Projeto AM-NS 2026-2*. Documento fornecido com a atividade, `Projeto-AMG-NS-2026-2.pdf`: Questão 1, páginas 2–3; Questão 2, página 4; atribuição da Equipe 08, página 6; orientações de entrega, página 7.

= Referências
[1] CARVALHO, Francisco de A. T. *Projeto AM-NS 2026-2*. Centro de Informática, UFPE, 2026.

[2] UCI MACHINE LEARNING REPOSITORY. *Iris*. DOI: #link("https://doi.org/10.24432/C56C76")[10.24432/C56C76].

[3] SCIKIT-LEARN. *Clustering — Clustering performance evaluation*. #link("https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation")[Documentação oficial].

[4] SCIKIT-LEARN. *PCA, KernelPCA, TSNE e GaussianMixture*. #link("https://scikit-learn.org/stable/modules/classes.html")[Referência da API].

[5] UMAP-LEARN. *Basic UMAP Parameters*. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Documentação oficial].

[6] KMEDOIDS. *Fast k-medoids clustering in Python*. #link("https://python-kmedoids.readthedocs.io/en/latest/")[Documentação oficial].
