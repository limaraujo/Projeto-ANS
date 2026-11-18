# Contrato de deck.json

JSON UTF-8, sem comentários. `assets/templates/deck.json` é um modelo pequeno; `tests/fixtures/dbscan.json` demonstra 12 slides. Validação de campos e limites em `scripts/model.mjs`. Chaves de conteúdo desconhecidas não são renderizadas; para novo layout, estenda compilador e testes.

Campos de topo: `title` (texto), `plan` (objeto), `slides` (array 1–200), `references` (array).

`plan`: `objective`, `audience`, `depth`, `language` (como pt-BR), `narrative` (textos); `minutes` (positivo); `slideCount` (igual ao array); `profile` (academic-minimal, dark-technical, modern-scientific ou retroui-pixel); `assumptions` (array de textos); `analysis` contendo `centralTheme` e arrays `concepts`, `arguments`, `results`, `visualOpportunities`. Registre fontes consultadas e limitações em `plan.sources` se necessário.

Todo slide exige `layout` e `title`; opcionais: `label` (curta classificação como Exemplo sintético), `citations` (array de ids), `notes` (texto de apresentação).

| Layout | Campos específicos |
| --- | --- |
| title | subtitle |
| bullets | bullets: 1–6 textos |
| columns | columns: dois objetos {title, bullets: 1–5 textos} |
| process | steps: 2–4 textos; takeaway: síntese |
| equation | equation: texto Unicode; bullets: 1–4 definições |
| code | code: linhas separadas por `\n`; caption |
| scatter | points: 1–500 objetos {x, y, group}; caption, xLabel, yLabel |
| bar | labels: 1–8 textos; values: números ≥0, algum >0; unit; caption |
| figure | path: imagem local relativa ao JSON; alt; caption; attribution |
| references | ids: 1–3 ids existentes |

`references`: objetos `{ "id": "E1996", "text": "Autores. Título. Veículo, ano, páginas.", "url": "https://..." }`. Para fonte local, use URI `file:` e descreva caminho e página em `text`; para publicação prefira URL persistente ou DOI. Toda citação precisa de entrada bibliográfica e aparição em slide references. `notes` são gravadas no PPTX e em notes.md; não adicionar instruções internas aos slides.

`label` é exibido acima do conteúdo. Código deve caber sem quebra automática: prefira até nove linhas curtas. A estimativa de largura é conservadora; longas URLs/títulos exigem ajuste real da composição. `bar` aceita somente uma série e valores não negativos. Para séries múltiplas, tabelas ou outros diagramas, adapte o código-fonte copiado e mantenha as verificações e inspeção.

Somente no tema retroui-pixel, há dez aliases de layout e opções `visual`, `badges`, `duck`, `duckPath`, `lineNumbers`, `mainFlow`, `highlightIndex`. Consulte [retroui-pixel.md](retroui-pixel.md) e o exemplo `tests/fixtures/retroui-pixel.json`. Os nomes canônicos da tabela também funcionam nesse tema.
