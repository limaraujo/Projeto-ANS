# Verificação do artigo revisado

## Separação das etapas e adaptação ao PDF de referência — 19/11/2026

O artigo foi reorganizado tomando `Downloads/artigo_teste.pdf` como referência de estrutura. A versão atual tem sete páginas A4, com protocolo em duas etapas, tabela conjunta da grade e dos perfis escolhidos, seis figuras de sensibilidade da rodada piloto e uma seção separada para o experimento final. O texto explica que a tunagem particional escolheu hiperparâmetros pela média das silhuetas em k = 2–5, sem selecionar k final; no experimento, a melhor execução por objetivo de cada k concorreu à escolha pela silhueta. DBSCAN e UPGMA têm procedimentos próprios explicitados.

Foram mantidas as sementes e as métricas dos registros locais: 42–51 na tunagem, 52–61 no experimento, 24 pares DBSCAN, 144 flores retidas e trustworthiness do t-SNE de 0,9888. O PDF de referência contém números diferentes, usados apenas como referência de organização. A grafia Rodrigo Gomes foi adotada conforme a autoria do PDF fornecido nesta etapa.

O script `gerar_figuras_tunagem_artigo.py` gera seis figuras `figuras/ieee/tunagem_*.pdf` e `resumo_etapas.json`, a partir dos CSV e JSON existentes, sem executar agrupadores. As tabelas novas apresentam as métricas em k = 3 e os intervalos das funções objetivo nas dez chamadas finais. Não se infere ótimo global da proximidade dos objetivos. Os artefatos experimentais foram preservados.

Reprodução dos novos artefatos: `.venv/bin/python docs/artigo/gerar_figuras_tunagem_artigo.py`, seguido de `typst compile docs/artigo/artigo_ieee_revisado.typ docs/artigo/artigo_ieee_revisado.pdf --root docs/artigo`. Compilação sem avisos; as sete páginas foram rasterizadas e inspecionadas visualmente.

## Tunagem e experimento da Questão 1 — 19/11/2026

Os arquivos canônicos são `artigo_ieee_revisado.typ` e `artigo_ieee_revisado.pdf`. O script `analisar_revisao.py` lê os resultados da Questão 1 e da Questão 2 e gera as tabelas, as figuras e `diagnosticos_revisao.json` usados nesta versão.

| Verificação | Resultado | Evidência |
|---|---|---|
| Tunagem | 1.120 ajustes particionais com sementes 42–51 e 24 candidatos DBSCAN. A média das quatro silhuetas definiu um perfil por método particional | `resultados/tunagem/particionais.csv` e `resultados/tunagem/dbscan.csv` |
| Experimento | 250 ajustes particionais com sementes 52–61, uma árvore UPGMA e um ajuste DBSCAN. A tunagem e o experimento somaram 1.396 ajustes | `resultados/metadados_questao_1.json` e `resultados/validacao.json` |
| Silhueta em k = 1 | Indefinida e fora da seleção | `resultados/metricas_por_k.csv` |
| ARI do experimento em k = 3 | UPGMA obteve 0,7184 e GMM com covariância esférica obteve 0,6199 | `resultados/metricas_por_k.csv` |
| DBSCAN sem ruído | Dois grupos, seis pontos de ruído e cobertura de 96%. Silhueta de 0,6035 e ARI de 0,5760 em 144 flores | `resultados/resumo_agrupamentos.csv` |
| Comparação na mesma amostra | As sete partições coincidem nas 144 flores retidas | `resultados/tunagem/comparacao_mesma_amostra.csv` |
| Artigo canônico | PDF A4, seis páginas, com tabelas de grade, métricas e cobertura | `artigo_ieee_revisado.pdf` |

## Histórico das verificações de 16 e 18/11/2026

As contagens, métricas e figuras descritas a seguir se referem às versões históricas do protocolo. O artigo original, o PDF atualizado em 18/11 e os CSVs e o log de `resultados/historico/` estão no commit `27bb65a`.

## Fase 1 — requisitos e auditoria inicial

| Requisito do PDF | Artefato | Seção do artigo | Situação |
|---|---|---|---|
| Sete agrupadores da Equipe 08 | PDF pp. 2–3, 6; `codigo/algoritmos.py`; execuções Q1 | Metodologia e resultados de agrupamento | Atendido nos registros |
| Dez ajustes para cada k de cinco métodos; uma árvore e um DBSCAN | `execucoes_questao_1.json`; `metricas_por_k.csv` | Metodologia | 250 + 1 + 1 confirmados nos registros |
| Seleção por objetivo, silhueta, ARI, seis curvas, dendrograma | Código, CSV, JSON e figuras | Resultados de agrupamento | Figuras e números presentes; recálculo independente parcial executado |
| PCA, Kernel PCA, t-SNE e UMAP, saídas e projeções | `execucoes_questao_2.json`, CSV e figuras | Redução de dimensionalidade | Presente; valores apoiados em registros preexistentes |
| Decisões comentadas e formato livre | PDF p. 7 | Todas | Artigo em estilo IEEE, duas colunas A4; não se afirma conformidade estrita com modelo oficial |

O arquivo utilizado é `codigo/iris/iris.data` (SHA-256 `6f608b71a7317216319b4d27b4d9bc84e6abd734eda7872b71a458569e2656c0`). A leitura direta encontrou 150 linhas, quatro atributos, três espécies balanceadas e nenhum valor vazio. A presença de `bezdekIris.data` foi mantida sem substituição da base usada.

## Fase 2 — matriz de evidências

| Afirmação | Fonte/localização | Limite |
|---|---|---|
| 252 ajustes principais | `execucoes_questao_1.json`, chaves de método e k; `validacao.json` | Registros não são prova independente da execução histórica |
| Seleção por função objetivo e ARI/silhueta | `codigo/algoritmos.py`; `metricas_por_k.csv`; rótulos em `execucoes_questao_1.json` | Recálculo independente confirmou os 25 melhores ajustes particionais; não reexecutou os algoritmos |
| k=2, Sil=0,580184, ARI=0,568116 nos seis métodos | `resumo_agrupamentos.csv` e contingências | Específico da base, escala e parâmetros |
| DBSCAN: dois grupos, quatro ruídos, Sil=0,596318, ARI=0,551755 | `resumo_agrupamentos.csv`; metadados Q1 | Silhueta exclui ruído; ARI o inclui |
| GMM em k=3: ARI=0,903874 | `metricas_por_k.csv` | Análise posterior, não critério de seleção |
| PCA, Kernel PCA, t-SNE, UMAP e trustworthiness | `execucoes_questao_2.json`, metadados Q2, componentes e coordenadas CSV | Uma execução por técnica; sem análise de estabilidade |
| 840 ajustes complementares | Apenas artigo anterior e código de tunagem | Não foram encontrados artefatos comprobatórios; afirmação removida |

O validador foi inspecionado, mas não executado porque grava sobre `resultados/validacao.json`. Seu registro preexistente foi consultado como evidência limitada. Uma checagem de leitura independente, sem gravações, refez ARI e silhueta dos 25 ajustes particionais selecionados e verificou a base local.

## Fontes teóricas por método

| Método ou métrica | Fonte verificada | Implementação usada | Conceito e seção |
|---|---|---|---|
| K-Means | MacQueen, 1967, Berkeley | scikit-learn/KMeans | Centroides e inicialização; Fundamentação |
| FCM | Bezdek, 1981, Springer | `fcmeans.FCM` | Pertinências e expoente; Fundamentação |
| Kernel FCM | Graves e Pedrycz, 2010, Fuzzy Sets and Systems | `fcmeans.KFCM`; código local | Variantes de protótipo e kernel; Fundamentação |
| K-Medoids/PAM | Kaufman e Rousseeuw, 1990, Wiley | `kmedoids.pam` | Medoides e custo; Fundamentação |
| GMM/EM | Dempster, Laird e Rubin, 1977, JRSS B | `GaussianMixture` | EM e verossimilhança; Fundamentação |
| UPGMA | Sokal e Michener, 1958, Kansas | SciPy `linkage` | Ligação média; Fundamentação |
| DBSCAN | Ester et al., 1996, KDD | scikit-learn/DBSCAN | Densidade e ruído; Fundamentação |
| PCA | Hotelling, 1933, J. Educational Psychology | scikit-learn/PCA | Componentes lineares; Fundamentação |
| Kernel PCA | Schölkopf, Smola e Müller, 1998, Neural Computation | scikit-learn/KernelPCA | Espectro do kernel; Fundamentação |
| t-SNE | van der Maaten e Hinton, 2008, JMLR | scikit-learn/TSNE | Afinidades e KL; Fundamentação |
| UMAP | McInnes, Healy e Melville, arXiv:1802.03426 | umap-learn | Vizinhanças e projeção; Fundamentação |
| Silhueta; ARI; trustworthiness | Rousseeuw, 1987; Hubert e Arabie, 1985; Venna e Kaski, 2001 | scikit-learn | Métricas; Fundamentação e avaliação |

As páginas editoriais ou institucionais e, onde disponíveis, textos dos trabalhos foram consultados para metadados e conceitos usados. Para comportamento exato das APIs, o artigo complementa fontes teóricas com documentação e código local; páginas bibliográficas isoladas não foram tratadas como leitura integral.

## Fases 3–5 — redação e revisão final

O fonte `artigo_ieee.typ` e o PDF original `artigo_ieee.pdf` estão no histórico do Git. Foi acrescentada fundamentação citada e removida a alegação sem suporte sobre o complemento. Foram mantidas as seis curvas, o dendrograma e quatro projeções. O PDF revisado compilou com Typst: A4, duas colunas, sete páginas. A extração textual confirmou seções e referências; não houve inspeção visual página a página nem reexecução dos 252 ajustes ou das quatro projeções. A conformidade com um template oficial IEEE não foi certificada.

## Revisão de 18/11/2026 — correções e diagnósticos complementares

Esta seção atualiza o estado da versão `artigo_ieee_revisado.typ/pdf` descrito acima.

- Autoria: Fátima Araújo (`frqal@cin.ufpe.br`) e Rogrigo Gomes (`rgar@cin.ufpe.br`), com grafia fornecida pelo usuário.
- Removidas notas de bastidores e repetição da introdução. Acrescentados comentários específicos dos sete métodos, justificativas de m, gamma e escala, e extremos preferidos dos objetivos.
- Referências renumeradas por primeira citação; a variante de Kernel FCM recebeu a publicação de Zhang e Chen de **2004**, verificada na editora (a sugestão mencionava 2003): https://www.sciencedirect.com/science/article/pii/S0933365704000351.
- PCA: valores singulares e média incluídos; loadings simplificados. Kernel PCA: traço completo 98,2247 e frações de 39,8394% e 18,1140% no espaço de características.
- UMAP: formato e limites calculados das coordenadas persistidas; a e b recalculados com `find_ab_params`. O ajuste original não foi cronometrado e nenhum tempo foi inventado.
- DBSCAN: varredura eps = 0,6–1,0 em passos de 0,1, mantendo min_samples = 5. A escolha original está em patamar localmente estável, sem alegação de seleção prospectiva pela varredura.
- UPGMA: silhueta Manhattan para os cortes de 2 a 5; mesma preferência por dois grupos. Dendrograma truncado com contagens e linhas de corte.
- FCM e Kernel FCM: ARI entre partições em k = 3 igual a 1, confirmando coincidência exata salvo nomes dos grupos.
- K-Means: análise separada com 100 inicializações aleatórias e semente 42: objetivo 140,9658166, ARI 0,6201352, silhueta 0,4589718. O objetivo próximo de 139,8 não foi encontrado nesta análise; não se afirma ótimo global.
- GMM: os cinco melhores modelos foram reconstruídos com seus parâmetros e sementes, e suas log-verossimilhanças foram conferidas com os registros. Pesos, contagens, autovalores mínimos das covariâncias e BIC estão no JSON. O BIC mínimo foi em k = 2. Em k = 5, há componente de peso 0,0604 e autovalor mínimo de 0,00000381.
- Curvas de silhueta consolidadas; todos os gráficos atuais usam vírgula decimal. O protocolo principal e os respectivos CSV/JSON permanecem preservados.

Reprodução: `analisar_revisao.py` gera `diagnosticos_revisao.json` e as figuras; a redação revisada é mantida diretamente em Typst. PDF compilado com Typst e páginas inspecionadas por rasterização. Não foram reexecutados os 252 ajustes nem as quatro projeções; os diagnósticos novos têm escopo explícito acima.


## Ajuste de fórmulas — 18/11/2026

Conforme a orientação final, a versão anterior foi restaurada e apenas a expressão do z-score foi acrescentada à preparação dos dados, com as definições da média e do desvio-padrão populacional.
