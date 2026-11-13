"""Gera o relatório Typst a partir dos resultados locais efetivamente executados."""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CODIGO = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
R = ROOT / "resultados"
q2 = json.loads((R / "execucoes_questao_2.json").read_text())
q1 = json.loads((R / "execucoes_questao_1.json").read_text())
m = pd.read_csv(R / "metricas_por_k.csv")
nomes = {
    "k-means": "K-Means",
    "fuzzy-k-means": "Fuzzy K-Means",
    "kernel-fuzzy-k-means": "Kernel Fuzzy K-Means",
    "k-medoids": "K-Medoids",
    "gaussian-mixture": "GMM/EM",
    "upgma": "UPGMA",
    "dbscan": "DBSCAN",
}

LEGENDAS_TABELAS = {
    "Atributo|Média (cm)|Escala (cm)": "Estatísticas dos atributos antes da padronização.",
    "Método|k escolhido|Silhueta|ARI|Ruído": "Agrupamentos selecionados e avaliação externa.",
    "Método|k = 2|k = 3|k = 4|k = 5": "Silhueta da melhor inicialização de cada configuração.",
    "Método|Silhueta em k = 3|ARI em k = 3": "Avaliação descritiva das partições com três grupos.",
    "Método|Mínimo|Máximo": "Intervalos das funções objetivo nas dez sementes para k igual a três.",
    "Componente|Autovalor|Variância (%)|Acumulada (%)": "Espectro e variância explicada da PCA.",
    "Atributo|PC1|PC2|PC3|PC4": "Coeficientes das componentes principais.",
    "Atributo|Loading 1|Loading 2|Loading 3|Loading 4": "Loadings da PCA na convenção adotada.",
    "Componente|Autovalor do kernel centralizado": "Autovalores retidos na Kernel PCA.",
    "Saída|Valor": "Saídas do ajuste de t-SNE.",
    "Projeção|Trustworthiness (10 vizinhos)": "Preservação de vizinhanças nas quatro projeções.",
    "Pacote|Versão": "Versões registradas na execução dos experimentos.",
}


def fmt(x):
    if pd.isna(x):
        return "—"
    if isinstance(x, (float, int)):
        return f"{x:.4f}".replace(".", ",")
    return str(x).replace("_", r"\_")


def tabela(headers, rows):
    cells = ",\n".join("[" + fmt(c) + "]" for row in rows for c in row)
    legenda = LEGENDAS_TABELAS.get(
        "|".join(headers),
        "Contingência entre espécies e grupos do GMM com três componentes.",
    )
    return (
        "#figure(kind: table, supplement: [Tabela], caption: ["
        + legenda
        + "], [\n"
        + "#table(columns: "
        + str(len(headers))
        + ", inset: 5pt, stroke: .35pt, table.header("
        + ",".join("[*" + h + "*]" for h in headers)
        + "),\n"
        + cells
        + "\n)\n])\n"
    )


def figura(nome, legenda, largura="90%"):
    return f'#figure(image("../resultados/figuras/{nome}.png", width: {largura}), caption: [{legenda}])\n'


s = """#set document(title: "Agrupamento e redução de dimensionalidade na base Iris", author: "Equipe 08")
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
Centro de Informática — UFPE \\
Novembro de 2026
]
#pagebreak()
#heading(numbering: none, outlined: false)[Resumo]
Este trabalho compara sete métodos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris, conforme o protocolo da Equipe 08. A análise utiliza 150 observações e quatro atributos padronizados. Foram realizados 250 ajustes particionais, uma hierarquia UPGMA e uma execução de DBSCAN. Os seis métodos com seleção de número de grupos escolheram k igual a 2 pela silhueta, separando as 50 setosas das demais espécies, com silhueta de 0,5802 e índice de Rand ajustado de 0,5681. Em análise complementar, o GMM com três componentes alcançou ARI de 0,9039, evidenciando que separação geométrica e concordância com espécies não são critérios equivalentes. Na redução de dimensionalidade, as duas primeiras componentes da PCA retiveram 95,80% da variância; t-SNE apresentou a maior trustworthiness para dez vizinhos, de 0,9888. Os resultados favorecem a interpretação conjunta de índices internos, avaliação externa e visualizações, com conclusões restritas à configuração experimental utilizada.

*Palavras-chave:* agrupamento; Iris; silhueta; índice de Rand ajustado; redução de dimensionalidade.

#outline(title: [Sumário], depth: 2)
#pagebreak()
= Objetivo e aderência ao enunciado
O aprendizado não supervisionado investiga a organização de observações a partir de seus atributos, sem fornecer ao modelo uma classe a ser prevista. No agrupamento, essa organização depende da representação dos dados, da medida de proximidade e do critério de ajuste. Uma partição geometricamente bem separada pode, portanto, divergir das categorias utilizadas para descrever os objetos no domínio de origem.

A base Iris permite examinar essa questão em um conjunto de pequenas dimensões: quatro medidas de flores são utilizadas para construir os modelos, e três espécies conhecidas permitem interpretar posteriormente os resultados. O objetivo geral deste trabalho é comparar sete métodos de agrupamento e quatro técnicas de redução de dimensionalidade, relacionando os critérios numéricos às estruturas observadas nas figuras.

Os objetivos específicos são selecionar o número de grupos pela silhueta após a escolha da melhor inicialização por função objetivo; avaliar a concordância com as espécies pelo índice de Rand ajustado; examinar a informação preservada nas projeções; e discutir os limites das conclusões. Essas etapas respondem a duas perguntas: qual divisão é favorecida pela geometria dos atributos e quanto dessa organização pode ser representado em duas dimensões?

A única fonte dos requisitos deste trabalho é o documento *Projeto-AMG-NS-2026-2.pdf*, de Francisco de A. T. de Carvalho. Para a Equipe 08, foram executados K-Means, Fuzzy K-Means, Kernel Fuzzy K-Means, K-Medoids euclidiano, misturas gaussianas via EM, UPGMA com distância city-block e DBSCAN. A Questão 2 contempla PCA, Kernel PCA, t-SNE e UMAP, com saídas numéricas, gráficos e interpretação.

O PDF determina dez execuções para cada valor de k de 1 a 5 nos métodos particionais e uma execução para UPGMA e DBSCAN. Foram realizados 250 ajustes particionais, uma hierarquia e um DBSCAN: 252 execuções principais. Os cinco cortes da hierarquia reutilizam o mesmo ajuste. A implementação de Kernel Fuzzy K-Means inicializa seus protótipos com FCM internamente; essas operações internas não são contadas como experimentos independentes. A busca exaustiva de K-Medoids com k igual a 1 é repetida nas dez chamadas, produzindo o mesmo ótimo.

As escolhas de padronização, sementes, kernel, hiperparâmetros e convenções de avaliação abaixo são decisões metodológicas da equipe, não exigências adicionais atribuídas ao PDF. As análises complementares de ARI por k e preservação de vizinhanças não alteram o protocolo de seleção solicitado.

= Fundamentação teórica
== Modelos de agrupamento
Uma partição exclusiva atribui cada observação a um único grupo. K-Means representa os grupos por centroides e minimiza distâncias quadráticas; K-Medoids utiliza observações reais como representantes e, na implementação adotada, minimiza a soma de distâncias euclidianas. Essa diferença entre objetivos pode produzir partições distintas mesmo quando os métodos recebem os mesmos dados [3, 7].

Em uma partição fuzzy, cada observação possui graus de pertinência a todos os grupos. Para dados $x_i$, protótipos $v_j$ e pertinências $u_(i j)$, o Fuzzy C-Means considera
$ J_m = sum_(i=1)^n sum_(j=1)^k u_(i j)^m norm(x_i - v_j)^2, quad sum_(j=1)^k u_(i j) = 1, $
com $m > 1$. A conversão em partição exclusiva escolhe a maior pertinência, descartando informações sobre ambiguidades. No Kernel Fuzzy C-Means, a distância do objetivo é induzida por um kernel. A metodologia explicita a variante computacional efetivamente usada.

Misturas gaussianas representam os dados por uma combinação de distribuições. O algoritmo EM alterna o cálculo de responsabilidades e a atualização de parâmetros, buscando aumentar a verossimilhança. As responsabilidades são probabilidades posteriores sob o modelo, diferentemente dos graus fuzzy. Covariâncias completas permitem componentes com orientações e dispersões distintas [8].

UPGMA constrói uma hierarquia de fusões por distância média entre grupos. Uma única árvore pode ser cortada em diferentes números de grupos. DBSCAN identifica regiões conectadas de alta densidade e admite pontos classificados como ruído; o raio de vizinhança e a quantidade mínima de pontos determinam a estrutura encontrada [3].

== Redução de dimensionalidade
A PCA busca direções lineares ortogonais que maximizam sucessivamente a variância projetada. O espectro permite quantificar a variabilidade retida e os coeficientes relacionam as componentes aos atributos. Kernel PCA aplica uma decomposição espectral ao kernel centralizado para representar relações não lineares [4, 9].

O t-SNE ajusta afinidades entre pares em baixa dimensão por uma divergência entre distribuições. UMAP constrói uma representação de vizinhanças e otimiza sua disposição no espaço reduzido. Esses métodos enfatizam relações locais e produzem eixos sem interpretação direta em centímetros ou em proporção de variância explicada. A aparência de grupos deve ser confrontada com as propriedades do espaço de origem e com medidas de preservação de vizinhanças [5, 6].

= Dados e preparação
Foi utilizado o arquivo local `codigo/iris/iris.data`, com 150 observações e quatro atributos em centímetros: comprimento e largura de sépala e comprimento e largura de pétala. Há 50 observações por espécie: Iris-setosa, Iris-versicolor e Iris-virginica. Linhas completamente vazias são ignoradas. A matriz numérica é separada dos rótulos antes dos ajustes; os rótulos servem apenas à avaliação externa e às cores e símbolos das figuras.

Cada atributo foi transformado pela subtração da média e divisão pelo desvio-padrão populacional, usando StandardScaler. Isso confere escala unitária às variáveis. Essa opção altera a geometria em relação aos dados em centímetros e influencia as conclusões. Não foi feita divisão treino/teste, pois o objetivo é a análise descritiva não supervisionada da base fornecida, e não a estimação de desempenho preditivo em novos dados.
"""
meta = json.loads((R / "metadados_questao_1.json").read_text())["preprocessamento"]
s += "A descrição da base e de seus atributos está disponível no repositório UCI [2]. Foi mantida a versão local fornecida na atividade; resultados de outras versões da Iris não são automaticamente intercambiáveis.\n\n"
s += tabela(
    ["Atributo", "Média (cm)", "Escala (cm)"],
    zip(
        meta["atributos"], meta["media_original"], meta["escala_original"], strict=False
    ),
)
s += """
= Metodologia experimental
== Desenho do estudo
O estudo é descritivo e comparativo e utiliza as 150 observações da base completa. A unidade de execução dos métodos particionais é um ajuste para uma combinação de algoritmo, k e semente. As dez inicializações examinam a dependência do otimizador em relação ao ponto de partida; elas não constituem amostras independentes da população de flores.

O fluxo consiste em carregar e padronizar os quatro atributos, ajustar os modelos sem acesso às espécies, selecionar a inicialização pelo objetivo e escolher k pela silhueta. Somente depois se calcula o ARI. As projeções utilizam a mesma matriz padronizada em um procedimento separado: os agrupamentos são obtidos no espaço de quatro atributos, e não sobre as coordenadas projetadas.

Os recursos computacionais incluem Python, NumPy e pandas para organização dos dados, scikit-learn para estimadores e métricas, SciPy para a hierarquia, fuzzy-c-means para os métodos fuzzy, kmedoids para PAM e umap-learn para UMAP. CSV e JSON armazenam os artefatos, Matplotlib e Seaborn produzem as figuras e Typst compõe o documento. Não foram registrados tempos ou hardware que sustentem comparações de custo computacional.

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

= Questão 1: resultados dos agrupamentos
== Resultados consolidados
"""
a = pd.read_csv(R / "resumo_agrupamentos.csv")
s += tabela(
    ["Método", "k escolhido", "Silhueta", "ARI", "Ruído"],
    [
        [nomes[r["Algoritmo"]], str(r["k*"]), r["Silhueta"], r["ARI"], str(r["Ruído"])]
        for _, r in a.iterrows()
    ],
)
s += """
Todos os seis métodos com seleção de k escolheram dois grupos e produziram a mesma partição, salvo permutação dos identificadores: um grupo contém as 50 setosas e o outro reúne as 50 versicolors e as 50 virginicas. Isso explica a igualdade das métricas, sem implicar igualdade dos centros, pertinências ou funções objetivo.

O DBSCAN reteve 49 setosas em um grupo e 50 versicolors mais 47 virginicas no outro. O ruído contém uma setosa e três virginicas: quatro pontos, ou 2,67% da base. Sua silhueta de 0,5963 supera numericamente 0,5802, mas exclui esses quatro pontos; portanto, não demonstra superioridade global. O ARI de 0,5518 é inferior ao dos demais resultados selecionados.

== Silhuetas e comparação por k
A tabela apresenta as silhuetas após a seleção pela função objetivo. Para todos os métodos, k igual a 1 é indefinido.
"""
s += tabela(
    ["Método", "k = 2", "k = 3", "k = 4", "k = 5"],
    [
        [nomes[n]]
        + [m[(m.algoritmo == n) & (m.k == k)].iloc[0].silhueta for k in range(2, 6)]
        for n in nomes
        if n != "dbscan"
    ],
)
for n, nome_exibicao in nomes.items():
    if n == "dbscan":
        continue
    legenda = (
        "Silhueta dos cinco cortes de uma única hierarquia UPGMA."
        if n == "upgma"
        else "Silhueta após seleção da execução por função objetivo: "
        + nome_exibicao
        + "."
    )
    s += figura("silhueta_" + n.replace("-", "_"), legenda, "72%")
s += """
A silhueta cai ao subdividir o bloco formado por versicolor e virginica. Isso favorece k igual a 2, apesar das três classes biológicas. O efeito é especialmente claro no GMM: a partição de três componentes tem menor silhueta, embora corresponda muito melhor às espécies. A tabela seguinte usa k igual a 3 apenas para interpretação posterior; ela não substitui a seleção exigida no enunciado.
"""
s += tabela(
    ["Método", "Silhueta em k = 3", "ARI em k = 3"],
    [[nomes[r.algoritmo], r.silhueta, r.ari] for _, r in m[m.k == 3].iterrows()],
)
s += """
O GMM obtém ARI de 0,9039 em k igual a 3, contra 0,5681 na solução escolhida pela silhueta. A modelagem por covariâncias completas permite grupos com formas distintas, enquanto a silhueta euclidiana favorece separação compacta. UPGMA alcança ARI de 0,7184 e K-Medoids 0,6765 em três grupos. Esses valores mostram que a avaliação interna e a recuperação das espécies respondem a perguntas diferentes. Não houve escolha retroativa pelo melhor ARI.

"""
gmm3 = max(q1["gaussian-mixture"]["3"], key=lambda run: run["objetivo"])
especies = pd.read_csv(CODIGO / "iris/iris.data", header=None).iloc[:, 4]
contagem = pd.crosstab(especies, pd.Series(gmm3["rotulos"]))
s += "A tabela de contingência da execução selecionada do GMM em k igual a 3 torna essa diferença explícita. Os identificadores dos grupos são arbitrários.\n"
s += tabela(
    ["Espécie"] + [f"Grupo {c}" for c in contagem.columns],
    [[especie] + [str(v) for v in linha] for especie, linha in contagem.iterrows()],
)
s += """
As 50 setosas formam um grupo exclusivo. Outro contém 45 versicolors, e o terceiro contém as 50 virginicas e cinco versicolors. Essa correspondência é observada após o ajuste e não representa acurácia preditiva em novas amostras. Em particular, ARI igual a 0,9039 não significa que 90,39% das flores foram classificadas corretamente.

== Dependência da inicialização
Para examinar a variação entre as dez sementes, a tabela apresenta o intervalo da função objetivo em k igual a 3. Cada linha deve ser interpretada na escala do próprio algoritmo; objetivos de métodos diferentes não são diretamente comparáveis.
"""
s += tabela(
    ["Método", "Mínimo", "Máximo"],
    [
        [
            nomes[n],
            min(run["objetivo"] for run in ks["3"]),
            max(run["objetivo"] for run in ks["3"]),
        ]
        for n, ks in q1.items()
        if n not in ("upgma", "dbscan")
    ],
)
s += (
    """
K-Means e GMM exibem diferenças entre as soluções encontradas. Fuzzy K-Means e Kernel Fuzzy K-Means apresentam objetivos praticamente iguais entre sementes na precisão exibida. Essa concordância numérica não prova ótimo global. No GMM, as dez execuções com três componentes registraram convergência pelo critério da biblioteca, embora tenham alcançado valores distintos de log-verossimilhança. Convergir e atingir a melhor solução possível são propriedades diferentes.

O orçamento de inicializações faz parte do protocolo. Uma chamada com `n_init` igual a 10, repetida dez vezes, representaria cem inicializações internas por configuração. Nesta entrega, os métodos particionais utilizam dez chamadas com uma inicialização principal em cada uma, observadas as particularidades de implementação descritas na metodologia.

== Hierarquia e dendrograma
"""
    + figura(
        "dendrograma_upgma",
        "Uma única árvore UPGMA, construída com distância Manhattan e ligação média.",
    )
    + """
O dendrograma registra a sequência de fusões; a altura corresponde à distância de ligação média na escala padronizada. O corte em dois grupos separa setosa das demais espécies. Cortes mais finos aumentam a correspondência com as espécies em alguns casos, mas reduzem a silhueta euclidiana. A árvore representa relações de proximidade, e não uma filogenia ou evidência causal.

= Questão 2: redução de dimensionalidade
As quatro técnicas receberam a mesma matriz padronizada de quatro atributos, sem rótulos de espécie durante o ajuste. As cores foram adicionadas posteriormente. PCA foi ajustada com quatro componentes para apresentar o espectro completo; seu gráfico usa apenas as duas primeiras. Os outros métodos foram ajustados diretamente para duas dimensões. As 150 coordenadas de cada método foram exportadas em CSV, com identificador de observação e espécie.

== PCA
As saídas de variância explicada, componentes e valores singulares seguem as definições do estimador PCA do scikit-learn [4].

A PCA utiliza decomposição SVD completa. As componentes são combinações lineares ortogonais dos atributos padronizados. A tabela mostra os autovalores da covariância amostral, as proporções explicadas e a soma acumulada.
"""
)
p = q2["pca"]
s += tabela(
    ["Componente", "Autovalor", "Variância (%)", "Acumulada (%)"],
    [
        [
            f"PC{i+1}",
            p["autovalores"][i],
            100 * p["variancia_explicada"][i],
            100 * p["variancia_acumulada"][i],
        ]
        for i in range(4)
    ],
)
s += "As duas primeiras componentes retêm 95,80% da variância da matriz padronizada. As duas omitidas representam 4,20%; portanto, o gráfico bidimensional preserva a maior parte da variabilidade linear, mas não toda a informação.\n\nCoeficientes das componentes (autovetores):\n"
s += tabela(
    ["Atributo", "PC1", "PC2", "PC3", "PC4"],
    [
        [attr] + [p["componentes"][j][i] for j in range(4)]
        for i, attr in enumerate(meta["atributos"])
    ],
)
s += """
PC1 atribui pesos positivos ao comprimento de sépala e às duas medidas de pétala, com peso negativo para largura de sépala. PC2 é dominada pela largura de sépala (coeficiente 0,9256). O sinal de um autovetor pode ser invertido sem alterar a solução; a interpretação depende dos pesos relativos.

Adotou-se como convenção de loadings o autovetor multiplicado pela raiz do autovalor. Esses valores não são exatamente os coeficientes acima nem, sem ajuste de escala amostral, as correlações com os atributos, pois StandardScaler usa variância populacional e a PCA reporta covariância amostral.
"""
s += tabela(
    ["Atributo", "Loading 1", "Loading 2", "Loading 3", "Loading 4"],
    [[attr] + p["loadings"][i] for i, attr in enumerate(meta["atributos"])],
)
s += figura("pca", "Projeção linear nas duas primeiras componentes principais.")
s += """
A projeção destaca a separação de setosa e a maior proximidade entre versicolor e virginica. A interpretação dos eixos pelos atributos é uma vantagem da PCA neste conjunto pequeno. A elevada variância retida não garante separação perfeita entre as espécies, pois variância e discriminação de classes não são o mesmo objetivo.

== Kernel PCA
Foi usado kernel RBF com gamma igual a 0,25, matriz de kernel centralizada, duas componentes e decomposição espectral densa. Essa escolha corresponde a uma escala característica de distância igual a 2 nas unidades padronizadas, pois o kernel vale exp(−1) nessa distância. O valor foi fixado, sem busca orientada pelas espécies.
"""
s += tabela(
    ["Componente", "Autovalor do kernel centralizado"],
    [[str(i + 1), v] for i, v in enumerate(q2["kernel_pca"]["autovalores"])],
)
s += figura("kernel_pca", "Duas primeiras componentes da Kernel PCA com kernel RBF.")
s += """
Os autovalores acima pertencem à matriz de kernel centralizada, não à covariância dos quatro atributos originais. Como foram retidas apenas duas componentes, não se divide sua soma para declarar uma porcentagem de variância original explicada. A transformação curva a organização dos pontos e evidencia relações não lineares, mas torna a interpretação por pesos dos atributos menos direta. A escolha de gamma altera a noção de proximidade e não foi submetida a análise de sensibilidade.

== t-SNE
Os parâmetros e as saídas de otimização são interpretados conforme a documentação de t-SNE [5].

Foram usados perplexidade 30, inicialização por PCA, distância euclidiana, semente 42, exagero inicial 12, método Barnes-Hut com ângulo 0,5 e limite de 1.000 iterações. A taxa de aprendizado automática efetiva foi 50. A perplexidade controla a escala de vizinhança, sem representar um número de grupos.
"""
s += tabela(
    ["Saída", "Valor"],
    [
        ["Divergência KL final", q2["tsne"]["divergencia_kl"]],
        ["n_iter_ reportado", str(q2["tsne"]["iteracoes"])],
        ["Taxa efetiva", q2["tsne"]["taxa_aprendizado_efetiva"]],
    ],
)
s += figura("tsne", "Projeção t-SNE com perplexidade 30 e semente 42.")
s += """
Setosa aparece isolada à esquerda, enquanto versicolor e virginica ocupam regiões próximas e parcialmente misturadas à direita. A divergência KL final quantifica o objetivo de preservação de afinidades desse ajuste, não uma taxa de erro de classificação. O atributo `n_iter_` reporta 999; não se toma o esgotamento do orçamento como prova de ótimo global. Distâncias entre ilhas, tamanhos e áreas não devem ser interpretados como distâncias e densidades fiéis do espaço original. Os eixos não têm o significado de componentes lineares nem proporção de variância explicada.

== UMAP
O papel do número de vizinhos e da distância mínima segue a documentação oficial do UMAP [6].

Foram usados 15 vizinhos, `min_dist` igual a 0,1, spread igual a 1, duas dimensões, distância euclidiana, inicialização espectral e semente 42. A execução foi limitada a uma thread para reprodutibilidade. O número de épocas foi deixado no modo automático da biblioteca, registrado como `n_epochs` nulo nos parâmetros; não se declara aqui um contador de épocas observado.
"""
s += figura("umap", "Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.")
s += """
Setosa forma uma região separada à esquerda. Versicolor e virginica aparecem à direita, com tendência de organização vertical e pontos misturados na transição. Os 15 vizinhos definem a escala da estrutura local; `min_dist` controla a compactação permitida na projeção. Distâncias entre regiões desconectadas e a orientação dos eixos não têm interpretação física direta. A presença de subestruturas visuais não demonstra novas classes biológicas.

== Preservação de vizinhanças nas projeções
Como diagnóstico adicional, calculou-se trustworthiness com dez vizinhos e distância euclidiana entre a matriz padronizada e cada representação 2D. Essa medida penaliza vizinhos artificiais introduzidos pela projeção; valores mais próximos de 1 são melhores nesse critério. Ela não utiliza espécies e não mede toda a estrutura global, nem equivale a acurácia.
"""
s += tabela(
    ["Projeção", "Trustworthiness (10 vizinhos)"],
    [[n.upper().replace("_", " "), r["trustworthiness_10"]] for n, r in q2.items()],
)
s += """
Nesta execução, t-SNE apresentou o maior valor local (0,9888), seguido de UMAP (0,9783) e PCA (0,9782), muito próximos entre si. Kernel PCA obteve 0,9322. Essa ordenação é específica dos hiperparâmetros, da semente e da vizinhança escolhida; não constitui superioridade universal. PCA oferece interpretação direta e alta retenção de variância, enquanto t-SNE e UMAP enfatizam relações locais. Não foram executados agrupamentos sobre as projeções: as métricas da Questão 1 pertencem ao espaço original padronizado.

= Discussão integrada
A escolha de dois grupos pelos seis métodos mostra que, sob a padronização e as configurações adotadas, a separação de setosa é a estrutura mais favorecida pela silhueta. A igualdade das partições selecionadas não estabelece equivalência entre algoritmos: quando k é fixado em três, as diferenças no ARI evidenciam que suas hipóteses e objetivos conduzem a soluções distintas.

O GMM com três componentes esclarece a diferença entre qualidade interna e concordância externa. A flexibilidade das covariâncias é compatível com uma partição que acompanha melhor as espécies, mas essa evidência não torna três o número selecionado pelo protocolo. As espécies fornecem uma referência biológica, enquanto a silhueta avalia a separação relativa na geometria escolhida. A análise ganha significado ao manter explícitas essas duas perguntas.

As projeções reforçam a interpretação da separação de setosa e da proximidade entre as outras espécies. PCA oferece uma síntese linear com elevada retenção de variância e eixos interpretáveis pelos atributos; t-SNE e UMAP complementam a leitura de relações locais. O maior valor de trustworthiness do t-SNE informa a preservação de vizinhos neste ajuste, mas não estabelece vantagem para classificação nem superioridade universal.

A comparação com DBSCAN exige considerar qualidade geométrica e cobertura. Sua silhueta utiliza 146 observações, enquanto a dos demais métodos utiliza 150. A exclusão dos quatro pontos de ruído modifica o conjunto avaliado. Uma conclusão sobre sua utilidade deve considerar também a proporção de ruído e a finalidade da análise.

= Limitações do estudo
Os resultados se referem ao arquivo local Iris, a uma padronização e a um conjunto fixo de hiperparâmetros. Dez reinicializações reduzem a dependência da inicialização dos agrupamentos, mas não asseguram ótimo global. Houve uma execução de cada projeção; não foram estimados intervalos de confiança ou estabilidade entre sementes. A sensibilidade de gamma, perplexidade, vizinhos e eps permanece fora desta análise.

A análise é restrita a uma base pequena e balanceada. Não foram realizados testes de significância, reamostragens ou avaliação em novas observações. As dez inicializações descrevem variação do otimizador neste conjunto, sem estimar incerteza populacional. As cores das projeções auxiliam a interpretação por espécie, mas não constituem evidência independente das coordenadas e métricas analisadas.

== Tunagem opcional
O projeto disponibiliza `codigo/tunagem.py` para comparar configurações sobre os atributos padronizados. Para DBSCAN, a grade combina `eps` de 0,4; 0,6; 0,8 e 1,0 com `min_samples` de 3, 5 e 10. Uma segunda grade usa fatores de 0,75; 1; 1,5 e 2 sobre a mediana da distância ao quinto vizinho, contando o próprio ponto. Para Kernel Fuzzy C-Means, combina gamma de 0,05; 0,25 e 1 com k de 1 a 5 e sementes de 42 a 51, retendo o menor objetivo dentro de cada configuração.

O script grava suas saídas em `resultados/tunagem/`. Este relatório descreve a disponibilidade desse recurso, sem apresentar resultados de execução das grades ou atribuir a elas a escolha dos hiperparâmetros principais. Na comparação de configurações DBSCAN, a silhueta deve ser acompanhada da quantidade de grupos e da fração de ruído; no Kernel FCM, a função objetivo serve para selecionar sementes dentro da mesma configuração.

= Conclusão
O protocolo aplicado à base Iris evidencia uma separação predominante entre setosa e o conjunto formado por versicolor e virginica. Os seis métodos com seleção de k escolheram dois grupos e alcançaram silhueta de 0,5802 e ARI de 0,5681. Com três componentes, o GMM obteve ARI de 0,9039, demonstrando que a estrutura favorecida pelo índice interno e a concordância com espécies são critérios distintos. O DBSCAN encontrou dois grupos e quatro pontos de ruído, exigindo atenção à cobertura dos pontos utilizados em cada métrica.

Na redução de dimensionalidade, as duas primeiras componentes da PCA retiveram 95,80% da variância e permitiram relacionar os eixos aos atributos. t-SNE apresentou a maior preservação local de vizinhanças no diagnóstico adotado, enquanto Kernel PCA e UMAP ampliaram a leitura visual. As duas questões convergem para uma interpretação: setosa é claramente distinguível nesta representação, enquanto a organização das outras espécies depende mais do método e do critério de análise.

O principal resultado é a caracterização do alcance de cada procedimento sob um protocolo explícito. Função objetivo, silhueta, ARI, variância explicada e preservação de vizinhanças avaliam propriedades diferentes. Sua interpretação conjunta explica as soluções observadas sem reduzir a comparação a um único número ou generalizar os resultados para outras configurações.

= Reprodutibilidade e artefatos
Os experimentos são executados por `codigo/main.py`; os agrupamentos estão implementados em `codigo/algoritmos.py` e a execução das duas questões em `codigo/questoes.py`. O arquivo `codigo/requirements.txt` fixa as versões instaladas. O relatório utiliza os resultados persistidos em `resultados/`, e não as explorações históricas.

Os JSONs de execuções armazenam parâmetros, sementes, funções objetivo, rótulos, centros e pertinências ou probabilidades, quando aplicáveis. O arquivo `metricas_por_k.csv` identifica as sementes vencedoras e as métricas por k. Os metadados registram a padronização e versões; o arquivo da Questão 2 também registra o SHA-256 dos dados. Coordenadas, componentes e loadings são fornecidos em CSV, e as onze figuras ficam em `resultados/figuras`.

O comando `python codigo/validar_resultados.py` audita a contagem de 252 ajustes, as sementes, a seleção por objetivo, as métricas recalculadas, a normalização das pertinências e probabilidades, o argmax dos rótulos e a finitude das quatro projeções. O resultado da auditoria consta em `resultados/validacao.json`. Isso verifica o protocolo e a consistência numérica dos artefatos, sem constituir prova de otimalidade dos algoritmos.

Para reproduzir, no ambiente com as dependências instaladas:
```sh
python codigo/main.py
python codigo/validar_resultados.py
python codigo/gerar_relatorio.py
typst compile docs/relatorio.typ docs/relatorio.pdf --root .
```
O relatório é gerado com tabelas dos arquivos de resultados. Sua discussão textual corresponde à configuração padrão desta entrega; mudanças de parâmetros exigem rever a interpretação, mesmo que as tabelas sejam atualizadas automaticamente.

== Versões utilizadas
"""
vers = json.loads((R / "metadados_questao_1.json").read_text())["versoes"]
vers.update(json.loads((R / "metadados_questao_2.json").read_text())["versoes"])
s += tabela(["Pacote", "Versão"], [[k, v] for k, v in vers.items() if k != "python"])
s += "\n= Fonte dos requisitos\nFrancisco de A. T. de Carvalho. *Projeto AM-NS 2026-2*. Documento fornecido com a atividade, `Projeto-AMG-NS-2026-2.pdf`: Questão 1, páginas 2–3; Questão 2, página 4; atribuição da Equipe 08, página 6; orientações de entrega, página 7. O documento informa entrega e apresentação da Equipe 08 em 26/11/2026 e duração de 30 minutos, incluindo discussão.\n"
s += """
= Referências
[1] CARVALHO, Francisco de A. T. *Projeto AM-NS 2026-2*. Centro de Informática, UFPE, 2026. Enunciado local: `Projeto-AMG-NS-2026-2.pdf`.

[2] UCI MACHINE LEARNING REPOSITORY. *Iris*. DOI: #link("https://doi.org/10.24432/C56C76")[10.24432/C56C76]. #link("https://archive.ics.uci.edu/dataset/53/iris")[Página da base].

[3] SCIKIT-LEARN. *Clustering — Clustering performance evaluation*. #link("https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation")[Documentação das métricas de agrupamento].

[4] SCIKIT-LEARN. *PCA*. #link("https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html")[Documentação do estimador].

[5] SCIKIT-LEARN. *TSNE*. #link("https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html")[Documentação do estimador].

[6] UMAP-LEARN. *Basic UMAP Parameters*. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Documentação dos parâmetros].

[7] KMEDOIDS. *Fast k-medoids clustering in Python*. #link("https://python-kmedoids.readthedocs.io/en/latest/")[Documentação oficial das implementações PAM e variantes].

[8] SCIKIT-LEARN. *Gaussian mixture models*. #link("https://scikit-learn.org/stable/modules/mixture.html")[Documentação dos modelos de mistura e do algoritmo EM].

[9] SCIKIT-LEARN. *KernelPCA*. #link("https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html")[Documentação do estimador].

As referências on-line fundamentam as definições e a interpretação dos métodos. As versões efetivamente usadas nos experimentos são as registradas na seção anterior; a documentação on-line pode corresponder a versões posteriores.
"""
(DOCS / "relatorio.typ").write_text(s, encoding="utf-8")
print("relatorio.typ atualizado com resultados executados.")
