# Protocolo de correção da entrega da Equipe 08

Use o [artigo revisado](artigo/artigo_ieee_revisado.pdf) e a [apresentação em PDF](../apresentacao_iris_retro.pdf) como referência da entrega. As correções abaixo partem dos resultados já registrados. A prioridade é explicar as escolhas experimentais, demonstrar o efeito dos parâmetros e alinhar o texto do artigo, dos slides, do notebook e do guia.

## 1. Justificar a cobertura mínima do DBSCAN

**Prioridade alta.** Edite a seção IV-A, a seção V-D, a Tabela VII e a conclusão do artigo. Atualize o slide 10 e suas notas.

1. Explique o piso de **95%** como um limite experimental para o descarte de observações. Na Iris, ele exige pelo menos 143 das 150 flores e permite excluir até sete. Entre candidatos com silhueta definida e cobertura suficiente, a regra escolhe a maior silhueta. Em caso de empate, use maior cobertura e depois a ordem original da grade. Calcule e interprete o ARI das flores retidas após a escolha.
2. Reaplique a regra aos 24 candidatos registrados, com pisos de 94%, 95% e 97%. Exiba o resultado como análise de sensibilidade do piso e indique que a configuração principal usa 95%. Compare os valores antes do arredondamento.

   | Piso | ε | `min_samples` | Flores retidas | Cobertura | Silhueta | ARI |
   |---:|---:|---:|---:|---:|---:|---:|
   | 94% | 0,694293 | 5 | 142 | 94,67% | 0,6104 | 0,5733 |
   | **95%** | **0,694293** | **3** | **144** | **96,00%** | **0,6035** | **0,5760** |
   | 97% | 1,000000 | 10 | 146 | 97,33% | 0,5984 | 0,5706 |

3. Use as duas primeiras linhas para mostrar o efeito de `min_samples` com ε fixo. Ao subir de 3 para 5, as partições continuam com dois grupos, a cobertura cai e a silhueta aumenta. Mostre no slide 10 o contraste entre o perfil escolhido e a maior silhueta bruta da grade, **0,6482 em 115 flores (76,67%)**. Nos resultados do artigo, registre que os seis descartes do perfil final incluem uma *setosa*, uma *versicolor* e quatro *virginicas*. Essa contagem é descritiva e posterior ao ajuste.
4. Retome na conclusão e no slide 16 que as sete partições coincidiram nas 144 flores, salvo a numeração dos grupos. Nomeie os dois ARIs para distinguir o **0,5760 com as espécies** do **1,0000 entre partições**. A diferença de silhueta entre as tabelas com 150 e 144 observações acompanha a mudança de amostra.

**Critério de aceite.** A regra e o piso aparecem no texto e no slide. A tabela de sensibilidade reproduz as linhas acima. A comparação comum usa a máscara do DBSCAN sobre as sete partições já ajustadas. [Grade](../resultados/tunagem/dbscan.csv) · [Amostra comum](../resultados/tunagem/comparacao_mesma_amostra.csv) · [Contingências](../resultados/contingencias.json)

## 2. Explicar a sensibilidade dos métodos particionais

**Prioridade alta.** Revise a justificativa da grade na seção IV-B e a interpretação da Tabela VI na seção V-C. Use comparações com *k* fixo e um parâmetro variando de cada vez.

- **Justificativa da grade.** Explique que `random` e `k-means++` no K-Means, e `random` e `build` no PAM, comparam estratégias de inicialização. Para os métodos fuzzy, relacione os valores de *m* ao perfil de referência com *m* = 2 e os valores de γ a escalas mais amplas ou mais locais do RBF. No GMM, explique as restrições de cada tipo de covariância e a variação da regularização em ordens de grandeza. No DBSCAN, relacione os raios fixos e relativos à escala padronizada e explicite a referência de distância ao quinto vizinho, contando o próprio ponto. Descreva os intervalos como exploratórios e documente a motivação efetivamente usada pela equipe.
- **Contrastes observados.** Em *k* = 3, use os exemplos abaixo para comentar a direção e a magnitude do efeito em cada métrica.

  | Método | Alteração | Silhueta | ARI |
  |---|---|---|---|
  | K-Means | `random` → `k-means++` | 0,4584 → 0,4590 | 0,6101 → 0,6201 |
  | PAM | `random` → `build` | 0,4497 → 0,4555 | 0,6765 → 0,6416 |
  | FCM | *m* de 2 para 1,5 | 0,4574 → 0,4590 | 0,6303 → 0,6201 |
  | Kernel FCM | Fixar *m* = 2 e variar γ de 0,25 para 1 | 0,4574 → 0,4562 | 0,6303 → 0,6648 |
  | GMM `full` | Regularização de 10⁻⁶ para 10⁻² | 0,3728 → 0,3685 | 0,9039 → 0,9222 |

- **Empates e legenda.** Na Tabela VI, indique o empate entre as três regularizações `spherical` na maior silhueta do GMM em *k* = 3. No slide 7, use a legenda “Faixas da grade em k = 3. O ponto mostra o perfil selecionado em k* = 2, avaliado em k = 3.” Nos slides 8 e 16, vincule o ARI 0,9039 ao perfil selecionado. No artigo, apresente o ARI 0,9222 como resultado descritivo de outro perfil da grade.

**Critério de aceite.** Cada comparação usa a execução de melhor objetivo da célula correspondente. O leitor consegue identificar o que foi variado, o que foi fixado e por que os efeitos de silhueta e ARI podem divergir. [Tabela da grade](../resultados/tunagem/particionais.csv) · [Figuras de sensibilidade](../resultados/tunagem/figuras/)

## 3. Corrigir as descrições técnicas

- **Chamadas e convergência.** Na discussão do artigo e nas notas dos slides 4 e 15, use “dez chamadas por perfil e *k*” ao contar o protocolo. Registre que as chamadas de PAM com `build` repetiram partição e objetivo em cada *k* da grade e que a busca de um único medoide em *k* = 1 foi exaustiva. Informe que dois ajustes do GMM atingiram o limite de 100 iterações sem convergir. São `full` com regularização 10⁻², *k* = 4, semente 45, e `diag` com regularização 10⁻², *k* = 5, semente 44. As melhores execuções nas duas células convergiram. [Execuções da grade](../resultados/tunagem/execucoes.json) · [Log](../resultados/execucao_console.txt)
- **Trustworthiness.** Na introdução da Questão 2 do notebook, no slide 14 e na fala de conclusão do guia, use a definição que já consta no artigo, § VI-E. “O índice penaliza pontos que entram na lista dos dez vizinhos após a projeção. A penalidade cresce quanto mais distante o ponto estava no ranking original.” Use “Maior *trustworthiness* com dez vizinhos” como título do slide 14. Vincule o valor 0,9888 à configuração avaliada. [Notebook](../codigo/Projeto_AMNS_Equipe8.ipynb) · [Guia](../GUIA_APRESENTACAO.md)
- **Controle de versões.** Corrija o glossário do guia para apresentar ε = 0,694293 e `min_samples=3` como escolha final, com ε = 0,8 e `min_samples=5` como referência. No README e no registro de verificação, identifique `artigo_ieee.pdf`, `artigo_ieee_atualizado.pdf` e `resultados/historico/` como materiais históricos. Registre que a comprovação dos 840 ajustes mencionados no artigo antigo depende de registros individuais ausentes. [README](../README.md) · [Verificação do artigo](artigo/verificacao_revisao.md)

## 4. Regenerar e conferir a entrega

1. Edite `docs/artigo/analisar_revisao.py` para calcular as novas sínteses a partir dos CSVs e JSONs existentes. Use o diagnóstico gerado como fonte comum para o Typst e o script `outputs/apresentacao-retro-src/gerar_apresentacao.py`. Atualize textos e notas nesse script. Use os comandos abaixo a partir da raiz. Abra os PDFs produzidos para checar legibilidade, eixos, legendas e referências antes de atualizar os arquivos de entrega.

   ```sh
   revisao_dir=$(mktemp -d)
   .venv/bin/python docs/artigo/analisar_revisao.py
   typst compile docs/artigo/artigo_ieee_revisado.typ "$revisao_dir/artigo_ieee_revisado.pdf" --root .
   .venv/bin/python outputs/apresentacao-retro-src/gerar_apresentacao.py
   node outputs/apresentacao-retro-src/engine/scripts/cli.mjs build --spec outputs/apresentacao-retro-src/deck.json --out "$revisao_dir/slides" --backend ooxml --pdf-engine native
   ```

2. Rode o validador em uma cópia temporária, pois ele grava `validacao.json` no diretório indicado. Confira no artigo, nos slides e nos arquivos de saída os marcos da tabela.

   ```sh
   cp -a resultados "$revisao_dir/resultados"
   .venv/bin/python codigo/validar_resultados.py --diretorio-resultados "$revisao_dir/resultados"
   ```

   | Verificação | Resultado esperado |
   |---|---|
   | Contagem da Questão 1 | 1.195 ajustes ao incluir a busca e 252 registros no protocolo final. Os 252 incluem 200 ajustes reaproveitados, 50 chamadas em *k* = 1, uma árvore e o DBSCAN selecionado |
   | Seis métodos na base completa | `k* = 2`, silhueta 0,5802, ARI 0,5681, 150 flores |
   | DBSCAN principal e amostra comum | Dois grupos, seis descartes, 144 flores, silhueta 0,6035, ARI com espécies 0,5760 e ARI entre partições 1,0000 |
   | GMM em três componentes | ARI 0,9039 no perfil selecionado e 0,9222 no perfil alternativo identificado na grade |
   | Questão 2 | Quatro gráficos 2D. PCA com 95,80% em dois eixos, Kernel PCA com 57,95% do traço do kernel, t-SNE com KL 0,1642 e *trustworthiness* 0,9888, UMAP com 15 vizinhos e `min_dist=0,1` |

3. Faça a leitura final dos slides 4, 7, 8, 10, 14, 15 e 16 e das respectivas notas. Confira que o PDF de entrega e o PPTX foram gerados da mesma revisão. Deixe o artigo revisado e a apresentação atual claramente identificados no README e no registro de verificação.

**Melhorias opcionais.** Repetir t-SNE e UMAP com outras sementes e escalas de vizinhança, ou registrar o critério de parada dos métodos fuzzy, exige experimentação adicional. Esses diagnósticos podem aprofundar a discussão em uma revisão posterior.
