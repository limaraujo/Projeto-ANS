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

A apresentação sintetiza o artigo revisado e os resultados já existentes no
projeto. Os experimentos não foram reexecutados. As figuras foram redesenhadas
a partir das métricas, coordenadas e matriz de hierarquia armazenadas. As
referências completas dos métodos permanecem no artigo revisado.

Pixelify Sans e JetBrains Mono estavam indisponíveis; utilizou-se Liberation
Mono. As fontes não estão embutidas. O PDF foi produzido pelo conversor nativo
Cairo/Pango do subconjunto OOXML gerado pela skill, pois a conversão automática
com LibreOffice falhou. A validação de ZIP/XML, texto editável, geometria e
renderização passou; não foi testada a abertura no Microsoft PowerPoint.

Para reproduzir PPTX, PDF e prévias a partir desta pasta:

```sh
cd source
node scripts/cli.mjs build --spec deck.json --out ../reproduced --backend ooxml --pdf-engine native
```

O script de composição das figuras está em
../apresentacao-retro-src/gerar_apresentacao.py e usa os artefatos locais do
projeto, com NumPy, pandas, Matplotlib e SciPy já disponíveis no ambiente.
