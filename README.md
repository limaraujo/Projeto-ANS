# Projeto AM-NS — Equipe 08

Implementação dos sete algoritmos de agrupamento da Equipe 08 e das técnicas PCA, Kernel PCA, t-SNE e UMAP sobre a base Iris.

## Organização

```text
.
├── codigo/       # scripts Python, dependências e base Iris
├── docs/         # enunciado, requisitos e artigo
├── outputs/      # apresentação, prévias e fontes dos slides
├── resultados/   # métricas, execuções e figuras
└── README.md
```

- `codigo/main.py`: interface de execução das duas questões.
- `codigo/algoritmos.py`: algoritmos, métricas, gráficos e persistência.
- `codigo/questoes.py`: execução completa das Questões 1 e 2.
- [Busca e análise de sensibilidade dos agrupadores](codigo/tunagem.py).
- `codigo/validar_resultados.py`: auditoria numérica dos artefatos.
- [Notebook para Jupyter ou Colab](codigo/Projeto_AMNS_Equipe8.ipynb).
- [Artigo revisado em PDF](docs/artigo/artigo_ieee_revisado.pdf).
- `resultados/figuras/`: gráficos produzidos pelos experimentos.

As versões anteriores do artigo e dos resultados estão no histórico do Git, no commit `27bb65a`.

## Execução

O ambiente utilizado foi Python 3.14. A partir da raiz do projeto:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r codigo/requirements.txt
.venv/bin/python codigo/main.py
.venv/bin/python codigo/validar_resultados.py
```

Para executar uma questão separadamente, use `codigo/main.py --questao 1` ou `codigo/main.py --questao 2`. Consulte `codigo/main.py --help` para os demais parâmetros.

Novas execuções gravam os artefatos em `resultados/`. A auditoria confere os 1.144 ajustes piloto e as 252 novas execuções oficiais da Questão 1.

## Artigo

Para regenerar as figuras vetoriais e compilar a versão revisada:

```sh
.venv/bin/python docs/artigo/analisar_revisao.py
.venv/bin/python docs/artigo/gerar_figuras_tunagem_artigo.py
typst compile docs/artigo/artigo_ieee_revisado.typ docs/artigo/artigo_ieee_revisado.pdf --root .
```

O enunciado oficial e os requisitos complementares estão disponíveis no repositório. [Enunciado](docs/Projeto-AMG-NS-2026-2.pdf) · [Requisitos](docs/requisitos.md)

## Apresentação

A apresentação e o guia abaixo documentam o protocolo anterior da Questão 1. Os resultados da rodada oficial atual estão no artigo revisado e em `resultados/`.

- [PowerPoint editável](outputs/apresentacao-iris-retro/presentation.pptx)
- [Apresentação em PDF](outputs/apresentacao-iris-retro/presentation.pdf)
- [Notas de fala](outputs/apresentacao-iris-retro/notes.md)
- [Guia de estudo e apresentação](GUIA_APRESENTACAO.md)
- [Instruções para reproduzir os slides](outputs/apresentacao-iris-retro/LEIA-ME.md)

## Busca de hiperparâmetros da Questão 1

No piloto, `codigo/main.py --questao 1` avalia cada configuração particional em `k=2..5` com as sementes 42–51 e os mesmos atributos padronizados. Para cada configuração e `k`, a silhueta usa a execução de melhor objetivo. A maior média aritmética das quatro silhuetas define a configuração de cada algoritmo. A configuração de referência tem prioridade em caso de empate.

Na rodada oficial, cada método particional usa a configuração escolhida e faz dez novas inicializações por `k=1..5`, com as sementes 52–61. A função objetivo determina a melhor execução de cada `k`, a maior silhueta válida determina `k*`, e o ARI avalia a partição escolhida. A silhueta de `k=1` é indefinida. Os cinco cortes do UPGMA vêm de uma única árvore Manhattan com ligação média.

O piloto do DBSCAN seleciona a maior silhueta válida com cobertura mínima de 95%. Na rodada oficial, executa-se o par selecionado uma vez. A silhueta e o ARI consideram as flores atribuídas a algum grupo. Consulte as [médias piloto](resultados/tunagem/particionais.csv), a [grade do DBSCAN](resultados/tunagem/dbscan.csv) e as [métricas oficiais](resultados/metricas_por_k.csv).

As seções V-C a V-E do artigo mostram a sensibilidade à inicialização, ao expoente fuzzy, à escala do RBF, à covariância e à regularização do GMM, ao raio e à densidade mínima do DBSCAN e ao corte do UPGMA. As comparações usam um parâmetro por vez. [Artigo revisado](docs/artigo/artigo_ieee_revisado.pdf) · [Gráficos da grade completa](resultados/tunagem/figuras/)
