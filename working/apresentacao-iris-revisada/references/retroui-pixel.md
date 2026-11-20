# retroui-pixel

Tema adicional inspirado na [RetroUI](https://retroui.io/) e na documentação de [Card](https://retroui.io/card), consultadas em 16 nov. 2026. O [repositório de referência](https://github.com/Dksie09/RetroUI) descreve componentes pixelados para React. Esta adaptação não importa React, Tailwind ou código da biblioteca, nem reproduz sua API. A paleta específica abaixo foi fornecida pelo usuário.

## Seleção

```bash
node scripts/cli.mjs build --spec ./deck.json --out ./outputs/retro --theme retroui-pixel
# Equivalente: --profile retroui-pixel, ou plan.profile no JSON.
# No ambiente sem npm/LibreOffice funcional:
node scripts/cli.mjs build --spec tests/fixtures/retroui-pixel.json \
  --out ./outputs/retro-offline --theme retroui-pixel --backend ooxml --pdf-engine native
```

No Codex: `$slides-creator Crie uma apresentação de 12 slides utilizando o tema retroui-pixel.` O agente sintetiza o conteúdo normalmente e seleciona `plan.profile: "retroui-pixel"`.

Se a cópia instalada estiver fora das permissões de escrita da sessão, execute na pasta atualizada: `node scripts/update-retro.mjs`. O comando atualiza a skill existente em `~/.agents/skills/slides-creator`, adiciona somente a nova entrada em profiles.json, preserva temas extras, faz backup dos arquivos alterados e recusa versões com alterações locais conflitantes. Use `--dry-run` para conferir a lista e `--dest /caminho/skill-existente` para outro destino. Não usa o instalador e não recria a skill.

## Tokens

| Cor | Hexadecimal | Aplicação |
| --- | --- | --- |
| background | 0B0B0B | Fundo |
| surface | 141414 | Corpo de cards/janelas |
| foreground / border | F5F5F5 | Texto e contorno |
| muted | 777777 | Token bruto, reservado para uso sem texto pequeno |
| accent | FFD400 | Badges, fluxo principal, palavras-chave e um resultado |
| shadow | 000000 | Retângulo deslocado, sem desfoque |

O cinza bruto 777777 não satisfaz o mínimo de 4,5:1 em todas as superfícies. O token adicional `readableMuted: AAAAAA` é usado para comentários, créditos e textos secundários. A validação de contraste não foi enfraquecida.

Títulos e etiquetas: **Pixelify Sans**; corpo e código: **JetBrains Mono**. O Fontconfig verifica a família efetivamente encontrada, pois fc-match pode retornar outra família sem falhar. Na ausência das solicitadas, o fallback é **Liberation Mono**, inclusive em títulos curtos, com registro em `scene.fonts` e `qa.fonts`. Se esse fallback também faltar, a geração falha com diagnóstico. Nenhuma fonte é baixada ou instalada automaticamente; regenere após instalar fontes. Elas não são embutidas no PPTX.

Títulos 32–40 pt; corpo 20–24 pt; código 20 pt; rótulos 18 pt; bibliografia 14–16 pt; rodapés 12 pt. Não use tipografia pixelada para parágrafos. As métricas conservadoras podem pedir divisão de conteúdo antes dos layouts clássicos, pois o corpo monoespaçado ocupa mais largura.

Os efeitos são medidas do documento: borda de **2 pt**, sombra deslocada **4 pt** em ambos os eixos, sem blur e sem arredondamento. Os campos shadowBlur e borderRadius são descritivos; não são passados como propriedades CSS ao PptxGenJS. O contorno em degraus é uma composição de retângulos vetoriais com recuos de 4 pt. A sombra preta tem contraste intencionalmente discreto no fundo quase preto; o contorno branco delimita o componente.

A grade usa 242424 a 35% sobre o fundo, com espaçamento padrão de 0,4 polegada. Sua cor final é calculada antes da geração e desenhada com retângulos de 0,006 polegada; ambos os backends produzem a mesma geometria sem depender de uma propriedade CSS de opacity.

## Componentes

As funções de `scripts/themes/pixel-components.mjs` recebem um contexto `pixelContext(theme, fonts, baseDir)` e opções geométricas em polegadas. Produzem as primitivas existentes da scene, consumidas pelo adaptador PptxGenJS e pelo fallback OOXML.

| Componente | Implementação PowerPoint |
| --- | --- |
| PixelCard | Superfície, borda em degraus e sombra como retângulos separados |
| PixelWindow | Card, barra branca com título e três controles quadrados |
| PixelBadge | Etiqueta retangular; amarelo somente quando destacada |
| PixelDivider | Separador vetorial com pequenos blocos 8-bit |
| PixelCodeBlock | Janela, tokens como texto colorido e números de linha opcionais |
| PixelDiagram | Nós em cards, conectores e setas em blocos; fluxo principal amarelo |
| PixelGridBackground | Grade discreta configurável, sempre atrás do conteúdo |
| PixelDuck | SVG/PNG local como objeto independente ou placeholder de quadrados nativos |

Esses elementos são editáveis individualmente. O destaque de sintaxe é lexical (palavras-chave comuns de Python/JS e alguns termos de pseudocódigo), não um parser completo. Tokens são caixas de texto independentes para manter compatibilidade com os backends atuais; editar uma linha inteira pode exigir selecionar mais de uma caixa. Não há execução do código apresentado. Linhas extensas ou código alto são recusados, sem diminuir a fonte.

O placeholder de pato é um desenho original mínimo, sem mascote fornecido por terceiros. Aparece por padrão na capa; outros slides precisam de `duck: true` ou `duckPath`. Arquivos locais mantêm proporção. Um caminho explícito inválido gera erro; ausência de caminho usa placeholder. A opção não autoriza baixar ou reutilizar imagens sem proveniência. Os recursos usados são copiados para source/assets/input na saída.

## Layouts e campos

| Nome associado ao tema | Conteúdo e campos |
| --- | --- |
| CoverSlide | title, subtitle; PixelBadge, separador e PixelDuck |
| SectionSlide | title, subtitle, section opcional; grade e separador |
| ContentSlide | bullets; PixelWindow; badges opcionais |
| TwoColumnSlide | columns: dois objetos title/bullets; duas janelas |
| CodeSlide | code, caption; codeTitle e lineNumbers opcionais |
| DiagramSlide | steps, takeaway; mainFlow opcional |
| ComparisonSlide | Mesmo contrato de columns, aplicado a uma comparação |
| ResultsSlide | labels, values, unit, caption; highlightIndex opcional |
| ConclusionSlide | bullets, windowTitle opcional |
| ReferencesSlide | ids; referências e URLs legíveis |

Esses aliases são restritos ao novo tema. Os nomes canônicos title, bullets, columns, code, process, bar e references continuam válidos, assim como equation, scatter e figure. Nenhum layout dos temas anteriores é modificado.

Configuração de exemplo no topo de deck.json:

```json
{
  "visual": {
    "grid": true,
    "gridOpacity": 0.35,
    "gridSpacing": 0.4,
    "lineNumbers": true,
    "duckPath": "assets/meu-pato.svg"
  }
}
```

Omitir duckPath ativa o placeholder. gridOpacity aceita 0–1; gridSpacing, 0,25–2 polegadas. Cada slide pode sobrescrever grid, lineNumbers e duckPath. badges aceita até três textos curtos; o primeiro é destacado. mainFlow é um array de índices dos conectores, começando em zero. highlightIndex escolhe a barra destacada; o padrão é o maior valor. Diagramas têm 2–4 etapas, preservando o contrato anterior. Conteúdo extenso deve ser redistribuído, não comprimido.

## Adaptação, validação e limites

Da RetroUI foram adaptados o contorno pixelado, o card modular, os cantos retos e a sombra rígida. Grade de slide, barra de janela, numeração de código, diagramas, bibliografia, seleção de fontes e placeholder são implementações próprias para apresentações. A biblioteca não é uma dependência da skill.

`tests/fixtures/retroui-pixel.json` demonstra os dez layouts e oito componentes em 12 slides. Os testes cobrem regressão exata das cenas clássicas, validação de fonte e contraste, grade, sintaxe, limites, alias de CLI, extração de geometria editável, mascotes SVG/PNG e reprodução dos recursos locais.

No backend PptxGenJS, os gráficos usam dados e objetos nativos da biblioteca já adotada. No fallback OOXML, barras e valores são formas/textos editáveis. As limitações de conversão e inspeção continuam as documentadas em validation.md: o PDF do subconjunto nativo não comprova renderização no Microsoft PowerPoint ou LibreOffice. A revisão deve abrir todos os PNGs e registrar seu resultado pelo comando review.

Verificação desta implementação: 14 testes, 13 aprovados, nenhuma falha e 1 ignorado (integração PptxGenJS, indisponível por falta de acesso ao npm). As cenas dos três temas anteriores coincidem com os hashes da versão original. A demonstração gerou 12 slides/páginas/prévias pelo backend OOXML e conversor nativo; todas as páginas foram inspecionadas, com revisão das setas e do agrupamento das referências após ajuste. Pixelify Sans e JetBrains Mono não estavam disponíveis, portanto os arquivos usam Liberation Mono e registram esse fallback. Uma cópia temporária da instalação antiga recebeu a atualização incremental, preservou um tema extra e gerou os 12 slides. A instalação real em ~/.agents/skills permanece pendente quando o sandbox não permite escrita nesse destino. Logs: tests/validation/retroui-pixel.tap e retroui-update-smoke.json.
