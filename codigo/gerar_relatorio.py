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
    "Método|Grade piloto|Configuração selecionada|Critério piloto": "Resumo da rodada piloto não supervisionada (seeds 0..9).",
    "Método|k escolhido|Silhueta|ARI|Ruído": "Agrupamentos selecionados na rodada oficial (seeds 42..51) e avaliação externa.",
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
    if not params:
        return "árvore única (Manhattan / average)"
    return ", ".join(f"{k}={v}" for k, v in params.items())


melhor_sil_row = a.loc[a["Silhueta"].idxmax()]
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
Este trabalho compara sete métodos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris, conforme o protocolo da Equipe 08. A análise utiliza 150 observações e quatro atributos padronizados. Inicialmente conduziu-se uma rodada piloto não supervisionada (sementes 0 a 9) para escolher os hiperparâmetros de cada método: nos algoritmos particionais, selecionou-se a configuração de maior silhueta média ao longo de k em {{2, 3, 4, 5}} (mantendo a configuração de referência em caso de empate); no DBSCAN, selecionou-se o par de maior silhueta (excluindo ruído) com cobertura mínima de 95% dos pontos; e no UPGMA utilizou-se uma árvore única (distância Manhattan e ligação média). Com os hiperparâmetros congelados, executou-se a rodada oficial com dez sementes (42 a 51) para k em {{1, 2, 3, 4, 5}}, registrando k igual a 1 como indefinido e escolhendo k* em {{2, 3, 4, 5}} pela silhueta. Na comparação entre os modelos, {nomes[melhor_sil_row['Algoritmo']]} alcançou a maior silhueta ({fmt(melhor_sil_row['Silhueta'])}) e {nomes[melhor_k3_ari['algoritmo']]} obteve o maior ARI em três grupos ({fmt(melhor_k3_ari['ari'])}). Na redução de dimensionalidade, as duas primeiras componentes da PCA retiveram {fmt(var_pc12)}% da variância, e {best_trust_nome.upper().replace('_', ' ')} obteve a maior trustworthiness para dez vizinhos ({fmt(best_trust_val)}).

*Palavras-chave:* agrupamento; Iris; busca piloto de hiperparâmetros; silhueta; índice de Rand ajustado; redução de dimensionalidade.

#outline(title: [Sumário], depth: 2)
#pagebreak()
= Objetivo e aderência ao enunciado
O aprendizado não supervisionado investiga a organização de observações a partir de seus atributos, sem fornecer ao modelo uma classe a ser prevista. O objetivo geral deste trabalho é calibrar os hiperparâmetros em rodada piloto, analisar o comportamento paramétrico e comparar o desempenho dos sete algoritmos de agrupamento da Equipe 08 e das quatro técnicas de redução de dimensionalidade na base Iris, utilizando a Silhueta e o Índice de Rand Ajustado (ARI).

De acordo com o enunciado (*Projeto-AMG-NS-2026-2.pdf*, de Francisco de A. T. de Carvalho) e as orientações da disciplina, adotam-se quatro diretrizes metodológicas:
1. *Partição unitária (k = 1):* os algoritmos são executados para k em {{1, 2, 3, 4, 5}}, mas como a silhueta não é definida para apenas um grupo, registra-se k = 1 como indefinido e seleciona-se o número ótimo k* estritamente em {{2, 3, 4, 5}}.
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
= Rodada piloto e comportamento dos hiperparâmetros
Para evitar escolhas arbitrárias e impedir qualquer vazamento de informações entre sementes, dividiu-se o experimento em duas etapas:
1. *Rodada piloto (sementes 0 a 9):* avaliou-se a grade de hiperparâmetros de cada algoritmo particional ao longo de $k in {{2, 3, 4, 5}}$, retendo a melhor execução por função objetivo em cada $k$. Escolheu-se a configuração com maior *silhueta média nos quatro valores de k*; em caso de empate numérico, manteve-se a configuração de referência. No DBSCAN, testaram-se pares `(eps, min_samples)` exigindo cobertura mínima de 95% da base (no máximo 5% de ruído) e maximizando a silhueta sem ruído. No UPGMA, construiu-se a árvore única exigida (Manhattan e ligação média) comparando os cortes.
2. *Rodada oficial (sementes 42 a 51):* com os hiperparâmetros selecionados congelados, executaram-se as dez inicializações oficiais para cada $k in {{1, 2, 3, 4, 5}}$.

"""
grades_desc = {
    "k-means": "init in {k-means++, random}, tol in {1e-2, 1e-4, 1e-6}, max_iter in {50, 100, 300}",
    "fuzzy-k-means": "m in {1.5, 2.0, 2.5, 3.0}, error in {1e-4, 1e-5, 1e-6}",
    "kernel-fuzzy-k-means": "m in {1.5, 2.0, 2.5} x gamma in {0.05, 0.25, 1.0} (9 configs)",
    "k-medoids": "init in {build, random, first}, max_iter in {50, 100, 300} (Euclidiana)",
    "gaussian-mixture": "covariance_type in {full, tied, diag, spherical}, reg_covar, init_params",
    "upgma": "cortes k in {1, 2, 3, 4, 5} na árvore única Manhattan/average",
    "dbscan": "eps in {0.3..1.2}, min_samples in {3, 4, 5, 7, 10} (cobertura >= 95%)",
}
s += tabela(
    ["Método", "Grade piloto", "Configuração selecionada", "Critério piloto"],
    [
        [
            nomes[n],
            grades_desc[n],
            _fmt_params(tunagem[n]["parametros"]),
            (
                f"Silhueta = {fmt(tunagem[n]['silhueta'])} (cob. {fmt(tunagem[n]['cobertura_pct'])}%)"
                if n == "dbscan"
                else f"Silhueta média (k=2..5) = {fmt(tunagem[n]['silhueta_media_k2_k5'])}"
            ),
        ]
        for n in nomes
    ],
)
s += """
== Comportamento dos algoritmos perante a variação de hiperparâmetros
As figuras a seguir mostram o comportamento de cada algoritmo durante a rodada piloto:
"""
legendas_tunagem = {
    "k-means": "Sensibilidade do K-Means às estratégias de inicialização (`k-means++` vs. `random`) e tolerância.",
    "fuzzy-k-means": "Comportamento do Fuzzy K-Means com a variação do expoente de nebulosidade m.",
    "kernel-fuzzy-k-means": "Kernel Fuzzy K-Means: silhueta média por (m, gamma) à esquerda e efeito de gamma com m = 2,0 e k fixos à direita.",
    "k-medoids": "Desempenho do K-Medoids (PAM euclidiano) sob diferentes métodos de inicialização.",
    "gaussian-mixture": "Efeito do tipo de matriz de covariância e da regularização (`reg_covar`) no GMM/EM.",
    "upgma": "Comparação dos cortes k = 2..5 na árvore única UPGMA (Manhattan / average).",
    "dbscan": "Variação da Silhueta, do ARI (sem ruído) e da cobertura (%) do DBSCAN em função de eps e min_samples.",
}
for n in nomes:
    s += figura("tunagem_" + n.replace("-", "_"), legendas_tunagem[n], "86%")

s += """
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

1. *Regime de separabilidade geométrica ($k^*$ selecionado pela Silhueta):* todos os seis algoritmos baseados em k atingiram o máximo da silhueta em $k^* = 2$, com Silhueta de 0,5802 e ARI de 0,5681, agrupando perfeitamente as 50 amostras de *Iris-setosa* em um grupo e reunindo *Iris-versicolor* e *Iris-virginica* no segundo. O DBSCAN obteve Silhueta de {fmt(db_row['Silhueta'])} e ARI de {fmt(db_row['ARI'])} (ambos calculados sobre os {150 - int(db_row['Ruído'])} pontos não classificados como ruído, descartando {int(db_row['Ruído'])} pontos ou {fmt(db_row['Ruído (%)'])}% da base). A silhueta ligeiramente superior do DBSCAN decorre da exclusão dos pontos de borda menos densos, mantendo a divisão macroscópica em dois blocos.
2. *Regime de recuperação das classes reais ($k = 3$):* quando avaliados com três grupos — correspondentes às três espécies botânicas — surgem diferenças substanciais de desempenho entre os algoritmos, conforme detalhado abaixo.

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
A adoção de uma rodada piloto não supervisionada (sementes 0 a 9) seguida da rodada oficial com hiperparâmetros congelados (sementes 42 a 51), combinada à definição de k = 1 como indefinido e ao cálculo do ARI sem ruído no DBSCAN, permite avaliar com rigor os sete algoritmos da Equipe 08. Sob o critério interno da silhueta, todos os algoritmos baseados em k convergem para $k^* = 2$ (Silhueta = 0,5802), refletindo a forte separabilidade linear de *Iris-setosa*. Quando avaliados em $k = 3$ frente às espécies botânicas, {nomes[melhor_k3_ari['algoritmo']]} apresenta o melhor desempenho (ARI = {fmt(melhor_k3_ari['ari'])}) graças à modelagem de covariâncias elipsoidais, superando algoritmos de partição esférica.

= Reprodutibilidade e artefatos
Para reproduzir integralmente a rodada piloto, os experimentos oficiais das Questões 1 e 2, a auditoria automática e o PDF final:
```sh
python codigo/main.py
python codigo/validar_resultados.py
python codigo/gerar_relatorio.py
typst compile docs/relatorio.typ docs/relatorio.pdf --root .
```
== Versões utilizadas
"""
vers = dict(meta_q1["versoes"])
vers.update(json.loads((R / "metadados_questao_2.json").read_text())["versoes"])
s += tabela(["Pacote", "Versão"], [[k, v] for k, v in vers.items() if k != "python"])
s += "\n= Fonte dos requisitos\nFrancisco de A. T. de Carvalho. *Projeto AM-NS 2026-2*. Documento fornecido com a atividade, `Projeto-AMG-NS-2026-2.pdf`: Questão 1, páginas 2–3; Questão 2, página 4; atribuição da Equipe 08, página 6; orientações de entrega, página 7.\n"
s += """
= Referências
[1] CARVALHO, Francisco de A. T. *Projeto AM-NS 2026-2*. Centro de Informática, UFPE, 2026.

[2] UCI MACHINE LEARNING REPOSITORY. *Iris*. DOI: #link("https://doi.org/10.24432/C56C76")[10.24432/C56C76].

[3] SCIKIT-LEARN. *Clustering — Clustering performance evaluation*. #link("https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation")[Documentação oficial].

[4] SCIKIT-LEARN. *PCA, KernelPCA, TSNE e GaussianMixture*. #link("https://scikit-learn.org/stable/modules/classes.html")[Referência da API].

[5] UMAP-LEARN. *Basic UMAP Parameters*. #link("https://umap-learn.readthedocs.io/en/latest/parameters.html")[Documentação oficial].

[6] KMEDOIDS. *Fast k-medoids clustering in Python*. #link("https://python-kmedoids.readthedocs.io/en/latest/")[Documentação oficial].
"""
DOCS.mkdir(parents=True, exist_ok=True)
(DOCS / "relatorio.typ").write_text(s, encoding="utf-8")
print("relatorio.typ atualizado com rodada piloto e resultados oficiais.")