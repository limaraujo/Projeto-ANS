## 1. Iris: grupos e projeções

Abertura (30 s). O estudo compara sete agrupadores e quatro projeções. Pergunta guia: a separação geométrica coincide com as três espécies? A apresentação sintetiza a revisão de 18/11/2026 e os resultados registrados.

## 2. Três espécies; quantos grupos?

Tempo: 1 min. Usou-se codigo/iris/iris.data. Para cada atributo, μ é a média das 150 observações e σ é a raiz da média dos desvios quadráticos em relação a μ. A análise é descritiva da base completa. Os rótulos de espécie servem à avaliação externa e à identificação visual.

## 3. Sete métodos, cinco perspectivas

Tempo: 1 min. K-Means minimiza distâncias quadráticas. FCM e Kernel FCM usam m=2. A variante de Zhang e Chen (2004) usa protótipos no espaço de entrada e RBF com gamma=0,25, igual ao inverso dos quatro atributos. Em k=3, FCM e Kernel FCM coincidiram na partição exclusiva (ARI entre partições = 1). K-Medoids usa PAM e distância euclidiana, com ARI externo de 0,6765 em k=3. GMM usa covariâncias completas. UPGMA usa ligação média com Manhattan. DBSCAN usa distância euclidiana.

## 4. O protocolo separa ajuste e avaliação

Tempo: 1,5 min. k varia de 1 a 5, sementes de 42 a 51. Há um único ajuste por chamada; K-Means e GMM usam n_init=1. Para cada método e k seleciona-se o menor objetivo, ou a maior log-verossimilhança no GMM. Objetivos não são comparados entre métodos. Fuzzy vira crisp pelo argmax das pertinências; GMM pela maior probabilidade posterior. UPGMA tem uma árvore e cinco cortes, não cinco novos ajustes. Após escolher k pela silhueta, calcula-se ARI com as espécies.

## 5. Silhueta e ARI respondem a perguntas distintas

Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.

## 6. A silhueta favorece dois grupos

Tempo: 1 min. Cada ponto corresponde à melhor execução do método naquele k, escolhida primeiro por sua função objetivo. Todas as séries coincidem em k=2 (0,580184). A subdivisão do bloco versicolor/virginica reduz a silhueta. Valores extraídos diretamente de metricas_por_k.csv.

## 7. Seis métodos chegam à mesma partição

Tempo: 1 min. K-Means, FCM, Kernel FCM, K-Medoids, GMM e UPGMA produzem a mesma partição selecionada, salvo permutações. As contingências confirmam 50/100. Isso explica a igualdade das métricas, sem implicar centros, pertinências ou funções objetivo iguais.

## 8. No GMM, três grupos elevam o ARI

Tempo: 1,5 min. Para k=2, silhueta 0,580184, ARI 0,568116 e BIC 797,6857. Para k=3, silhueta 0,372773, ARI 0,903874 e BIC 804,5072. Em três componentes: 50 setosas, 45 versicolors e 50 virginicas + cinco versicolors. O BIC foi calculado nos cinco modelos selecionados por log-verossimilhança e também favoreceu k=2. Em k=5, uma componente tem peso de 0,0604 e autovalor mínimo da covariância de 0,00000381, compatível com um ajuste muito estreito.

## 9. Uma árvore permite vários cortes

Tempo: 1 min. UPGMA com ligação média e Manhattan. O dendrograma usa as 12 subárvores finais, com contagens de folhas entre parênteses. As linhas marcam os cortes em dois e três grupos. A avaliação principal usa distância euclidiana. O diagnóstico com Manhattan retorna 0,6192, 0,5024, 0,4084 e 0,3770 para k de 2 a 5. Em k=3, o ARI externo é 0,7184.

## 10. DBSCAN encontra dois grupos e ruído

Tempo: 1 min. Os grupos têm 49 setosas e 97 flores (50 versicolors + 47 virginicas). O próprio ponto conta em min_samples. O ARI inclui o rótulo −1 do ruído. Com min_samples=5, os cinco raios de 0,6 a 1,0 produziram dois grupos, com 26, 8, 4, 4 e 3 pontos de ruído. A silhueta de 0,6405 em eps=0,6 usa apenas 124 flores. Os raios 0,8 e 0,9 produziram as mesmas contagens e silhueta, um patamar observado após a escolha inicial.

## 11. PCA retém 95,80% em dois eixos

Tempo: 1,5 min. A PCA foi ajustada com quatro componentes e SVD completa. Valores singulares: 20,8955, 11,7551, 4,7014 e 1,7582. A média de entrada é numericamente próxima de zero após o z-score. PC1 explica 72,7705% e PC2 23,0305%. Os maiores loadings da PC1 estão em comprimento e largura de pétala (0,9950 e 0,9682). PC2 enfatiza largura de sépala (0,8913). As cores e os símbolos indicam as espécies conhecidas.

## 12. Kernel PCA muda a geometria

Tempo: 1 min. Usa-se RBF com gamma=0,25, duas componentes e solver denso. Os autovalores 39,1321 e 17,7924 representam 39,8394% e 18,1140% do traço completo (98,2247). O percentual acumulado descreve a variância no espaço de características do RBF. Gamma foi fixado antes do ajuste. As cores e os símbolos indicam espécies.

## 13. t-SNE e UMAP enfatizam vizinhanças

Tempo: 1,5 min. t-SNE: perplexidade 30, inicialização PCA, semente 42, máximo de 1.000 iterações, KL final 0,1642 e taxa efetiva 50. O atributo n_iter_ registrou 999. UMAP: 15 vizinhos, min_dist=0,1, spread=1, inicialização espectral, semente 42 e uma thread. A saída 150 × 2 variou de −5,8964 a 10,1182 no eixo 1 e de 2,2188 a 9,0128 no eixo 2. A curva de similaridade usa a=1,5769 e b=0,8951. Cada técnica teve uma execução, com eixos sem unidade física.

## 14. t-SNE preservou mais vizinhos locais

Tempo: 1 min. Trustworthiness penaliza vizinhos artificiais introduzidos pela projeção comparando o espaço padronizado 4D com o 2D, usando dez vizinhos e distância euclidiana. PCA=0,978156, Kernel PCA=0,932238, t-SNE=0,988813 e UMAP=0,978349. PCA e UMAP são muito próximos neste índice. Os valores não demonstram superioridade universal nem estabilidade entre sementes. O gráfico tem origem zero e valores numéricos explícitos.

## 15. O alcance das conclusões é descritivo

Tempo: 1 min. Como diagnóstico separado, o K-Means com k=3, semente 42 e 100 inicializações obteve objetivo 140,9658, ARI 0,6201 e silhueta 0,4590. O melhor objetivo do protocolo principal foi 140,9684, uma redução de 0,0018%. O diagnóstico complementa as dez sementes originais e a varredura de eps. Gamma, perplexidade e número de vizinhos ficaram fixos. As métricas de agrupamento são do espaço padronizado de quatro atributos.

## 16. Grupos geométricos diferem de espécies

Fechamento (45 s). Responder à pergunta inicial: a geometria favoreceu setosa versus demais, enquanto a referência botânica tem três espécies. Essa diferença explica o contraste silhueta/ARI. Projeções complementam a leitura, preservando aspectos diferentes da estrutura. Abrir para perguntas.

## 17. Fontes e rastreabilidade

Material de apoio. ART: artigo revisado em 18/11/2026 e bibliografia. EXP: arquivos da Questão 1 e da Questão 2 em resultados/. DIAG: diagnósticos complementares da revisão.
