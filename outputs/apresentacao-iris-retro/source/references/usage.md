# Uso e instalação

Node ≥18 e Python ≥3; LibreOffice Impress e Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`). `doctor` inspeciona os comandos antes de instalar qualquer ferramenta. `SOFFICE=/caminho/soffice` e `PYTHON=/caminho/python3` permitem selecionar binários. Em Linux, há detecção de uma instalação Snap existente quando seu lançador não inicia; nada é instalado no sistema.

Instale a skill a partir de uma pasta permitida:

```bash
node scripts/install.mjs
# Alternativa por projeto:
node scripts/install.mjs --dest /caminho/projeto/.agents/skills/slides-creator
```

O instalador copia a skill, exclui saídas/cache/node_modules e recusa sobrescrever destino existente. O destino padrão é `~/.agents/skills/slides-creator`. Execute em um terminal com permissão para esse destino; o instalador não contorna o sandbox. O backend OOXML funciona imediatamente. Para o preferencial:

```bash
cd ~/.agents/skills/slides-creator
npm install --no-audit --no-fund
node scripts/cli.mjs doctor
```

A dependência direta é `pptxgenjs@4.0.1`, local ao projeto. A instalação npm gera o lockfile; não há dependências Python extras para PPTX. Sem rede/npm, o backend OOXML continua funcional. Um pedido natural é processado pelo Codex com a skill, sem chamar outro modelo nem cobrar outra API:

```bash
codex '$slides-creator Crie 12 slides sobre redes neurais convolucionais.'
codex '$slides-creator Transforme ./artigo.pdf em uma apresentação de 15 minutos.'
codex '$slides-creator Explique DBSCAN com diagramas, exemplos, notas e perfil Dark Technical.'
```

Também é possível trabalhar com o gerador determinístico:

```bash
node scripts/cli.mjs profiles
node scripts/cli.mjs build --spec tests/fixtures/retroui-pixel.json --out ./outputs/retro-demo --theme retroui-pixel
node scripts/cli.mjs prepare --prompt 'Crie 12 slides sobre DBSCAN' --out ./working/dbscan
node scripts/cli.mjs extract --input ./artigo.pdf --out ./working/fontes
# O Codex analisa fontes e escreve deck.json conforme a referência spec.md.
node scripts/cli.mjs build --spec ./deck.json --out ./outputs/apresentacao --profile 'Dark Technical'
node scripts/cli.mjs build --spec ./deck.json --out ./outputs/apresentacao --backend ooxml --force
node scripts/cli.mjs build --spec ./deck.json --out ./outputs/offline --backend ooxml --pdf-engine native
node scripts/cli.mjs validate --out ./outputs/apresentacao
node scripts/cli.mjs review --out ./outputs/apresentacao --file ./review.json
npm test
npm run demo
```

`prepare` não gera conteúdo científico sozinho: salva pedido/padrões e extrai uma fonte opcional com `--input`. O agente completa o plano e JSON. Idioma, público, duração e quantidade são campos do JSON preenchidos a partir da linguagem natural; `--profile` pode sobrescrever o perfil. Saídas completas sempre incluem PDF.

`--theme` é um alias de `--profile` em build e prepare. Se ambos forem fornecidos, precisam indicar o mesmo perfil. Para a identidade retro, consulte [retroui-pixel.md](retroui-pixel.md). Exemplo no Codex: `codex '$slides-creator Crie uma apresentação de 12 slides utilizando o tema retroui-pixel.'`.

`--pdf-engine` aceita `auto` (padrão: tenta LibreOffice e recorre ao subconjunto nativo se necessário), `libreoffice` (falha se o CLI não exportar), `libreofficekit` (API C estável da instalação selecionada), `native` (subconjunto explícito). O nativo usa bibliotecas Linux existentes `libcairo`, `libpango`, `libpangocairo`, `libgobject` e `librsvg` por ctypes, sem pacotes Python. JPEG nesse modo requer Pillow já disponível; PNG e SVG não. O nativo produz PDF vetorial a partir do PPTX, mas não implementa todo OOXML nem valida compatibilidade com Office; hyperlinks ficam como texto. Gráficos PptxGenJS exigem LibreOffice para conversão. Prefira testar o fluxo LibreOffice em um ambiente que permita sua inicialização normal.

Arquivos em `--out`: presentation.pptx, presentation.pdf, previews/slide-N.png, previews/index.html, source/ (código e recursos portáteis), plan.json, scene.json, layout.json, qa.json, visual-review.json e notes.md se houver notas. `source/deck.json` usa caminhos portáteis para imagens copiadas. A partir de source/, `node scripts/cli.mjs build --spec deck.json --out ../reproduced --backend ooxml` reproduz o resultado em outra pasta. `reproduce.txt` acompanha cada saída.

Cada build usa pasta nova. `--force` só aceita saída marcada por esta ferramenta e limpa os arquivos gerados conhecidos; não o use para guardar originais. Guarde deck.json fora da pasta de saída. Não há `--skip-validation`: falhas de layout/conversão/renderização precisam ser corrigidas ou declaradas como bloqueio.

Fontes da implementação, consultadas em 2026-11-16:

- Skills Codex: https://developers.openai.com/codex/skills/ (redireciona para https://learn.chatgpt.com/docs/build-skills).
- Padrão aberto: https://agentskills.io/specification.
- PptxGenJS: https://gitbrent.github.io/PptxGenJS/docs/api-text/, /api-images/ e /api-charts/; versão confirmada no package.json oficial do projeto.
- LibreOffice: https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html.
- API C LibreOfficeKit: https://github.com/LibreOffice/core/blob/master/include/LibreOfficeKit/LibreOfficeKit.h e LibreOfficeKitInit.h na mesma pasta.
