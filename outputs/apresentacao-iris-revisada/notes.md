## 1. Iris: grupos e projeções

Abertura (30 s). A separação geométrica coincide com as três espécies? O estudo compara sete agrupadores, incluindo sensibilidade aos hiperparâmetros, e quatro projeções.

## 2. Três espécies; quantos grupos?

Tempo: 1 min. Usou-se codigo/iris/iris.data, correspondente à edição da UCI. As linhas 35 e 38 diferem de load_iris do scikit-learn; por isso a origem do arquivo precisa ser explicitada. Para cada atributo, μ é a média das 150 observações e σ é o desvio-padrão populacional. Os rótulos de espécie não entram no ajuste nem na seleção.

## 3. Sete métodos, cinco perspectivas

Tempo: 1 min. O Kernel FCM usa protótipos no espaço de entrada e kernel RBF. K-Medoids usa PAM e Euclidiana. UPGMA usa ligação média com Manhattan. Perfis selecionados: K-Means: k-means++, k=2. FCM: m = 2, k=2. Kernel FCM: m = 2; γ = 0,05, k=2. K-Medoids: build, k=2. GMM/EM: spherical; reg = 0.01, k=2. UPGMA: ligação média, Manhattan, k=2. DBSCAN: ε = 0,694; min_samples = 3, k=2.

## 4. Tunagem e rodada final são separadas

Tempo: 1,5 min. A tunagem inclui 1120 ajustes particionais em k de 2 a 5 e 24 candidatos do DBSCAN: 1.144 ajustes. Em cada configuração e k, a melhor execução é escolhida pela função objetivo. O perfil fixado maximiza a média das quatro silhuetas, sem escolher k nessa etapa. A rodada final usa novas sementes, 52 a 61, nos cinco valores de k. Só então k é escolhido pela silhueta. UPGMA usa uma árvore; DBSCAN, a configuração elegível com pelo menos 95.0% de cobertura. O ARI não orienta nenhuma escolha.

## 5. Silhueta e ARI respondem a perguntas distintas

Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.

## 6. Rodada final: silhueta favorece k = 2

Tempo: 1 min. Cada ponto usa a execução de melhor objetivo no perfil escolhido e no respectivo k. Os seis métodos selecionaram a mesma partição em k=2. Um grupo reúne as 50 setosas. O outro contém 50 versicolors e 50 virginicas. Silhueta 0,5802 e ARI 0,5681 em 150 flores.

## 7. Tunagem: inicialização e difusividade

Tempo: 1,5 min. K-Means comparou random e k-means++; a diferença média foi pequena e k-means++ foi selecionado. No FCM, m = 2 venceu a média; m controla a difusividade das pertinências. No K-Medoids, a inicialização build foi superior à random na média. Cada ponto representa a melhor das dez execuções pela função objetivo, usando sementes 42–51.

## 8. Tunagem: perfis escolhidos em amarelo

Tempo: 2 min. Amarelo marca somente os perfis efetivamente escolhidos. O Kernel FCM selecionou m = 2 e gamma = 0,05. O GMM selecionou covariância spherical e regularização 0,01; em k = 3, esse perfil obteve silhueta 0,4568 e ARI 0,6199. Esses valores não pertencem ao perfil full. O DBSCAN selecionou epsilon 0,694 e min_samples 3 sob piso de 95% de cobertura.

## 9. GMM: critério interno não maximiza ARI

Tempo: 1,5 min. O perfil selecionado pela silhueta média foi spherical com regularização 0,01. Em k=3, ele obteve silhueta 0,4568 e ARI 0,6199. Na tunagem, full com a mesma regularização obteve silhueta menor, 0,3685, e ARI maior, 0,9222. Não são duas execuções do mesmo perfil. O ARI não participou da seleção; por isso a alternativa full não definiu o experimento final.

## 10. UPGMA: ARI 0,7184 no corte k = 3

Tempo: 1 min. O UPGMA usa ligação média e distância Manhattan para construir uma única árvore. As folhas mostradas são subárvores agregadas; os números entre parênteses são contagens de observações, não identificadores. As linhas marcam os cortes em dois e três grupos. Em k = 3, ARI = 0,7184 e silhueta euclidiana = 0,4517.

## 11. DBSCAN: cobertura muda a leitura da silhueta

Tempo: 1 min. O piso de 95% foi fixado antes da seleção dos hiperparâmetros. Os pisos inferiores foram examinados depois como análise de sensibilidade. Quando o DBSCAN descarta mais flores, a silhueta aumenta, mas as métricas passam a descrever amostras diferentes. Por isso, silhuetas sob coberturas distintas não devem ser comparadas sem considerar quais observações foram retidas. A configuração escolhida formou dois grupos e marcou seis flores como ruído: uma setosa, uma versicolor e quatro virginica.

## 12. PCA retém 95,80% em dois eixos

Tempo: 1,5 min. A PCA foi ajustada com quatro componentes e SVD completa. Valores singulares: 20,8955, 11,7551, 4,7014 e 1,7582. A média de entrada é numericamente próxima de zero após o z-score. PC1 explica 72,7705% e PC2 23,0305%. Os maiores loadings da PC1 estão em comprimento e largura de pétala (0,9950 e 0,9682). PC2 enfatiza largura de sépala (0,8913). As cores e os símbolos indicam as espécies conhecidas.

## 13. Kernel PCA muda a geometria

Tempo: 1 min. Usa-se RBF com gamma=0,25, duas componentes e solver denso. Os autovalores 39,1321 e 17,7924 representam 39,8394% e 18,1140% do traço completo (98,2247). O percentual acumulado descreve a variância no espaço de características do RBF. Gamma foi fixado antes do ajuste. As cores e os símbolos indicam espécies.

## 14. t-SNE e UMAP enfatizam vizinhanças

Tempo: 1,5 min. t-SNE: perplexidade 30, inicialização PCA, semente 42, máximo de 1.000 iterações, KL final 0,1642 e taxa efetiva 50. O atributo n_iter_ registrou 999. UMAP: 15 vizinhos, min_dist=0,1, spread=1, inicialização espectral, semente 42 e uma thread. A saída 150 × 2 variou de −5,8964 a 10,1182 no eixo 1 e de 2,2188 a 9,0128 no eixo 2. A curva de similaridade usa a=1,5769 e b=0,8951. Cada técnica teve uma execução, com eixos sem unidade física.

## 15. Maior preservação local: t-SNE

Tempo: 1 min. Trustworthiness penaliza vizinhos artificiais introduzidos pela projeção comparando o espaço padronizado 4D com o 2D, usando dez vizinhos e distância euclidiana. PCA=0,978156, Kernel PCA=0,932238, t-SNE=0,988813 e UMAP=0,978349. PCA e UMAP são muito próximos neste índice. Os valores não demonstram superioridade universal nem estabilidade entre sementes. O gráfico tem origem zero e valores numéricos explícitos.

## 16. Inicializações alteram o ARI em k = 3

Tempo: 1 min. Em k = 3, o K-Means atingiu o melhor objetivo em 1 de 10 execuções e o ARI variou de 0,4290 a 0,6451. No GMM, o ARI variou de 0,4199 a 0,6199. Considerando como equivalentes os objetivos a até 10^-3 do melhor valor, 6 de 10 execuções do GMM atingiram o melhor objetivo; as log-verossimilhanças são próximas, não exatamente iguais. Dez inicializações não equivalem a dez amostras independentes do conjunto de dados.

## 17. Grupos geométricos diferem de espécies

Fechamento (45 s). Os seis métodos selecionaram a mesma partição em k=2. Um grupo reúne as 50 setosas. O outro contém 50 versicolors e 50 virginicas. Silhueta 0,5802 e ARI 0,5681 em 150 flores. As sete partições coincidem nas 144 flores retidas, com silhueta 0,6035 e ARI 0,5760. Retomar a comparação com as três espécies e o papel das projeções.

## 18. Referências acadêmicas

Material de apoio. As referências foram preservadas do artigo IEEE revisado. Não são exibidos caminhos, diretórios ou identificadores internos do projeto.
