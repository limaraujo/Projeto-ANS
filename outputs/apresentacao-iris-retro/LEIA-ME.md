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

A apresentação sintetiza a revisão do artigo de 18/11/2026 e os resultados
registrados no projeto. Os gráficos usam as métricas, coordenadas e matriz de
hierarquia armazenadas. As notas incluem os diagnósticos complementares de
K-Means, GMM, UPGMA, DBSCAN e projeções. O artigo contém a bibliografia completa.

Pixelify Sans e JetBrains Mono estavam indisponíveis; utilizou-se Liberation
Mono. As fontes não estão embutidas. O PDF foi produzido pelo conversor nativo
Cairo/Pango da skill. A validação cobre ZIP/XML, texto editável, geometria e
renderização. A abertura no Microsoft PowerPoint permanece sem verificação.

Para reproduzir PPTX, PDF e prévias a partir desta pasta:

```sh
cd source
node scripts/cli.mjs build --spec deck.json --out ../reproduced --backend ooxml --pdf-engine native
```

O script de composição das figuras está em
../apresentacao-retro-src/gerar_apresentacao.py e usa os artefatos locais do
projeto, com NumPy, pandas, Matplotlib e SciPy já disponíveis no ambiente.
