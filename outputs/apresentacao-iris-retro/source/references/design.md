# Sistema visual

Os tokens estão em `assets/templates/profiles.json`; layouts em `scripts/layout.mjs`. Todos usam 13,3333 × 7,5 polegadas (16:9), margem horizontal ≥0,65, conteúdo abaixo de 1,85 e rodapé em 7,13. Grade de composição com intervalos típicos de 0,2–0,45 polegada.

| Perfil | Uso | Fundo | Texto | Acento |
| --- | --- | --- | --- | --- |
| Academic Minimal | Defesa, seminário, aula | branco | azul escuro | azul |
| Dark Technical | Algoritmos, engenharia | azul quase preto | branco | ciano |
| Modern Scientific | Ciência, síntese de resultados | cinza muito claro | verde escuro | verde |
| retroui-pixel | Identidade retro em conteúdo técnico | preto | branco | amarelo |

O perfil `retroui-pixel` possui compositor próprio e componentes nativos descritos em [retroui-pixel.md](retroui-pixel.md). Os tokens e tamanhos dos três perfis originais permanecem iguais. As fontes descritas abaixo são desses perfis; o novo usa Pixelify Sans/JetBrains Mono com detecção de disponibilidade e fallback explícito.

Fontes: Liberation Sans; código: Liberation Mono. Não são embutidas. Se faltarem, o sistema pode substituí-las; confira com `fc-match 'Liberation Sans'`. Título de capa 44 pt, títulos 32 pt, corpo 22–26 pt. Mínimos automáticos: títulos 30, corpo/código 20, legendas/rótulos 18, URLs bibliográficas 14, créditos/rodapés 12. Elementos de conteúdo exigem contraste ≥4,5:1; rótulos pequenos também. Nunca diminuir fonte para esconder excesso.

Layouts: capa, pontos, comparação em duas colunas, processo de 2–4 etapas, equação, pseudocódigo, dispersão, barras, figura e bibliografia de até três entradas. Para mais referências, divida em slides. Para texto longo, reestruture ou amplie o número de slides e atualize `plan.slideCount`.

Diagramas usam formas nativas alinhadas, numeração, espaçamento e conectores. Cores distinguem grupos, sempre com rótulos. Gráficos têm unidade, legenda e descrição da origem; dispersões são esquemas com marcadores nativos e rótulos dos eixos, não ferramenta de leitura numérica exata. Use gráfico de dispersão específico ou figure com escala/ticks se os valores exatos dos eixos forem essenciais. O gráfico de barras nativo tem dados embutidos com PptxGenJS; no modo OOXML, barras e números são formas/textos editáveis. Figuras PNG/JPG/SVG mantêm a proporção. Evite imagens sem função explicativa.
