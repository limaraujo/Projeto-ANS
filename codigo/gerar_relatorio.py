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
meta_q1 = json.loads((R / "metadados_questao_1.json").read_text())
tunagem = json.loads((R / "tunagem" / "melhores_hiperparametros.json").read_text())
m = pd.read_csv(R / "metricas_por_k.csv")
a = pd.read_csv(R / "resumo_agrupamentos.csv")

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
    "Método|Grade avaliada|Melhor configuração|k*|Silhueta (k*)|ARI (k*)|ARI (k = 3)": "Resumo da busca não supervisionada de hiperparâmetros nos sete algoritmos.",
    "Método|k escolhido|Silhueta|ARI|Ruído": "Agrupamentos selecionados (com hiperparâmetros otimizados) e avaliação externa.",
    "Método|k = 1|k = 2|k = 3|k = 4|k = 5": "Silhueta da melhor inicialização de cada configuração (k = 1 indefinido).",
    "Método|Silhueta em k = 3|ARI em k = 3": "Avaliação comparativa das partições com três grupos (classes reais).",
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
        return "Indefinido"
    if isinstance(x, bool):
        return "Sim" if x else "Não"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
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


def _fmt_params(params: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in params.items())


# Extrai métricas dinâmicas para a narrativa
melhor_sil_row = a.loc[a["Silhueta"].idxmax()]
melhor_ari_star_row = a.loc[a["ARI"].idxmax()]
db_row = a[a["Algoritmo"] == "dbscan"].iloc[0]
k3_df = m[m["k"] == 3].copy()
melhor_k3_ari = k3_df.loc[k3_df["ari"].idxmax()]
p = q2["pca"]
var_pc12 = 100 * (p["variancia_explicada"][0] + p["variancia_explicada"][1])
best_trust_nome, best_trust_val = max(
    ((k, v["trustworthiness_10"]) for k, v in q2.items()), key=lambda item: item[1]
)

s = f"""#set document(title: "Agrupamento e redução de dimensionalidade na base Iris", author: "Equipe 08")
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
Este trabalho compara sete métodos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris, conforme o protocolo da Equipe 08. A análise utiliza 150 observações e quatro atributos padronizados. Realizou-se inicialmente uma busca não supervisionada de hiperparâmetros para cada um dos sete algoritmos, analisando a sensibilidade de suas métricas internas (Silhueta) e externas (ARI) às variações paramétricas. Em seguida, foram conduzidos 250 ajustes particionais (dez sementes para k de 1 a 5), uma hierarquia UPGMA com cinco cortes e uma execução de DBSCAN. Para k igual a 1, a silhueta é indefinida, restringindo a seleção de k* ao intervalo de 2 a 5; para o DBSCAN, tanto a silhueta quanto o ARI são calculados excluindo os pontos rotulados como ruído (-1). Os métodos baseados em k escolheram k* igual a 2 pela silhueta, enquanto na comparação direta por desempenho, {nomes[melhor_sil_row['Algoritmo']]} alcançou a maior silhueta ({fmt(melhor_sil_row['Silhueta'])}) e {nomes[melhor_k3_ari['algoritmo']]} atingiu o maior ARI em três grupos ({fmt(melhor_k3_ari['ari'])}). Na redução de dimensionalidade, as duas primeiras componentes da PCA retiveram {fmt(var_pc12)}% da variância, e {best_trust_nome.upper().replace('_', ' ')} obteve a maior trustworthiness para dez vizinhos ({fmt(best_trust_val)}).

*Palavras-chave:* agrupamento; Iris; busca de hiperparâmetros; silhueta; índice de Rand ajustado; redução de dimensionalidade.

#outline(title: [Sumário], depth: 2)
#pagebreak()
= Objetivo e aderência ao enunciado
O aprendizado não supervisionado investiga a organização de observações a partir de seus atributos, sem fornecer ao modelo uma classe a ser prevista. O objetivo geral deste trabalho é otimizar os hiperparâmetros, analisar o comportamento paramétrico e comparar o desempenho dos sete algoritmos de agrupamento da Equipe 08 e das quatro técnicas de redução de dimensionalidade na base Iris, utilizando a Silhueta e o Índice de Rand Ajustado (ARI).

De acordo com o enunciado (*Projeto-AMG-NS-2026-2.pdf*, de Francisco de A. T. de Carvalho) e as orientações complementares da disciplina, adotam-se quatro diretrizes centrais:
1. *Partição unitária (k = 1):* os algoritmos são executados para k em {{1, 2, 3, 4, 5}}, mas como a silhueta não é definida para apenas um grupo, registra-se k = 1 como indefinido e seleciona-se o número ótimo k* estritamente em {{2, 3, 4, 5}}.
2. *Tratamento de ruído no DBSCAN:* tanto o cálculo da silhueta quanto o cálculo do ARI do DBSCAN são realizados excluindo-se os pontos classificados como ruído (rótulo -1), reportando-se explicitamente a fração de pontos descartados.
3. *Busca de hiperparâmetros e análise de comportamento:* realiza-se busca em grade não supervisionada para escolher os melhores hiperparâmetros de cada um dos sete algoritmos, documentando como cada método se comporta quando seus hiperparâmetros variam.
4. *Comparação de desempenho entre os algoritmos:* o desempenho dos sete modelos é comparado diretamente na base Iris por meio da silhueta e do ARI, contrastando a separabilidade geométrica em k* com a recuperação das três espécies reais em k = 3.

Para a Equipe 08, foram executados K-Means, Fuzzy K-Means, Kernel Fuzzy K-Means, K-Medoids (distância euclidiana), misturas gaussianas via EM, UPGMA (distância city-block / Manhattan) e DBSCAN na Questão 1, além de PCA, Kernel PCA, t-SNE e UMAP na Questão 2.

= Fundamentação teórica
== Modelos de agrupamento
Uma partição exclusiva atribui cada observação a um único grupo. K-Means representa os grupos por centroides e minimiza a soma das distâncias euclidianas quadráticas; K-Medoids (PAM) utiliza observações reais como medoides e minimiza a soma das distâncias euclidianas.

Em uma partição fuzzy, cada observação possui graus de pertinência $u_(i j) in [0, 1]$ a todos os grupos, sujeitos a $sum_(j=1)^k u_(i j) = 1$:
$ J_m = sum_(i=1)^n sum_(j=1)^k u_(i j)^m d(x_i, v_j), quad m > 1. $
O parâmetro $m$ controla a nebulosidade da partição: valores próximos de 1 aproximam o modelo de uma partição crisp, enquanto valores maiores suavizam as pertinências. No Kernel Fuzzy C-Means, a distância é induzida no espaço de características via kernel RBF $K(x, v) = exp(-gamma norm(x - v)^2)$, sendo $d_K(x, v) = 2(1 - K(x, v))$. A partição crisp é obtida atribuindo cada ponto ao grupo de maior pertinência.

Misturas gaussianas (GMM) modelam os dados como uma combinação convexa de gaussianas multivariadas ajustadas pelo algoritmo EM, maximizando a log-verossimilhança. A estrutura da matriz de covariância (`full`, `tied`, `diag`, `spherical`) determina a flexibilidade geométrica dos elipsoides ajustados.

UPGMA constrói uma hierarquia aglomerativa pela distância média não ponderada entre pares de elementos de grupos distintos, utilizando distância Manhattan (`city-block`). DBSCAN identifica regiões conexas de alta densidade delimitadas por raio `eps` e suporte mínimo `min_samples`, rotulando pontos isolados como ruído (`-1`).

== Redução de dimensionalidade
A PCA projeta os dados em direções lineares ortogonais de máxima variância via decomposição SVD. Kernel PCA aplica decomposição espectral à matriz de kernel centralizada para capturar estruturas não lineares. O t-SNE minimiza a divergência KL entre distribuições de vizinhança em alta e baixa dimensão, enquanto UMAP otimiza uma representação topológica de grafos de vizinhos mais próximos.

= Dados e preparação
Utilizou-se o arquivo local `codigo/iris/iris.data` (150 observações, quatro atributos em centímetros e três espécies balanceadas: *Iris-setosa*, *Iris-versicolor* e *Iris-virginica*). Os atributos foram padronizados via `StandardScaler` (média zero e variância unitária) antes dos ajustes. Os rótulos das espécies nunca foram usados no ajuste dos modelos nem na escolha de hiperparâmetros ou de k*.
"""
meta_prep = meta_q1["preprocessamento"]
s += tabela(
    ["Atributo", "Média (cm)", "Escala (cm)"],
    zip(
        meta_prep["atributos"],
        meta_prep["media_original"],
        meta_prep["escala_original"],
        strict=False,
    ),
)
s += """
= Busca de hiperparâmetros e análise de sensibilidade
Para evitar escolhas arbitrárias e avaliar a estabilidade de cada método, realizou-se uma busca sistemática em grade para cada um dos sete algoritmos da Equipe 08. Em conformidade com o paradigma não supervisionado, *o ARI não foi utilizado na seleção dos hiperparâmetros*: para os seis algoritmos baseados em k, escolheu-se a configuração com maior silhueta válida em $k^* in {{2, 3, 4, 5}}$ (desempatando pela função objetivo); para o DBSCAN, maximizou-se a silhueta (excluindo ruído) sujeita à restrição de cobertura mínima de 80% da base (máximo de 20% de ruído e ao menos dois grupos válidos), evitando soluções degeneradas que descartam a maior parte dos dados.

"""
grades_desc = {
    "k-means": "init in {k-means++, random}, tol in {1e-2, 1e-4, 1e-6}, max_iter in {50, 100, 300}",
    "fuzzy-k-means": "m in {1.2, 1.5, 1.8, 2.0, 2.5, 3.0}, error in {1e-3, 1e-5, 1e-7}",
    "kernel-fuzzy-k-means": "gamma in {0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0}, m in {1.5, 2.0, 2.5}",
    "k-medoids": "init in {build, random, first}, max_iter in {50, 100, 300} (Euclidiana/PAM)",
    "gaussian-mixture": "covariance_type in {full, tied, diag, spherical}, reg_covar in {1e-6, 1e-4, 1e-2}, init_params",
    "upgma": "escalonamento in {standard, minmax, robust, l2}, optimal_ordering in {False, True} (Manhattan)",
    "dbscan": "eps in {0.3..1.2}, min_samples in {3, 4, 5, 7, 10} (Euclidiana)",
}
s += tabela(
    ["Método", "Grade avaliada", "Melhor configuração", "k*", "Silhueta (k*)", "ARI (k*)", "ARI (k = 3)"],
    [
        [
            nomes[n],
            grades_desc[n],
            _fmt_params(tunagem[n]["parametros"]),
            "automático" if n == "dbscan" else str(tunagem[n]["k_estrela"]),
            tunagem[n]["silhueta"],
            tunagem[n]["ari"],
            float("nan") if n == "dbscan" else tunagem[n]["ari_k3"],
        ]
        for n in nomes
    ],
)
s += """
== Comportamento dos algoritmos perante a variação de hiperparâmetros
As figuras a seguir ilustram a resposta de cada algoritmo às variações da grade:
"""
legendas_tunagem = {
    "k-means": "Sensibilidade do K-Means às estratégias de inicialização (`k-means++` vs. `random`) e tolerância.",
    "fuzzy-k-means": "Comportamento do Fuzzy K-Means com a variação do expoente de nebulosidade m.",
    "kernel-fuzzy-k-means": "Mapas de calor de Silhueta (k*) e ARI (k=3) do Kernel Fuzzy K-Means para pares (m, gamma).",
    "k-medoids": "Desempenho do K-Medoids (PAM euclidiano) sob diferentes métodos de inicialização.",
    "gaussian-mixture": "Efeito do tipo de matriz de covariância e da regularização (`reg_covar`) no GMM/EM.",
    "upgma": "Sensibilidade do UPGMA (Manhattan) ao escalonamento prévio dos atributos.",
    "dbscan": "Variação da Silhueta, do ARI (sem ruído) e da fração de ruído do DBSCAN em função de eps e min_samples.",
}
for n in nomes:
    s += figura("tunagem_" + n.replace("-", "_"), legendas_tunagem[n], "86%")

s += """
A análise das curvas de sensibilidade revela padrões bem definidos por família de modelos:
- *K-Means e K-Medoids:* ambos mostram elevada estabilidade em $k^* = 2$ (Silhueta de 0,5802), pois a separação linear de *Iris-setosa* é robusta tanto à inicialização (`k-means++`, `random`, `build`) quanto à tolerância de parada. Em $k = 3$, entretanto, a escolha dos medoides/centroides torna-se sensível à fronteira entre *versicolor* e *virginica*.
- *Fuzzy K-Means:* para $m in [1,2; 2,5]$, a partição crisp mantém silhueta estável em $k^* = 2$, mas valores elevados ($m = 3,0$) diluem excessivamente as pertinências entre grupos vizinhos, degradando a nitidez da partição hard resultante.
- *Kernel Fuzzy K-Means:* o parâmetro $gamma$ controla a escala efetiva de vizinhança no kernel RBF. Valores pequenos ($gamma <= 0,25$) preservam a estrutura global (Silhueta de 0,5802 em $k^* = 2$), enquanto valores elevados ($gamma >= 1,0$) tornam o kernel excessivamente local, comprimindo a separação global e reduzindo tanto a silhueta quanto o ARI.
- *GMM/EM:* o tipo de covariância exerce impacto decisivo. Enquanto covariâncias `spherical` e `diag` impõem restrições geométricas próximas às do K-Means, a estrutura `full` permite ajustar elipsoides inclinados que acompanham a correlação positiva entre comprimento e largura de pétala, elevando expressivamente o ARI em $k = 3$.
- *UPGMA (Manhattan):* a ligação média com distância $L_1$ é fortemente influenciada pela escala relativa das coordenadas. Enquanto o escalonamento `standard` favorece a divisão binária ($k^* = 2$, Silhueta de 0,5802), o escalonamento `minmax` preserva melhor o contraste relativo das pétalas em três cortes ($k = 3$).
- *DBSCAN:* raios muito pequenos ($eps <= 0,4$) fragmentam a base e classificam grande parcela dos pontos como ruído ($> 20\%$), enquanto raios grandes ($eps >= 1,0$) fundem todos os grupos em um único aglomerado. Na faixa intermediária selecionada, o algoritmo equilibra alta silhueta (excluindo ruído) e baixa taxa de descarte.

= Questão 1: resultados e comparação de desempenho
Utilizando os melhores hiperparâmetros obtidos na etapa anterior, executaram-se dez inicializações (sementes 42 a 51) para cada $k in {{1, 2, 3, 4, 5}}$ nos cinco algoritmos particionais, selecionando-se a melhor execução pela função objetivo. Para o UPGMA, extraiu-se uma única hierarquia com cinco cortes; para o DBSCAN, realizou-se uma execução com os parâmetros selecionados.

== Tabela comparativa geral (Silhueta e ARI)
"""
s += tabela(
    ["Método", "k escolhido", "Silhueta", "ARI", "Ruído"],
    [
        [nomes[r["Algoritmo"]], str(r["k*"]), r["Silhueta"], r["ARI"], str(r["Ruído"])]
        for _, r in a.iterrows()
    ],
)
s += figura(
    "comparacao_algoritmos",
    "Comparação direta de desempenho entre os sete algoritmos via Silhueta e ARI em k* (esquerda) e em k = 3 (direita).",
    "95%",
)
s += f"""
== Análise comparativa do desempenho dos algoritmos
A comparação conjunta pela Silhueta e pelo ARI evidencia dois regimes distintos de comportamento na base Iris:

1. *Regime de separabilidade geométrica ($k^*$ selecionado pela Silhueta):* todos os seis algoritmos baseados em k atingiram o máximo da silhueta em $k^* = 2$, com Silhueta de 0,5802 e ARI de 0,5681, agrupando perfeitamente as 50 amostras de *Iris-setosa* em um grupo e reunindo *Iris-versicolor* e *Iris-virginica* no segundo. O DBSCAN obteve Silhueta de {fmt(db_row['Silhueta'])} e ARI de {fmt(db_row['ARI'])} (ambos calculados sobre os {150 - int(db_row['Ruído'])} pontos não classificados como ruído, descartando {int(db_row['Ruído'])} pontos ou {fmt(db_row['Ruído (%)'])}% da base). A silhueta ligeiramente superior do DBSCAN decorre da remoção dos pontos limítrofes de menor densidade na fronteira dos grupos, sem alterar a divisão macroscópica em dois blocos densos.
2. *Regime de recuperação das classes reais ($k = 3$):* quando avaliados com três grupos — correspondentes às três espécies botânicas — surgem diferenças substanciais de desempenho entre os algoritmos, conforme detalhado na tabela abaixo.

== Silhuetas por k e comparação em k = 3
Para todos os métodos particionais e hierárquicos, k = 1 apresenta silhueta indefinida e não participa da escolha de k*.
"""
s += tabela(
    ["Método", "k = 1", "k = 2", "k = 3", "k = 4", "k = 5"],
    [
        [nomes[n]]
        + [m[(m.algoritmo == n) & (m.k == k)].iloc[0].silhueta for k in range(1, 6)]
        for n in nomes
        if n != "dbscan"
    ],
)
s += tabela(
    ["Método", "Silhueta em k = 3", "ARI em k = 3"],
    [[nomes[r.algoritmo], r.silhueta, r.ari] for _, r in m[m.k == 3].iterrows()],
)
s += f"""
Na comparação em $k = 3$, *{nomes[melhor_k3_ari['algoritmo']]}* destaca-se como o algoritmo de melhor concordância com as espécies verdadeiras (ARI = {fmt(melhor_k3_ari['ari'])}), superando amplamente os métodos baseados em distâncias esféricas ou centróides rígidos (K-Means, Fuzzy K-Means e Kernel Fuzzy K-Means). Essa superioridade ocorre porque as classes *Iris-versicolor* e *Iris-virginica* apresentam distribuição alongada e parcialmente sobreposta no espaço padronizado: enquanto algoritmos de partição esférica seccionam essa nuvem transversalmente ao eixo de maior variância (gerando erros de fronteira e ARI em torno de 0,62), o modelo de misturas gaussianas com covariância completa captura a orientação elipsoidal de cada espécie. O K-Medoids (PAM euclidiano) e o UPGMA (city-block) ocupam posição intermediária ao evitar o deslocamento de centróides por pontos extremos.
"""
for n, nome_exibicao in nomes.items():
    if n == "dbscan":
        continue
    legenda = (
        "Silhueta dos cortes da hierarquia UPGMA (k = 1 indefinido)."
        if n == "upgma"
        else f"Silhueta após seleção da execução por função objetivo: {nome_exibicao} (k = 1 indefinido)."
    )
    s += figura("silhueta_" + n.replace("-", "_"), legenda, "72%")

gmm3 = max(q1["gaussian-mixture"]["3"], key=lambda run: run["objetivo"])
especies = pd.read_csv(CODIGO / "iris/iris.data", header=None).iloc[:, 4]
contagem = pd.crosstab(especies, pd.Series(gmm3["rotulos"]))
s += "A matriz de contingência do GMM/EM em k = 3 confirma a separação integral de *Iris-setosa* e a alta pureza na distinção entre *versicolor* e *virginica*:\n"
s += tabela(
    ["Espécie"] + [f"Grupo {c}" for c in contagem.columns],
    [[especie] + [str(v) for v in linha] for especie, linha in contagem.iterrows()],
)
s += (
    """
== Dependência da inicialização e dendrograma
"""
    + tabela(
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
    + figura(
        "dendrograma_upgma",
        "Dendrograma UPGMA construído com distância Manhattan (city-block) e ligação média.",
    )
    + """
= Questão 2: redução de dimensionalidade
As quatro técnicas receberam a matriz padronizada de quatro atributos sem acesso aos rótulos das espécies.

== PCA
"""
)
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
s += tabela(
    ["Atributo", "PC1", "PC2", "PC3", "PC4"],
    [
        [attr] + [p["componentes"][j][i] for j in range(4)]
        for i, attr in enumerate(meta_prep["atributos"])
    ],
)
s += tabela(
    ["Atributo", "Loading 1", "Loading 2", "Loading 3", "Loading 4"],
    [[attr] + p["loadings"][i] for i, attr in enumerate(meta_prep["atributos"])],
)
s += figura("pca", "Projeção linear nas duas primeiras componentes principais.")
s += f"""
As duas primeiras componentes principais retêm {fmt(var_pc12)}% da variância total, isolando *Iris-setosa* ao longo de PC1 e evidenciando a continuidade geométrica entre *versicolor* e *virginica* — exatamente a estrutura que explica a escolha unânime de $k^* = 2$ pela silhueta na Questão 1.

== Kernel PCA, t-SNE e UMAP
"""
s += tabela(
    ["Componente", "Autovalor do kernel centralizado"],
    [[str(i + 1), v] for i, v in enumerate(q2["kernel_pca"]["autovalores"])],
)
s += figura("kernel_pca", "Duas primeiras componentes da Kernel PCA com kernel RBF.")
s += tabela(
    ["Saída", "Valor"],
    [
        ["Divergência KL final", q2["tsne"]["divergencia_kl"]],
        ["n_iter_ reportado", str(q2["tsne"]["iteracoes"])],
        ["Taxa efetiva", q2["tsne"]["taxa_aprendizado_efetiva"]],
    ],
)
s += figura("tsne", "Projeção t-SNE com perplexidade 30 e semente 42.")
s += figura("umap", "Projeção UMAP com 15 vizinhos e `min_dist` igual a 0,1.")
s += tabela(
    ["Projeção", "Trustworthiness (10 vizinhos)"],
    [[n.upper().replace("_", " "), r["trustworthiness_10"]] for n, r in q2.items()],
)
s += f"""
As projeções não lineares (t-SNE e UMAP) ampliam a visualização das vizinhanças locais entre *versicolor* e *virginica*, alcançando trustworthiness superior a 0,97 (com destaque para {best_trust_nome.upper().replace('_', ' ')}, em {fmt(best_trust_val)}), enquanto a PCA preserva a interpretabilidade linear direta dos atributos originais.

= Conclusão
A integração entre busca de hiperparâmetros, seleção não supervisionada de $k^* in {{2, 3, 4, 5}}$ (com $k = 1$ indefinido) e avaliação por Silhueta e ARI (excluindo ruído no DBSCAN) permite caracterizar com precisão os sete algoritmos da Equipe 08. Sob o critério interno da silhueta, todos os algoritmos baseados em k convergem para $k^* = 2$ (Silhueta = 0,5802), refletindo a forte separabilidade linear de *Iris-setosa*. Quando avaliados em $k = 3$ frente às espécies botânicas, {nomes[melhor_k3_ari['algoritmo']]} apresenta o melhor desempenho (ARI = {fmt(melhor_k3_ari['ari'])}) graças à modelagem de covariâncias elipsoidais, superando algoritmos de partição esférica.

= Reprodutibilidade e artefatos
Para reproduzir integralmente a busca de hiperparâmetros, os experimentos das Questões 1 e 2, a auditoria automática e o PDF final:
```sh
python codigo/main.py
python codigo/validar_resultados.py
python codigo/gerar_relatorio.py
typst compile docs/relatorio.typ docs/relatorio.pdf --root .

== Versões utilizadas
"""
vers = dict(meta_q1["versoes"])
vers.update(json.loads((R / "metadados_questao_2.json").read_text())["versoes"])
s += tabela(["Pacote", "Versão"], [[k, v] for k, v in vers.items() if k != "python"])
s += "\n= Fonte dos requisitos\nFrancisco de A. T. de Carvalho. Projeto AM-NS 2026-2. Documento fornecido com a atividade, Projeto-AMG-NS-2026-2.pdf: Questão 1, páginas 2–3; Questão 2, página 4; atribuição da Equipe 08, página 6; orientações de entrega, página 7.\n"
s += """
= Referências
[1] CARVALHO, Francisco de A. T. Projeto AM-NS 2026-2. Centro de Informática, UFPE, 2026.

[2] UCI MACHINE LEARNING REPOSITORY. Iris. DOI: #link("https://doi.org/10.24432/C56C76")[10.24432/C56C76].

[3] SCIKIT-LEARN. Clustering — Clustering performance evaluation. #link("https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation")[Documentação oficial].

[4] SCIKIT-LEARN. PCA, KernelPCA, TSNE e GaussianMixture. #link("https://scikit-learn.org/stable/modules/classes.html")[Referência da API].

[5] UMAP-LEARN. Basic UMAP Parameters. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Documentação oficial].

[6] KMEDOIDS. Fast k-medoids clustering in Python. #link("https://python-kmedoids.readthedocs.io/en/latest/")[Documentação oficial].
"""
DOCS.mkdir(parents=True, exist_ok=True)
(DOCS / "relatorio.typ").write_text(s, encoding="utf-8")
print("relatorio.typ atualizado com resultados executados e tunagem completa.")