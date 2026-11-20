# Apresentação Iris — Equipe 08

18 slides em português, formato 16:9, tema retroui-pixel, sem pato.
Duração estimada: 22 minutos, reservando cerca de 8 minutos para discussão.
Notas de fala incluídas no PPTX e em notes.md.

- presentation.pptx: textos, cards, diagrama e barras editáveis.
- presentation.pdf: versão para exibição e compartilhamento.
- previews/index.html: galeria das 17 páginas.
- [Conteúdo e plano](../apresentacao-retro-src/deck.json)
- [Gerador](../apresentacao-retro-src/engine/) e [figuras PNG e SVG](../apresentacao-retro-src/assets/)
- qa.json e visual-review.json: validação técnica e registro da inspeção visual.

A apresentação sintetiza `artigo_iris_ieee_paginacao_corrigida.pdf`, definido
como a fonte correta. Ela separa a tunagem (1.144 ajustes, sementes 42–51) da
rodada final (252 ajustes, sementes 52–61), totalizando 1.396 ajustes, e mantém
a exclusão do ruído das métricas do DBSCAN. Dois slides mostram a resposta
dos algoritmos aos hiperparâmetros, e o slide do GMM separa o perfil esférico
selecionado da alternativa full observada na tunagem. Os gráficos usam
as métricas, a grade de configurações, a árvore UPGMA e as coordenadas
armazenadas. As notas explicam a sensibilidade dos agrupamentos e a comparação
na amostra comum de 144 flores. O artigo contém a bibliografia completa.

Pixelify Sans e JetBrains Mono estavam indisponíveis; utilizou-se Liberation
Mono. As fontes não estão embutidas. O PDF foi produzido pelo conversor nativo
Cairo/Pango da skill. A validação cobre ZIP/XML, texto editável, geometria e
renderização. A abertura no Microsoft PowerPoint permanece sem verificação.

Para reproduzir PPTX, PDF e prévias, execute a partir da raiz do projeto.

```sh
slides_dir=$(mktemp -d)
node outputs/apresentacao-retro-src/engine/scripts/cli.mjs build \
  --spec outputs/apresentacao-retro-src/deck.json \
  --out "$slides_dir" --backend ooxml --pdf-engine native
```

Para atualizar as figuras e o conteúdo com os resultados locais, execute
`docs/artigo/analisar_revisao.py` e `outputs/apresentacao-retro-src/gerar_apresentacao.py`,
nessa ordem, a partir da raiz do projeto.
