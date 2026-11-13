# Especificação de requisitos — Agrupamento e redução de dimensionalidade na base Iris

## 1. Objetivo

Implementar e avaliar sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade sobre a base **Iris** (UCI), registrando métricas, visualizações e interpretações dos resultados.

**Base:** https://archive.ics.uci.edu/dataset/53/iris

## 2. Escopo e algoritmos

### 2.1. Agrupamento (Questão 1)

| ID | Algoritmo | Categoria | Execuções |
|---|---|---|---|
| A01 | K-Means | Partição exclusiva (crisp) | 10 por valor de *k* |
| A02 | Fuzzy K-Means | Partição não exclusiva (fuzzy) | 10 por valor de *k* |
| A03 | Kernel Fuzzy K-Means | Partição não exclusiva (fuzzy) | 10 por valor de *k* |
| A04 | K-Medoids (distância euclidiana) | Partição exclusiva | 10 por valor de *k* |
| A05 | Misturas Gaussianas via EM | Modelo probabilístico | 10 por valor de *k* |
| A06 | Aglomerativo hierárquico UPGMA (*average linkage*, distância Manhattan/*city-block*) | Hierárquico | 1 execução |
| A07 | DBSCAN | Baseado em densidade | 1 execução |

> **Nota:** UPGMA corresponde ao método de ligação média não ponderada (*unweighted average linkage*); não são algoritmos separados.

Para os cinco algoritmos particionais, executar dez inicializações para cada $k \in \{1,2,3,4,5\}$: **250 ajustes**. Somando UPGMA e DBSCAN, são **252 execuções** no total. A extração de cinco cortes do dendrograma não constitui cinco novas execuções do hierárquico.

### 2.2. Redução de dimensionalidade (Questão 2)

| ID | Técnica | Saída requerida |
|---|---|---|
| D01 | PCA | Saídas pertinentes e gráfico PC1 × PC2 |
| D02 | Kernel PCA | Saídas pertinentes e gráfico das duas primeiras componentes |
| D03 | t-SNE | Saídas pertinentes e projeção 2D |
| D04 | UMAP | Saídas pertinentes e projeção 2D |

## 3. Requisitos funcionais — dados

- **RF01 — Carregamento:** carregar a Iris com quatro atributos numéricos e rótulos das espécies.
- **RF02 — Separação:** separar matriz de atributos `X` e rótulos verdadeiros `y`. Não usar `y` no treinamento dos agrupamentos; utilizá-lo somente em análises externas e na identificação visual das espécies.
- **RF03 — Pré-processamento:** disponibilizar padronização dos atributos e registrar a escolha aplicada aos experimentos.
- **RF04 — Reprodutibilidade:** registrar parâmetros, sementes aleatórias, versões de bibliotecas e resultados de cada execução.

## 4. Requisitos funcionais — execução dos agrupamentos

- **RF05 — Algoritmos com k:** executar A01–A05 dez vezes para cada $k \in \{1,2,3,4,5\}$.
- **RF06 — Melhor execução:** selecionar, **para cada algoritmo e cada k**, a execução que otimiza sua própria função objetivo:

  | Algoritmo | Critério |
  |---|---|
  | K-Means | Minimizar soma de quadrados intragrupo (inércia) |
  | Fuzzy K-Means | Minimizar função objetivo fuzzy |
  | Kernel Fuzzy K-Means | Minimizar função objetivo no espaço de características |
  | K-Medoids | Minimizar soma das distâncias aos medoides |
  | Misturas Gaussianas (EM) | Maximizar log-verossimilhança |

  As funções objetivo **não são diretamente comparáveis entre algoritmos diferentes**.

- **RF07 — Partição fuzzy para crisp:** para A02 e A03, converter cada observação para o grupo de maior pertinência: $c_i=\arg\max_j u_{ij}$.
- **RF08 — Partição probabilística para crisp:** para A05, atribuir cada observação ao componente com maior probabilidade posterior: $c_i=\arg\max_j P(z_i=j\mid x_i)$.
- **RF09 — Hierárquico:** executar UPGMA uma vez usando Manhattan e *average linkage*, gerar dendrograma e extrair partições para $k \in \{1,2,3,4,5\}$.
- **RF10 — DBSCAN:** executar uma vez com `eps` e `min_samples` documentados; registrar clusters e observações classificadas como ruído.

## 5. Requisitos funcionais — métricas e seleção

- **RF11 — Silhueta:** calcular o coeficiente de silhueta das partições crisp selecionadas para os algoritmos A01–A06, quando definido.
- **RF12 — Escolha de k:** selecionar $k^*=\arg\max_k \mathrm{Sil}(k)$ dentre os valores com silhueta válida.
- **RF13 — Índice de Rand Ajustado (ARI):** calcular o ARI da partição escolhida em $k^*$ comparando-a com os rótulos das espécies da Iris.
- **RF14 — DBSCAN:** registrar número de clusters, quantidade e percentual de ruído, silhueta (se definida) e ARI. Documentar o tratamento do ruído nas métricas.

### 5.1. Limitações matemáticas e convenções

A silhueta **não é definida para k = 1**; nesse caso registrar `NaN` (ou equivalente), não zero. Logo, para os algoritmos com escolha de k, a busca por $k^*$ considera, em condições usuais, $k \in \{2,3,4,5\}$, desde que a partição contenha ao menos dois rótulos distintos e menos rótulos do que observações.

Para DBSCAN, uma convenção defensável é calcular o **ARI com todas as observações**, mantendo `-1` como rótulo do ruído, e calcular a **silhueta sobre os pontos não classificados como ruído**, caso sobrem ao menos dois clusters válidos. Essa convenção deve constar no relatório, pois afeta a comparabilidade.

> A seleção da melhor execução deve ocorrer pela **função objetivo**, antes de calcular e comparar silhuetas. Não selecionar a execução de melhor silhueta em substituição ao critério do enunciado.

## 6. Requisitos funcionais — visualização e síntese

- **RF15 — Silhueta × k:** gerar um gráfico para cada um dos seis algoritmos A01–A06, com eixo horizontal `k`, eixo vertical `Sil`, identificação de $k^*$ e indicação da indefinição para `k = 1`.
- **RF16 — Dendrograma:** gerar dendrograma correspondente ao UPGMA com distância Manhattan.
- **RF17 — Tabela comparativa:** consolidar algoritmo, $k^*$ (quando aplicável), silhueta e ARI.

| Algoritmo | k* | Silhueta | ARI |
|---|---:|---:|---:|
| K-Means | — | — | — |
| Fuzzy K-Means | — | — | — |
| Kernel Fuzzy K-Means | — | — | — |
| K-Medoids | — | — | — |
| EM | — | — | — |
| UPGMA | — | — | — |
| DBSCAN | Automático | — | — |

Os campos devem ser preenchidos somente após a execução.

## 7. Requisitos funcionais — redução de dimensionalidade

- **RF18 — PCA:** executar PCA; apresentar componentes, variância explicada, variância acumulada, pesos dos atributos (*loadings*, conforme convenção adotada) e gráfico PC1 × PC2; comentar os resultados.
- **RF19 — Kernel PCA:** executar Kernel PCA; registrar kernel e parâmetros, autovalores disponibilizados e coordenadas transformadas; gerar gráfico 2D e comentar. **Não** pressupor proporções de variância explicada diretamente comparáveis às da PCA linear.
- **RF20 — t-SNE:** executar t-SNE para duas dimensões; registrar hiperparâmetros, coordenadas, divergência KL final (se disponível), projeção 2D e comentários.
- **RF21 — UMAP:** executar UMAP para duas dimensões; registrar hiperparâmetros, coordenadas, projeção 2D e comentários.

## 8. Requisitos não funcionais

| ID | Requisito | Descrição |
|---|---|---|
| RNF01 | Linguagem | Python |
| RNF02 | Modularidade | Separar algoritmos, dados, métricas, visualização e experimentação |
| RNF03 | Reprodutibilidade | Registrar sementes e configurações |
| RNF04 | Persistência | Salvar métricas, gráficos e execuções |
| RNF05 | Configurabilidade | Ajustar parâmetros sem alterar a lógica principal |
| RNF06 | Robustez | Tratar falhas e métricas indefinidas |
| RNF07 | Rastreabilidade | Associar resultados aos parâmetros e à execução |
| RNF08 | Comparabilidade | Manter critérios consistentes de pré-processamento e avaliação |

## 9. Estrutura sugerida de diretórios

```text
iris-clustering/
├── data/
│   └── iris.csv
├── src/
│   ├── data/
│   │   ├── loader.py
│   │   └── preprocessing.py
│   ├── clustering/
│   │   ├── kmeans.py
│   │   ├── fuzzy_kmeans.py
│   │   ├── kernel_fuzzy_kmeans.py
│   │   ├── kmedoids.py
│   │   ├── gaussian_mixture.py
│   │   ├── hierarchical.py
│   │   └── dbscan.py
│   ├── dimensionality_reduction/
│   │   ├── pca.py
│   │   ├── kernel_pca.py
│   │   ├── tsne.py
│   │   └── umap.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── selection.py
│   ├── visualization/
│   │   ├── clustering_plots.py
│   │   └── reduction_plots.py
│   └── experiments/
│       ├── clustering.py
│       └── reduction.py
├── results/
│   ├── metrics/
│   ├── plots/
│   └── executions/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

Os módulos dos algoritmos podem ser **adaptadores de bibliotecas existentes**; o enunciado não exige reimplementações matemáticas do zero.

## 10. Configuração inicial dos experimentos

```python
ALGORITMOS = {
    "kmeans": {
        "nome": "K-Means", "tipo": "crisp",
        "execucoes": 10, "valores_k": [1, 2, 3, 4, 5],
        "objetivo": "minimizar",
    },
    "fuzzy_kmeans": {
        "nome": "Fuzzy K-Means", "tipo": "fuzzy",
        "execucoes": 10, "valores_k": [1, 2, 3, 4, 5],
        "objetivo": "minimizar",
    },
    "kernel_fuzzy_kmeans": {
        "nome": "Kernel Fuzzy K-Means", "tipo": "fuzzy",
        "execucoes": 10, "valores_k": [1, 2, 3, 4, 5],
        "objetivo": "minimizar",
    },
    "kmedoids": {
        "nome": "K-Medoids", "tipo": "crisp",
        "distancia": "euclidean", "execucoes": 10,
        "valores_k": [1, 2, 3, 4, 5], "objetivo": "minimizar",
    },
    "em": {
        "nome": "Gaussian Mixture", "tipo": "probabilistico",
        "execucoes": 10, "valores_k": [1, 2, 3, 4, 5],
        "objetivo": "maximizar",
    },
    "upgma": {
        "nome": "UPGMA", "tipo": "hierarquico",
        "distancia": "manhattan", "linkage": "average",
        "execucoes": 1, "valores_k": [1, 2, 3, 4, 5],
    },
    "dbscan": {
        "nome": "DBSCAN", "tipo": "densidade",
        "execucoes": 1, "valores_k": None,
    },
}
```

## 11. Decisões metodológicas sugeridas

| Tema | Decisão inicial | Observação |
|---|---|---|
| Padronização | `StandardScaler` | Registrar que os experimentos usam atributos padronizados |
| Silhueta | Distância euclidiana como referência comparativa | Explicitar que difere da distância Manhattan usada para construir o UPGMA |
| K-Medoids | Euclidiana | Exigência do enunciado |
| UPGMA | Manhattan + *average linkage* | Exigência do enunciado |
| DBSCAN | Estabelecer regra justificável para `eps` e `min_samples` | Evitar ajuste oportunista em função do ARI |

A maior silhueta **não implica necessariamente** maior concordância com as três espécies da Iris. A silhueta é uma métrica interna; o ARI é uma avaliação externa com rótulos de referência.

## 12. Contrato sugerido para resultados

Cada ajuste deve produzir registro estruturado, com campos aplicáveis ao método:

```python
{
    "algoritmo": "kmeans",
    "k": 3,
    "execucao": 1,
    "seed": 42,
    "parametros": {},
    "funcao_objetivo": None,
    "labels": None,
    "silhueta": None,
    "ari": None,
}
```

**Atenção:** `silhueta` e `ari` podem ser calculados em etapa posterior. Para métodos fuzzy/probabilísticos, armazenar também pertinências ou probabilidades posteriores, quando aplicável. Para DBSCAN, `k` é derivado do resultado e não um hiperparâmetro de entrada.

## 13. Critérios de aceitação

- [ ] Executar os sete algoritmos de agrupamento.
- [ ] Realizar as 252 execuções previstas.
- [ ] Registrar parâmetros, sementes e resultados de cada ajuste.
- [ ] Selecionar por função objetivo a melhor execução de A01–A05 em cada `k`.
- [ ] Converter partições fuzzy e probabilísticas para crisp.
- [ ] Calcular as silhuetas válidas, tratando `k = 1` como indefinido.
- [ ] Selecionar o melhor `k` para A01–A06 por silhueta.
- [ ] Calcular o ARI das partições selecionadas e do DBSCAN.
- [ ] Registrar explicitamente o tratamento do ruído do DBSCAN.
- [ ] Gerar seis gráficos Sil × k e um dendrograma.
- [ ] Consolidar os resultados em tabela comparativa.
- [ ] Executar PCA, Kernel PCA, t-SNE e UMAP.
- [ ] Gerar os quatro gráficos bidimensionais e apresentar as saídas pertinentes.
- [ ] Comentar os resultados dos dois conjuntos de experimentos.

## 14. Próxima etapa

Definir uma interface uniforme para os algoritmos e o esquema de persistência das execuções. Depois, implementar o orquestrador de experimentos e as métricas compartilhadas, antes de codificar ou integrar cada algoritmo específico.
