# Projeto AM-NS — Equipe 08

A única fonte dos requisitos é **Projeto-AMG-NS-2026-2.pdf**. `requisitos.md` é uma anotação anterior e não substitui o enunciado. Os arquivos `.mch` não integram estes experimentos.

Implementa os sete agrupamentos da Equipe 08 e PCA, Kernel PCA, t-SNE e UMAP. O relatório completo está em `relatorio.pdf`, com fonte em `relatorio.typ`.

## Execução

Para publicar este projeto em um repositório privado na sua conta GitHub e convidar
`rRodrigoGomes` como colaborador com acesso de escrita, instale o GitHub CLI (`gh`)
e execute, com as alterações locais já commitadas:

```sh
bash publicar_github.sh
```

O script solicita login pelo navegador se necessário. O nome padrão é
`projeto-amns-equipe08`; para usar outro nome, execute
`bash publicar_github.sh outro-nome`. Repositórios privados e convites já existentes
são reutilizados. O script interrompe a publicação se `origin` apontar para outro
destino, se o repositório for público ou se houver históricos incompatíveis.
Consulte `bash publicar_github.sh --help` para mais detalhes.
O fluxo utiliza o [GitHub CLI](https://cli.github.com/manual/gh_repo_create) e a
[API de colaboradores](https://docs.github.com/en/rest/collaborators/collaborators#add-a-repository-collaborator).

### Executar os experimentos

O ambiente utilizado foi Python 3.14. As versões instaladas estão fixadas em `requirements.txt`.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
.venv/bin/python validar_resultados.py
.venv/bin/python gerar_relatorio.py
typst compile relatorio.typ relatorio.pdf
```

Para executar separadamente: `main.py --questao 1` ou `main.py --questao 2`. Consulte `main.py --help` para os parâmetros disponíveis. O ambiente de avaliação pode usar `MPLCONFIGDIR=/tmp/matplotlib-iris` para um cache gravável e `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1` para limitar threads. UMAP pode demorar na primeira execução por compilar rotinas JIT.

As saídas são relativas ao diretório dos scripts. Novas execuções sobrescrevem os resultados e as figuras correspondentes. Para reproduzir a entrega e usar a auditoria, utilize os parâmetros padrão. A auditoria é específica da base padronizada e do protocolo de 252 ajustes. Ao mudar os parâmetros, revise também a discussão textual do relatório; suas tabelas são atualizadas a partir dos arquivos, mas as interpretações não são recalculadas automaticamente.

## Organização

- `algoritmos.py`: carregamento, algoritmos de agrupamento, seleção, métricas, gráficos e persistência comum.
- `questoes.py`: execução completa da Questão 1 e da Questão 2, incluindo resultados, figuras e metadados.
- `main.py`: interface única de execução das duas questões.
- `validar_resultados.py`: auditoria numérica dos artefatos persistidos.
- `gerar_relatorio.py`: geração do relatório Typst a partir dos resultados.
- `resultados/`: execuções completas, metadados, métricas por k, contingências, componentes, loadings, coordenadas e validação.
- `figuras/`: seis curvas de silhueta, um dendrograma e quatro projeções.
- `exploracao_kmeans.py`: exploração interativa original, preservada; não é necessária para reproduzir a entrega.

Os arquivos antigos `q1_resumo.csv`, `q1_silhueta_ari_por_k.csv` e `saidas_console.txt` estão em `historico/`. O relatório usa exclusivamente os resultados da execução atual em `resultados/`.

## Protocolo

São 250 ajustes particionais (cinco algoritmos × cinco valores de k × dez sementes, 42–51), uma árvore UPGMA Manhattan/average e uma execução DBSCAN (eps 0,8; min_samples 5). A melhor inicialização é escolhida pela função objetivo e k pela silhueta euclidiana. Fuzzy e GMM usam argmax das pertinências/posteriores. A silhueta do DBSCAN remove ruído; o ARI mantém todos os pontos. Espécies nunca são passadas ao ajuste dos modelos.

PCA usa quatro componentes e apresenta as duas primeiras; Kernel PCA usa RBF/gamma 0,25; t-SNE usa perplexidade 30; UMAP usa 15 vizinhos/min_dist 0,1. As projeções estocásticas usam semente 42. O relatório distingue os requisitos do PDF das escolhas metodológicas.

## Artigo no estilo IEEE

`artigo/artigo_ieee.pdf` apresenta uma versão de artigo em português, com duas colunas, resumo, palavras-chave, seções numeradas, tabelas e figuras vetoriais. A fonte editável é `artigo/artigo_ieee.typ`; a autoria está identificada como Equipe 08. A diagramação é uma adaptação em Typst do estilo IEEE conference A4, não utiliza a classe oficial LaTeX IEEEtran. Orientações consultadas: [IEEE — modelos de conferência](https://cai.ieee.org/2025/manuscript-templates-for-conference-proceedings/). O conteúdo experimental continua baseado exclusivamente no enunciado fornecido e nos resultados locais.

Para regenerar a versão de artigo e seus gráficos sem refazer os ajustes:

```sh
.venv/bin/python artigo/gerar_artigo_ieee.py
typst compile artigo/artigo_ieee.typ artigo/artigo_ieee.pdf
```

O gerador utiliza `relatorio.typ` e os artefatos em `resultados/`. Os gráficos para o artigo estão em `artigo/figuras/ieee/`.

## Notebook Jupyter consolidado

Abra **`notebooks/Projeto_AMNS_Equipe08.ipynb`** no JupyterLab ou no VS Code e selecione um kernel Python com as dependências do projeto. O notebook incorpora a base Iris e todo o código Python: algoritmos, métricas, execução das duas questões, validação, exploração histórica e geração dos dois documentos. Não depende dos scripts `.py` externos.

```sh
.venv/bin/python -m pip install -r requirements-notebook.txt
.venv/bin/python -m jupyterlab notebooks/Projeto_AMNS_Equipe08.ipynb
```

Execute as células na ordem, com **Restart Kernel and Run All**. As saídas são gravadas em `execucao_notebook/`. A exploração histórica fica desativada por padrão para não acrescentar ajustes ao protocolo principal. Typst é necessário somente para compilar os PDFs; os fontes dos documentos são gerados mesmo sem ele.

O notebook inclui saídas reais da execução sequencial de suas células em Python. A validação neste ambiente foi realizada sem kernel Jupyter, pois os pacotes Jupyter não estavam instalados e o acesso ao PyPI estava indisponível. Essa informação também consta nos metadados do notebook. A instalação e a abertura no Jupyter devem ser feitas em um ambiente com esses pacotes disponíveis.
