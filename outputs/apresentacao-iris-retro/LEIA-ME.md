# Apresentação Iris — Equipe 08

17 slides em português, formato 16:9, tema retroui-pixel, sem pato.
Duração estimada: 18 minutos. Notas de fala incluídas no PPTX e em notes.md.

- presentation.pptx: textos, cards, diagrama e barras editáveis.
- presentation.pdf: versão para exibição e compartilhamento.
- previews/index.html: galeria das 17 páginas.
- source/deck.json: conteúdo e plano da apresentação.
- source/scripts/: gerador portátil da skill, com a opção duck=false na capa.
- source/assets/input/: imagens utilizadas; source/figuras-svg/: fontes vetoriais adicionais.
- qa.json e visual-review.json: validação técnica e registro da inspeção visual.

A apresentação sintetiza a versão do artigo que incorpora a busca de
hiperparâmetros e a exclusão do ruído das métricas do DBSCAN. Os gráficos usam
as métricas, a grade de configurações, a árvore UPGMA e as coordenadas
armazenadas. As notas explicam a sensibilidade dos agrupamentos e a comparação
na amostra comum de 144 flores. O artigo contém a bibliografia completa.

Pixelify Sans e JetBrains Mono estavam indisponíveis; utilizou-se Liberation
Mono. As fontes não estão embutidas. O PDF foi produzido pelo conversor nativo
Cairo/Pango da skill. A validação cobre ZIP/XML, texto editável, geometria e
renderização. A abertura no Microsoft PowerPoint permanece sem verificação.

Para reproduzir PPTX, PDF e prévias a partir desta pasta:

```sh
cd source
node scripts/cli.mjs build --spec deck.json --out ../reproduced --backend ooxml --pdf-engine native
```

O script `../apresentacao-retro-src/gerar_apresentacao.py` recompõe as figuras e
o conteúdo da apresentação com os resultados locais. Execute antes o script
`docs/artigo/analisar_revisao.py` a partir da raiz do projeto para atualizar as
tabelas e os diagnósticos usados pela apresentação.
