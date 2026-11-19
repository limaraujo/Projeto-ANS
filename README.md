# Projeto AM-NS — Equipe 08

Implementação dos sete algoritmos de agrupamento da Equipe 08 e das técnicas PCA, Kernel PCA, t-SNE e UMAP sobre a base Iris.

## Organização

```text
.
├── codigo/       # scripts Python, dependências e base Iris
├── docs/         # enunciado, requisitos, relatório e artigo
├── resultados/   # métricas, execuções, figuras e histórico
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
- `resultados/historico/`: resultados antigos preservados.

## Execução

O ambiente utilizado foi Python 3.14. A partir da raiz do projeto:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r codigo/requirements.txt
.venv/bin/python codigo/main.py
.venv/bin/python codigo/validar_resultados.py
```

Para executar uma questão separadamente, use `codigo/main.py --questao 1` ou `codigo/main.py --questao 2`. Consulte `codigo/main.py --help` para os demais parâmetros.

Novas execuções gravam os artefatos em `resultados/`. O conjunto final da Questão 1 contém 250 ajustes particionais, uma árvore UPGMA e um ajuste DBSCAN. Os ajustes das configurações selecionadas são reaproveitados da busca quando disponíveis. A auditoria confere a busca e as 252 execuções integrantes do protocolo final.

## Artigo

Para regenerar as figuras vetoriais e compilar a versão revisada:

```sh
.venv/bin/python docs/artigo/analisar_revisao.py
typst compile docs/artigo/artigo_ieee_revisado.typ docs/artigo/artigo_ieee_revisado.pdf --root .
```

O enunciado oficial e os requisitos complementares estão disponíveis no repositório. [Enunciado](docs/Projeto-AMG-NS-2026-2.pdf) · [Requisitos](docs/requisitos.md)

## Apresentação

A apresentação da Equipe 08 acompanha a versão revisada do artigo.

- [PowerPoint editável](apresentacao_iris_retro.pptx)
- [Apresentação em PDF](apresentacao_iris_retro.pdf)
- [Notas de fala](outputs/apresentacao-iris-retro/notes.md)
- [Guia de estudo e apresentação](GUIA_APRESENTACAO.md)

## Busca de hiperparâmetros da Questão 1

A execução de `codigo/main.py --questao 1` avalia cada configuração particional em `k=2..5`, com as sementes 42–51. A função objetivo seleciona a execução de cada configuração e `k`. A silhueta seleciona os hiperparâmetros e `k*`. Para `k=1`, executam-se as configurações selecionadas e registra-se a silhueta como indefinida. No UPGMA, todos os cortes vêm da mesma árvore Manhattan com ligação média.

No DBSCAN, a silhueta e o ARI usam os pontos atribuídos a algum grupo. A escolha automática busca a maior silhueta válida com cobertura mínima de 95%. O ARI é usado na avaliação externa após a escolha. Consulte `resultados/tunagem/` para as grades, execuções individuais, gráficos de sensibilidade e a comparação dos sete métodos no subconjunto de pontos retido pelo DBSCAN.
