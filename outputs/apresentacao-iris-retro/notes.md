## 1. Iris: grupos e projeções

Abertura (30 s). O estudo compara sete agrupadores e quatro projeções. Pergunta guia: a separação geométrica coincide com as três espécies? A apresentação sintetiza o artigo revisado e os artefatos existentes; os ajustes não foram reexecutados.

## 2. Três espécies; quantos grupos?

Tempo: 1 min. Usou-se codigo/iris/iris.data. A padronização subtrai a média e divide pelo desvio-padrão populacional. A análise é descritiva da base completa, sem treino/teste. As espécies conhecidas fornecem uma referência posterior, não uma resposta usada durante o treinamento.

## 3. Sete métodos, cinco perspectivas

Tempo: 1 min. K-Means minimiza distâncias quadráticas; FCM usa m=2. Kernel FCM utiliza RBF, gamma=0,25, e protótipos no espaço de entrada. K-Medoids usa PAM e distância euclidiana. GMM usa covariâncias completas. UPGMA usa ligação média com Manhattan. DBSCAN usa distância euclidiana. As explicações teóricas são sínteses da fundamentação citada no artigo local, não novas verificações bibliográficas.

## 4. O protocolo separa ajuste e avaliação

Tempo: 1,5 min. k varia de 1 a 5, sementes de 42 a 51. Há um único ajuste por chamada; K-Means e GMM usam n_init=1. Para cada método e k seleciona-se o menor objetivo, ou a maior log-verossimilhança no GMM. Objetivos não são comparados entre métodos. Fuzzy vira crisp pelo argmax das pertinências; GMM pela maior probabilidade posterior. UPGMA tem uma árvore e cinco cortes, não cinco novos ajustes. Após escolher k pela silhueta, calcula-se ARI com as espécies.

## 5. Silhueta e ARI respondem a perguntas distintas

Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.

## 6. A silhueta favorece dois grupos

Tempo: 1 min. Cada ponto corresponde à melhor execução do método naquele k, escolhida primeiro por sua função objetivo. Todas as séries coincidem em k=2 (0,580184). A subdivisão do bloco versicolor/virginica reduz a silhueta. Valores extraídos diretamente de metricas_por_k.csv.

## 7. Seis métodos chegam à mesma partição

Tempo: 1 min. K-Means, FCM, Kernel FCM, K-Medoids, GMM e UPGMA produzem a mesma partição selecionada, salvo permutações. As contingências confirmam 50/100. Isso explica a igualdade das métricas, sem implicar centros, pertinências ou funções objetivo iguais.

## 8. No GMM, três grupos elevam o ARI

Tempo: 1,5 min. Esta é uma análise posterior do mesmo protocolo, sem mudar a seleção oficial k=2. Para k=2, silhueta 0,580184 e ARI 0,568116; para k=3, silhueta 0,372773 e ARI 0,903874. Em três componentes: um grupo com 50 setosas, outro com 45 versicolors e outro com 50 virginicas + cinco versicolors. ARI de 0,9039 não significa 90,39% de acurácia preditiva.

## 9. Uma árvore permite vários cortes

Tempo: 1 min. O dendrograma é redesenhado a partir da matriz de ligações armazenada em execucoes_questao_1.json, não recalculada. A exibição é truncada às 12 subárvores finais; parênteses indicam a quantidade de folhas agregadas. A linha amarela é um corte ilustrativo entre as duas últimas alturas, resultando em dois grupos. Cinco cortes de uma árvore contam como uma execução no protocolo. A silhueta da partição usa distância euclidiana.

## 10. DBSCAN encontra dois grupos e ruído

Tempo: 1 min. Os grupos têm 49 setosas e 97 flores (50 versicolors + 47 virginicas). O próprio ponto conta em min_samples. A silhueta do DBSCAN exclui quatro ruídos e descreve 146 pontos; os demais métodos usam os 150. Portanto a maior silhueta numérica não demonstra superioridade global. O ARI inclui o rótulo −1 do ruído. Não houve otimização orientada pelas espécies.

## 11. PCA retém 95,80% em dois eixos

Tempo: 1,5 min. A PCA foi ajustada com quatro componentes e SVD completa, exibindo aqui as duas primeiras. PC1 explica 72,7705% e PC2 23,0305%. Os maiores loadings da PC1 estão em comprimento e largura de pétala (0,9950 e 0,9682); PC2 enfatiza largura de sépala (0,8913). Loadings são autovetores multiplicados pela raiz do autovalor. Variância alta não equivale a separação perfeita das espécies. Cores e símbolos representam rótulos posteriores; não são clusters ajustados na projeção.

## 12. Kernel PCA muda a geometria

Tempo: 1 min. Usa-se kernel RBF gamma=0,25, matriz centralizada, duas componentes e solver denso. Autovalores: 39,132080 e 17,792370. São do kernel centralizado, não da covariância original. Não se divide apenas sua soma para anunciar variância original explicada. A escala gamma foi fixa; não houve análise de sensibilidade. Cores e símbolos indicam espécies.

## 13. t-SNE e UMAP enfatizam vizinhanças

Tempo: 1,5 min. t-SNE: perplexidade 30, inicialização PCA, seed 42, máximo de 1.000 iterações, KL final 0,164197, taxa efetiva 50; n_iter_ reportado 999. UMAP: 15 vizinhos, min_dist=0,1, spread=1, inicialização espectral, seed 42 e uma thread. Uma execução por técnica. Eixos sem unidade física; orientação, distâncias entre ilhas e densidades não são reproduções fiéis do espaço original. Não foram feitos agrupamentos nestas projeções.

## 14. t-SNE preservou mais vizinhos locais

Tempo: 1 min. Trustworthiness penaliza vizinhos artificiais introduzidos pela projeção comparando o espaço padronizado 4D com o 2D, usando dez vizinhos e distância euclidiana. PCA=0,978156, Kernel PCA=0,932238, t-SNE=0,988813 e UMAP=0,978349. PCA e UMAP são muito próximos neste índice. Os valores não demonstram superioridade universal nem estabilidade entre sementes. O gráfico tem origem zero e valores numéricos explícitos.

## 15. O alcance das conclusões é descritivo

Tempo: 1 min. Repetir sementes não cria novas amostras nem garante ótimo global. O artigo revisado não inclui as alegadas 840 execuções complementares do artigo anterior por ausência de artefatos. A apresentação usa os resultados existentes, sem reexecutar ajustes ou certificar a execução histórica. As métricas de agrupamento são do espaço original padronizado, não das projeções.

## 16. Grupos geométricos diferem de espécies

Fechamento (45 s). Responder à pergunta inicial: a geometria favoreceu setosa versus demais, enquanto a referência botânica tem três espécies. Essa diferença explica o contraste silhueta/ARI. Projeções complementam a leitura, preservando aspectos diferentes da estrutura. Abrir para perguntas.

## 17. Fontes e rastreabilidade

Material de apoio. ART: artigo revisado da Equipe 08, com fundamentação e bibliografia original. EXP: CSV e execuções Q1/metadados/contingências. PROJ: execuções Q2 e CSV de coordenadas. As figuras foram redesenhadas a partir desses artefatos. Todos os dados já estavam no projeto. Consulte o artigo para as referências primárias dos algoritmos e métricas.
