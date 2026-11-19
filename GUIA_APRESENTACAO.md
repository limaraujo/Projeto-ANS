# Guia de estudo e apresentação — Projeto AM-NS / Equipe 08

Este guia prepara você para **explicar o projeto e defender sua base técnica**. Ele acompanha os 17 slides da [apresentação em PowerPoint](outputs/apresentacao-iris-retro/presentation.pptx) e da [versão em PDF](outputs/apresentacao-iris-retro/presentation.pdf).

As configurações e os números foram conferidos no código e nos artefatos existentes. As explicações distinguem o funcionamento geral dos métodos da configuração efetivamente utilizada. A elaboração deste guia não reexecutou os experimentos.

## Como estudar

1. Leia as seções 1–4 para entender a pergunta, os dados e o protocolo.
2. Estude as seções 5–7 para dominar os sete agrupadores e a avaliação.
3. Estude as seções 8–9 para entender as quatro projeções e sua comparação.
4. Ensaie pela seção 11, com os slides abertos.
5. Use as seções 12–14 para responder perguntas e revisar antes de apresentar.

As equações são apoio ao raciocínio: o essencial é saber dizer **o que cada símbolo significa, o que o método otimiza e como isso afeta o resultado**. Exemplos marcados como didáticos não são novas medições da Iris.

## Sumário

- [1. A ideia central e os números essenciais](#1-a-ideia-central-e-os-números-essenciais)
- [2. Dados, padronização e distâncias](#2-dados-padronização-e-distâncias)
- [3. Conceitos matemáticos necessários](#3-conceitos-matemáticos-necessários)
- [4. O protocolo experimental](#4-o-protocolo-experimental)
- [5. Como funcionam os sete agrupadores](#5-como-funcionam-os-sete-agrupadores)
- [6. Silhueta, ARI e avaliação](#6-silhueta-ari-e-avaliação)
- [7. Como interpretar os resultados de agrupamento](#7-como-interpretar-os-resultados-de-agrupamento)
- [8. Como funcionam as quatro técnicas de projeção](#8-como-funcionam-as-quatro-técnicas-de-projeção)
- [9. Como avaliar e ler as projeções](#9-como-avaliar-e-ler-as-projeções)
- [10. Organização do código e reprodução](#10-organização-do-código-e-reprodução)
- [11. Roteiro de fala para os 17 slides](#11-roteiro-de-fala-para-os-17-slides)
- [12. Perguntas prováveis e respostas](#12-perguntas-prováveis-e-respostas)
- [13. Erros de interpretação a evitar](#13-erros-de-interpretação-a-evitar)
- [14. Revisão rápida antes da apresentação](#14-revisão-rápida-antes-da-apresentação)
- [15. Fontes e aprofundamento](#15-fontes-e-aprofundamento)

## 1. A ideia central e os números essenciais

O projeto compara **sete algoritmos de agrupamento** e **quatro técnicas de redução de dimensionalidade** usando as medidas de flores da base Iris.

A pergunta orientadora é:

> Sem informar as espécies aos algoritmos, quais estruturas aparecem nas medidas das flores e como podemos visualizá-las em duas dimensões?

Há dois objetivos relacionados:

- **Questão 1:** formar grupos, escolher o número de grupos quando aplicável e comparar os agrupamentos com as espécies conhecidas.
- **Questão 2:** representar os dados em 2D e analisar a informação preservada pelas projeções.

A conclusão que conecta tudo:

> A geometria favoreceu dois grupos, mas esses grupos não reproduzem completamente as três espécies. A silhueta e o ARI capturam aspectos diferentes desse resultado.

### 1.1. O que você precisa lembrar de cabeça

| Item | Resultado ou configuração |
|---|---|
| Dados | 150 flores, quatro atributos, três espécies com 50 flores cada |
| Pré-processamento | Atributos padronizados por z-score |
| Ajustes da Q1 | 1.195 ao todo. O protocolo final reúne 252 registros |
| Valores de k | 1, 2, 3, 4 e 5 |
| Reinicializações particionais | Dez por perfil e k, com sementes de 42 a 51 |
| Melhor k dos seis métodos com seleção | 2 |
| Silhueta desses seis métodos | 0,5802 |
| ARI desses seis métodos | 0,5681 |
| DBSCAN | Dois grupos, seis pontos de ruído e cobertura de 96%. Silhueta 0,6035 e ARI 0,5760 em 144 flores |
| Perfil escolhido do GMM, avaliado em k = 3 | ARI 0,9039 e silhueta 0,3728 |
| PCA nas duas primeiras componentes | 95,80% da variância |
| Maior trustworthiness nesta configuração | t-SNE: 0,9888, com dez vizinhos |

### 1.2. Apresentação do projeto em aproximadamente um minuto

> “Nós estudamos a base Iris, que tem 150 flores descritas por quatro medidas. Aplicamos sete agrupadores sem usar os rótulos das espécies durante o ajuste. Para os métodos particionais, repetimos cada configuração dez vezes e escolhemos a melhor execução pela função objetivo. Depois escolhemos os perfis e k pela silhueta e avaliamos a concordância com as espécies pelo ARI. Os seis métodos com escolha de k selecionaram dois grupos. Porém, ao observar o GMM com três componentes, encontramos um ARI maior, mostrando que boa separação geométrica e recuperação das espécies são critérios diferentes. Também comparamos quatro projeções: a PCA reteve 95,80% da variância em dois eixos, e o t-SNE teve a maior preservação local pelo diagnóstico utilizado.”

## 2. Dados, padronização e distâncias

### 2.1. O que existe na base Iris

Cada linha representa uma flor. As quatro colunas numéricas são:

| Atributo | Significado |
|---|---|
| `sepal_length` | Comprimento da sépala |
| `sepal_width` | Largura da sépala |
| `petal_length` | Comprimento da pétala |
| `petal_width` | Largura da pétala |

As medidas originais estão em centímetros. Pétalas são as estruturas mais associadas visualmente à flor; sépalas ficam na região externa que protege o botão floral.

As espécies de referência são **Iris-setosa, Iris-versicolor e Iris-virginica**, com 50 observações cada. O arquivo usado é [codigo/iris/iris.data](codigo/iris/iris.data).

No código:

```text
X: matriz 150 × 4, usada nos ajustes.
y: vetor com 150 rótulos de espécies, usado na avaliação externa e nas cores.
```

**Ter rótulos disponíveis não torna o ajuste supervisionado.** O que define isso é seu uso: os algoritmos recebem as medidas, sem a espécie como atributo ou alvo do treinamento.

Também não houve divisão treino/teste: o objetivo foi descrever a estrutura da base completa. Assim, os índices apresentados não estimam desempenho preditivo em novas flores.

### 2.2. Por que padronizar

Mesmo atributos medidos na mesma unidade podem variar em escalas diferentes. Uma variável com maior dispersão pode influenciar mais a distância entre as flores.

Para cada atributo j:

$$
z_{ij}=\frac{x_{ij}-\mu_j}{\sigma_j}.
$$

- `xᵢⱼ`: medida original da flor i no atributo j.
- `μⱼ`: média desse atributo na base.
- `σⱼ`: seu desvio-padrão populacional.
- `zᵢⱼ`: medida padronizada.

Após a transformação, cada coluna tem média aproximadamente zero e variância populacional um. Um valor `z = 2` indica uma medida dois desvios-padrão acima da média daquela coluna.

**Exemplo didático:** uma medida de 7,0 em um atributo com média 5,0 e desvio 1,0 vira `(7 − 5)/1 = 2`.

Padronizar dá uma escala comum às variações dos atributos. Isso **não remove correlações, não produz distribuição normal e não elimina outliers**. A escolha altera a geometria; os resultados deste projeto dizem respeito à versão padronizada.

### 2.3. Euclidiana, euclidiana quadrática e Manhattan

Para dois vetores x e v com quatro atributos:

$$
d_E(x,v)=\sqrt{\sum_{j=1}^{4}(x_j-v_j)^2},
\qquad
d_M(x,v)=\sum_{j=1}^{4}|x_j-v_j|.
$$

A euclidiana corresponde à linha reta; Manhattan soma deslocamentos por coordenada. A distância euclidiana quadrática é `d_E²`: remove a raiz e dá maior peso a diferenças grandes.

**Exemplo didático em 2D:** entre `(0,0)` e `(3,4)`, a euclidiana é 5, a euclidiana quadrática é 25 e Manhattan é 7.

No projeto, K-Means e FCM usam distâncias euclidianas quadráticas em seus objetivos; K-Medoids soma distâncias euclidianas; UPGMA constrói a árvore com Manhattan. A silhueta é sempre euclidiana, inclusive ao avaliar os cortes dessa árvore.

## 3. Conceitos matemáticos necessários

### 3.1. Centroide, medoide e protótipo

**Centroide** é a média dos vetores de um grupo. Pode representar uma flor que não existe na base. **Medoide** é uma observação real escolhida como representante. **Protótipo** é um termo mais geral para o representante de um grupo; no Kernel FCM deste projeto ele permanece no espaço original dos atributos.

**Exemplo didático:** nos valores `1, 2, 10`, o centroide é `4,33`. O medoide, usando distância absoluta em 1D, é `2`, pois minimiza a soma das distâncias aos demais. O exemplo também mostra por que a média pode se deslocar mais com um valor extremo.

### 3.2. Crisp, fuzzy e probabilístico

| Tipo | Saída antes da avaliação | Interpretação |
|---|---|---|
| Crisp ou exclusivo | Um rótulo por flor | A flor pertence ao grupo escolhido |
| Fuzzy | Graus de pertinência aos grupos | Representa associação parcial segundo o objetivo fuzzy |
| Probabilístico | Probabilidades posteriores dos componentes | Associação sob um modelo probabilístico de geração dos dados |

**Exemplo didático:** uma saída fuzzy `[0,6; 0,3; 0,1]` vira o rótulo do primeiro grupo pelo maior valor. O projeto faz isso com `argmax`. No GMM, também se aplica `argmax`, mas sobre probabilidades posteriores.

Pertinências fuzzy normalizadas **não são automaticamente probabilidades posteriores**. Somar um não basta para dar a elas a interpretação probabilística do GMM.

### 3.3. Função objetivo, convergência e mínimo local

Uma função objetivo mede o que o algoritmo tenta melhorar. K-Means minimiza dispersão; GMM maximiza log-verossimilhança.

Um **ótimo local** é uma solução que não melhora com os movimentos locais considerados, embora possam existir soluções melhores em outras regiões. O ponto de partida pode levar a resultados diferentes.

**Convergir** significa satisfazer um critério de parada, como mudança pequena nas pertinências, nos centros ou no objetivo. Isso não garante alcançar o melhor valor global possível.

Uma **iteração** é uma rodada interna de atualização. Uma **execução ou ajuste** é uma chamada completa ao método. Uma **reinicialização** começa outra tentativa a partir de um estado inicial. Essas três contagens são diferentes.

### 3.4. Semente aleatória e hiperparâmetros

A semente fixa o estado do gerador pseudoaleatório e ajuda a repetir uma execução. Ela não demonstra que o resultado é estável entre sementes ou ambientes.

**Hiperparâmetros** são escolhas fornecidas antes do ajuste, como k, gamma, eps e perplexidade. **Parâmetros aprendidos** incluem os centros, as médias e covariâncias do GMM e as coordenadas das projeções.

### 3.5. Variância e covariância

A variância mede dispersão em uma variável. A covariância mede como duas variáveis variam juntas. Para uma matriz centralizada X, a covariância amostral pode ser escrita como:

$$
S=\frac{X^T X}{n-1}.
$$

Na Iris, S tem dimensão `4 × 4`. Sua diagonal contém variâncias; os demais termos descrevem relações entre atributos. Covariância zero não implica independência em geral.

### 3.6. Autovetores, autovalores e SVD

Se `S v = λ v`, v é uma direção que a transformação S apenas multiplica por λ. Na PCA, os autovetores da covariância são as direções principais; os autovalores indicam a variância nessas direções.

A decomposição em valores singulares escreve a matriz como `X = U D Vᵀ`. Ela permite obter as direções principais sem precisar decompor explicitamente a covariância. Foi usada SVD completa na PCA do projeto.

### 3.7. Densidade, probabilidade, logaritmo e variável latente

Uma densidade contínua não é a probabilidade de um ponto exato e pode ter valor maior que um. Probabilidades de regiões são obtidas integrando a densidade.

No GMM, o componente que gerou cada flor é uma **variável latente**: não é observado. O algoritmo estima sua associação aos componentes.

O logaritmo transforma produtos de densidades em somas. Isso facilita trabalhar numericamente com a verossimilhança de muitas observações. Uma log-verossimilhança negativa é normal; ao maximizar, `−292` é melhor que `−326`.

### 3.8. Kernel, grafo e vizinhança

Um **kernel** permite expressar similaridades associadas a um produto interno em outro espaço. No RBF, a similaridade diminui quando a distância cresce.

Um **grafo** representa observações por nós e relações por arestas. Uma vizinhança pode ser definida por um raio, como no DBSCAN, ou por uma quantidade de pontos próximos, como no UMAP. Essas definições não são intercambiáveis.

## 4. O protocolo experimental

### 4.1. Quantos ajustes foram executados

A busca cruza 28 perfis dos cinco métodos particionais com quatro valores de k e dez sementes. O DBSCAN avalia 24 configurações. Os perfis escolhidos são completados com dez chamadas de k = 1 por método. A contagem total é

```text
28 perfis × 4 valores de k × 10 sementes = 1.120 ajustes particionais na busca.
1.120 + 24 DBSCAN + 50 chamadas com k = 1 + 1 árvore = 1.195 ajustes.
5 métodos × 5 valores de k × 10 sementes + 1 árvore + 1 DBSCAN = 252 registros finais.
```

O protocolo final reaproveita os ajustes dos perfis escolhidos e a execução do DBSCAN selecionada da grade. Os cinco cortes do UPGMA vêm de uma única árvore. As quatro projeções pertencem à Questão 2.

A contagem usa chamadas aos métodos. O Kernel FCM inicializa os protótipos por um FCM interno que faz parte da própria chamada.

### 4.2. A ordem da seleção precisa estar clara

```text
Para cada método particional:
    para cada perfil e k em {2, 3, 4, 5}:
        executar com as sementes 42, 43, ..., 51
        escolher a melhor execução pela função objetivo do método
        obter os rótulos crisp e calcular a silhueta, se definida
    escolher perfil e k* pela maior silhueta válida
    completar as 10 chamadas de k = 1 do perfil escolhido
    avaliar com ARI após a seleção
```

No GMM, a melhor execução é a de **maior** objetivo. Nos outros quatro, a de **menor** objetivo. Empates de objetivo retêm a menor semente. Empates de silhueta favorecem menor k e depois a ordem dos perfis, com a referência primeiro. No DBSCAN, a seleção exige silhueta válida e cobertura de pelo menos 95%.

O código também calcula ARI das melhores execuções em outros valores de k e os grava no CSV. Isso permite a análise posterior em k = 3, mas esses valores de ARI não orientam a seleção oficial.

### 4.3. Por que não usar o próprio objetivo para escolher k

Aumentar a quantidade de centros normalmente permite reduzir a inércia do K-Means. Aumentar componentes também dá flexibilidade ao GMM. Melhorar o objetivo bruto pode simplesmente refletir maior complexidade.

O objetivo escolhe a **melhor execução para um perfil e k fixos**. A silhueta escolhe **entre perfis e valores de k** usando as partições que venceram a primeira etapa.

### 4.4. Por que os objetivos não são comparáveis entre métodos

Uma inércia de 223 e um objetivo fuzzy de 182 não permitem dizer qual método é melhor. As expressões, pesos e escalas são diferentes. Os objetivos servem à seleção de execuções do mesmo método e k; as métricas comuns apoiam a comparação posterior.

## 5. Como funcionam os sete agrupadores

### 5.1. K-Means — aproximar cada grupo por sua média

**Intuição:** colocar k representantes no espaço e fazer cada flor se associar ao representante mais próximo. Depois mover os representantes para a média das flores associadas.

O objetivo é:

$$
J=\sum_{i=1}^{n}\|x_i-\mu_{c_i}\|^2.
$$

`xᵢ` é a flor i, `cᵢ` é seu grupo e `μ` é o centroide. J é a soma de quadrados intragrupo, também chamada de inércia.

**Etapas do algoritmo:**

1. Inicializar k centros.
2. Atribuir cada flor ao centro mais próximo: `cᵢ = argminⱼ ‖xᵢ − μⱼ‖²`.
3. Atualizar cada centro pela média do seu grupo: `μⱼ = soma dos xᵢ do grupo / tamanho do grupo`.
4. Repetir até satisfazer o critério de parada ou atingir o limite de iterações.

A média aparece porque minimiza a soma de distâncias quadráticas aos pontos de um grupo fixo. Na formulação ideal, atribuição e atualização não aumentam J; isso não garante o mínimo global.

**Exemplo didático:** com os pontos `1, 2, 8, 9` e dois centros iniciais em `1` e `8`, a atribuição forma `{1,2}` e `{8,9}`. Os centros passam a `1,5` e `8,5`.

**Configuração do projeto:** `KMeans`, inicialização `random`, `n_init=1` por chamada e sementes externas de 42 a 51. A melhor chamada para cada k minimiza `inertia_`.

**Pontos fortes e limites:** é simples e interpretável, mas favorece grupos compactos na geometria euclidiana; pode sofrer com escalas inadequadas, valores extremos e inicializações diferentes. O centroide não precisa ser uma flor real.

**Como explicar oralmente:** “O K-Means alterna entre atribuir flores ao centro mais próximo e recalcular esses centros pela média, reduzindo a dispersão quadrática dos grupos.”

Referência de implementação: [KMeans no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html). Configuração efetiva: [codigo/algoritmos.py](codigo/algoritmos.py), função `k_means`.

### 5.2. Fuzzy C-Means — distribuir pertinências entre os grupos

No projeto ele aparece como **Fuzzy K-Means**, mas a biblioteca o implementa como **FCM, Fuzzy C-Means**.

**Intuição:** uma flor pode estar parcialmente associada a vários grupos. Em vez de escolher um único centro a cada rodada, o algoritmo atualiza quanto ela pertence a cada grupo.

As pertinências satisfazem `uᵢⱼ ≥ 0` e `Σⱼ uᵢⱼ = 1`. O objetivo é:

$$
J_m=\sum_{i=1}^{n}\sum_{j=1}^{k}u_{ij}^{m}\|x_i-v_j\|^2,
\qquad m>1.
$$

`vⱼ` é o protótipo; `m` controla a difusividade. Com m mais próximo de 1, as associações tendem a ficar mais concentradas; valores maiores tendem a distribuir mais as pertinências.

**Etapas:**

1. Inicializar pertinências normalizadas.
2. Atualizar os centros como médias ponderadas por `uᵢⱼᵐ`.
3. Recalcular as pertinências a partir das distâncias aos centros.
4. Repetir até a mudança nas pertinências ficar suficientemente pequena ou atingir o limite.

As atualizações teóricas são:

$$
v_j=\frac{\sum_i u_{ij}^{m}x_i}{\sum_i u_{ij}^{m}},
\qquad
u_{ij}=\frac{1}{\sum_{\ell=1}^{k}\left(d_{ij}/d_{i\ell}\right)^{2/(m-1)}}.
$$

A segunda expressão vale para distâncias não nulas. Se a flor coincide com um centro, a implementação atribui pertinência apenas aos centros coincidentes, dividindo-a se houver empate. A inversão das distâncias explica por que centros próximos recebem pertinência maior.

**Configuração:** `fcmeans.FCM`, `m=2`, máximo de 300 iterações, tolerância `1e-5` e dez sementes por k. O objetivo usado na seleção é `Σ u² d²`.

Para avaliar com silhueta e ARI, o projeto converte a saída em `cᵢ = argmaxⱼ uᵢⱼ`. As pertinências originais também são preservadas.

**Pontos fortes e limites:** representa transições entre grupos, mas continua dependendo de escala, número de grupos e inicialização. O argmax descarta parte da informação de associação parcial: duas flores com pertinências `[0,99; 0,01]` e `[0,51; 0,49]` recebem o mesmo rótulo, embora tenham ambiguidades diferentes.

**Como explicar:** “O FCM substitui a associação exclusiva por graus de pertinência e usa essas pertinências como pesos para atualizar os centros.”

Base conferida: função `_executar_fuzzy` em [codigo/algoritmos.py](codigo/algoritmos.py) e código local da biblioteca `fcmeans.FCM`.

### 5.3. Kernel Fuzzy C-Means — mudar a similaridade usada pelo FCM

**Intuição:** manter a associação fuzzy, mas medir proximidade por uma transformação não linear.

O kernel RBF é:

$$
K(x,v)=\exp(-\gamma\|x-v\|^2).
$$

Se x e v coincidem, o kernel vale 1. Com a distância crescente, ele se aproxima de zero. Gamma maior faz a similaridade cair mais rapidamente; gamma menor considera similares pontos a distâncias maiores.

Na variante usada:

$$
d_K^2(x,v)=2\bigl(1-K(x,v)\bigr),
\qquad
J_m=\sum_i\sum_j u_{ij}^{m}d_K^2(x_i,v_j).
$$

Essa distância deriva de `‖φ(x) − φ(v)‖² = K(x,x) + K(v,v) − 2K(x,v)`. Para o RBF, os dois termos diagonais valem 1. Não é necessário calcular explicitamente o vetor φ.

**Detalhe específico deste projeto:** os protótipos v continuam nas quatro dimensões de entrada. Não se trata de primeiro projetar os dados com Kernel PCA e depois executar FCM.

**Etapas na biblioteca instalada:**

1. Usar um ajuste FCM para inicializar centros e pertinências.
2. Calcular o kernel entre flores e centros.
3. Atualizar centros com pesos `uᵢⱼᵐ K(xᵢ,vⱼ)`.
4. Atualizar pertinências usando a distância induzida pelo kernel.
5. Repetir até a parada; converter por argmax para a avaliação crisp.

A atualização do protótipo tem a forma iterativa:

$$
v_j^{novo}=\frac{\sum_i u_{ij}^{m}K(x_i,v_j^{atual})x_i}{\sum_i u_{ij}^{m}K(x_i,v_j^{atual})}.
$$

**Configuração:** RBF, `gamma=0,25`, `m=2`, máximo de 300 iterações e tolerância `1e-5`. A função objetivo registrada no código corresponde à formulação acima.

**Exemplo didático calculado:** com gamma 0,25 e distância euclidiana igual a 2, o kernel vale `exp(−1) ≈ 0,3679` e a distância quadrática induzida vale aproximadamente `1,2642`.

**Pontos fortes e limites:** permite uma noção não linear de proximidade, mas o comportamento depende do kernel e de gamma. Na grade da Iris, m e gamma alteraram as partições em k = 3. Os perfis Kernel FCM e FCM selecionados atingiram as mesmas métricas em k = 2.

**Como explicar:** “O Kernel FCM mantém as pertinências fuzzy, mas troca a distância convencional por uma distância induzida pelo RBF. Nesta variante, os centros continuam no espaço de entrada.”

Base conferida: `_executar_fuzzy`, `kernel_fuzzy_k_means` e código local de `fcmeans.KFCM`. Há variantes de Kernel FCM; esta explicação descreve a efetivamente instalada.

### 5.4. K-Medoids / PAM — representar grupos por observações reais

**Intuição:** escolher k flores reais como representantes e minimizar a distância das demais a essas flores.

O objetivo é:

$$
J=\sum_{i=1}^{n}\min_{j=1,\ldots,k} d_E(x_i,m_j),
\qquad m_j\in\{x_1,\ldots,x_n\}.
$$

Note duas diferenças em relação ao K-Means: o representante é uma amostra existente e o custo usa distâncias euclidianas sem elevá-las ao quadrado.

O PAM, **Partitioning Around Medoids**, busca melhorar o conjunto de medoides por trocas:

1. Escolher medoides iniciais.
2. Associar cada flor ao medoide mais próximo.
3. Avaliar trocas entre medoides e flores ainda não escolhidas.
4. Aceitar melhorias no custo e repetir até a parada.

O algoritmo pode parar em uma solução local; avaliar trocas não equivale a enumerar todos os conjuntos possíveis de k flores.

**Configuração:** `kmedoids.pam`, matriz de distâncias euclidianas, inicialização aleatória e máximo de 300 iterações para k > 1. O objetivo é `modelo.loss`.

**Caso especial k = 1:** o código calcula a soma das distâncias de cada flor às demais e escolhe o mínimo por busca exaustiva. As dez chamadas desse caso repetem a mesma solução, independentemente da semente.

**Pontos fortes e limites:** o representante real é interpretável e o método pode ser menos sensível a valores extremos que a média quadrática. Isso não garante robustez em qualquer base. Construir e usar a matriz de distâncias pode ser caro em bases grandes.

**Como explicar:** “O K-Medoids usa flores reais como representantes e procura substituí-las por outras quando a troca reduz o custo total.”

Base da configuração: função `kmedoids` em [codigo/algoritmos.py](codigo/algoritmos.py).

### 5.5. GMM com EM — modelar uma mistura de distribuições

**Intuição:** supor que os dados podem ser descritos por uma mistura de k distribuições gaussianas, cada uma com centro, dispersão e peso próprios.

$$
p(x_i)=\sum_{j=1}^{k}\pi_j\,\mathcal{N}(x_i\mid\mu_j,\Sigma_j),
\qquad \sum_j\pi_j=1.
$$

- `πⱼ`: peso do componente.
- `μⱼ`: média, um vetor com quatro elementos.
- `Σⱼ`: covariância, uma matriz `4 × 4` neste projeto.
- `N`: densidade gaussiana multivariada.

Com covariância completa, cada componente pode representar uma elipse em 2D ou um elipsoide em dimensões maiores, com orientações e dispersões próprias.

O objetivo é a log-verossimilhança:

$$
\ell=\sum_{i=1}^{n}\log\left[\sum_{j=1}^{k}\pi_j\mathcal{N}(x_i\mid\mu_j,\Sigma_j)\right].
$$

**Por que EM:** não sabemos qual componente está associado a cada flor. O algoritmo alterna entre estimar essa associação e atualizar os parâmetros.

**Passo E — Expectation:** calcular a responsabilidade de cada componente:

$$
r_{ij}=\frac{\pi_j\mathcal{N}(x_i\mid\mu_j,\Sigma_j)}{\sum_{\ell=1}^{k}\pi_\ell\mathcal{N}(x_i\mid\mu_\ell,\Sigma_\ell)}.
$$

É a probabilidade posterior de associação ao componente j, dadas a flor e a configuração atual do modelo.

**Passo M — Maximization:** atualizar pesos, médias e covariâncias usando essas responsabilidades:

$$
N_j=\sum_i r_{ij},\quad
\pi_j=\frac{N_j}{n},\quad
\mu_j=\frac{\sum_i r_{ij}x_i}{N_j},
$$

$$
\Sigma_j=\frac{\sum_i r_{ij}(x_i-\mu_j)(x_i-\mu_j)^T}{N_j}.
$$

E e M são repetidos até a parada. A formulação ideal do EM melhora ou mantém a verossimilhança; inicialização, degenerações e questões numéricas continuam relevantes.

**Configuração:** covariâncias `full`, `init_params="random_from_data"`, `n_init=1`, tolerância `1e-5` e regularização `reg_covar=1e-6`. A regularização adiciona um pequeno valor à diagonal das covariâncias, ajudando a evitar matrizes singulares. O objetivo registrado é `score(X) × n`, isto é, a log-verossimilhança total, e deve ser maximizado.

Para produzir rótulos crisp, o código usa `argmax` das probabilidades posteriores. As probabilidades são preservadas nos registros.

**Pontos fortes e limites:** representa dispersões orientadas e associações probabilísticas. Depende de inicialização, quantidade de componentes e adequação do modelo de mistura. Um componente não precisa corresponder a uma espécie. Convergência não comprova ótimo global.

**Como explicar:** “O GMM ajusta uma mistura de gaussianas. O EM alterna entre estimar a probabilidade de cada flor vir de cada componente e atualizar as distribuições com essas probabilidades como pesos.”

Referência conceitual: [misturas gaussianas no scikit-learn](https://scikit-learn.org/stable/modules/mixture.html). Configuração efetiva: função `gaussian_mixture` no código local.

### 5.6. UPGMA — construir uma hierarquia por ligação média

**Intuição:** começar com uma flor por grupo e juntar progressivamente os dois grupos mais próximos.

Neste projeto a distância entre grupos A e B é a média das distâncias Manhattan entre todos os pares que atravessam os dois grupos:

$$
D(A,B)=\frac{1}{|A||B|}\sum_{x\in A}\sum_{v\in B}d_M(x,v).
$$

**Etapas:**

1. Inicializar 150 grupos unitários.
2. Encontrar os dois grupos com menor distância média.
3. Uni-los e atualizar as distâncias do novo grupo aos demais.
4. Repetir até formar um único grupo.
5. Extrair cortes da mesma árvore para obter diferentes números de grupos.

Ao unir A e B, a atualização também pode ser escrita como:

$$
D(A\cup B,C)=\frac{|A|D(A,C)+|B|D(B,C)}{|A|+|B|}.
$$

O nome **unweighted** significa que as observações originais recebem o mesmo peso; não significa dar sempre peso 1/2 a cada subgrupo. A segunda regra, independente dos tamanhos, corresponde ao WPGMA.

**Como ler o dendrograma:** folhas representam flores ou subárvores agregadas; a altura da união representa a dissimilaridade no momento da fusão. A ordem horizontal das folhas não é um eixo de distância. Um corte horizontal define grupos pelas ramificações que cruza.

**Configuração:** `linkage(pdist(X, metric="cityblock"), method="average")`, seguido de `cut_tree` para k de 1 a 5. `cityblock` é Manhattan. A matriz de ligações tem `149 × 4`: dois identificadores de grupos, altura e quantidade de observações reunidas.

O slide mostra apenas as 12 subárvores finais para manter legibilidade. As contagens entre parênteses indicam folhas agregadas; números sem parênteses podem identificar observações individuais.

**Pontos fortes e limites:** permite explorar vários cortes, mas decisões de fusão anteriores não são desfeitas. Distância e regra de ligação alteram a árvore. A altura é dissimilaridade, não probabilidade ou confiança estatística.

**Como explicar:** “O UPGMA constrói uma única árvore, unindo os grupos cuja distância média entre observações é menor. Depois escolhemos o corte pela silhueta.”

Referência da regra de ligação e da matriz: [linkage na documentação do SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html).

### 5.7. DBSCAN — conectar regiões densas e identificar ruído

**Intuição:** grupos são regiões em que há pontos suficientemente próximos e conectados; observações fora dessas regiões podem ficar sem grupo.

Dois hiperparâmetros definem a densidade considerada:

- `eps`: raio de vizinhança.
- `min_samples`: quantidade mínima de pontos nessa vizinhança, incluindo o próprio ponto na implementação utilizada.

$$
N_\varepsilon(x)=\{v:d_E(x,v)\leq\varepsilon\}.
$$

Um ponto é **central ou core** quando `|Nε(x)| ≥ min_samples`. Um ponto **de borda** não é central, mas está na vizinhança de um ponto central. Um ponto **de ruído** não integra os grupos encontrados e recebe o rótulo `−1`.

**Etapas:**

1. Identificar pontos centrais pela densidade da vizinhança.
2. Conectar pontos centrais que podem ser alcançados por cadeias de vizinhanças de pontos centrais.
3. Incorporar os pontos de borda alcançáveis.
4. Rotular como ruído os pontos restantes.

Um ponto de borda não prolonga por conta própria a cadeia de expansão: a propagação depende de pontos centrais.

**Configuração selecionada na Q1.** A maior silhueta válida com pelo menos 95% de cobertura ocorreu com `eps≈0,694293` e `min_samples=3`. O raio mede 1,5 vez a mediana da distância ao quinto vizinho no espaço padronizado.

**Se mudar os parâmetros:** eps menor costuma fragmentar grupos e aumentar ruído; eps maior pode conectar regiões antes separadas. Aumentar `min_samples` exige maior densidade. São tendências, não uma promessa sobre o número de grupos em toda base.

**Pontos fortes e limites:** não exige k e permite ruído, mas exige uma escala de densidade. Uma configuração global pode ter dificuldade com grupos de densidades diferentes. Pontos de borda compartilhados podem ter atribuições dependentes da ordem; não o descreva como invariável a qualquer mudança.

**Como explicar:** “O DBSCAN procura regiões densas conectadas. O número de grupos emerge de eps e min_samples, e pontos que não se encaixam nessas regiões ficam como ruído.”

A distinção entre core, borda e ruído é descrita na [documentação de DBSCAN](https://scikit-learn.org/stable/modules/clustering.html#dbscan). Os parâmetros efetivos estão nos metadados da Q1.

### 5.8. Comparação dos mecanismos

| Método | Representação principal | O que orienta o ajuste | Exige k? |
|---|---|---|---|
| K-Means | Centroides | Soma de distâncias quadráticas | Sim |
| FCM | Centros e pertinências | Objetivo fuzzy | Sim |
| Kernel FCM | Protótipos e pertinências | Objetivo fuzzy com distância de kernel | Sim |
| K-Medoids | Observações representantes | Soma de distâncias aos medoides | Sim |
| GMM/EM | Pesos, médias e covariâncias | Log-verossimilhança | Sim |
| UPGMA | Árvore de fusões | Menor distância média a cada união | A árvore não; o corte pode ser definido por k |
| DBSCAN | Regiões densas e ruído | Conectividade por densidade | Não; exige eps e min_samples |

Nenhuma dessas definições pressupõe que os grupos sejam espécies botânicas. Essa associação é uma avaliação posterior.

## 6. Silhueta, ARI e avaliação

### 6.1. Silhueta: quão bem separado está cada ponto

Para uma observação i:

- `a(i)`: distância média às demais observações do seu grupo.
- `b(i)`: menor distância média a algum outro grupo; calcula-se a média para cada grupo alternativo e escolhe-se a menor.

$$
s(i)=\frac{b(i)-a(i)}{\max\{a(i),b(i)\}},
\qquad
\operatorname{Sil}=\frac{1}{n}\sum_i s(i).
$$

| Valor | Leitura |
|---|---|
| Próximo de 1 | O ponto está, em média, bem mais próximo do próprio grupo |
| Próximo de 0 | Há proximidade entre o próprio grupo e uma alternativa |
| Negativo | O ponto está, em média, mais próximo de outro grupo |

**Exemplo didático:** se `a=1` e `b=4`, a silhueta é `3/4=0,75`. Se `a=4` e `b=1`, ela é `−0,75`.

Não se usa espécie no cálculo: é uma métrica **interna**. O “grupo alternativo mais próximo” é escolhido pela distância média, não apenas pelo ponto isolado mais próximo.

Com apenas um grupo, não existe outro grupo para definir b. Por isso **k = 1 fica como indefinido/NaN**, e não como zero. A implementação também requer menos grupos que observações. Para um grupo unitário dentro de uma partição válida, a biblioteca adota silhueta zero para aquele ponto.

No projeto, escolhe-se `k* = argmax Sil(k)` entre as partições válidas. As métricas são calculadas nas **quatro dimensões padronizadas**. O desenho 2D não é a entrada desses cálculos.

### 6.2. ARI: quão parecidas são duas partições

O **Adjusted Rand Index**, ou índice de Rand ajustado, compara a partição dos clusters com a partição das espécies, considerando pares de flores e descontando a concordância esperada ao acaso sob o modelo usado pelo índice.

Para cada par, interessa saber se as flores estão juntas ou separadas em cada partição. O ARI não exige correspondência entre os números dos grupos e os nomes das espécies.

| Valor | Leitura |
|---|---|
| 1 | Partições equivalentes, mesmo que os identificadores sejam permutados |
| Próximo de 0 | Concordância próxima à referência de acaso do índice |
| Negativo | Concordância inferior a essa referência |

**Exemplo didático:** os rótulos `[0,0,1,1]` e `[7,7,3,3]` descrevem a mesma partição; o ARI é 1. Os nomes dos grupos mudaram, mas seus membros não.

Se precisar apresentar a fórmula, use a tabela de contingência. Seja `nᵢⱼ` o número de flores da espécie i no grupo j, `aᵢ` o total da linha e `bⱼ` o total da coluna. Defina:

$$
I=\sum_{ij}\binom{n_{ij}}{2},\quad
A=\sum_i\binom{a_i}{2},\quad
B=\sum_j\binom{b_j}{2},\quad
E=\frac{AB}{\binom{n}{2}}.
$$

Então, nos casos não degenerados:

$$
ARI=\frac{I-E}{\tfrac12(A+B)-E}.
$$

`C(t,2)=t(t−1)/2` conta pares. O numerador subtrai o acordo esperado; o denominador normaliza em relação ao máximo de referência. A biblioteca trata também casos degenerados da fórmula.

É uma avaliação **externa**, porque consulta as espécies. **ARI = 0,9039 não significa 90,39% de acurácia** e não estima uma taxa de acerto em flores novas.

Definições de referência: [silhueta](https://scikit-learn.org/stable/modules/clustering.html#silhouette-coefficient) e [ARI](https://scikit-learn.org/stable/modules/clustering.html#adjusted-rand-index), na documentação de avaliação de agrupamentos.

### 6.3. Por que duas métricas podem discordar

A silhueta pergunta se os grupos estão compactos e separados segundo uma distância. O ARI pergunta se a composição dos grupos corresponde à referência das espécies.

Imagine duas espécies cujas medidas se sobrepõem bastante. Juntá-las pode melhorar uma métrica geométrica, embora perca a distinção botânica. Essa é a situação central observada no projeto.

### 6.4. A convenção do ruído no DBSCAN

A silhueta e o ARI do DBSCAN incluem as **144 flores retidas**. A máscara exclui o rótulo `−1` da partição prevista e aplica a mesma exclusão aos rótulos das espécies no ARI. O DBSCAN encontrou dois grupos entre as flores retidas e marcou seis flores como ruído.

A comparação de amostra comum recalcula os dois índices para os sete métodos nas mesmas 144 flores. Todos coincidem nesse subconjunto, com silhueta 0,6035 e ARI 0,5760.

## 7. Como interpretar os resultados de agrupamento

### 7.1. Resultado das partições selecionadas

| Método | k selecionado ou encontrado | Silhueta | ARI | Ruído |
|---|---:|---:|---:|---:|
| K-Means | 2 | 0,5802 | 0,5681 | 0 |
| FCM | 2 | 0,5802 | 0,5681 | 0 |
| Kernel FCM | 2 | 0,5802 | 0,5681 | 0 |
| K-Medoids | 2 | 0,5802 | 0,5681 | 0 |
| GMM/EM | 2 | 0,5802 | 0,5681 | 0 |
| UPGMA | 2 | 0,5802 | 0,5681 | 0 |
| DBSCAN | 2, emergentes da densidade | 0,6035* | 0,5760* | 6 |

`*` As duas métricas do DBSCAN usam os pontos retidos. [Resumo dos agrupamentos](resultados/resumo_agrupamentos.csv) · [Comparação nas mesmas flores](resultados/tunagem/comparacao_mesma_amostra.csv)

Os seis métodos com escolha de k chegaram à mesma partição, salvo permutações dos identificadores:

| Espécie | Grupo A | Grupo B |
|---|---:|---:|
| Setosa | 50 | 0 |
| Versicolor | 0 | 50 |
| Virginica | 0 | 50 |

É por isso que as métricas coincidem. Não é apenas um empate numérico de partições potencialmente diferentes: as [contingências salvas](resultados/contingencias.json) mostram a mesma composição. Isso não significa que os centros, pertinências, parâmetros e objetivos sejam iguais.

### 7.2. O que as curvas de silhueta mostram

| Método | k = 2 | k = 3 | k = 4 | k = 5 |
|---|---:|---:|---:|---:|
| K-Means | 0,5802 | 0,4584 | 0,3883 | 0,3477 |
| FCM | 0,5802 | 0,4574 | 0,4006 | 0,3342 |
| Kernel FCM | 0,5802 | 0,4574 | 0,3941 | 0,3285 |
| K-Medoids | 0,5802 | 0,4497 | 0,4080 | 0,3421 |
| GMM/EM | 0,5802 | 0,3728 | 0,3455 | 0,1503 |
| UPGMA | 0,5802 | 0,4517 | 0,3991 | 0,3824 |

Fonte: [metricas_por_k.csv](resultados/metricas_por_k.csv). k = 1 não aparece na comparação por ser indefinido.

**Interpretação:** nesta geometria, separar setosa das outras duas espécies produz maior silhueta que subdividir o bloco versicolor/virginica. Isso é evidência sobre essa base, padronização, métrica e faixa de k; não prova que há apenas duas espécies ou duas classes “verdadeiras”.

### 7.3. Por que o GMM em k = 3 merece destaque

| Perfil escolhido de GMM | Silhueta | ARI |
|---|---:|---:|
| k = 2, selecionada pelo protocolo | 0,5802 | 0,5681 |
| k = 3, interpretação posterior | 0,3728 | 0,9039 |

Em k = 3, a composição, após reorganizar os identificadores para leitura, é:

| Espécie | Grupo A | Grupo B | Grupo C |
|---|---:|---:|---:|
| Setosa | 50 | 0 | 0 |
| Versicolor | 0 | 45 | 5 |
| Virginica | 0 | 0 | 50 |

O GMM recupera melhor a divisão entre versicolor e virginica nesse ajuste, mas paga uma redução de silhueta. Sua flexibilidade de covariâncias é uma explicação compatível com o mecanismo do modelo; o experimento não isola causalmente a razão dessa vantagem.

**Frase para defender o resultado:** “A seleção oficial continua sendo k = 2. A análise em k = 3 esclarece o alcance da silhueta e mostra maior concordância externa, sem mudar o critério depois de observar o ARI.”

### 7.4. O que aconteceu com o DBSCAN

Um grupo contém 49 setosas. O outro contém 49 versicolors e 46 virginicas. O ruído contém uma setosa, uma versicolor e quatro virginicas.

O melhor par elegível reteve 96% das flores. A maior silhueta de toda a grade, 0,6482, reteve 76,67%. A cobertura ajuda a interpretar as métricas porque os parâmetros podem mudar a quantidade de flores avaliadas. Na amostra comum aos sete métodos, as partições são iguais.

A atribuição de ruído descreve a conectividade de cada flor sob o raio e o número mínimo de vizinhos testados. [Grade do DBSCAN](resultados/tunagem/dbscan.csv)

## 8. Como funcionam as quatro técnicas de projeção

### 8.1. O que significa reduzir dimensionalidade

Cada flor originalmente ocupa uma posição em um espaço de quatro atributos. Uma projeção 2D produz duas coordenadas por flor. Isso permite desenhar os pontos, mas normalmente descarta ou distorce parte da estrutura.

Reduzir dimensionalidade não é o mesmo que agrupar. As quatro técnicas produziram coordenadas; os sete agrupadores da Q1 foram ajustados no espaço 4D padronizado. O projeto **não agrupou as projeções** para produzir os índices da Q1.

### 8.2. PCA — encontrar direções lineares de maior variância

**Intuição:** trocar os eixos de medição por combinações dos atributos que concentrem a variação das flores. A primeira componente busca a direção de maior variância; as seguintes são ortogonais às anteriores.

Para uma direção unitária v:

$$
\operatorname{Var}(Xv)=v^T S v,
\qquad \|v\|=1.
$$

Maximizar essa expressão conduz ao autovetor de S associado ao maior autovalor. As direções seguintes correspondem aos autovalores restantes em ordem decrescente.

**Etapas:**

1. Centralizar os atributos; neste projeto, eles já chegam padronizados.
2. Obter as direções principais por SVD.
3. Ordenar as componentes pela variância.
4. Projetar cada flor: `Z = X V₂`, usando as duas primeiras direções como colunas de V₂.

Na [implementação PCA do scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html), centralizar não substitui padronizar. O escalonamento foi feito antes, pelo `StandardScaler`.

**Configuração:** quatro componentes ajustadas e `svd_solver="full"`; as figuras usam apenas PC1 e PC2.

**Resultados:**

| Componente | Variância explicada | Acumulada |
|---|---:|---:|
| PC1 | 72,7705% | 72,7705% |
| PC2 | 23,0305% | 95,8010% |
| PC3 | 3,6838% | 99,4848% |
| PC4 | 0,5152% | 100% |

A proporção da componente j é `λⱼ / Σ λ`. Assim, duas dimensões retêm cerca de 95,80% da variância **do espaço de atributos padronizados**.

Isso não significa 95,80% de acerto, de informação biológica ou de separação entre espécies. PCA maximiza variância sem consultar as espécies.

#### Coeficientes de componentes versus loadings

Os coeficientes definem a combinação linear. Na ordem comprimento da sépala, largura da sépala, comprimento da pétala e largura da pétala, a PC1 é aproximadamente:

```text
PC1 = 0,5224 z_sepal_length − 0,2634 z_sepal_width
    + 0,5813 z_petal_length + 0,5656 z_petal_width
```

Os **loadings** adotados no projeto são `autovetor × raiz do autovalor`:

| Atributo | Loading PC1 | Loading PC2 |
|---|---:|---:|
| Comprimento da sépala | 0,8942 | 0,3585 |
| Largura da sépala | −0,4508 | 0,8913 |
| Comprimento da pétala | 0,9950 | 0,0203 |
| Largura da pétala | 0,9682 | 0,0630 |

Nessa convenção, PC1 se associa fortemente às medidas das pétalas, enquanto PC2 enfatiza a largura da sépala. Não confunda os coeficientes da equação com os loadings da tabela.

Há um detalhe de convenção: o StandardScaler usa variância populacional e os autovalores da PCA usam denominador `n−1`. Portanto, esses loadings não devem ser chamados de correlações exatas sem considerar o fator de escala correspondente. A interpretação de intensidade relativa permanece útil.

O sinal de uma componente pode ser invertido sem mudar sua informação: o autovetor v e o autovetor −v representam o mesmo eixo com orientação oposta.

**Como explicar:** “A PCA cria combinações lineares dos atributos para concentrar variância. Nesta base, PC1 e PC2 retêm 95,80%, mas ainda existe sobreposição entre versicolor e virginica.”

### 8.3. Kernel PCA — componentes principais em um espaço implícito

**Intuição:** procurar direções principais depois de representar as flores por relações não lineares de similaridade.

Em vez de formar explicitamente φ(x), o método monta a matriz de Gram:

$$
K_{ij}=K(x_i,x_j)=\exp(-\gamma\|x_i-x_j\|^2).
$$

Na Iris, K tem dimensão `150 × 150`. Para centralizar no espaço implícito:

$$
H=I-\frac{1}{n}\mathbf{1}\mathbf{1}^T,
\qquad K_c=H K H.
$$

Depois resolve-se `Kc aⱼ = λⱼ aⱼ`. Para as amostras de treinamento, com autovetores normalizados, as coordenadas são proporcionais a `sqrt(λⱼ) aⱼ`.

**Etapas:** calcular similaridades, centralizar K, decompor Kc e usar as componentes de maior autovalor para formar o mapa.

**Configuração:** RBF, `gamma=0,25`, duas componentes e `eigen_solver="dense"`. Autovalores registrados: **39,1321** e **17,7924**.

Esses são autovalores da matriz de kernel centralizada. Não estão na escala da covariância dos quatro atributos originais. Dividir um deles pela soma dos dois retidos não fornece um percentual da variância original explicada.

**Diferença para Kernel FCM:** Kernel PCA produz coordenadas para visualizar ou transformar os dados. Kernel FCM produz pertinências e grupos. Ambos usam RBF neste estudo, mas otimizam problemas diferentes.

**Pontos fortes e limites:** admite relações não lineares, mas depende de gamma e torna a interpretação dos eixos por atributos menos direta. A transformação não assegura melhor separação ou maior preservação local.

**Como explicar:** “A Kernel PCA faz uma análise espectral da matriz de similaridades RBF centralizada. Seus eixos não são combinações lineares simples dos quatro atributos originais.”

Referências: configuração em `executar_questao_2` e [KernelPCA no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html).

### 8.4. t-SNE — aproximar distribuições de vizinhança

**Intuição:** posicionar pontos em 2D para que relações de proximidade importantes no espaço original continuem próximas no mapa.

No espaço original, o método atribui afinidades condicionais:

$$
p_{j\mid i}=\frac{\exp(-\|x_i-x_j\|^2/(2\sigma_i^2))}{\sum_{\ell\ne i}\exp(-\|x_i-x_\ell\|^2/(2\sigma_i^2))},
\qquad j\ne i.
$$

A escala σᵢ é adaptada para alcançar a perplexidade escolhida. Ela equivale a `2` elevado à entropia em bits dessa distribuição. A perplexidade é uma escala efetiva de vizinhança, **não é k de agrupamento nem uma contagem rígida de vizinhos**.

As afinidades são simetrizadas. No mapa, os pontos z usam uma distribuição t com um grau de liberdade:

$$
q_{ij}=\frac{(1+\|z_i-z_j\|^2)^{-1}}{\sum_{a\ne b}(1+\|z_a-z_b\|^2)^{-1}}.
$$

A cauda mais pesada facilita acomodar separações no espaço de baixa dimensão. O objetivo é minimizar:

$$
KL(P\|Q)=\sum_{i\ne j}p_{ij}\log\frac{p_{ij}}{q_{ij}}.
$$

**Etapas:** construir afinidades no espaço original, inicializar o mapa e mover os pontos por otimização para aproximar as afinidades 2D das originais. O ajuste usa forças atrativas e repulsivas associadas ao objetivo.

As expressões descrevem o objetivo teórico; o projeto usou a aproximação **Barnes-Hut**, não o cálculo exato de todas as forças. A formulação original está em [van der Maaten e Hinton, 2008](https://jmlr.org/papers/v9/vandermaaten08a.html); os controles de execução são descritos na [API TSNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html).

**Configuração registrada:** duas dimensões, perplexidade 30, inicialização PCA, semente 42, distância euclidiana, `max_iter=1000`, exagero inicial 12, Barnes-Hut com ângulo 0,5 e taxa automática que resultou em **50**.

**Saídas:** KL final **0,164197** e `n_iter_` reportado **999**. KL não é taxa de erro de classificação. Não use esse contador ou o fim do orçamento como evidência de ótimo global.

O exagero inicial aumenta temporariamente a atração associada às afinidades durante a fase inicial. A taxa de aprendizado controla o tamanho dos passos. Ambos podem alterar o resultado.

**Pontos fortes e limites:** pode revelar vizinhanças e transições, mas distâncias entre ilhas, áreas ocupadas e densidades visuais não são reproduções fiéis do espaço original. Não existe percentual de variância explicada análogo ao da PCA. Uma única semente não estabelece estabilidade.

**Como explicar:** “O t-SNE cria distribuições de afinidade nas quatro dimensões e no mapa 2D. Ele ajusta as posições para reduzir a divergência entre essas distribuições, enfatizando relações locais.”

### 8.5. UMAP — organizar em 2D um grafo de vizinhanças

**Intuição:** construir uma rede de relações locais entre as flores e buscar uma disposição em 2D que preserve as conexões relevantes.

**Etapas:**

1. Encontrar vizinhanças no espaço original.
2. Atribuir pesos às conexões, adaptando a escala local.
3. Combinar as conexões dirigidas em um grafo fuzzy simétrico.
4. Inicializar as coordenadas e otimizar atrações e repulsões no mapa.

Uma forma de expressar a intensidade dirigida é:

$$
w_{i\to j}=\exp\left[-\frac{\max(0,d(x_i,x_j)-\rho_i)}{\sigma_i}\right].
$$

`ρᵢ` ajusta a conectividade local e `σᵢ` controla a escala. Na união fuzzy usada com a configuração padrão do projeto:

$$
w_{ij}=w_{i\to j}+w_{j\to i}-w_{i\to j}w_{j\to i}.
$$

No mapa, a força de conexão pode ser modelada por `qᵢⱼ = 1/(1+a‖zᵢ−zⱼ‖²ᵇ)`. Os parâmetros a e b são obtidos de uma curva associada a `min_dist` e `spread`.

Um objetivo teórico de comparação dos grafos usa termos como:

$$
-\sum_{i<j}\left[w_{ij}\log q_{ij}+(1-w_{ij})\log(1-q_{ij})\right].
$$

A implementação usa otimização estocástica com amostragem de arestas e amostras negativas; essa expressão dá a interpretação, sem afirmar que o código soma exatamente todos os pares a cada iteração. Visão conceitual: [como o UMAP funciona](https://umap-learn.readthedocs.io/en/latest/how_umap_works.html).

**Configuração:** `n_neighbors=15`, `min_dist=0,1`, `spread=1`, duas dimensões, distância euclidiana, inicialização espectral, semente 42 e `n_jobs=1`.

O registro deixa `n_epochs` como nulo, isto é, a quantidade é escolhida automaticamente pela biblioteca. Não declare um contador de épocas observado que não foi registrado.

**O que controlar:** `n_neighbors` menor enfatiza relações mais locais; maior considera vizinhanças mais amplas. `min_dist` controla a compactação favorecida no mapa. Ele **não é um limite rígido que impede dois pontos de ficarem mais próximos**, nem o raio usado para encontrar vizinhos no espaço original. Veja os [parâmetros oficiais do UMAP](https://umap-learn.readthedocs.io/en/latest/parameters.html).

**Pontos fortes e limites:** oferece uma representação não linear por vizinhanças, mas aparência, compactação e ilhas dependem dos hiperparâmetros. Orientação e distância entre regiões desconectadas não têm significado físico direto. O uso de conceitos fuzzy no grafo não o transforma em FCM.

**Como explicar:** “O UMAP constrói um grafo de vizinhanças com pesos locais e otimiza sua disposição em duas dimensões. Quinze vizinhos definem a escala local e min_dist influencia a compactação visual.”

### 8.6. Comparação das quatro técnicas

| Técnica | Estrutura privilegiada | Como entender os eixos | Principal cuidado |
|---|---|---|---|
| PCA | Variância linear | Combinações dos atributos | Variância não é separação de espécies |
| Kernel PCA | Estrutura espectral do kernel | Coordenadas não lineares dependentes do kernel | Autovalores não são variância original |
| t-SNE | Afinidades, com ênfase local | Coordenadas de um mapa otimizado | Distâncias entre ilhas podem enganar |
| UMAP | Grafo de vizinhanças | Coordenadas de um grafo disposto em baixa dimensão | Compactação depende da configuração |

## 9. Como avaliar e ler as projeções

### 9.1. O que é trustworthiness

O índice pergunta se vizinhos próximos no mapa 2D também eram próximos no espaço original. Ele penaliza **vizinhos artificiais introduzidos pela projeção**.

Se `Uᵢ` contém os vizinhos do mapa que não pertenciam aos k vizinhos originais e `r(i,j)` é o ranking original do ponto j em relação a i, então:

$$
T(k)=1-\frac{2}{nk(2n-3k-1)}\sum_i\sum_{j\in U_i}\bigl(r(i,j)-k\bigr).
$$

Quanto mais distante era originalmente um novo vizinho, maior a penalidade. Neste diagnóstico, k é a quantidade de vizinhos da **métrica**, não o número de clusters. Usou-se **k = 10**, n = 150 e distância euclidiana.

O índice varia de zero a um, com valores maiores indicando melhor preservação segundo esse critério. Ele não utiliza as espécies e não mede toda a geometria global. Veja a [definição de trustworthiness](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.trustworthiness.html).

### 9.2. Resultado observado

| Técnica | Trustworthiness com dez vizinhos |
|---|---:|
| PCA | 0,9782 |
| Kernel PCA | 0,9322 |
| t-SNE | 0,9888 |
| UMAP | 0,9783 |

Fonte: [execucoes_questao_2.json](resultados/execucoes_questao_2.json).

O t-SNE apresentou o maior valor nesta configuração. PCA e UMAP foram muito próximos. Isso não permite concluir que essa ordenação é universal ou estatisticamente estável: houve uma execução por técnica, sem intervalo de confiança ou comparação entre sementes.

### 9.3. Como comentar os desenhos

Setosa aparece mais separada. Versicolor e virginica apresentam maior proximidade e mistura em regiões de transição. As quatro técnicas mostram essa estrutura sob representações diferentes.

As cores e os símbolos identificam as espécies depois do ajuste; não são grupos que essas quatro técnicas aprenderam como classes. Um desenho com três cores é consequência da legenda fornecida, não uma prova de recuperação perfeita de três classes.

### 9.4. Por que não declarar uma projeção “a melhor” sem critério

PCA teve alta retenção de variância e permite interpretar os eixos. t-SNE teve maior trustworthiness no diagnóstico utilizado. Esses critérios não são equivalentes; a escolha depende do que se pretende preservar.

Também não se deve comparar a KL do t-SNE com a inércia do K-Means, ou com autovalores de PCA e Kernel PCA. Cada quantidade pertence a um problema de otimização diferente.

## 10. Organização do código e reprodução

### 10.1. Onde cada parte está implementada

| Arquivo | Papel |
|---|---|
| [codigo/main.py](codigo/main.py) | Lê os argumentos e chama as questões |
| [codigo/questoes.py](codigo/questoes.py) | Organiza as execuções completas, projeções e gravação dos artefatos |
| [codigo/algoritmos.py](codigo/algoritmos.py) | Carrega dados, adapta bibliotecas, seleciona execuções, calcula métricas e produz figuras |
| [codigo/validar_resultados.py](codigo/validar_resultados.py) | Confere consistência dos resultados persistidos |
| [codigo/tunagem.py](codigo/tunagem.py) | Executa e registra a busca de hiperparâmetros integrada à Questão 1 |
| [resultados/](resultados/) | Registros, métricas, coordenadas, parâmetros e figuras |
| [docs/artigo/artigo_ieee_revisado.pdf](docs/artigo/artigo_ieee_revisado.pdf) | Artigo revisado que fundamenta a apresentação |

Os algoritmos são executados por adaptadores de bibliotecas: `scikit-learn`, `fcmeans`, `kmedoids`, SciPy e `umap-learn`. O código próprio organiza o experimento, controla parâmetros e sementes, uniformiza as saídas, aplica a seleção e registra as avaliações. Não apresente as bibliotecas como reimplementações próprias do zero.

O registro efetivamente usado para os agrupadores é definido pelo decorador `@algoritmo` em `algoritmos.py`. O arquivo `algoritmos.json` descreve configurações, mas não é a fonte carregada pelo fluxo principal atual.

### 10.2. Como os resultados circulam no programa

```text
main.py
  → executar_questao_1()
      → carregar_iris()
      → pesquisar perfis e escolher execuções pelo objetivo
      → escolher perfis e k pela silhueta
      → completar k = 1, cortar uma árvore UPGMA e selecionar DBSCAN
      → calcular ARI, comparar amostra comum e persistir figuras, CSV e JSON
  → executar_questao_2()
      → carregar_iris()
      → fit_transform(X) de cada projeção
      → variância/autovalores/KL/trustworthiness conforme aplicável
      → coordenadas, figuras e metadados
```

A classe `ResultadoAgrupamento` organiza rótulos, objetivo, parâmetros e, conforme o método, centros, pertinências, probabilidades, hierarquia e ruído. Nem todos os campos se aplicam a todo método.

### 10.3. Comandos úteis

Estes comandos usam o ambiente já existente na raiz do projeto:

```sh
# Apenas consultar as opções
.venv/bin/python codigo/main.py --help

# Reexecutar cada questão
.venv/bin/python codigo/main.py --questao 1
.venv/bin/python codigo/main.py --questao 2

# Reexecutar as duas
.venv/bin/python codigo/main.py

# Auditar os resultados salvos
.venv/bin/python codigo/validar_resultados.py
```

As execuções gravam nos caminhos fixos de `resultados/` e podem substituir as métricas e figuras existentes. O validador também grava `resultados/validacao.json`. Para uma demonstração ao vivo, prefira apresentar os arquivos prontos; se decidir reexecutar, preserve a versão usada nos slides antes.

### 10.4. Detalhes que podem virar pergunta técnica

- `--seed` controla as projeções; a Q1 usa a sequência 42–51.
- `--gamma` controla a Kernel PCA. A Q1 busca o gamma do Kernel FCM na grade de hiperparâmetros.
- Na execução padrão da Q1, o DBSCAN é selecionado pela grade. `--eps` e `--min-samples` permitem substituir o par escolhido numa execução explícita.
- `n_init=1` no K-Means e GMM evita multiplicar dez chamadas por dez inicializações internas. O protocolo principal tem dez tentativas externas por k.
- A PCA ajusta quatro componentes; as coordenadas, métricas locais e figuras usam as duas primeiras quando indicado.
- UMAP pode mostrar parâmetros `target_*` em `get_params()`, mas o ajuste foi `fit_transform(X)` sem y. A presença desses defaults no registro não significa uso supervisionado das espécies.
- `json` salva como `null` os valores não finitos convertidos pelo código; o CSV pode deixar a silhueta de k = 1 em branco. Isso representa indefinição, não falha a ser substituída por zero.

### 10.5. O que a validação realmente verifica

O validador confere, entre outros pontos, quantidade de chamadas e sementes, escolha do melhor objetivo por k, recálculo de silhueta e ARI dos ajustes particionais selecionados, normalização de pertinências e probabilidades, compatibilidade do argmax com rótulos e dimensões/finitude das projeções.

A auditoria inclui a grade, a seleção por silhueta, as métricas do UPGMA e do DBSCAN, e o recálculo na amostra comum. Consulte os itens registrados no [relatório de validação](resultados/validacao.json).

## 11. Roteiro de fala para os 17 slides

Use as falas como base e adapte ao seu jeito de explicar. Para aproximadamente 18 minutos, priorize a pergunta, o protocolo, o contraste silhueta/ARI e a leitura das projeções. As derivações deste guia preparam a defesa; não é necessário recitá-las integralmente no slide de visão geral dos métodos.

### Slide 1 — Iris: grupos e projeções

**Objetivo:** apresentar a pergunta, em cerca de 30 segundos.

> “Nosso projeto compara agrupamento e redução de dimensionalidade na Iris. Queremos investigar quais estruturas aparecem nas medidas das flores quando as espécies não são fornecidas no ajuste. A pergunta principal é se grupos bem separados geometricamente correspondem às três espécies conhecidas.”

Transição: “Primeiro, precisamos entender como representamos cada flor.”

### Slide 2 — Três espécies; quantos grupos?

**Objetivo:** explicar os dados e o uso dos rótulos, em cerca de um minuto.

> “Temos 150 flores, com 50 de cada espécie, descritas por comprimento e largura de sépalas e pétalas. Separamos as quatro medidas dos nomes das espécies. Padronizamos os atributos para trabalhar com suas variações em uma escala comum. As espécies só entram depois, para avaliar a concordância e identificar as cores dos gráficos.”

Se perguntarem o que é padronização, explique `(valor − média)/desvio-padrão`. Transição: “Sobre essa mesma representação, comparamos mecanismos diferentes de agrupamento.”

### Slide 3 — Sete métodos, cinco perspectivas

**Objetivo:** distinguir os mecanismos, em cerca de um minuto.

> “O K-Means representa grupos por médias. O FCM permite pertinência parcial, e sua versão kernel muda a noção de proximidade. O K-Medoids usa flores reais como representantes. O GMM modela componentes probabilísticos. O UPGMA constrói uma hierarquia por fusões, e o DBSCAN conecta regiões densas e pode marcar ruído.”

As cinco perspectivas são partição exclusiva, fuzzy, probabilística, hierárquica e por densidade. Guarde as equações para explicar em perguntas ou em uma apresentação com mais tempo.

### Slide 4 — O protocolo separa ajuste e avaliação

**Objetivo:** deixar a ordem de seleção inequívoca, em aproximadamente um minuto e meio.

> “Testamos uma grade de parâmetros sobre k de 2 a 5, com dez sementes por combinação. Escolhemos a melhor execução pelo objetivo do método e usamos a silhueta para selecionar o perfil e k. O ARI avalia as escolhas em relação às espécies. O protocolo final conserva 252 registros, dentro de 1.195 ajustes executados.”

Mostre as setas do processo. Ressalte que os cortes vêm de uma só árvore. Transição: “As duas métricas têm funções diferentes.”

### Slide 5 — Silhueta e ARI respondem a perguntas distintas

**Objetivo:** explicar o significado de cada índice, em cerca de um minuto.

> “A silhueta compara a distância média de cada flor ao próprio grupo com a distância média ao grupo alternativo mais próximo. Ela avalia coesão e separação sem consultar espécies. O ARI compara a composição dos grupos com as espécies e desconta a concordância de referência ao acaso. Por isso uma partição pode ter silhueta maior e ARI menor.”

Lembre que k = 1 é indefinido para silhueta. Transição: “As curvas mostram qual estrutura foi favorecida pelo critério interno.”

### Slide 6 — A silhueta favorece dois grupos

**Objetivo:** ler o gráfico, em cerca de um minuto.

> “Cada ponto representa a melhor execução daquele método e k, escolhida antes pelo objetivo. As seis curvas atingem a maior silhueta em k igual a 2. Ao criar mais grupos, a silhueta diminui. Nesta geometria, a divisão em dois blocos é mais favorável do que subdividir a região em que versicolor e virginica se aproximam.”

Na partição escolhida, um grupo reúne 50 setosas e o outro reúne as 100 flores das duas espécies restantes. O resultado explica a igualdade das duas métricas entre os seis métodos na base completa.

### Slide 7 — Hiperparâmetros afetam as métricas

As linhas mostram os menores e maiores valores entre perfis em k = 3. O ponto destaca a métrica do perfil escolhido pela busca para esse mesmo k.

> “Testar a inicialização produz diferenças pequenas de silhueta no K-Means. No PAM, a inicialização build melhora a silhueta e reduz o ARI. Os perfis fuzzy produzem silhuetas próximas. No GMM, variar a covariância e a regularização dá a maior amplitude de sensibilidade das duas métricas.”

### Slide 8 — GMM em dois e três componentes

**Objetivo:** defender a conclusão central, em aproximadamente um minuto e quinze segundos.

> “No perfil escolhido do GMM, passar de dois para três componentes eleva o ARI para 0,9039 e reduz a silhueta para 0,3728. O k selecionado pela silhueta foi 2. A grade completa registra como outros tipos de covariância e valores de regularização afetam as duas métricas.”

Se pedirem a composição, cite 50 setosas, 45 versicolors e um terceiro grupo com 50 virginicas e cinco versicolors. Não converta ARI em acurácia.

### Slide 9 — Uma árvore permite vários cortes

**Objetivo:** explicar o dendrograma, em cerca de um minuto.

> “O UPGMA começa com uma flor por grupo e vai unindo os pares de grupos com menor média de distâncias Manhattan. A altura indica a dissimilaridade da fusão. Podemos cortar a mesma árvore em diferentes alturas. O slide resume as 12 subárvores finais e destaca um corte que gera dois grupos.”

Se perguntarem pela distância da avaliação, responda que a silhueta dos cortes foi euclidiana para manter a convenção comparativa da Q1.

### Slide 10 — DBSCAN avalia os pontos retidos

**Objetivo:** explicar a diferença de amostra nas métricas, em cerca de um minuto.

> “A grade escolheu eps aproximadamente 0,694 e mínimo de três pontos, com pelo menos 95% das flores atribuídas a grupos. O DBSCAN encontrou dois grupos e seis pontos de ruído. Nas 144 flores retidas, a silhueta foi 0,6035 e o ARI foi 0,5760. Os outros métodos coincidiram com o DBSCAN ao comparar as mesmas flores.”

Transição: “Agora passamos dos grupos às representações em duas dimensões.”

### Slide 11 — PCA retém 95,80% em dois eixos

**Objetivo:** conectar variância, atributos e figura, em aproximadamente um minuto e quinze segundos.

> “A PCA encontra direções lineares que concentram variância. A primeira explica 72,77% e a segunda 23,03%, somando 95,80%. A primeira está fortemente associada às medidas das pétalas, e a segunda destaca a largura da sépala. Setosa se separa visualmente, enquanto versicolor e virginica mantêm sobreposição.”

Complete: “Retenção de variância não significa percentual de classificação correta.”

### Slide 12 — Kernel PCA muda a geometria

**Objetivo:** explicar a transformação não linear, em cerca de um minuto.

> “A Kernel PCA usa similaridades RBF, com gamma 0,25, e decompõe a matriz de kernel centralizada. Os autovalores 39,1321 e 17,7924 pertencem a essa matriz. Eles não são porcentagens da variância dos atributos originais. O método produz uma organização não linear, com eixos de interpretação menos direta.”

Transição: “As próximas técnicas enfatizam relações de vizinhança.”

### Slide 13 — t-SNE e UMAP enfatizam vizinhanças

**Objetivo:** explicar o princípio dos dois mapas, em aproximadamente um minuto e meio.

> “O t-SNE ajusta o mapa para aproximar distribuições de afinidade, usando perplexidade 30. O UMAP constrói um grafo de vizinhanças, aqui com 15 vizinhos e min_dist 0,1, e otimiza sua disposição em 2D. Ambos mostram setosa isolada e uma relação mais próxima entre as outras espécies. Porém, a distância entre ilhas e a área ocupada no mapa não são medidas fiéis da geometria original.”

As duas técnicas usaram semente 42. Não afirme que o algoritmo descobriu as três cores: elas vêm das espécies usadas na legenda.

### Slide 14 — t-SNE preservou mais vizinhos locais

**Objetivo:** apresentar o diagnóstico com sua limitação, em aproximadamente 45 segundos.

> “Com dez vizinhos, medimos quantos vizinhos artificiais o mapa introduziu, ponderando a distância deles no ranking original. O t-SNE apresentou o maior trustworthiness, 0,9888. UMAP e PCA ficaram muito próximos. A comparação vale para esta execução e essa configuração; não estabelece superioridade universal ou estabilidade estatística.”

### Slide 15 — O alcance das conclusões é descritivo

**Objetivo:** demonstrar consciência metodológica, em aproximadamente 45 segundos.

> “Os métodos compartilham base e padronização. As grades mostram a sensibilidade dentro dos parâmetros testados. As dez sementes mudam a inicialização sobre as mesmas flores, e cada projeção usa uma configuração. A cobertura é parte da interpretação das métricas do DBSCAN.”

### Slide 16 — Grupos geométricos diferem de espécies

**Objetivo:** fechar a resposta à pergunta inicial, em aproximadamente 45 segundos.

> “A silhueta favoreceu dois grupos, separando setosa das demais. Em três componentes, o perfil escolhido do GMM alcançou ARI de 0,9039. Nas projeções, a PCA reteve 95,80% da variância em dois eixos e o t-SNE teve maior preservação local na escala de dez vizinhos.”

### Slide 17 — Fontes e rastreabilidade

**Objetivo:** indicar de onde saíram os números, sem prolongar a fala.

> “As configurações, tabelas e figuras estão ligadas ao artigo revisado e aos registros das duas questões. Os arquivos de resultados permitem conferir as métricas e os parâmetros apresentados.”

Abra para perguntas. Se quiser demonstrar uma evidência, mostre o CSV pertinente, evitando reexecutar tudo durante a defesa.

## 12. Perguntas prováveis e respostas

### 12.1. “Se sabemos que existem três espécies, por que não fixar k = 3?”

Porque o objetivo foi investigar a estrutura favorecida pelos dados e pelo critério interno, sem usar as espécies para orientar k. Fixar três seria outro protocolo, adequado a outra pergunta. O caso GMM com três componentes foi examinado depois para interpretar a diferença entre geometria e classes.

### 12.2. “Por que usar uma base rotulada em aprendizado não supervisionado?”

Os rótulos ficam separados do ajuste e permitem avaliação externa posterior. Eles são uma referência para analisar os grupos, não uma entrada fornecida aos agrupadores.

### 12.3. “Por que o ARI é igual em todos os seis métodos?”

Porque a partição escolhida foi a mesma, com setosa em um grupo e versicolor mais virginica no outro. Igualdade de índices sozinha não provaria isso; a composição foi conferida nas contingências.

### 12.4. “Qual algoritmo foi melhor?”

Os sete métodos coincidiram quando avaliados nas mesmas 144 flores retidas pelo DBSCAN. Em k = 3, o GMM apresentou o maior ARI entre os seis perfis selecionados. A silhueta escolheu k = 2.

### 12.5. “Por que o K-Means não usa a média de todos os pontos como solução?”

Com k = 1, ele usa um único centro e a média global é a solução do objetivo. Com k > 1, o método busca uma média por grupo e precisa decidir como dividir as observações. Essas decisões dependem umas das outras e geram a otimização alternada.

### 12.6. “FCM é um K-Means probabilístico?”

Ele estende a associação exclusiva para pertinências fuzzy, mas não define a mesma interpretação de geração probabilística do GMM. O GMM obtém probabilidades posteriores a partir de densidades e pesos de mistura. São modelos diferentes, mesmo quando ambos fornecem vetores normalizados.

### 12.7. “Por que usar m = 2 no FCM?”

Foram avaliados 1,5, 2 e 2,5. Os perfis empataram na maior silhueta em k = 2, e a ordem da grade reteve m = 2. Em k = 3, variar m alterou as métricas.

### 12.8. “Kernel FCM é FCM depois da Kernel PCA?”

Não neste projeto. O Kernel FCM utiliza diretamente a distância induzida pelo RBF entre observações e protótipos; a Kernel PCA é uma transformação independente da Questão 2.

### 12.9. “Gamma 0,25 foi o melhor valor encontrado?”

Com gamma 0,25 e m = 2, o perfil de referência empatou em maior silhueta em k = 2 e permaneceu pela ordem da grade. Foram testados também gamma 0,05 e 1. Variar gamma muda a escala de proximidade.

### 12.10. “K-Medoids sempre resiste a outliers?”

Ele usa representantes reais e, neste caso, custo sem quadrado da distância, o que pode reduzir a influência de extremos em comparação com K-Means. Ainda depende de k, da geometria e da distribuição dos pontos; não há garantia universal de robustez.

### 12.11. “O que significa covariância full no GMM?”

Cada componente aprende sua própria matriz de covariância completa. As variâncias e relações entre atributos permitem elipsoides com formas e orientações diferentes. Isso aumenta a flexibilidade e a quantidade de parâmetros a estimar.

### 12.12. “Por que a log-verossimilhança é negativa?”

Porque o logaritmo de uma densidade menor que um é negativo. Valores de densidade dependem da escala; negatividade não significa falha. Para o mesmo k e dados, escolhemos a execução com maior log-verossimilhança, ainda que todas sejam negativas.

### 12.13. “O GMM convergiu, então encontrou a melhor solução?”

Ele satisfez o critério de parada registrado pela biblioteca. Pode haver ótimos locais diferentes, razão para repetir inicializações. Uma execução convergida não comprova a melhor solução global.

### 12.14. “UPGMA e average linkage são algoritmos separados?”

Aqui não. A ligação média sobre todos os pares de observações entre grupos corresponde ao UPGMA. A distância base foi Manhattan. Uma média simples das duas distâncias de subgrupos, sem ponderar seus tamanhos, corresponderia a outra regra, WPGMA.

### 12.15. “Por que Manhattan na árvore e euclidiana na silhueta?”

A construção segue a configuração UPGMA com Manhattan, e a avaliação usa a convenção euclidiana comum aos métodos. São operações distintas. Essa escolha precisa ser declarada e limita a interpretação; não se afirma que a silhueta está na mesma geometria de construção da árvore.

### 12.16. “DBSCAN descobre o número de grupos automaticamente?”

Ele não recebe k, mas seu resultado depende de eps, min_samples e da escala dos atributos. Portanto, o número emerge da configuração de densidade; isso não significa ausência de hiperparâmetros ou descoberta do número verdadeiro de classes.

### 12.17. “Os seis pontos de ruído são erros na base?”

Não há evidência disso. São flores não incorporadas às regiões densas sob os parâmetros adotados. Poderiam ser pontos legítimos de regiões menos densas.

### 12.18. “Por que não selecionar a semente de maior silhueta?”

Porque a regra experimental é selecionar primeiro pela função objetivo do algoritmo, para cada k. Trocar o critério das sementes mudaria o protocolo. A silhueta atua na escolha entre valores de k das execuções já selecionadas.

### 12.19. “Qual é a diferença entre 252 e 1.195?”

Os 1.195 ajustes incluem os 1.120 da busca particional, os 24 do DBSCAN, as 50 chamadas de k = 1 e a árvore UPGMA. O recorte final contém os 250 ajustes dos perfis particionais escolhidos, a árvore e o DBSCAN selecionado.

### 12.20. “PCA escolhe os dois atributos mais importantes?”

PCA cria novos eixos como combinações lineares dos atributos. Não é uma simples seleção de duas colunas. Os coeficientes mostram como cada variável participa de uma componente.

### 12.21. “95,80% de variância é 95,80% de informação preservada?”

É correto falar em variância retida na representação padronizada. Informação é uma noção mais ampla: uma direção de baixa variância ainda pode conter uma diferença relevante para determinada tarefa. Não use esse percentual como acurácia ou informação biológica geral.

### 12.22. “Por que as coordenadas da PCA podem aparecer invertidas?”

O sinal de um autovetor pode ser trocado. A nuvem pode ser espelhada sem alterar variância, distâncias na projeção ou informação representada. Uma inversão do eixo, por si só, não é inconsistência do resultado.

### 12.23. “Por que não apresentar variância explicada da Kernel PCA como na PCA?”

Os autovalores registrados pertencem ao kernel centralizado. Não estão na escala da variância dos atributos de entrada. Normalizar somente os dois valores retidos não recupera o percentual da variância original explicada.

### 12.24. “Perplexidade 30 significa 30 clusters?”

Não. É uma escala de vizinhança definida pela entropia das afinidades condicionais. Não determina uma quantidade de grupos nem exatamente 30 vizinhos com peso igual.

### 12.25. “Min_dist = 0,1 é a menor distância possível no UMAP?”

Não é uma restrição rígida sobre todos os pares do resultado. Influencia a curva de similaridade de baixa dimensão e a compactação favorecida. Pontos podem aparecer mais próximos que esse valor.

### 12.26. “t-SNE ganhou do UMAP?”

O t-SNE teve maior trustworthiness com dez vizinhos nesta configuração. Não houve estudo de estabilidade, comparação de tempo ou avaliação global suficiente para declarar superioridade geral. PCA e UMAP ficaram muito próximos no mesmo diagnóstico.

### 12.27. “Os gráficos provam que existem três grupos?”

Eles mostram relações e sobreposições projetadas; as cores foram fornecidas pelas espécies conhecidas. A visualização pode distorcer densidades e separações. Para afirmar clusters, precisamos considerar o método de agrupamento, seus parâmetros e critérios de avaliação.

### 12.28. “Usar as espécies para pintar o gráfico causa vazamento?”

Pintar depois de ajustar permite interpretação sem alterar o ajuste. Haveria influência supervisionada se as espécies fossem usadas para ajustar os grupos ou orientar a escolha das configurações apresentadas como não supervisionadas. O fluxo principal passa apenas X aos ajustes.

### 12.29. “As dez sementes são validação cruzada?”

Não. São dez inicializações sobre as mesmas 150 flores. Não houve divisão em folds, reamostragem ou estimativa de desempenho fora da amostra.

### 12.30. “Qual seria um próximo passo?”

Comparar escalas dos atributos, repetir t-SNE e UMAP com várias sementes e medir preservação em diferentes escalas de vizinhança.

### 12.31. “Qual método tem menor custo computacional?”

O projeto não apresenta um benchmark de tempo que sustente um vencedor. Conceitualmente, métodos baseados em todas as distâncias ou em matrizes de kernel podem consumir memória quadrática em n. Na Iris, a matriz de distâncias ou kernel tem 150 × 150 = 22.500 posições, e a forma condensada das distâncias tem 11.175 pares. Em bases maiores, essas estruturas crescem rapidamente. Não converta essa observação em uma comparação de tempos que não foi medida.

### 12.32. “Quem implementou os algoritmos?”

O projeto implementa a organização experimental e adaptadores sobre bibliotecas. Usamos K-Means, GMM, DBSCAN, PCA, Kernel PCA e t-SNE do scikit-learn; FCM e Kernel FCM do fcmeans; PAM do kmedoids; hierarquia do SciPy; UMAP do umap-learn. A contribuição do código inclui controlar as chamadas, padronizar dados, selecionar execuções, tratar saídas e persistir métricas e parâmetros.

## 13. Erros de interpretação a evitar

| Evite dizer | Formulação tecnicamente correta |
|---|---|
| “Os algoritmos provaram que há duas espécies.” | “A silhueta favoreceu duas regiões geométricas na configuração avaliada.” |
| “ARI de 0,9039 é 90,39% de acerto.” | “O ARI mede concordância ajustada entre partições.” |
| “FCM fornece a probabilidade de cada espécie.” | “FCM fornece pertinências aos grupos; as espécies não entram no ajuste.” |
| “GMM treinou uma gaussiana por espécie.” | “GMM ajustou componentes sem acesso às espécies.” |
| “A melhor execução foi a de maior silhueta.” | “A melhor execução por k foi escolhida pelo objetivo; a silhueta escolheu k.” |
| “Escolhemos k = 3 porque seu ARI era melhor.” | “O protocolo escolheu k = 2; k = 3 foi examinado para interpretação posterior.” |
| “O DBSCAN teve maior silhueta e venceu.” | “Na amostra comum de 144 flores, os sete métodos coincidiram.” |
| “PCA preservou 95,80% das classes.” | “PC1 e PC2 retiveram 95,80% da variância dos atributos padronizados.” |
| “Autovalores da Kernel PCA são percentuais.” | “São valores do espectro da matriz de kernel centralizada.” |
| “A ilha maior tem mais variabilidade original.” | “Área e densidade em mapas não lineares podem ser distorcidas.” |
| “Uma semente fixa garante estabilidade.” | “Ela auxilia a reprodução daquela execução; estabilidade exige comparação.” |
| “Dez execuções são dez conjuntos de dados.” | “São dez inicializações na mesma base.” |
| “UPGMA foi treinado cinco vezes.” | “Uma árvore foi construída e dela foram extraídos cinco cortes.” |
| “Os 252 ajustes incluem as quatro projeções.” | “252 é a contagem principal da Q1; a Q2 tem quatro técnicas separadas.” |
| “Convergência garante ótimo global.” | “Convergência indica que o critério de parada foi satisfeito.” |

## 14. Revisão rápida antes da apresentação

### 14.1. Uma frase por algoritmo

- **K-Means:** alterna atribuição ao centro mais próximo e atualização pela média, minimizando soma de quadrados.
- **FCM:** atualiza centros e pertinências fuzzy, minimizando distâncias ponderadas por `uᵐ`.
- **Kernel FCM:** usa pertinências com distância RBF e protótipos no espaço de entrada nesta variante.
- **K-Medoids:** procura observações reais que minimizem o custo de representar os grupos.
- **GMM/EM:** alterna responsabilidades probabilísticas e atualização das gaussianas para aumentar a log-verossimilhança.
- **UPGMA:** une grupos pela menor distância média e gera uma hierarquia reutilizável em vários cortes.
- **DBSCAN:** conecta regiões densas e permite deixar pontos como ruído.
- **PCA:** projeta em direções lineares ortogonais de maior variância.
- **Kernel PCA:** encontra componentes no espaço implícito de um kernel centralizado.
- **t-SNE:** aproxima distribuições de afinidade por um mapa otimizado, com ênfase local.
- **UMAP:** constrói um grafo de vizinhanças e otimiza sua disposição em baixa dimensão.

### 14.2. Símbolos que aparecem nas equações

| Símbolo | Significado neste guia |
|---|---|
| n | Quantidade de flores: 150 |
| d | Quantidade de atributos originais: 4 |
| k | Quantidade de grupos ou componentes; na métrica local, quantidade de vizinhos |
| xᵢ | Vetor de atributos da flor i |
| cᵢ | Rótulo do grupo atribuído à flor i |
| μⱼ ou vⱼ | Centro ou protótipo do grupo j |
| uᵢⱼ | Pertinência fuzzy da flor i ao grupo j |
| m | Expoente de difusividade fuzzy: 2 no projeto |
| rᵢⱼ | Responsabilidade posterior do componente j no GMM |
| πⱼ | Peso de mistura do componente j |
| Σⱼ | Covariância do componente j |
| gamma / γ | Escala do kernel RBF: 0,25 na configuração apresentada |
| eps / ε | Raio de vizinhança do DBSCAN: 0,8 |
| λ | Autovalor, com significado dependente da matriz analisada |
| zᵢ | Coordenada projetada; na seção de padronização, zᵢⱼ é o valor padronizado |
| argmin / argmax | Índice que alcança o menor ou maior valor |

### 14.3. Autoavaliação

Antes de apresentar, tente responder sem ler:

- [ ] Consigo explicar a pergunta do projeto em um minuto?
- [ ] Sei por que a padronização afeta as distâncias?
- [ ] Consigo diferenciar centroide, medoide, pertinência e probabilidade?
- [ ] Sei explicar ao menos uma atualização de cada algoritmo?
- [ ] Consigo justificar a contagem 250 + 1 + 1?
- [ ] Sei a diferença entre seleção da semente e seleção de k?
- [ ] Sei por que k = 1 não recebe silhueta zero?
- [ ] Consigo explicar o contraste do GMM em k = 2 e k = 3?
- [ ] Lembro que a silhueta do DBSCAN exclui quatro pontos?
- [ ] Sei dizer o que PC1 e PC2 explicam e o que não explicam?
- [ ] Consigo diferenciar Kernel PCA e Kernel FCM?
- [ ] Sei explicar perplexidade e min_dist sem confundi-los com clusters?
- [ ] Consigo interpretar trustworthiness sem chamá-lo de acurácia?
- [ ] Lembro que os agrupadores foram ajustados em 4D, não nos mapas 2D?
- [ ] Sei quais limitações são sustentadas pelo desenho experimental?

Se faltar tempo de estudo, priorize: protocolo, sete mecanismos de agrupamento, diferença silhueta/ARI, GMM em k = 3, DBSCAN, PCA e leitura responsável de mapas. As fórmulas completas de kernel, t-SNE e UMAP aprofundam a defesa, mas não precisam substituir essas ideias essenciais.

## 15. Fontes e aprofundamento

### 15.1. Evidências locais do projeto

Os dados e resultados específicos deste guia vêm destes arquivos, que devem prevalecer sobre exemplos genéricos da internet:

- [Artigo revisado](docs/artigo/artigo_ieee_revisado.pdf): fundamentação, protocolo, resultados e limitações; fonte editável em [Typst](docs/artigo/artigo_ieee_revisado.typ).
- [Código dos agrupadores](codigo/algoritmos.py) e [orquestração das questões](codigo/questoes.py): implementação efetivamente chamada.
- [Resumo Q1](resultados/resumo_agrupamentos.csv) e [métricas por k](resultados/metricas_por_k.csv): números das tabelas de agrupamento.
- [Contingências](resultados/contingencias.json) e [execuções Q1](resultados/execucoes_questao_1.json): membros dos grupos, objetivos, pertinências, probabilidades e árvore.
- [Execuções Q2](resultados/execucoes_questao_2.json): parâmetros, coordenadas, variâncias, autovalores, KL e trustworthiness.
- [Metadados Q1](resultados/metadados_questao_1.json) e [Q2](resultados/metadados_questao_2.json): padronização e versões registradas.
- [Coeficientes PCA](resultados/pca_componentes.csv) e [loadings](resultados/pca_loadings.csv): pesos e convenção usados na interpretação.
- [Verificação do artigo revisado](docs/artigo/verificacao_revisao.md): alcance da conferência e exclusão de afirmações sem artefatos.

FCM e Kernel FCM também foram conferidos no código da biblioteca instalada, incluindo atualização de pertinências, tratamento de distância zero e inicialização do KFCM por FCM.

### 15.2. Documentação técnica consultada

Estas fontes oficiais apoiam a explicação geral; as configurações numéricas do projeto vêm dos arquivos locais. Páginas online podem descrever versões diferentes da biblioteca instalada: a implementação local e seus metadados definem o experimento apresentado.

- [KMeans — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).
- [Agrupamento e avaliação — scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
- [Misturas gaussianas e EM — scikit-learn](https://scikit-learn.org/stable/modules/mixture.html).
- [Ligação hierárquica, UPGMA e matriz Z — SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html).
- [PCA — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html).
- [KernelPCA — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html).
- [TSNE — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html).
- [van der Maaten e Hinton. Visualizing Data using t-SNE. JMLR, 2008](https://jmlr.org/papers/v9/vandermaaten08a.html).
- [Funcionamento do UMAP — documentação oficial](https://umap-learn.readthedocs.io/en/latest/how_umap_works.html).
- [Parâmetros do UMAP — documentação oficial](https://umap-learn.readthedocs.io/en/latest/parameters.html).
- [Trustworthiness — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.trustworthiness.html).

Para as referências acadêmicas de FCM, Kernel FCM, K-Medoids, silhueta, ARI e demais métodos, consulte a bibliografia do artigo revisado. Este guia explica a base técnica e sua aplicação no projeto; não afirma ter refeito a revisão integral de todos os trabalhos citados pelo artigo.
