# Validação e correção

`build` verifica o conteúdo e a geometria antes de escrever e depois exige conversão do PPTX para PDF e renderização real pelo Poppler. O motor preferencial é LibreOffice. `qa.conversion` identifica o motor efetivo; se o modo automático recorrer ao conversor nativo, registra também a falha original. Falhas retornam código 1, preservando qa.json com status failed. O conversor nativo lê o PPTX efetivamente escrito, não reutiliza a cena como se tivesse aberto o arquivo.

Verificações: CRC do ZIP, XML bem formado, partes obrigatórias, destinos das relações internas, quantidade de slides declarados e presentes, texto nativo em todos os slides, geometria OOXML, quantidade de páginas PDF, presença do texto de cada caixa no PDF, limites das palavras no PDF, assinatura e quantidade de PNGs. O scene também verifica limites, fonte mínima, contraste e colisões entre caixas de conteúdo. Painéis, dados e conectores têm sobreposição intencional e são excluídos da detecção de colisões.

A quebra de linhas é automática e não diminui a fonte. Excesso de texto é bloqueado: o agente deve condensar com rigor, redistribuir ou dividir slides. Corrija o deck.json original e use `build ... --force`; a revisão visual é invalidada pela regeneração. Não edite apenas um PNG ou o PDF, pois o PPTX ficaria divergente.

Após gerar, abra **cada PNG**. Confira títulos, última linha das caixas, fórmulas, fontes substituídas, acentos, conectores, contraste, sequência, legendas, escalas e citações. O relatório só passa após declaração de inspeção com todos os números de página e sem problemas abertos:

```json
{"status":"passed","pages":[1,2,3],"issues":[],"reviewer":"Codex","method":"Inspeção visual de cada PNG com a ferramenta de imagens","observations":["Títulos e última linha conferidos"]}
```

Use `node scripts/cli.mjs review --out outputs/exemplo --file review.json`. Com falhas abertas use status failed e detalhe issues; sem visualizador use unavailable e descreva o motivo. `validate --out ...` reexecuta os testes e combina com a revisão existente. Um SHA-256 do PPTX, PDF, cena e PNGs vincula a revisão aos artefatos: alterações invalidam a conclusão visual. Regenerar com --force também invalida a revisão.

Limites: métricas de texto são heurísticas; presença no PDF não prova visibilidade completa; interseções podem ter falsos positivos/negativos; não há OCR/segmentação visual automática nem auditoria científica automática. ZIP/XML não equivalem a validação completa ECMA-376. Abertura no LibreOffice fornece evidência adicional quando disponível; conversão nativa não estabelece compatibilidade com Office. O conversor nativo aceita somente formas e textos do subconjunto gerado pela skill, além de imagens; rejeita gráficos Office, grupos, transformações e conteúdo que não sabe representar. Não use seu PDF para afirmar que um PPTX arbitrário abre corretamente no PowerPoint. A revisão registrada é humana/do agente, não verificação independente de visão computacional.
