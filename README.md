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
- `codigo/validar_resultados.py`: auditoria numérica dos artefatos.
- `codigo/gerar_relatorio.py`: geração do relatório Typst.
- `docs/relatorio.pdf`: relatório completo.
- `docs/artigo/`: versão em formato de artigo IEEE.
- `resultados/figuras/`: gráficos produzidos pelos experimentos.
- `resultados/historico/`: resultados antigos preservados.

## Execução

O ambiente utilizado foi Python 3.14. A partir da raiz do projeto:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r codigo/requirements.txt
.venv/bin/python codigo/main.py
.venv/bin/python codigo/validar_resultados.py
.venv/bin/python codigo/gerar_relatorio.py
typst compile docs/relatorio.typ docs/relatorio.pdf --root .
```

Para executar uma questão separadamente, use `codigo/main.py --questao 1` ou `codigo/main.py --questao 2`. Consulte `codigo/main.py --help` para os demais parâmetros.

Novas execuções gravam os artefatos em `resultados/` e as imagens em `resultados/figuras/`. A auditoria considera a base padronizada e o protocolo padrão de 252 ajustes.

## Artigo

Para regenerar a versão em duas colunas e suas figuras vetoriais:

```sh
.venv/bin/python docs/artigo/gerar_artigo_ieee.py
typst compile docs/artigo/artigo_ieee.typ docs/artigo/artigo_ieee.pdf --root docs/artigo
```

O enunciado oficial está em `docs/Projeto-AMG-NS-2026-2.pdf`; `docs/requisitos.md` é material auxiliar.

## Tunagem opcional

```sh
.venv/bin/python codigo/tunagem.py
```

O script mantém somente as grades de hiperparâmetros do DBSCAN (`eps` e
`min_samples`) e do Kernel Fuzzy C-Means (`gamma` e `k`). Os resultados são
gravados em `resultados/tunagem/`. Essa etapa é opcional e não altera os
resultados obrigatórios do projeto.

O código complementar é organizado em etapas: `estabilidade`, `comparar_escalas`,
`sensibilidade_dbscan`, `sensibilidade_kernel` e `avaliar_projecoes`.
`run()` apenas prepara os dados, chama essas etapas e registra os metadados.
A grade DBSCAN e o ajuste Kernel FCM usados na tunagem são compartilhados em
`codigo/tunagem.py`; os dois métodos fuzzy principais compartilham o ajuste em
`codigo/algoritmos.py`.
