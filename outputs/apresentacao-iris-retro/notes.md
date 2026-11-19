## 1. Iris: grupos e projeções

Abertura (30 s). A separação geométrica coincide com as três espécies? O estudo compara sete agrupadores, incluindo sensibilidade aos hiperparâmetros, e quatro projeções.

## 2. Três espécies; quantos grupos?

Tempo: 1 min. Usou-se codigo/iris/iris.data. Para cada atributo, μ é a média das 150 observações e σ é a raiz da média dos desvios quadráticos em relação a μ. A análise é descritiva da base completa. Os rótulos de espécie servem à avaliação externa e à identificação visual.

## 3. Sete métodos, cinco perspectivas

Tempo: 1 min. O Kernel FCM usa protótipos no espaço de entrada e kernel RBF. K-Medoids usa PAM e Euclidiana. UPGMA usa ligação média com Manhattan. Perfis selecionados: K-Means: random, k=2. FCM: m = 2, k=2. Kernel FCM: m = 2; γ = 0,25, k=2. K-Medoids: random, k=2. GMM/EM: full; reg = 1e-06, k=2. UPGMA: ligação média, Manhattan, k=2. DBSCAN: ε = 0,694; min_samples = 3, k=2.

## 4. O protocolo separa ajuste e avaliação

Tempo: 1,5 min. A grade inclui 1120 ajustes nos métodos particionais em k de 2 a 5 e 24 candidatos no DBSCAN. Em cada perfil e k, escolhe-se a melhor execução pela função objetivo. Silhueta seleciona perfil e k, com desempate por menor k e ordem da grade. Os perfis escolhidos acrescentam dez execuções em k=1. UPGMA usa cinco cortes da mesma árvore. O DBSCAN escolhe a maior silhueta válida com pelo menos 95.0% de cobertura. O ARI é calculado depois das escolhas.

## 5. Silhueta e ARI respondem a perguntas distintas

Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.

## 6. A silhueta favorece dois grupos

Tempo: 1 min. Cada ponto usa a execução de melhor objetivo no perfil escolhido e no respectivo k. Os seis métodos selecionaram a mesma partição em k=2. Um grupo reúne as 50 setosas. O outro contém 50 versicolors e 50 virginicas. Silhueta 0,5802 e ARI 0,5681 em 150 flores.

## 7. Hiperparâmetros afetam as métricas

Tempo: 1,5 min. Cada extremo usa a melhor execução por objetivo da sua configuração. K-Means: extremos random (0,4584) e k-means++ (0,4590); ARI 0,6101 a 0,6201. FCM: extremos m = 2 (0,4574) e m = 1,5 (0,4590); ARI 0,6201 a 0,6303. Kernel FCM: extremos m = 2; γ = 1 (0,4562) e m = 1,5; γ = 0,05 (0,4590); ARI 0,6201 a 0,6648. K-Medoids: extremos random (0,4497) e build (0,4555); ARI 0,6416 a 0,6765. GMM/EM: extremos tied; reg = 1e-06 (0,2406) e spherical; reg = 0.01 (0,4568); ARI 0,4375 a 0,9222.

## 8. GMM em dois e três componentes

Tempo: 1,5 min. Em k=2, silhueta 0,5802 e ARI 0,5681. Em k=3, silhueta 0,3728 e ARI 0,9039. Comparamos o mesmo perfil em k distintos. A silhueta orientou a escolha; o ARI descreve a concordância com as espécies.

## 9. Uma árvore permite vários cortes

Tempo: 1 min. UPGMA com ligação média e Manhattan. O dendrograma usa as 12 subárvores finais, com contagens de folhas entre parênteses. As linhas marcam os cortes em dois e três grupos. A avaliação principal usa distância euclidiana. O diagnóstico com Manhattan retorna 0,6192, 0,5024, 0,4084 e 0,3770 para k de 2 a 5. Em k=3, o ARI externo é 0,7184.

## 10. DBSCAN avalia os pontos retidos

Tempo: 1 min. Excluir os rótulos −1 do DBSCAN reduz a amostra de ambas as métricas. O mínimo de 3 inclui o próprio ponto. A maior silhueta da grade foi 0,6482 com cobertura de 76,67%. As sete partições coincidem nas 144 flores retidas, com silhueta 0,6035 e ARI 0,5760.

## 11. PCA retém 95,80% em dois eixos

Tempo: 1,5 min. A PCA foi ajustada com quatro componentes e SVD completa. Valores singulares: 20,8955, 11,7551, 4,7014 e 1,7582. A média de entrada é numericamente próxima de zero após o z-score. PC1 explica 72,7705% e PC2 23,0305%. Os maiores loadings da PC1 estão em comprimento e largura de pétala (0,9950 e 0,9682). PC2 enfatiza largura de sépala (0,8913). As cores e os símbolos indicam as espécies conhecidas.

## 12. Kernel PCA muda a geometria

Tempo: 1 min. Usa-se RBF com gamma=0,25, duas componentes e solver denso. Os autovalores 39,1321 e 17,7924 representam 39,8394% e 18,1140% do traço completo (98,2247). O percentual acumulado descreve a variância no espaço de características do RBF. Gamma foi fixado antes do ajuste. As cores e os símbolos indicam espécies.

## 13. t-SNE e UMAP enfatizam vizinhanças

Tempo: 1,5 min. t-SNE: perplexidade 30, inicialização PCA, semente 42, máximo de 1.000 iterações, KL final 0,1642 e taxa efetiva 50. O atributo n_iter_ registrou 999. UMAP: 15 vizinhos, min_dist=0,1, spread=1, inicialização espectral, semente 42 e uma thread. A saída 150 × 2 variou de −5,8964 a 10,1182 no eixo 1 e de 2,2188 a 9,0128 no eixo 2. A curva de similaridade usa a=1,5769 e b=0,8951. Cada técnica teve uma execução, com eixos sem unidade física.

## 14. t-SNE preservou mais vizinhos locais

Tempo: 1 min. Trustworthiness penaliza vizinhos artificiais introduzidos pela projeção comparando o espaço padronizado 4D com o 2D, usando dez vizinhos e distância euclidiana. PCA=0,978156, Kernel PCA=0,932238, t-SNE=0,988813 e UMAP=0,978349. PCA e UMAP são muito próximos neste índice. Os valores não demonstram superioridade universal nem estabilidade entre sementes. O gráfico tem origem zero e valores numéricos explícitos.

## 15. O alcance das conclusões é descritivo

Tempo: 1 min. As sementes variam a inicialização com as mesmas observações. As configurações vencedoras dependem da grade e, para DBSCAN, do mínimo de cobertura. Na Questão 2, cada projeção usa uma configuração. As métricas de agrupamento são calculadas no espaço padronizado de quatro atributos.

## 16. Grupos geométricos diferem de espécies

Fechamento (45 s). Os seis métodos selecionaram a mesma partição em k=2. Um grupo reúne as 50 setosas. O outro contém 50 versicolors e 50 virginicas. Silhueta 0,5802 e ARI 0,5681 em 150 flores. As sete partições coincidem nas 144 flores retidas, com silhueta 0,6035 e ARI 0,5760. Retomar a comparação com as três espécies e o papel das projeções.

## 17. Fontes e rastreabilidade

Material de apoio. ART corresponde ao artigo e à bibliografia. EXP corresponde às grades, métricas e projeções em resultados/. DIAG corresponde às tabelas e aos diagnósticos produzidos para o artigo.
