# Fundamentação matemática dos algoritmos — Agrupamento e projeções na Iris

## Objetivo e modo de estudo

Esta apostila aprofunda os **sete agrupadores** e as **quatro técnicas de redução de dimensionalidade** utilizados no projeto. O foco é entender de onde vêm as equações, o que cada etapa resolve e em quais condições uma afirmação sobre o algoritmo é válida.

O [guia de apresentação](GUIA_APRESENTACAO.md) organiza a fala e os resultados. Este documento desenvolve sua base matemática. Não é necessário decorar cada derivação, mas você deve conseguir reconstruir o raciocínio: **representação → objetivo ou regra de construção → atualização → parada → interpretação**.

As configurações do projeto foram conferidas em [algoritmos.py](codigo/algoritmos.py), [questoes.py](codigo/questoes.py), nos resultados persistidos e, para detalhes específicos, no código das bibliotecas instaladas. Nenhum experimento principal foi reexecutado para produzir o texto. Exemplos numéricos identificados como didáticos são independentes da Iris.

### Organização

1. [Notação e dimensões](#1-notação-e-dimensões)
2. [Fundamentos matemáticos](#2-fundamentos-matemáticos)
3. [K-Means](#3-k-means)
4. [Fuzzy C-Means](#4-fuzzy-c-means)
5. [Kernel Fuzzy C-Means](#5-kernel-fuzzy-c-means)
6. [K-Medoids e PAM](#6-k-medoids-e-pam)
7. [Misturas gaussianas e EM](#7-misturas-gaussianas-e-em)
8. [UPGMA](#8-upgma)
9. [DBSCAN](#9-dbscan)
10. [PCA](#10-pca)
11. [Kernel PCA](#11-kernel-pca)
12. [t-SNE](#12-t-sne)
13. [UMAP](#13-umap)
14. [Matemática das métricas](#14-matemática-das-métricas)
15. [Relações entre os métodos e custos](#15-relações-entre-os-métodos-e-custos)
16. [Aplicação ao projeto](#16-aplicação-ao-projeto)
17. [Exercícios com resolução](#17-exercícios-com-resolução)
18. [Fontes e alcance](#18-fontes-e-alcance)

Sugestão de sequência: primeiro capítulos 1–4; depois 5–9; em seguida 10–13; por fim métricas, relações e exercícios. As equações usam LaTeX entre `$$`, que pode ser visualizado em leitores Markdown com suporte matemático.

## 1. Notação e dimensões

Considere n observações com d atributos. Na Iris, `n = 150` e `d = 4`.

$$
X=\begin{bmatrix}x_1^T\\\vdots\\x_n^T\end{bmatrix}\in\mathbb R^{n\times d}.
$$

Cada vetor xᵢ é tratado matematicamente como coluna, embora ocupe uma linha de X. A transposta deixa explícita essa convenção.

| Símbolo | Significado | Dimensão típica |
|---|---|---|
| xᵢ | Atributos da observação i | d × 1 |
| k | Quantidade de grupos ou componentes | Escalar inteiro |
| cᵢ | Grupo exclusivo atribuído a i | Inteiro |
| vⱼ ou μⱼ | Centro ou protótipo j | d × 1 |
| U = [uᵢⱼ] | Matriz de pertinências fuzzy | n × k |
| R = [rᵢⱼ] | Responsabilidades no GMM | n × k |
| Σⱼ | Covariância do componente j | d × d |
| D = [dᵢⱼ] | Dissimilaridades entre observações | n × n |
| K | Matriz de kernel entre observações | n × n |
| Z | Coordenadas da projeção | n × q, com q = 2 nas figuras |
| zᵢ | Posição de i no mapa | q × 1 |
| W | Base de projeção linear | d × q |

O rótulo botânico yᵢ é uma referência externa. Ele não participa dos ajustes. Os identificadores dos clusters podem ser permutados sem mudar uma partição.

Nos capítulos de vizinhança, usaremos **h** para a quantidade de vizinhos de uma métrica e **M** para o parâmetro de vizinhança do UMAP, evitando confundi-los com k de agrupamento.

## 2. Fundamentos matemáticos

### 2.1. Produto interno, norma e distância

O produto interno euclidiano é:

$$
\langle x,v\rangle=x^Tv=\sum_{a=1}^{d}x_av_a.
$$

Ele relaciona comprimento e orientação: `xᵀv = ‖x‖ ‖v‖ cos θ`. Vetores ortogonais têm produto interno zero.

As normas mais utilizadas aqui são:

$$
\|x\|_2=\sqrt{x^Tx},\qquad \|x\|_1=\sum_a|x_a|.
$$

As respectivas distâncias são `‖x−v‖₂` e `‖x−v‖₁`, conhecidas como euclidiana e Manhattan. Uma distância métrica deve ser não negativa, simétrica, anular apenas para pontos iguais e satisfazer a desigualdade triangular.

**A distância euclidiana ao quadrado não é uma métrica.** Em 1D, de 0 a 2 o quadrado vale 4, enquanto os quadrados de 0 a 1 e de 1 a 2 somam 2. A desigualdade triangular falha. Isso não impede seu uso como custo de otimização no K-Means.

### 2.2. Por que a padronização muda o problema

Se cada atributo a é transformado em `(xₐ−médiaₐ)/sₐ`, a distância quadrática entre duas observações passa a ser:

$$
\sum_a\frac{(x_a-v_a)^2}{s_a^2}
=(x-v)^T A(x-v),\qquad A=\operatorname{diag}(s_1^{-2},\ldots,s_d^{-2}).
$$

Portanto, padronizar equivale a mudar os pesos da geometria original. A média subtraída desaparece nas diferenças; são as escalas que alteram essa distância.

A distância de Mahalanobis generaliza a ideia:

$$
d_\Sigma^2(x,v)=(x-v)^T\Sigma^{-1}(x-v),
$$

quando Σ é definida positiva. Ela leva em conta variâncias e correlações. O StandardScaler usa escalas por coluna e não remove correlações. **Padronização não é branqueamento**: branquear busca uma covariância proporcional à identidade, usando também direções conjuntas de variação.

No projeto, o StandardScaler divide pelo desvio-padrão populacional. Valores padronizados representam desvios da média em unidades de desvio-padrão, não centímetros.

### 2.3. Matrizes simétricas e formas quadráticas

Uma matriz simétrica A satisfaz `Aᵀ = A`. Ela é **semidefinida positiva**, ou PSD, quando:

$$
x^TAx\geq0\quad\text{para todo }x.
$$

É definida positiva quando a desigualdade é estrita para todo x não nulo. Covariâncias são PSD; uma covariância singular não tem inversa comum. Matrizes de Gram de kernels válidos também são PSD.

Para uma matriz simétrica:

$$
A=V\Lambda V^T,
$$

com autovetores ortonormais em V e autovalores reais na diagonal de Λ. A matriz é PSD se seus autovalores forem não negativos. Essa decomposição fundamenta a PCA e a Kernel PCA.

### 2.4. Gradiente, Hessiana e estacionariedade

O gradiente reúne derivadas parciais. Aponta a direção de maior crescimento local de uma função diferenciável. Um passo de descida usa:

$$
\theta^{(t+1)}=\theta^{(t)}-\eta_t\nabla f(\theta^{(t)}),\qquad \eta_t>0.
$$

A Hessiana contém segundas derivadas. Se for positiva definida em uma região apropriada, há curvatura de minimização; em um problema estritamente convexo, um ponto estacionário é o único mínimo global.

Derivadas que utilizaremos:

$$
\nabla_v\|x-v\|^2=2(v-x),
\qquad
\nabla_v\sum_i a_i\|x_i-v\|^2=2\sum_i a_i(v-x_i),
$$

para pesos fixos não negativos aᵢ. Se sua soma é positiva, a solução é uma média ponderada.

**Cuidado:** resolver exatamente um bloco de variáveis não torna o problema conjunto convexo. Centros e associações podem formar um problema difícil mesmo quando cada atualização isolada é simples.

### 2.5. Multiplicadores de Lagrange

Para minimizar f(u) sob `g(u)=0`, introduzimos:

$$
\mathcal L(u,\lambda)=f(u)+\lambda g(u).
$$

Buscamos pontos que anulem as derivadas em relação a u e satisfaçam a restrição. A equação da derivada em λ recupera `g(u)=0`.

No FCM, a restrição faz as pertinências de uma observação somarem um. Na PCA, a restrição impede aumentar indefinidamente a variância apenas multiplicando a direção por uma constante: exigimos norma unitária.

Quando também há desigualdades, entram condições de Karush–Kuhn–Tucker. Nas derivações internas do FCM usaremos o caso de distâncias positivas; os casos de fronteira serão tratados à parte.

### 2.6. Otimização alternada e critérios de parada

Uma otimização em blocos alterna, por exemplo:

```text
fixar associações → atualizar centros
fixar centros → atualizar associações
```

Se cada etapa reduz o mesmo objetivo e ele tem limite inferior, a sequência de **valores do objetivo** converge. Isso, sozinho, não garante unicidade, convergência de todos os parâmetros ou ótimo global.

Uma tolerância pode medir variação dos parâmetros, das associações ou do objetivo. O significado depende da implementação. No FCM instalado, o critério usa a norma da diferença entre matrizes de pertinência consecutivas.

### 2.7. Probabilidade condicional e regra de Bayes

Para eventos ou variáveis com probabilidades bem definidas:

$$
P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}.
$$

No GMM, A será “componente j” e B será a observação x. O peso do componente funciona como probabilidade a priori; a densidade gaussiana mede compatibilidade com x; a posterior combina as duas informações.

Uma densidade contínua pode exceder um. A probabilidade de uma região é sua integral; a probabilidade de um ponto isolado em uma distribuição contínua usual é zero. Não confunda densidade com probabilidade de pertencer a um componente.

### 2.8. Logaritmo e estabilidade numérica

Para observações independentes, a verossimilhança é um produto de densidades. Aplicar log transforma o produto em soma e preserva a ordem das soluções por ser uma função estritamente crescente.

Para calcular a soma de exponenciais sem produzir overflow, usa-se:

$$
\log\sum_j e^{a_j}=m+\log\sum_j e^{a_j-m},\qquad m=\max_j a_j.
$$

Essa identidade, chamada log-sum-exp, é importante no cálculo estável de posteriores do GMM e de outras normalizações exponenciais.

### 2.9. Entropia e divergência KL

A entropia de uma distribuição discreta p é:

$$
H(p)=-\sum_jp_j\log p_j.
$$

Adota-se `0 log 0 = 0` por limite. Uma distribuição concentrada tem entropia menor que uma distribuição uniforme no mesmo suporte.

A divergência de Kullback–Leibler é:

$$
KL(p\|q)=\sum_jp_j\log\frac{p_j}{q_j}.
$$

Ela é não negativa para distribuições normalizadas, mas não é simétrica nem é uma distância métrica. Se `pⱼ>0` e `qⱼ=0`, a divergência é infinita.

Um modo de ver sua não negatividade usa `log t ≤ t−1`:

$$
-KL(p\|q)=\sum_jp_j\log(q_j/p_j)
\leq\sum_j(q_j-p_j)=0,
$$

para distribuições positivas; os casos com zeros seguem por extensão apropriada. Essa mesma lógica aparece na interpretação de EM e t-SNE.

### 2.10. Kernels e espaços de características

Um kernel de produto interno permite escrever:

$$
K(x,v)=\langle\phi(x),\phi(v)\rangle_{\mathcal H},
$$

onde φ leva os dados a um espaço de características, possivelmente de dimensão infinita. Trabalhamos com K sem construir explicitamente φ.

Exemplo didático: em 2D, `K(x,v)=(xᵀv)²` corresponde ao mapeamento:

$$
\phi(x_1,x_2)=(x_1^2,\sqrt2x_1x_2,x_2^2).
$$

Expandindo o produto interno desses três termos, obtemos `(x₁v₁+x₂v₂)²`. Uma relação linear nesse espaço contém termos quadráticos no espaço original.

Um kernel PSD produz matrizes de Gram PSD para qualquer conjunto finito de observações. Uma função qualquer de similaridade não possui automaticamente essa propriedade.

O RBF usado no projeto é:

$$
K(x,v)=e^{-\gamma\|x-v\|^2},\qquad\gamma>0.
$$

Como `K(x,x)=1`, os vetores φ(x) têm norma um. Isso explica a expressão `2(1−K)` usada na distância do Kernel FCM.

## 3. K-Means

### 3.1. Variáveis e objetivo

O método escolhe centros `v₁,…,vₖ` e uma associação exclusiva cᵢ por observação:

$$
J(C,V)=\sum_{i=1}^{n}\|x_i-v_{c_i}\|^2.
$$

Alternativamente, com indicadores `rᵢⱼ∈{0,1}` e `Σⱼrᵢⱼ=1`:

$$
J(R,V)=\sum_i\sum_jr_{ij}\|x_i-v_j\|^2.
$$

Esse R binário é apenas notação deste capítulo; não são as responsabilidades suaves do GMM.

### 3.2. Derivando a atribuição ao centro mais próximo

Fixados os centros, cada observação contribui independentemente para J. Escolher o grupo j com menor distância quadrática minimiza sua parcela:

$$
c_i=\operatorname*{argmin}_{j}\|x_i-v_j\|^2.
$$

Escolher pela distância ou por seu quadrado produz o mesmo argmin, porque elevar ao quadrado preserva a ordem dos valores não negativos. O quadrado passa a importar no cálculo do custo e na atualização dos centros.

### 3.3. Derivando a média como atualização

Com um grupo Cⱼ fixo:

$$
J_j(v)=\sum_{i\in C_j}(x_i-v)^T(x_i-v).
$$

Derivando e igualando a zero:

$$
\nabla_vJ_j=-2\sum_{i\in C_j}x_i+2|C_j|v=0
\quad\Rightarrow\quad
v=\frac{1}{|C_j|}\sum_{i\in C_j}x_i.
$$

A Hessiana é `2|Cⱼ| I`, positiva definida se o grupo não estiver vazio. Logo, a média é o mínimo global único desse subproblema.

Uma identidade reforça a interpretação:

$$
\sum_{i\in C_j}\|x_i-v\|^2
=\sum_{i\in C_j}\|x_i-\bar x_j\|^2+|C_j|\|v-\bar x_j\|^2.
$$

O segundo termo é não negativo e zera exatamente na média. Isso prova a atualização sem usar cálculo diferencial.

### 3.4. Algoritmo de Lloyd e convergência

```text
inicializar k centros
repetir:
    associar cada ponto ao centro mais próximo
    recalcular cada centro pela média de seu grupo
até a parada
```

Cada passo ideal não aumenta J. Como `J≥0`, seus valores convergem. Há um conjunto finito de associações exclusivas; com regras consistentes e evitando empates degenerados, o procedimento chega a uma partição estável. Implementações com tolerância podem parar antes dessa estabilização exata e precisam tratar grupos vazios.

O problema conjunto continua não convexo. A inicialização pode levar a diferentes soluções; repetição de sementes explora algumas delas.

### 3.5. Geometria das fronteiras

A fronteira entre centros a e b satisfaz:

$$
\|x-a\|^2=\|x-b\|^2
\quad\Rightarrow\quad
2x^T(b-a)=\|b\|^2-\|a\|^2.
$$

É um hiperplano. As regiões de atribuição são células de Voronoi convexas. Isso ajuda a entender a dificuldade de representar diretamente grupos em anéis ou formas muito não convexas usando um único centro por grupo.

### 3.6. Exemplo didático completo

Dados `1,2,8,9`, k = 2, centros iniciais `1` e `2`:

| Etapa | Grupos | Centros | Objetivo após a etapa |
|---|---|---|---:|
| Primeira atribuição | `{1}` e `{2,8,9}` | 1 e 2 | 85 |
| Atualização | Mesmos grupos | 1 e 19/3 | 86/3 ≈ 28,6667 |
| Nova atribuição | `{1,2}` e `{8,9}` | 1 e 19/3 | 98/9 ≈ 10,8889 |
| Atualização | Mesmos grupos | 1,5 e 8,5 | 1 |

Na última etapa, cada ponto fica a distância 0,5 do próprio centro: quatro quadrados de 0,5 somam 1.

### 3.7. Interpretação e conexão com o projeto

O método prioriza dispersão euclidiana quadrática. Valores extremos podem deslocar a média, e aumentar k nunca piora o **melhor objetivo global possível**. Os valores de execuções locais, porém, podem depender da inicialização.

No projeto: `KMeans(init="random", n_init=1, random_state=seed)`, com dez chamadas externas por k. Seleciona-se a menor inércia por k e, depois, k pela maior silhueta válida. Referência de comportamento da API: [KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).

## 4. Fuzzy C-Means

### 4.1. O que muda em relação à associação exclusiva

Cada observação tem uma linha de pertinências:

$$
u_{ij}\geq0,\qquad\sum_{j=1}^{k}u_{ij}=1.
$$

O objetivo é:

$$
J_m(U,V)=\sum_i\sum_ju_{ij}^m\|x_i-v_j\|^2,\qquad m>1.
$$

O expoente m controla a difusividade. A expressão não é uma log-verossimilhança e não define por si uma distribuição geradora dos dados.

### 4.2. Derivação dos centros

Fixe U. Cada grupo tem o subproblema quadrático:

$$
\frac{\partial J_m}{\partial v_j}=2\sum_i u_{ij}^m(v_j-x_i)=0.
$$

Se `Σᵢuᵢⱼᵐ>0`:

$$
\boxed{v_j=\frac{\sum_i u_{ij}^m x_i}{\sum_i u_{ij}^m}}.
$$

É uma média ponderada: pontos com maior pertinência contribuem mais, e m modifica a intensidade dessa ponderação.

### 4.3. Derivação das pertinências com Lagrange

Fixe os centros e uma observação i. Escreva `aⱼ=‖xᵢ−vⱼ‖²>0`. Precisamos minimizar:

$$
f_i(u)=\sum_j a_j u_j^m,\qquad\sum_ju_j=1.
$$

A Lagrangiana é:

$$
\mathcal L=\sum_j a_j u_j^m+\lambda\left(\sum_ju_j-1\right).
$$

A condição estacionária fornece:

$$
ma_ju_j^{m-1}+\lambda=0
\quad\Rightarrow\quad
u_j=\left(\frac{-\lambda}{m}\right)^{1/(m-1)}a_j^{-1/(m-1)}.
$$

O fator comum é determinado pela soma unitária. Portanto:

$$
\boxed{u_{ij}=\frac{(d_{ij}^2)^{-1/(m-1)}}{\sum_\ell(d_{i\ell}^2)^{-1/(m-1)}}}
=\frac{1}{\sum_\ell(d_{ij}/d_{i\ell})^{2/(m-1)}}.
$$

Para distâncias positivas, a função é estritamente convexa em u para m > 1, garantindo o mínimo único desse bloco. Isso não garante convexidade conjunta em U e V.

### 4.4. Distâncias nulas e limites de m

Se uma distância é zero, a fórmula de potências inversas não pode ser aplicada diretamente. Associar a observação apenas aos centros coincidentes permite custo zero naquele ponto. Se há vários centros coincidentes, qualquer distribuição de pertinência somente entre eles minimiza a parcela; a biblioteca instalada divide igualmente.

Quando `m→1⁺`, as pertinências concentram-se nos centros mais próximos, salvo empates. Para distâncias estritamente positivas, quando `m→∞`, o expoente inverso tende a zero e as pertinências tendem a `1/k`. Os casos com distância zero exigem o tratamento anterior.

### 4.5. Exemplo didático de uma atualização

Uma observação tem distâncias 1 e 2 aos centros; m = 2. Os pesos inversos quadráticos são 1 e 1/4. Normalizando:

$$
u_1=\frac{1}{1+1/4}=0,8,\qquad u_2=0,2.
$$

Sua parcela no objetivo é:

$$
0,8^2\cdot1^2+0,2^2\cdot2^2=0,64+0,16=0,8.
$$

Uma associação exclusiva ao primeiro centro produziria custo 1 nessa expressão. A associação suave pode diminuir o objetivo justamente porque as pertinências aparecem elevadas a m. Isso mostra por que comparar numericamente objetivo FCM e inércia K-Means não cria um ranking de qualidade.

### 4.6. Algoritmo e parada usados

```text
inicializar U com linhas normalizadas
repetir:
    U_anterior ← U
    V ← médias ponderadas por U^m
    U ← pertinências pelas distâncias aos centros
    parar se ||U − U_anterior||_F < tolerância
```

Na biblioteca instalada, a norma matricial chamada sem outra opção corresponde à norma de Frobenius. Com a configuração principal: m = 2, até 300 iterações e tolerância `1e-5`.

A alternância ideal resolve os blocos e não aumenta o objetivo. Centros e pertinências finais podem satisfazer as equações apenas aproximadamente, conforme o critério de parada. Não há garantia de ótimo global.

### 4.7. O que o argmax perde

Para a avaliação crisp:

$$
c_i=\operatorname*{argmax}_j u_{ij}.
$$

Os vetores `(0,99;0,01)` e `(0,51;0,49)` recebem o mesmo rótulo, mas têm graus de ambiguidade diferentes. O projeto preserva U e usa os rótulos exclusivos para silhueta e ARI. Pertinência não é automaticamente posterior probabilística.

## 5. Kernel Fuzzy C-Means

### 5.1. Distância no espaço do kernel

Expanda o quadrado da norma no espaço de características:

$$
\|\phi(x)-\phi(v)\|_{\mathcal H}^2
=K(x,x)+K(v,v)-2K(x,v).
$$

Com RBF:

$$
\delta^2(x,v)=2\left(1-e^{-\gamma\|x-v\|^2}\right).
$$

Ela varia de zero a valores que se aproximam de 2. A distância, com raiz, aproxima-se de `√2`. Ao contrário da distância quadrática euclidiana, o custo de um ponto cada vez mais distante satura.

O objetivo da variante usada é:

$$
J_K(U,V)=2\sum_i\sum_j u_{ij}^m\left(1-e^{-\gamma\|x_i-v_j\|^2}\right).
$$

**Os protótipos vⱼ continuam em ℝᵈ.** Isso restringe seus representantes no espaço de características à forma φ(vⱼ). É diferente de permitir um centro arbitrário em ℋ, que poderia ser uma combinação de todos os φ(xᵢ).

### 5.2. Atualização das pertinências

Com os centros fixos, a derivação do FCM continua válida ao substituir `d²` por `δ²`:

$$
u_{ij}=\frac{(\delta_{ij}^2)^{-1/(m-1)}}{\sum_\ell(\delta_{i\ell}^2)^{-1/(m-1)}}.
$$

Distâncias nulas exigem tratamento especial, como no FCM. Não é necessário calcular o espaço φ para fazer essa atualização.

### 5.3. Derivação da condição dos protótipos

Com U fixo, para um grupo:

$$
J_j(v)=2\sum_i u_{ij}^m(1-K_i(v)),\qquad K_i(v)=e^{-\gamma\|x_i-v\|^2}.
$$

Como:

$$
\nabla_vK_i(v)=-2\gamma K_i(v)(v-x_i),
$$

temos:

$$
\nabla_vJ_j(v)=4\gamma\sum_i u_{ij}^mK_i(v)(v-x_i).
$$

Igualar a zero produz:

$$
v=\frac{\sum_i u_{ij}^mK_i(v)x_i}{\sum_i u_{ij}^mK_i(v)}.
$$

O próprio v aparece nos pesos. Essa é uma **equação implícita de ponto fixo**, e não a média com pesos constantes do FCM.

A biblioteca usa uma atualização iterativa:

$$
v^{(t+1)}=\frac{\sum_i u_{ij}^mK_i(v^{(t)})x_i}{\sum_i u_{ij}^mK_i(v^{(t)})}.
$$

Não confunda derivar uma condição estacionária com provar que uma única atualização encontra o mínimo global do bloco. O objetivo em v não é uma quadrática convexa geral.

### 5.4. O que gamma controla

Para pequenas distâncias, a expansão `e⁻ᵗ≈1−t` dá:

$$
\delta^2(x,v)\approx2\gamma\|x-v\|^2.
$$

Localmente, a geometria é aproximadamente uma versão escalada da euclidiana. Em distâncias grandes, ocorre saturação. Gamma maior faz a transição ocorrer em distâncias menores.

O fator K também reduz a contribuição de pontos distantes na atualização dos protótipos. Entretanto, um ponto distante de **todos** os centros pode ter distâncias de kernel quase iguais e pertinências próximas de uniformes. Portanto, não existe garantia automática de recuperação de clusters ou detecção de anomalias.

### 5.5. Exemplo didático

Com gamma = 0,25:

| Distância euclidiana | Kernel RBF | Distância quadrática induzida |
|---:|---:|---:|
| 0 | 1 | 0 |
| 1 | 0,778801 | 0,442398 |
| 2 | 0,367879 | 1,264241 |
| 4 | 0,018316 | 1,963369 |

Para uma observação às distâncias 1 e 2 dos dois centros, com m = 2, normalizar os inversos das duas distâncias quadráticas induzidas dá pertinências aproximadamente **0,7408 e 0,2592**. Elas diferem dos 0,8 e 0,2 do FCM euclidiano.

### 5.6. Implementação e cuidados numéricos

Na versão instalada, KFCM começa por um ajuste FCM interno com a mesma semente. Depois usa atualizações ponderadas pelo kernel e o critério de mudança de U. Isso é uma inicialização interna, não mais uma das chamadas principais do protocolo.

Para calcular `1−exp(−t)` em t muito pequeno, a biblioteca usa a identidade estável `−expm1(−t)`. Pesos muito pequenos podem sofrer underflow; se o denominador de um centro for zero, a implementação preserva o centro anterior.

Na configuração selecionada, gamma = 0,25 e m = 2. O adaptador usa até 300 iterações e tolerância de `1e-5`. Para cada configuração avaliada, calcula o objetivo `Σ uᵐ δ²` com o expoente m usado no ajuste.

## 6. K-Medoids e PAM

### 6.1. Um problema de seleção discreta

Seja M um subconjunto de k índices das observações. O custo é:

$$
J(M)=\sum_{i=1}^{n}\min_{j\in M}d(x_i,x_j),\qquad |M|=k.
$$

Os representantes precisam pertencer à amostra. Assim, a busca ocorre sobre `C(n,k)` subconjuntos, em vez de sobre todos os vetores possíveis do espaço.

Para grupos fixos, o medoide de um grupo C resolve:

$$
m_C=\operatorname*{argmin}_{x_j\in C}\sum_{x_i\in C}d(x_i,x_j).
$$

Ele não é a mesma coisa que a mediana geométrica, cuja localização pode estar fora da amostra. Em 1D com distância absoluta, uma mediana observada é um medoide; em dimensões maiores, “tomar a mediana de cada coluna” não resolve em geral o problema do medoide.

### 6.2. A troca do PAM

PAM procura melhorias trocando um medoide atual m por um não medoide h. Para cada ponto i, mantenha:

- `d₁(i)`: distância ao medoide mais próximo.
- `d₂(i)`: distância ao segundo medoide mais próximo, quando k ≥ 2.
- `a(i)`: identificador do medoide mais próximo.

Após remover m e inserir h, a nova distância é:

$$
d_{novo}(i)=
\begin{cases}
\min\{d(i,h),d_2(i)\},&a(i)=m,\\
\min\{d(i,h),d_1(i)\},&a(i)\ne m.
\end{cases}
$$

Logo, a variação da troca é:

$$
\Delta(m,h)=\sum_i[d_{novo}(i)-d_1(i)].
$$

Uma troca com Δ negativo reduz o custo. O PAM avalia candidatas e realiza melhorias até seu critério de parada. A manutenção das duas menores distâncias evita recalcular todo o conjunto de comparações para cada contribuição.

### 6.3. Exemplo didático de troca

Dados `0,2,3,10`, distância euclidiana em 1D, medoides iniciais `{0,2}`:

| Ponto | Distância inicial ao representante | Distância após trocar 0 por 10 | Mudança |
|---:|---:|---:|---:|
| 0 | 0 | 2 | +2 |
| 2 | 0 | 0 | 0 |
| 3 | 1 | 1 | 0 |
| 10 | 8 | 0 | −8 |
| **Total** | **9** | **3** | **−6** |

O método aceita uma perda para o ponto 0 porque ela é compensada por uma redução maior no ponto 10.

### 6.4. Inicialização e alcance da solução

O PAM clássico pode usar uma etapa de construção chamada BUILD. O projeto usa a opção **aleatória** da biblioteca; não diga que BUILD foi executado.

Na parada ideal por ausência de melhoria, nenhum movimento de uma troca considerado melhora o conjunto. Isso é um ótimo local em relação àquela vizinhança discreta, não uma enumeração dos `C(n,k)` subconjuntos. Parar pelo limite de iterações é ainda outra condição.

Com k = 1, é viável verificar todas as observações como candidata. O código escolhe o índice de menor soma na matriz de distâncias e encontra o medoide global para esse caso.

### 6.5. O que se ganha e o que custa

A distância sem quadrado dá menor crescimento do custo com afastamento que a perda quadrática. O representante real também pode facilitar a interpretação. Nenhuma dessas propriedades assegura resistência a todos os padrões de contaminação.

No código, usa-se uma matriz densa de distâncias euclidianas `n × n`, `kmedoids.pam`, máximo de 300 iterações para k > 1 e dez sementes externas. Foram conferidos também o contrato e a documentação local da função `pam` instalada.

## 7. Misturas gaussianas e EM

### 7.1. A gaussiana multivariada

Para média μ e covariância definida positiva Σ:

$$
\mathcal N(x\mid\mu,\Sigma)=
\frac{1}{(2\pi)^{d/2}|\Sigma|^{1/2}}
\exp\left[-\frac12(x-\mu)^T\Sigma^{-1}(x-\mu)\right].
$$

O termo quadrático é uma distância de Mahalanobis ao quadrado. O determinante `|Σ|` participa da normalização e reflete o volume de dispersão. Dois componentes não competem apenas pela distância a suas médias: dispersão, orientação e peso também importam.

Com covariância esférica `σ²I`, superfícies de igual densidade são esferas. Com covariância completa, são elipsoides cujos eixos seguem os autovetores de Σ e cujos tamanhos se relacionam às raízes dos autovalores.

### 7.2. Modelo gerador com componente latente

Para gerar uma observação segundo o modelo:

1. Escolher um componente j com probabilidade πⱼ.
2. Gerar x segundo `N(μⱼ,Σⱼ)`.

Se `sᵢⱼ` é um indicador latente binário de qual componente gerou i:

$$
p(x_i,s_{ij}=1\mid\theta)=\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j),
$$

com `πⱼ≥0` e `Σⱼπⱼ=1`. Sem observar o componente, somamos as alternativas:

$$
p(x_i\mid\theta)=\sum_j\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j).
$$

Não existe uma espécie supervisionada escondida na notação: os componentes são variáveis do modelo, e sua correspondência às espécies é avaliada depois.

### 7.3. Verossimilhança observada e completa

Assumindo independência entre observações, a log-verossimilhança observada é:

$$
\ell(\theta)=\sum_i\log\sum_j\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j).
$$

A soma dentro do log acopla os componentes. Se soubéssemos os indicadores, a expressão seria mais simples:

$$
\ell_c(\theta)=\sum_i\sum_js_{ij}
\left[\log\pi_j+\log\mathcal N(x_i\mid\mu_j,\Sigma_j)\right].
$$

EM explora essa forma completa sem precisar observar os indicadores.

### 7.4. Por que o passo E usa a posterior

Introduza distribuições auxiliares `qᵢⱼ`, com soma um em cada linha. Por concavidade do log:

$$
\log\sum_j\pi_j\mathcal N_{ij}
=\log\sum_jq_{ij}\frac{\pi_j\mathcal N_{ij}}{q_{ij}}
\geq\sum_jq_{ij}\log\frac{\pi_j\mathcal N_{ij}}{q_{ij}}.
$$

Somando sobre i, obtemos um limite inferior:

$$
\mathcal F(q,\theta)=\sum_{ij}q_{ij}
[\log\pi_j+\log\mathcal N_{ij}-\log q_{ij}].
$$

Mais precisamente:

$$
\ell(\theta)=\mathcal F(q,\theta)
+\sum_i KL\left(q_i\|p(s_i\mid x_i,\theta)\right).
$$

O limite coincide com a log-verossimilhança quando q é a posterior atual. Portanto, o passo E escolhe:

$$
\boxed{r_{ij}=\frac{\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j)}{\sum_\ell\pi_\ell\mathcal N(x_i\mid\mu_\ell,\Sigma_\ell)}}.
$$

Essas responsabilidades são probabilidades condicionais sob o modelo, não pertinências definidas pelo objetivo FCM.

### 7.5. Derivando o passo M

Com R fixo, o termo de entropia das responsabilidades não depende dos parâmetros. Maximizamos:

$$
Q(\theta)=\sum_{ij}r_{ij}[\log\pi_j+\log\mathcal N(x_i\mid\mu_j,\Sigma_j)].
$$

Defina o tamanho efetivo `Nⱼ=Σᵢrᵢⱼ`. Ele pode ser não inteiro.

Para os pesos, usamos a restrição de soma um. Derivar `ΣⱼNⱼlogπⱼ + λ(Σⱼπⱼ−1)` produz `Nⱼ/πⱼ+λ=0`; normalizando:

$$
\boxed{\pi_j=N_j/n}.
$$

Para as médias, a parte relevante é uma soma ponderada de distâncias de Mahalanobis. Sua derivada fornece:

$$
\Sigma_j^{-1}\sum_ir_{ij}(x_i-\mu_j)=0
\quad\Rightarrow\quad
\boxed{\mu_j=\frac{\sum_ir_{ij}x_i}{N_j}}.
$$

Para a covariância, com a média atualizada, defina:

$$
A_j=\sum_ir_{ij}(x_i-\mu_j)(x_i-\mu_j)^T.
$$

A parcela de Q é `−(Nⱼ/2)log|Σⱼ| − (1/2)tr(Σⱼ⁻¹Aⱼ)`. Usando a matriz de precisão `Λⱼ=Σⱼ⁻¹`, sua derivada em Λ é `(Nⱼ/2)Λⱼ⁻¹ − Aⱼ/2`. Igualar a zero dá:

$$
\boxed{\Sigma_j=A_j/N_j}.
$$

Essas são as atualizações não regularizadas. A implementação do projeto adiciona `1e-6` à diagonal das covariâncias para estabilizar o ajuste.

### 7.6. Por que EM melhora a verossimilhança na formulação ideal

No passo E, o limite inferior toca o valor atual de ℓ. No passo M, maximizar Q aumenta ou mantém esse limite. Como ℓ está acima do limite, a nova log-verossimilhança não diminui na atualização ideal.

Essa propriedade não prova ótimo global. Também é preciso distinguir o modelo matemático sem regularização, a regularização diagonal usada, precisão finita, tolerâncias e limites de execução. Não afirme que a implementação numérica herda todas as garantias de uma derivação ideal sem condições.

### 7.7. Exemplo didático de posterior

Duas gaussianas 1D têm médias 0 e 3, variâncias 1 e pesos iguais. Para x = 0, a razão da densidade do segundo componente pela do primeiro é `exp(−9/2)`. Assim:

$$
r_1=\frac{1}{1+e^{-4,5}}\approx0,989013,
\qquad r_2\approx0,010987.
$$

Em x = 1,5, a simetria faz as duas responsabilidades valerem 0,5. Se os pesos ou variâncias fossem diferentes, o ponto de posterior igual poderia mudar.

### 7.8. Exemplo didático de uma etapa M

Para x = `(0,1,4)` e responsabilidades dadas por:

$$
R=\begin{bmatrix}0,9&0,1\\0,8&0,2\\0,1&0,9\end{bmatrix},
$$

obtemos `N₁=1,8`, `N₂=1,2`, pesos `0,6` e `0,4`, médias `2/3` e `19/6`. As variâncias não regularizadas são `8/9 ≈ 0,888889` e `77/36 ≈ 2,138889`.

As responsabilidades desta etapa são didáticas e não precisam ser as posteriores de um ajuste anterior específico. O exemplo isola como a atualização usa seus pesos.

### 7.9. Relação com K-Means e singularidades

Com pesos iguais e covariância esférica comum `σ²I`:

$$
r_{ij}\propto\exp\left[-\frac{\|x_i-\mu_j\|^2}{2\sigma^2}\right].
$$

Quando `σ²→0`, as responsabilidades concentram-se na média mais próxima, salvo empates. Essa relação explica uma conexão com K-Means. Ela não torna o GMM full do projeto equivalente ao K-Means.

Uma mistura gaussiana sem restrições pode aumentar a verossimilhança sem limite fazendo um componente colapsar sobre uma observação com variância tendendo a zero. A regularização combate a degeneração numérica, mas não transforma o problema em convexo.

Com d = 4, cada componente full tem quatro médias e dez entradas livres de covariância simétrica. Somando k−1 pesos livres, há `15k−1` parâmetros: 29 para k = 2 e 44 para k = 3. Essa é uma contagem formal do modelo, não um critério de seleção já aplicado. BIC poderia penalizar complexidade em outro protocolo; aqui k foi escolhido pela silhueta.

### 7.10. Configuração efetiva

No projeto: `GaussianMixture`, covariância full, inicialização `random_from_data`, `n_init=1`, tolerância `1e-5`, regularização `1e-6` e dez sementes externas. O objetivo salvo é `modelo.score(X) × n`, a log-verossimilhança total. Para obter a partição crisp, aplica-se argmax à posterior.

Documentação de referência para o modelo e as opções de covariância: [misturas gaussianas do scikit-learn](https://scikit-learn.org/stable/modules/mixture.html). A derivação acima explicita os subproblemas algébricos das atualizações.

## 8. UPGMA

### 8.1. Uma regra aglomerativa, sem função global comum aos anteriores

UPGMA constrói uma árvore por escolhas locais de fusão. Não é uma otimização alternada de centros e não possui, no projeto, uma função objetivo global salva para selecionar reinicializações.

Para conjuntos de observações A e B:

$$
D(A,B)=\frac{1}{|A||B|}\sum_{x\in A}\sum_{v\in B}d(x,v).
$$

A cada rodada, une os dois grupos com menor D. No projeto, d é Manhattan.

### 8.2. Derivação da atualização por tamanhos

Após unir A e B, as comparações com C se decompõem em dois conjuntos de pares:

$$
\begin{aligned}
D(A\cup B,C)
&=\frac{\sum_{x\in A,v\in C}d(x,v)+\sum_{x\in B,v\in C}d(x,v)}{(|A|+|B|)|C|}\\
&=\frac{|A|D(A,C)+|B|D(B,C)}{|A|+|B|}.
\end{aligned}
$$

A atualização pondera os subgrupos por suas quantidades de observações para dar peso igual a cada ponto original. O “unweighted” do nome não significa ignorar seus tamanhos nessa equação.

Na regra WPGMA, a atualização seria `[D(A,C)+D(B,C)]/2`, mesmo com tamanhos distintos. As duas coincidem apenas em casos específicos.

### 8.3. Exemplo didático da diferença para WPGMA

Considere A = `{0,2}`, B = `{10}` e C = `{20}`, em 1D. Temos `D(A,C)=19` e `D(B,C)=10`.

UPGMA calcula `(2×19+1×10)/3 = 16`. Isso coincide com a média das três distâncias `20,18,10`. A média simples entre os dois subgrupos daria 14,5 e seria outra regra.

### 8.4. Exemplo didático da árvore

Com `1,2,8,9`, as uniões naturais são `{1,2}` e `{8,9}`, ambas à altura 1. A união final ocorre à altura:

$$
\frac{|1-8|+|1-9|+|2-8|+|2-9|}{4}=7.
$$

Uma matriz de ligações possível, com índices originais de 0 a 3, é:

```text
[0, 1, 1, 2]  # cria o grupo 4
[2, 3, 1, 2]  # cria o grupo 5
[4, 5, 7, 4]  # cria o grupo 6
```

Cada linha informa os dois grupos unidos, a altura e o total de folhas do novo grupo. Empates podem mudar a ordem de fusões equivalentes.

### 8.5. O que significa cortar a árvore

Uma árvore com n folhas tem n−1 fusões. Para manter k grupos, é possível parar após n−k fusões. Cortes por quantidade de grupos e por altura estão relacionados; empates nas alturas podem exigir uma convenção específica.

O `cut_tree` do projeto extrai quantidades de grupos da matriz armazenada. Não reconstrói a hierarquia para cada k.

As alturas representam a dissimilaridade da fusão. A ordem horizontal das folhas é uma escolha de desenho e não mede distância. A árvore é uma representação hierárquica produzida pela regra; ela não é automaticamente uma árvore filogenética verdadeira ou uma estimativa de probabilidades de parentesco.

### 8.6. Implementação

Usa-se `pdist(X, metric="cityblock")`, `linkage(..., method="average")` e cinco cortes da mesma árvore. Para 150 observações, o vetor condensado contém 11.175 distâncias e a matriz de ligações tem 149 linhas.

A [documentação do SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html) define a regra average/UPGMA e o contrato dessa matriz. As equações de atualização foram desenvolvidas acima a partir da média entre pares.

## 9. DBSCAN

### 9.1. Vizinhança e núcleo

Para raio ε, defina:

$$
N_\varepsilon(x)=\{v\in X:d(x,v)\leq\varepsilon\}.
$$

Um ponto é central, ou **core**, se `|Nε(x)| ≥ min_samples`. Na implementação usada, o próprio ponto participa da contagem.

Uma observação **de borda** não é core, mas está ao alcance direto de um core. **Ruído** é o que não é incorporado a nenhum agrupamento sob a configuração adotada.

### 9.2. Alcançabilidade direta, por cadeia e conexão

Um ponto b é diretamente alcançável por densidade a partir de a quando b pertence a `Nε(a)` e a é core. A relação pode ser assimétrica: b pode ser de borda e não servir como origem de expansão.

b é alcançável a partir de a se existe uma cadeia de passos diretos. Pontos intermediários que prolongam a cadeia precisam ser core.

Dois pontos são conectados por densidade quando existe algum ponto a partir do qual ambos são alcançáveis. Essa formulação permite reunir núcleos conectados e suas bordas.

### 9.3. Interpretação por componentes de um grafo

Construa um grafo apenas com pontos core; ligue dois núcleos se sua distância for no máximo ε. As componentes conexas desse grafo formam o esqueleto dos clusters.

Em seguida, anexe pontos de borda vizinhos aos núcleos. Se um ponto de borda encosta em componentes distintas sem ser core, sua atribuição pode depender da ordem de expansão. Ele não deve unir automaticamente os dois grupos: uma borda não propaga a conexão como um núcleo.

Essa leitura explica como o DBSCAN pode seguir formas não convexas. O agrupamento é definido por cadeias locais, não por proximidade a um único centro.

### 9.4. Exemplo didático

Pontos 1D: `0; 0,1; 0,2; 1; 1,1; 1,2; 3`. Use eps = 0,15 e min_samples = 3.

- O ponto 0,1 tem os vizinhos `{0;0,1;0,2}` e é core.
- Os pontos 0 e 0,2 têm apenas dois pontos em suas vizinhanças, mas são bordas do core 0,1.
- Analogamente, 1,1 é core, com bordas 1 e 1,2.
- O ponto 3 fica como ruído.

O resultado tem dois grupos e um ruído. O método não recebeu esse número de grupos como entrada.

### 9.5. Parâmetros, escalas e limitações

Aumentar ε só adiciona relações de vizinhança e pode criar núcleos ou unir componentes. O número de clusters, porém, não precisa variar de forma monotônica: novos núcleos podem formar grupos antes inexistentes e, depois, grupos podem se fundir.

Aumentar min_samples torna mais exigente a condição de núcleo. Uma única escala de densidade pode fragmentar um grupo esparso ou juntar grupos densos, dependendo da configuração. Em alta dimensão, a noção de vizinhança também pode se tornar menos discriminativa.

Não há um objetivo de centroides sendo minimizado, e o ruído não é uma classe biológica adicional. `−1` é uma convenção para observações não agrupadas.

### 9.6. Configuração no projeto

A busca selecionou eps = 0,6943 e min_samples = 3 com distância euclidiana nos dados padronizados. A configuração produziu dois grupos e classificou seis pontos como ruído. A silhueta e o ARI foram calculados nos 144 pontos atribuídos a grupos.

As definições de parâmetros e a inclusão do próprio ponto são documentadas na [API DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html). A derivação por componentes do grafo descreve a estrutura da regra de conectividade.

## 10. PCA

### 10.1. Centralização, covariância e direção de projeção

Considere X centralizada, isto é, cada coluna tem média zero. A covariância amostral é:

$$
S=\frac{X^TX}{n-1}.
$$

Escolher uma direção unitária w produz a coordenada escalar `zᵢ=xᵢᵀw`. Como a média dessas coordenadas é zero:

$$
\operatorname{Var}(Xw)=\frac{\|Xw\|^2}{n-1}=w^TSw.
$$

A primeira componente resolve `max wᵀSw` sob `wᵀw=1`.

### 10.2. Derivação pelo quociente de Rayleigh

Use a Lagrangiana:

$$
\mathcal L(w,\lambda)=w^TSw-\lambda(w^Tw-1).
$$

Como S é simétrica:

$$
2Sw-2\lambda w=0\quad\Rightarrow\quad Sw=\lambda w.
$$

Ou seja, uma direção candidata é um autovetor. Escreva qualquer direção unitária na base ortonormal de autovetores: `w=Σₐcₐvₐ`, com `Σₐcₐ²=1`. Então:

$$
w^TSw=\sum_a\lambda_a c_a^2\leq\lambda_1\sum_ac_a^2=\lambda_1.
$$

O maior valor é alcançado pelo autovetor associado ao maior autovalor. Não basta apenas dizer que a derivada produziu autovetores: esta desigualdade identifica qual deles maximiza a variância.

### 10.3. Componentes seguintes

A segunda direção deve ter norma um e ser ortogonal à primeira. Isso elimina o coeficiente da primeira direção na expansão anterior; o maior valor restante é λ₂. Repetindo, obtemos autovetores ordenados por autovalor.

Com q direções reunidas em W:

$$
W^TW=I_q,\qquad Z=XW,\qquad\operatorname{Cov}(Z)=W^TSW.
$$

Se W contém autovetores, essa covariância é diagonal. As componentes são não correlacionadas na amostra; isso não prova independência probabilística, exceto sob hipóteses adicionais, como normalidade conjunta.

### 10.4. Equivalência com reconstrução de menor erro

A reconstrução ortogonal usando q componentes é:

$$
\widehat X=ZW^T=XWW^T.
$$

Como WWᵀ é um projetor ortogonal:

$$
\|X-XWW^T\|_F^2
=\|X\|_F^2-\|XW\|_F^2.
$$

Minimizar o erro quadrático de reconstrução equivale a maximizar a variância total projetada, `tr(WᵀSW)`. A solução retém as q maiores direções, e o erro ótimo é:

$$
\boxed{\|X-\widehat X\|_F^2=(n-1)\sum_{a=q+1}^{d}\lambda_a}.
$$

Essa propriedade se refere a projeções lineares ortogonais e perda quadrática. Ela não garante melhor preservação de classes ou de todas as vizinhanças.

### 10.5. Como a SVD implementa a solução

Se:

$$
X=U\operatorname{diag}(s_1,\ldots,s_r)V^T,
$$

então:

$$
X^TX=V\operatorname{diag}(s_1^2,\ldots,s_r^2)V^T,
\qquad \lambda_a=s_a^2/(n-1).
$$

As colunas de V são as direções principais; os scores são `XVq=Uq diag(s₁,…,s_q)`. A implementação usa SVD e pode armazenar as direções transpostas, como linhas em `components_`.

Formar XᵀX explicitamente pode piorar o condicionamento: sua razão entre maior e menor autovalor positivo é o quadrado da razão entre os valores singulares correspondentes de X. A SVD evita precisar dessa formação para obter as direções.

### 10.6. Exemplo didático com uma covariância conhecida

Considere:

$$
S=\begin{bmatrix}2&1\\1&2\end{bmatrix}.
$$

O polinômio característico é `(2−λ)²−1`, cujas raízes são 3 e 1. Autovetores normalizados:

$$
v_1=\frac{1}{\sqrt2}\begin{bmatrix}1\\1\end{bmatrix},
\qquad v_2=\frac{1}{\sqrt2}\begin{bmatrix}1\\-1\end{bmatrix}.
$$

A primeira direção acompanha o crescimento conjunto dos atributos; a segunda mede seu contraste. PC1 explica `3/(3+1)=75%` da variância. A projeção de uma observação centralizada `(1,0)` é `1/√2` em PC1. Sua reconstrução com apenas essa direção é `(0,5;0,5)`.

### 10.7. Proporção de variância e loadings

A proporção explicada é:

$$
\operatorname{VE}_a=\lambda_a/\sum_b\lambda_b.
$$

No projeto, os loadings são `Lⱼₐ=Vⱼₐ sqrt(λₐ)`. Já os coeficientes Vⱼₐ definem a combinação linear. São objetos diferentes.

A correlação amostral entre o atributo j e o score a é:

$$
\operatorname{Corr}(X_j,Z_a)
=\frac{\lambda_aV_{ja}}{\sqrt{S_{jj}\lambda_a}}
=\frac{V_{ja}\sqrt{\lambda_a}}{\sqrt{S_{jj}}}.
$$

Se o escalonamento deu variância populacional um, a variância amostral da coluna é `n/(n−1)`. Logo, nesse caso:

$$
\operatorname{Corr}(X_j,Z_a)=L_{ja}\sqrt{(n-1)/n}.
$$

Isso explica por que os loadings usados são próximos de correlações, mas não exatamente iguais sob a combinação de convenções adotada.

### 10.8. Unicidade e limitações

O sinal de um autovetor é arbitrário: v e −v produzem eixos espelhados equivalentes. Se dois autovalores são iguais, qualquer base ortonormal de seu subespaço é válida; comparar coeficientes eixo a eixo pode ser enganoso.

PCA é sensível à escala e a valores extremos. Uma direção de pequena variância ainda pode ser relevante para outra tarefa. A garantia de reconstrução quadrática não é uma garantia de discriminação botânica.

### 10.9. Projeto

Foram ajustadas quatro componentes com SVD completa e exibidas as duas primeiras. Elas retiveram 72,7705% e 23,0305%, totalizando 95,8010%. A variância total da matriz padronizada, na convenção amostral, é `4×150/149`, consistente com os autovalores registrados.

A [API PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html) documenta atributos como `components_`, variância explicada e valores singulares. As identidades acima derivam a relação entre eles.

## 11. Kernel PCA

### 11.1. PCA no espaço de características

Considere os vetores φ(xᵢ) em ℋ e sua média `φ̄`. Os vetores centralizados são `φ̃ᵢ=φ(xᵢ)−φ̄`. A covariância nesse espaço pode ser escrita como operador:

$$
C=\frac{1}{n-1}\sum_i\widetilde\phi_i\widetilde\phi_i^T.
$$

Essa expressão é conceitual: em um espaço de dimensão infinita não queremos construir a matriz completa. Usaremos somente produtos internos.

### 11.2. Por que basta a matriz de Gram

Uma direção com autovalor não nulo pertence ao espaço gerado pelas observações centralizadas. Escreva:

$$
w=\sum_i\alpha_i\widetilde\phi_i.
$$

O produto interno entre observações é `Kcᵢⱼ=⟨φ̃ᵢ,φ̃ⱼ⟩`. Se `Kc a=κa`, com `aᵀa=1` e κ > 0, uma direção normalizada em ℋ é:

$$
\boxed{w=\frac{1}{\sqrt\kappa}\sum_i a_i\widetilde\phi_i}.
$$

De fato, `‖w‖²=(aᵀKc a)/κ=1`. O autovalor do operador de covariância C correspondente é `κ/(n−1)`. **κ da matriz de Gram não é numericamente o mesmo autovalor da covariância normalizada.**

### 11.3. Centralização do kernel

Defina:

$$
H=I_n-\frac1n\mathbf1\mathbf1^T.
$$

H é simétrica, satisfaz `H²=H` e remove a média. A matriz centralizada é:

$$
\boxed{K_c=HKH}.
$$

Elemento a elemento:

$$
(K_c)_{ij}=K_{ij}-\frac1n\sum_\ell K_{i\ell}
-\frac1n\sum_\ell K_{\ell j}
+\frac1{n^2}\sum_{\ell,m}K_{\ell m}.
$$

Centralizar as entradas originais X não substitui essa centralização em ℋ. Uma transformação não linear de dados centralizados pode ter média não nula no espaço de características.

### 11.4. Coordenadas de treinamento e de uma nova observação

Para uma observação de treinamento t:

$$
z_t=\langle\widetilde\phi_t,w\rangle
=\frac{(K_c a)_t}{\sqrt\kappa}
=\sqrt\kappa\,a_t.
$$

Para uma observação nova x, não se recalcula a média incluindo x. Centraliza-se em relação ao treinamento:

$$
\widetilde k_i(x)=K(x,x_i)-\frac1n\sum_\ell K(x,x_\ell)
-\frac1n\sum_\ell K(x_\ell,x_i)
+\frac1{n^2}\sum_{\ell,m}K(x_\ell,x_m).
$$

Então:

$$
z(x)=\frac{a^T\widetilde k(x)}{\sqrt\kappa}.
$$

Isso permite uma transformação de novos dados baseada no ajuste. Encontrar uma pré-imagem nos atributos originais a partir de coordenadas reduzidas é outro problema, geralmente não trivial.

### 11.5. Exemplo didático de duas observações

Considere x₁ = 0 e x₂ = 1, com gamma = ln 2. Esse gamma é didático, não o do projeto. Como o RBF fora da diagonal vale 1/2:

$$
K=\begin{bmatrix}1&1/2\\1/2&1\end{bmatrix},
\qquad
K_c=\frac14\begin{bmatrix}1&-1\\-1&1\end{bmatrix}.
$$

O autovalor positivo é κ = 1/2, com `a=(1,−1)/√2`. As coordenadas da única componente não nula são `(1/2,−1/2)`. Sua distância quadrática é 1, exatamente a distância de kernel `2(1−1/2)` nesse exemplo de posto um.

### 11.6. O que se pode dizer de variância

Se fossem conhecidos todos os autovalores positivos da Gram centralizada, a razão `κₐ/Σκ` descreveria a proporção de variância **no espaço de características** sob essa convenção. Isso continua não sendo a variância original dos quatro atributos.

No projeto foram retidos dois autovalores. Normalizar apenas esses dois faz suas proporções somarem um por construção, mesmo quando existe espectro omitido. Portanto, não se pode usar essa normalização para anunciar variância total original explicada.

### 11.7. Configuração e leitura

RBF, gamma = 0,25, duas componentes, decomposição densa; κ registrados aproximadamente 39,1321 e 17,7924. O método pode alterar a geometria de forma não linear, mas seus eixos dependem do kernel e não têm a interpretação linear direta da PCA.

Contrato da implementação: [KernelPCA no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html). O projeto não ativou a estimação de transformação inversa.

## 12. t-SNE

### 12.1. Converter distância em distribuição local

Para i fixo, são atribuídas probabilidades condicionais aos demais pontos:

$$
p_{j\mid i}=\frac{\exp[-\|x_i-x_j\|^2/(2\sigma_i^2)]}
{\sum_{\ell\ne i}\exp[-\|x_i-x_\ell\|^2/(2\sigma_i^2)]},\quad j\ne i.
$$

O próprio ponto é excluído, com `pᵢ|ᵢ=0`. Cada σᵢ é adaptado à região: o mesmo raio global poderia dar uma distribuição muito concentrada em regiões esparsas e muito difusa nas densas.

### 12.2. Perplexidade e busca da escala

Com entropia em bits:

$$
H_2(P_i)=-\sum_jp_{j\mid i}\log_2p_{j\mid i},
\qquad\operatorname{Perp}(P_i)=2^{H_2(P_i)}.
$$

Se a probabilidade se distribui igualmente entre m vizinhos, a perplexidade vale m. Por exemplo, `(0,5;0,5)` tem entropia 1 bit e perplexidade 2; uma distribuição concentrada em um ponto tem perplexidade 1.

Aumentar σᵢ suaviza a distribuição e aumenta sua perplexidade, em geral permitindo uma busca binária pela escala desejada. Empates e distâncias degeneradas limitam quais valores são efetivamente atingíveis. Perplexidade não impõe exatamente m arestas nem m clusters.

### 12.3. Simetrização

Definimos:

$$
p_{ij}=\frac{p_{j\mid i}+p_{i\mid j}}{2n},\qquad p_{ii}=0.
$$

Assim P é simétrica e `Σᵢ≠ⱼpᵢⱼ=1`, usando pares ordenados. O denominador 2n vem das duas somas de condicionais, cada uma totalizando n.

### 12.4. Similaridade no mapa e o problema de aglomeração

Um espaço de baixa dimensão oferece menos volume para acomodar vizinhanças intermediárias. Essa diferença contribui para o problema de aglomeração, ou **crowding**: não é possível preservar indiscriminadamente todas as relações de um espaço mais complexo em um plano.

No mapa, usa-se:

$$
w_{ij}=(1+\|z_i-z_j\|^2)^{-1},\qquad
Q_{ij}=\frac{w_{ij}}{\mathcal Z},\qquad
\mathcal Z=\sum_{a\ne b}w_{ab}.
$$

O fator corresponde à cauda de uma distribuição t com um grau de liberdade. A cauda mais pesada permite manter afinidades em separações maiores no mapa que uma gaussiana equivalente. Ela reduz dificuldades de acomodação, sem tornar possível preservar toda a geometria.

### 12.5. Objetivo e sua assimetria

$$
C(Z)=KL(P\|Q)=\sum_{i\ne j}p_{ij}\log\frac{p_{ij}}{q_{ij}}.
$$

P é fixada pelos dados e pela perplexidade; Z modifica Q. Um par com p grande e q muito pequeno recebe penalidade importante. Por isso perder uma relação forte de vizinhança pode pesar muito. A normalização global de Q faz todos os pares interagirem indiretamente.

Não é o mesmo problema que minimizar diferenças de distâncias originais e projetadas. O valor KL depende das afinidades e do próprio ajuste, não de rótulos botânicos.

### 12.6. Derivando o gradiente

Escreva `sᵢⱼ=‖zᵢ−zⱼ‖²`. Como P soma um:

$$
C=\text{constante}+\sum_{i\ne j}p_{ij}\log(1+s_{ij})+\log\mathcal Z.
$$

Na derivada em zᵢ, os pares `(i,j)` e `(j,i)` contribuem. A derivada do primeiro termo variável é:

$$
4\sum_{j\ne i}p_{ij}w_{ij}(z_i-z_j).
$$

Como `∇zᵢ wᵢⱼ = −2wᵢⱼ²(zᵢ−zⱼ)`, a derivada de `log ℨ` é:

$$
-\frac4{\mathcal Z}\sum_{j\ne i}w_{ij}^2(z_i-z_j)
=-4\sum_{j\ne i}q_{ij}w_{ij}(z_i-z_j).
$$

Somando:

$$
\boxed{\nabla_{z_i}C=4\sum_{j\ne i}(p_{ij}-q_{ij})
\frac{z_i-z_j}{1+\|z_i-z_j\|^2}}.
$$

Se p > q, a contribuição do gradiente aponta para longe de j; o **passo de descida**, com sinal negativo, aproxima os pontos. Se q > p, a descida tende a afastá-los. É importante distinguir o sinal do gradiente do sentido do movimento.

O objetivo, a distribuição t e a expressão do gradiente são apresentados no [artigo original de t-SNE, seção 3 e apêndice A](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf). A sequência algébrica acima explicita a normalização e a contagem de pares.

### 12.7. Uma contribuição numérica didática

Considere um par com `p=0,1`, `q=0,02` e deslocamento `zᵢ−zⱼ=(1,0)`. A contribuição desse par ao gradiente é:

$$
4(0,1-0,02)\frac{(1,0)}{2}=(0,16;0).
$$

Com taxa η = 0,5, essa contribuição isolada deslocaria i em `(−0,08;0)`, aproximando-o de j. O gradiente total inclui todos os pares; o exemplo não especifica um mapa global completo.

### 12.8. Otimização real

A implementação usa inicialização, descida com mecanismos como momentum e adaptação dos passos, além de uma fase de exagero inicial das afinidades atrativas. Durante essa fase, não se deve interpretar o fator de exagero como uma distribuição P normalizada inalterada.

O modo Barnes-Hut aproxima contribuições repulsivas de grupos de pontos distantes. A expressão anterior descreve o gradiente exato do objetivo; o código com aproximação não avalia exatamente todos os seus termos em cada passo. O custo por passo pode se aproximar de `O(n log n)` em condições favoráveis, enquanto o cálculo exato denso envolve `O(n²)` pares. A construção das afinidades tem seus próprios custos.

Não há garantia de ótimo global. A aparência também depende de inicialização, perplexidade, taxa, exagero e orçamento de otimização.

### 12.9. Invariâncias e novos pontos

Transladar, girar ou refletir todo o mapa preserva as distâncias e o objetivo. A escala, em geral, não é uma invariância, porque altera os fatores `1/(1+s)`.

A versão comum de t-SNE ajusta as posições das observações fornecidas, sem aprender uma única matriz de projeção como na PCA. A API utilizada não oferece uma transformação direta `transform` para inserir flores novas no mesmo mapa. Extensões paramétricas existem, mas não foram utilizadas.

### 12.10. Projeto

Duas dimensões, perplexidade 30, inicialização PCA, seed 42, máximo de 1.000 iterações, exagero inicial 12, Barnes-Hut, ângulo 0,5 e taxa automática efetiva 50. A execução registrou KL = 0,164197 e `n_iter_ = 999`.

O [contrato da API TSNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html) orienta a interpretação dos parâmetros e atributos. A interpretação do resultado deve se concentrar em relações locais, com cuidado para áreas, densidades e distâncias entre ilhas.

## 13. UMAP

### 13.1. Variedade, dimensão intrínseca e aproximação local

Uma variedade de dimensão r é um espaço que, em pequenas regiões, pode ser descrito por coordenadas em ℝʳ. Ela pode estar imersa em um espaço de dimensão d maior. Um círculo no plano tem dimensão intrínseca um, embora precise de duas coordenadas no desenho usual.

A motivação do UMAP combina aproximações locais de geometria e conexões entre vizinhanças. Isso não significa que o algoritmo prove que a Iris está exatamente em uma variedade ou recupere sua topologia sem erro.

Na implementação prática, a informação essencial da primeira etapa é um **grafo ponderado esparso de vizinhanças**. Não precisamos construir todos os objetos abstratos da teoria topológica para executar o algoritmo.

### 13.2. Grafo local e escalas adaptativas

Para cada observação i, obtenha seus vizinhos mais próximos. A intensidade dirigida de uma ligação é:

$$
p_{i\to j}=\exp\left[-\frac{\max(0,d(x_i,x_j)-\rho_i)}{\sigma_i}\right],
$$

para vizinhos considerados. Fora dessa vizinhança, a aresta local não é adicionada. A diagonal é zerada.

Com conectividade local igual a um, ρᵢ é ligado à distância ao vizinho distinto mais próximo; duplicatas e escassez de distâncias não nulas exigem os tratamentos da implementação. A escala σᵢ é ajustada para controlar a soma das intensidades locais.

No código instalado, `smooth_knn_dist` busca uma soma próxima de `log₂(M)` quando `bandwidth=1`. A busca normalmente recebe uma lista de M distâncias que inclui o próprio ponto na posição inicial, e a soma da busca pula essa posição. Portanto, o número de arestas efetivas e o parâmetro M não devem ser tratados como sinônimos exatos em toda situação.

### 13.3. Exemplo didático da escala local

Considere a lista de distâncias `(0,1,2,3)`, com M = 4, ρ = 1 e o próprio ponto na primeira posição. A soma procurada é `log₂4 = 2`:

$$
1+e^{-1/\sigma}+e^{-2/\sigma}=2.
$$

Defina `t=e⁻¹/σ`. Temos `t+t²=1`; a raiz positiva é `(√5−1)/2 ≈ 0,618034`. Logo:

$$
\sigma=-1/\log t\approx2,078087.
$$

Os três pesos são aproximadamente `1;0,618034;0,381966`, somando 2. É um exemplo de cardinalidade suave, não uma probabilidade de classe.

### 13.4. Por que a relação dirigida precisa ser combinada

Ser vizinho de i não implica que i esteja na lista de vizinhos de j; as escalas locais também diferem. Para obter a união fuzzy simétrica:

$$
\boxed{w_{ij}=p_{i\to j}+p_{j\to i}-p_{i\to j}p_{j\to i}}.
$$

A expressão corresponde à soma probabilística de duas intensidades: `1−(1−p)(1−q)`. Ela não pressupõe que essas intensidades sejam probabilidades de espécies.

Se as intensidades dirigidas são 0,8 e 0,5, a união dá 0,9. A interseção por produto daria 0,4. O projeto usa a união da configuração padrão `set_op_mix_ratio=1`.

### 13.5. Inicialização espectral

Se A é a matriz simétrica de pesos e D contém os graus, uma forma normalizada do Laplaciano do grafo é:

$$
L_{sym}=I-D^{-1/2}AD^{-1/2}.
$$

Autovetores associados a autovalores pequenos descrevem variações suaves sobre o grafo e podem fornecer coordenadas iniciais. A direção trivial constante ou relacionada aos graus é descartada conforme o problema.

Grafos desconectados exigem tratamento de múltiplas componentes; suas posições relativas no mapa não devem ser interpretadas como distância física inferida com precisão. A inicialização é uma etapa, depois modificada pela otimização não linear.

### 13.6. Similaridades no mapa

No espaço reduzido, defina `sᵢⱼ=‖zᵢ−zⱼ‖²` e:

$$
q_{ij}=\frac{1}{1+a s_{ij}^{b}},\qquad a,b>0.
$$

Ao contrário de Q no t-SNE, os q do UMAP não são normalizados globalmente para somar um sobre todos os pares. Eles representam intensidades de arestas individuais.

A biblioteca ajusta a e b por uma aproximação de curva, associada a `min_dist` e `spread`: uma região de intensidade desejada aproximadamente unitária até min_dist, seguida de decaimento. Min_dist influencia compactação, mas não impõe uma restrição rígida `‖zᵢ−zⱼ‖≥min_dist`.

### 13.7. Objetivo teórico de comparação dos grafos

Para cada par, a divergência entre duas intensidades de Bernoulli contém:

$$
w_{ij}\log\frac{w_{ij}}{q_{ij}}+
(1-w_{ij})\log\frac{1-w_{ij}}{1-q_{ij}}.
$$

Os termos com apenas w são constantes durante a disposição do mapa. Assim, o problema equivalente é minimizar:

$$
\mathcal L(Z)=-\sum_{i<j}
\left[w_{ij}\log q_{ij}+(1-w_{ij})\log(1-q_{ij})\right].
$$

O primeiro termo favorece aproximação para arestas fortes; o segundo penaliza conectar demais pares com w pequeno. Esse é o objetivo teórico de comparação, não uma afirmação de que a implementação calcula exatamente a soma de todos os pares a cada passo.

Visão conceitual da construção e da comparação: [documentação “How UMAP Works”](https://umap-learn.readthedocs.io/en/latest/how_umap_works.html). As próximas derivadas explicitam a regra de movimento a partir de um termo desse objetivo.

### 13.8. Derivação do gradiente de um par

Com w fixo e s > 0, escreva:

$$
\ell(s)=-w\log q(s)-(1-w)\log(1-q(s)),
\quad q(s)=(1+as^b)^{-1}.
$$

As derivadas são:

$$
\frac{d\ell}{dq}=\frac{q-w}{q(1-q)},\qquad
\frac{dq}{ds}=-ab s^{b-1}q^2.
$$

Como `1−q=asᵇq`, simplificamos:

$$
\frac{d\ell}{ds}=\frac{b(w-q)}{s}.
$$

Usando `∇zᵢ s=2(zᵢ−zⱼ)`:

$$
\boxed{\nabla_{z_i}\ell=\frac{2b(w-q)}{s}(z_i-z_j)}.
$$

Para uma aresta positiva tratada com w = 1, a contribuição de descida é:

$$
-\nabla\ell_{+}=-\frac{2ab s^{b-1}}{1+as^b}(z_i-z_j).
$$

Para uma amostra negativa tratada com w = 0:

$$
-\nabla\ell_{-}=\frac{2b}{s(1+as^b)}(z_i-z_j).
$$

O primeiro movimento aproxima; o segundo afasta. As fórmulas foram derivadas para s > 0; em proximidade extrema, a implementação usa proteção numérica e limitação de gradiente.

### 13.9. Amostragem de arestas e negativas

Somar todos os pares em cada passo seria caro. O código usa a frequência das arestas para representar suas intensidades e amostra outros vértices como exemplos negativos. Essas negativas não são “classes erradas”: são pares usados na força repulsiva.

O otimizador instalado inclui taxa de amostragem negativa, clipping e um estabilizador no denominador repulsivo. Também há um parâmetro de força repulsiva chamado `gamma` internamente, distinto do gamma RBF usado em Kernel FCM e Kernel PCA.

Uma descrição rigorosa distingue o objetivo de todos os pares da dinâmica efetiva com amostragem: sem analisar as distribuições e os pesos de correção, não se deve afirmar que cada passo é um estimador não enviesado do gradiente da soma completa. A ponderação efetiva das forças pode depender do esquema de amostragem.

O [artigo de UMAP, seções 4.1–4.2](https://arxiv.org/html/1802.03426v3) apresenta o procedimento de otimização por amostragem. Para esta apostila, as fórmulas de escala e as atualizações foram também conferidas nos módulos locais `umap_.py` e `layouts.py`.

### 13.10. Exemplo didático da força de um par

Tome a = b = 1, s = 1 e deslocamento `(1,0)`, de modo que q = 1/2. Para w = 0,9:

$$
\nabla\ell=2(0,9-0,5)(1,0)=(0,8;0).
$$

Um passo de descida de tamanho 0,1 contribui com `(−0,08;0)`. Se w = 0,1, o gradiente passa a `(−0,8;0)` e a descida contribui com afastamento. É um cálculo de um termo teórico, não um mapa completo nem a parametrização a,b ajustada na Iris.

### 13.11. Projeto e interpretação

M = 15, min_dist = 0,1, spread = 1, duas dimensões, distância euclidiana, inicialização espectral, seed 42 e uma thread. `n_epochs` foi deixado automático; o registro de parâmetros não contém um contador de épocas observado.

UMAP preserva aspectos de conectividade e vizinhança segundo o grafo e sua disposição. Não oferece garantia de preservar toda a topologia, densidade ou distância global em duas dimensões. Uma ilha visual pode refletir escolhas de vizinhança e otimização; não é prova de uma nova classe natural.

## 14. Matemática das métricas

### 14.1. Silhueta: uma comparação relativa de duas médias

Para uma observação i em um grupo Cᵢ com pelo menos dois membros:

$$
a(i)=\frac{1}{|C_i|-1}\sum_{j\in C_i,\,j\ne i}d(x_i,x_j).
$$

Para cada outro grupo C, calcule a distância média de i a seus membros. Escolha a menor:

$$
b(i)=\min_{C\ne C_i}\frac{1}{|C|}\sum_{j\in C}d(x_i,x_j).
$$

Então:

$$
s(i)=\frac{b(i)-a(i)}{\max\{a(i),b(i)\}}.
$$

Como a e b são não negativos, s fica entre −1 e 1 nos casos não degenerados. A normalização permite uma interpretação relativa:

- Se `b≥a`, temos `s=1−a/b`.
- Se `a>b`, temos `s=b/a−1`.

Um valor 0,75 no primeiro caso significa que a distância média ao próprio grupo é um quarto da distância média ao grupo alternativo escolhido. Isso não dá uma probabilidade de acerto.

A silhueta global é a média por observação. Logo, grupos maiores têm mais contribuição para essa média; ela não é necessariamente a média simples das médias de cada cluster.

### 14.2. Exemplo didático calculado de silhueta

Considere `C₁={0,1}` e `C₂={4,5}`, com distância absoluta. Para x = 0, `a=1`, `b=(4+5)/2=4,5`; sua silhueta é `7/9 ≈ 0,777778`.

Para x = 1, `a=1`, `b=(3+4)/2=3,5`; sua silhueta é `5/7 ≈ 0,714286`. Por simetria, x = 4 e x = 5 repetem esses valores em ordem inversa.

A média global é:

$$
\frac{7/9+5/7+5/7+7/9}{4}=\frac{47}{63}\approx0,746032.
$$

Se multiplicarmos todas as distâncias por uma mesma constante positiva, a e b são multiplicados pela constante e a silhueta não muda. Padronização por coluna geralmente muda proporções entre distâncias e, portanto, não tem essa invariância.

### 14.3. Casos especiais e uso no projeto

Com um único grupo, b não existe. Com tantos grupos quanto observações, não há a comparação intragrupo usual. A implementação requer de dois a n−1 rótulos distintos.

Para uma observação em grupo unitário dentro de uma partição válida, o scikit-learn atribui silhueta zero por convenção. Distâncias degeneradas também exigem tratamento numérico.

Na Q1, a silhueta é euclidiana e usa as quatro dimensões padronizadas. A silhueta do DBSCAN descreve os 144 pontos atribuídos a grupos. O resultado principal dos outros seis métodos usa as 150 observações. A análise de mesma amostra recalcula as métricas dos sete métodos nos 144 pontos retidos pelo DBSCAN.

### 14.4. ARI: contagem de pares

Considere uma tabela `nᵢⱼ` cruzando classes de referência i e clusters estimados j. Defina margens `aᵢ=Σⱼnᵢⱼ`, `bⱼ=Σᵢnᵢⱼ` e `T=C(n,2)`.

As quantidades:

$$
A=\sum_i\binom{a_i}{2},\quad
B=\sum_j\binom{b_j}{2},\quad
I=\sum_{ij}\binom{n_{ij}}{2}
$$

contam pares juntos na referência, juntos na estimação e juntos nas duas, respectivamente.

O número de pares separados nas duas é `T−A−B+I`. O Rand Index não ajustado seria:

$$
RI=\frac{I+(T-A-B+I)}{T}.
$$

### 14.5. De onde vem a correção pelo acaso

Sob um modelo de permutação que mantém os tamanhos das partes, um par que está junto na referência tem probabilidade `B/T` de também ficar junto na partição permutada. Portanto:

$$
E[I]=A\frac BT.
$$

O índice ajustado é:

$$
\boxed{ARI=\frac{I-AB/T}{\tfrac12(A+B)-AB/T}}.
$$

A normalização é a adotada pelo índice; a expressão é aplicada com convenções adequadas nos casos degenerados. Valores iguais a um indicam partições equivalentes, e o esperado sob a referência de acaso é aproximadamente zero. É possível obter valores negativos.

“Corrigido pelo acaso” não significa comparar com toda definição possível de aleatoriedade: o modelo de referência fixa as margens.

### 14.6. Dois exemplos didáticos de ARI

Para `[[2,0],[0,2]]`, temos `n=4`, `T=6`, `A=B=I=2`. Assim `E=2/3`, numerador e denominador são `4/3`, e ARI = 1.

Para `[[1,1],[1,1]]`, temos `A=B=2` e `I=0`. O numerador é `−2/3` e o denominador `4/3`, produzindo **ARI = −0,5**. A partição está em desacordo com a referência além do esperado pelo modelo de permutação.

Permutar nomes de grupos apenas troca linhas ou colunas da tabela e não muda as somas. Por isso o ARI não exige mapear “cluster 0” a uma espécie específica.

### 14.7. ARI da partição comum na Iris

A tabela das partições selecionadas tem 50 setosas em um grupo e 50 versicolors mais 50 virginicas no outro. Logo:

$$
A=3\binom{50}{2}=3675,
\qquad
B=\binom{50}{2}+\binom{100}{2}=6175,
$$

$$
I=3\binom{50}{2}=3675,
\qquad T=\binom{150}{2}=11175.
$$

Substituir na fórmula dá aproximadamente **0,568116**, o valor registrado. Não há conversão desse número em percentual de flores corretamente classificadas.

As definições e convenções de avaliação estão na [documentação de silhueta](https://scikit-learn.org/stable/modules/clustering.html#silhouette-coefficient) e na [documentação de ARI](https://scikit-learn.org/stable/modules/clustering.html#adjusted-rand-index). As contas acima explicitam as margens e a expectativa combinatória.

### 14.8. Trustworthiness e vizinhos artificiais

Seja h o número de vizinhos avaliado. Para cada i, compare os h vizinhos da projeção com os h vizinhos originais. Defina Uᵢ como aqueles que se tornaram vizinhos no mapa, embora não estivessem entre os h originais.

Se `r(i,j)` é a posição de j no ranking original, a penalidade é `r(i,j)−h`. Então:

$$
\boxed{T(h)=1-\frac{2}{nh(2n-3h-1)}
\sum_i\sum_{j\in U_i}[r(i,j)-h]}.
$$

Um vizinho artificial que era o 11º no original é menos penalizado que um que era o 100º quando h = 10. Isso é mais informativo que apenas contar interseções de vizinhos.

A biblioteca exige `h<n/2` para a faixa normalizada usada. Com n = 150 e h = 10:

$$
nh(2n-3h-1)=150\cdot10\cdot269=403500.
$$

A normalização converte a soma de penalidades em uma perda relativa de confiança local. Uma unidade a mais nessa soma reduz o índice em `2/403500`.

### 14.9. O que o índice local não mede

Trustworthiness pune a introdução de vizinhos artificiais. Uma métrica complementar, chamada continuidade, considera vizinhos originais que deixam de ser próximos no mapa, usando rankings no sentido inverso. O projeto não calculou continuidade.

Assim, trustworthiness alto não é prova de distâncias globais corretas, preservação de densidade, identificação de espécies ou estabilidade entre sementes. Deve-se também explicitar h: uma projeção pode preservar melhor uma escala de vizinhança que outra.

No projeto, os valores foram PCA 0,978156, Kernel PCA 0,932238, t-SNE 0,988813 e UMAP 0,978349, com h = 10. Referência de fórmula e restrições: [trustworthiness no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.trustworthiness.html).

## 15. Relações entre os métodos e custos

### 15.1. Três modos de representar associação

| Modelo | Associação | Como a distância influencia a associação |
|---|---|---|
| K-Means | Exclusiva | Seleciona apenas o menor custo quadrático |
| FCM | Pertinência fuzzy | Normaliza potências inversas das distâncias |
| GMM esférico, pesos iguais | Probabilidade posterior | Normaliza exponenciais negativas dos quadrados |

Mesmo quando duas saídas somam um, sua origem matemática difere. Um FCM com m = 2 não reproduz em geral as posteriores de uma mistura gaussiana.

### 15.2. Centros livres, representantes observados e grafos

K-Means e FCM atualizam médias em um espaço contínuo. K-Medoids escolhe observações de um conjunto finito. O Kernel FCM estudado mantém protótipos contínuos no espaço original, mas mede seu custo em ℋ.

UPGMA trabalha com conjuntos e uma árvore; DBSCAN trabalha com conectividade por densidade; UMAP constrói e dispõe um grafo ponderado. Compartilhar a palavra “grupo” ou “vizinhança” não torna seus objetivos equivalentes.

### 15.3. Comparação dos objetivos de projeção

PCA e Kernel PCA resolvem problemas espectrais, com solução global do subproblema de projeção no espaço correspondente. t-SNE e a disposição do UMAP usam objetivos não convexos nas posições do mapa.

A existência de autovetores e autovalores não implica que todo o procedimento seja livre de escolhas: PCA depende da escala; Kernel PCA depende ainda do kernel; UMAP usa uma inicialização espectral antes de sua otimização.

### 15.4. Custos assintóticos: o que está sendo contado

Os custos abaixo descrevem formas usuais ou diretas dos cálculos. T é quantidade de iterações/rodadas, q é a dimensão do mapa, M é a vizinhança do UMAP e L é a taxa de negativas. Não são tempos medidos, nem uma promessa de desempenho de toda biblioteca.

| Método | Operação relevante | Ordem de custo de referência |
|---|---|---|
| K-Means | Distâncias ponto–centro e médias | `O(T n k d)` |
| FCM | Distâncias e atualizações vetorizadas | `O(T n k d)` |
| Kernel FCM desta variante | Kernel ponto–protótipo e atualizações | `O(T n k d)`, além da inicialização FCM |
| K-Medoids/PAM direto | Matriz de distâncias e avaliação de trocas | Matriz `O(n²d)`; rodada direta de trocas `O(k(n−k)n)` |
| GMM full | Formas quadráticas e fatorações de covariância | Aproximadamente `O(T(nkd²+kd³))` |
| UPGMA average do SciPy | Distâncias e cadeia de vizinhos mais próximos | Distâncias `O(n²d)`; ligação `O(n²)` |
| DBSCAN por consultas diretas | Todas as vizinhanças | Pode chegar a `O(n²d)`; índices podem ajudar |
| PCA por SVD densa reduzida | Decomposição de X | Ordem `O(nd min(n,d))` |
| Kernel PCA densa | Gram e decomposição | `O(n²d+n³)` |
| t-SNE exato | Forças entre pares a cada passo | `O(T n²q)`, além das afinidades |
| t-SNE Barnes-Hut | Aproximação de forças | Próximo de `O(T n log n)` para q fixo sob condições favoráveis |
| UMAP, disposição do grafo | Amostragem de arestas e negativas | `O(T |E| q(1+L))`, além da busca de vizinhos |

O tempo real depende de convergência, vetorização, paralelismo, dimensão, implementação e estruturas de consulta. A contagem de 252 chamadas principais não torna o esforço de cada método equivalente.

### 15.5. Memória e matrizes grandes

A matriz densa de distâncias de PAM, a Gram da Kernel PCA e o armazenamento usual do hierárquico exigem ordem `n²`. No DBSCAN do scikit-learn, materializar muitas vizinhanças também pode atingir memória quadrática. Isso não é uma obrigação de toda implementação concebível do conceito DBSCAN.

FCM e Kernel FCM desta variante armazenam matrizes de associação `n × k`; o Kernel FCM não exige necessariamente uma Gram `n × n`, pois calcula kernels ponto–protótipo. Essa distinção evita atribuir custo quadrático a todo método só porque usa kernel.

Para n = 150, `n²=22.500` e o vetor condensado tem 11.175 entradas. Essas quantidades são pequenas neste estudo, mas crescem por um fator 100 quando n cresce por um fator 10.

### 15.6. O que cada tipo de convergência permite afirmar

| Situação | O que sustenta | O que não sustenta sozinha |
|---|---|---|
| Queda do objetivo em blocos exatos | Melhoria ou manutenção do valor | Ótimo global do problema conjunto |
| Tolerância de U no FCM | Pequena mudança das pertinências | Igualdade exata de todas as equações estacionárias |
| Parada PAM sem trocas melhores | Estabilidade na vizinhança de uma troca | Melhor conjunto entre todos os subconjuntos |
| Convergência EM registrada | Critério de parada da biblioteca satisfeito | Melhor mistura possível |
| SVD/autodecomposição | Solução espectral do problema escolhido | Relevância biológica do critério |
| Fim das iterações de um mapa | Orçamento de otimização encerrado | Estabilidade, ótimo global ou classes verdadeiras |

## 16. Aplicação ao projeto

### 16.1. Configurações que você deve saber justificar

| Método | Configuração principal |
|---|---|
| K-Means | `random`, uma inicialização por chamada |
| FCM | m = 2, 300 iterações, tolerância 10⁻⁵ |
| Kernel FCM | RBF gamma = 0,25; m = 2; protótipos no espaço de entrada |
| K-Medoids | PAM, euclidiana, inicialização aleatória; k = 1 por busca exaustiva |
| GMM/EM | Full, `random_from_data`, tolerância 10⁻⁵, regularização 10⁻⁶ |
| UPGMA | Average linkage, Manhattan, uma árvore |
| DBSCAN | Euclidiana, eps = 0,6943, min_samples = 3 |
| PCA | Quatro componentes, SVD completa; figura usa duas |
| Kernel PCA | RBF gamma = 0,25, duas componentes, solver denso |
| t-SNE | Perplexidade 30, init PCA, seed 42, Barnes-Hut |
| UMAP | 15 vizinhos, min_dist 0,1, spread 1, init espectral, seed 42 |

Os parâmetros dos agrupadores foram escolhidos pelas silhuetas obtidas na Iris e nas grades avaliadas. Nos cinco métodos particionais, as configurações de referência empataram com outras configurações em k = 2 e foram selecionadas pelo desempate.

### 16.2. Orçamento e seleção

O conjunto final inclui 250 ajustes particionais, uma árvore UPGMA e uma configuração DBSCAN. A busca avaliou 1.120 ajustes particionais em k de 2 a 5 e 24 configurações DBSCAN. Com os 50 ajustes de k = 1 e a árvore UPGMA, o total executado foi de 1.195 ajustes. As quatro projeções foram executadas separadamente.

Para cada método, configuração e k, a função objetivo selecionou a semente. Usou-se o menor custo nos quatro primeiros métodos e a maior log-verossimilhança no GMM. Os hiperparâmetros e o k foram escolhidos pela maior silhueta válida. No DBSCAN, a escolha também exigiu pelo menos 95% de cobertura. O ARI foi calculado depois da seleção.

Operações auxiliares internas, como a inicialização do KFCM por FCM, e iterações não são novas chamadas principais na contagem do protocolo.

### 16.3. Como a teoria explica os resultados

Os seis métodos com seleção de k produziram a mesma partição em k = 2: 50 setosas de um lado, 50 versicolors e 50 virginicas do outro. A silhueta 0,580184 favorece essa separação geométrica, enquanto o ARI 0,568116 indica correspondência incompleta com as três espécies.

GMM com k = 3 atingiu ARI 0,903874 e silhueta 0,372773. A capacidade de covariâncias completas é compatível com maior flexibilidade para a organização das espécies, mas o experimento não isolou causalmente esse mecanismo. Esse caso foi interpretado posteriormente; não substituiu k = 2 na seleção oficial.

O DBSCAN cobriu 144 pontos e classificou seis como ruído. Nesse subconjunto, os sete métodos obtiveram partições equivalentes, com silhueta 0,603455 e ARI 0,576048 em relação às espécies.

### 16.4. Como a teoria limita as conclusões das projeções

A PCA reteve 95,80% da variância padronizada nas duas primeiras componentes, coerente com um erro linear quadrático relativamente pequeno. Isso não obriga a separação das espécies.

Kernel PCA apresentou autovalores do kernel, sem uma proporção diretamente equivalente da variância dos atributos. t-SNE teve o maior trustworthiness com dez vizinhos, mas isso mede uma direção de preservação local sob uma configuração específica.

Não houve agrupamento das coordenadas 2D, repetição de sementes das projeções ou benchmark de desempenho que sustente conclusões adicionais sobre esses aspectos.

## 17. Exercícios com resolução

Os exercícios seguintes usam dados didáticos. Procure resolver antes de ler a conta final.

### Exercício 1 — Distância quadrática é métrica?

**Enunciado:** avalie a desigualdade triangular para os pontos 0, 1 e 2 em 1D usando quadrados das distâncias.

**Resolução:** `d²(0,2)=4`, mas `d²(0,1)+d²(1,2)=2`. Como 4 > 2, ela não satisfaz a desigualdade. Usar esse quadrado como perda continua válido; só não se pode transferir automaticamente toda propriedade de métricas para ele.

### Exercício 2 — Uma atualização de centroide

**Enunciado:** encontre o centro que minimiza a soma de quadrados para `1,2,9`.

**Resolução:** a média é 4. O custo é `9+4+25=38`. Para um centro qualquer v, a identidade do capítulo 3 dá `J(v)=38+3(v−4)²`, que prova ser impossível obter custo menor.

### Exercício 3 — Por que o medoide pode mudar?

**Enunciado:** para os mesmos pontos `1,2,9`, escolha um representante observado minimizando soma das distâncias absolutas.

**Resolução:** custos dos candidatos 1, 2 e 9 são 9, 8 e 15. O medoide é 2. A diferença para a média decorre tanto do domínio discreto quanto da perda sem quadrado.

### Exercício 4 — Pertinências FCM

**Enunciado:** um ponto está às distâncias 2 e 6 dos centros. Calcule suas pertinências com m = 2.

**Resolução:** pesos inversos quadráticos `1/4` e `1/36`, cuja soma é `10/36`. Assim as pertinências são 0,9 e 0,1. O rótulo crisp escolhe o primeiro grupo. A parcela do objetivo vale `0,9²×4+0,1²×36=3,6`.

### Exercício 5 — Distância do Kernel FCM

**Enunciado:** com gamma = 0,25 e distância original 2, calcule K, δ² e δ.

**Resolução:** `K=e⁻¹≈0,367879`; `δ²=2(1−e⁻¹)≈1,264241`; `δ≈1,124385`. O quadrado não é 4, pois a geometria foi alterada.

### Exercício 6 — Troca PAM

**Enunciado:** usando o exemplo `{0,2,3,10}`, explique por que trocar medoide 0 por 10 melhora o custo.

**Resolução:** o ponto 0 sofre acréscimo 2; o ponto 10 ganha redução 8; os outros mantêm o custo. A mudança total é −6, levando o objetivo de 9 a 3. Não é necessário que a troca melhore o custo de todos os pontos individualmente.

### Exercício 7 — Peso a priori no GMM

**Enunciado:** as duas densidades em x são iguais, mas os pesos são 0,8 e 0,2. Quais as responsabilidades?

**Resolução:** como o fator de densidade é comum, cancela-se na normalização. As posteriores são 0,8 e 0,2. Estar à mesma compatibilidade de densidade não obriga posterior 0,5 quando os pesos diferem.

### Exercício 8 — Média ponderada no passo M

**Enunciado:** para pontos 0 e 10, um componente tem responsabilidades 0,9 e 0,1. Calcule sua média atualizada.

**Resolução:** `N=1`, e a média é `(0×0,9+10×0,1)/1=1`. O segundo componente, se tiver as responsabilidades complementares, tem média 9. O exemplo evidencia a diferença entre média global e média ponderada por posterior.

### Exercício 9 — UPGMA versus WPGMA

**Enunciado:** |A| = 4, |B| = 1, D(A,C) = 2 e D(B,C) = 10. Calcule a nova distância após unir A e B.

**Resolução:** UPGMA dá `(4×2+1×10)/5=3,6`. WPGMA daria 6. Ponderar pelo tamanho é o que mantém pesos iguais para as observações originais.

### Exercício 10 — Um ponto de borda conecta dois clusters?

**Enunciado:** uma observação não core está a distância no máximo eps de núcleos de duas componentes distintas. Ela deve necessariamente fundir os clusters?

**Resolução:** não. Pontos de borda não prolongam a cadeia como núcleos. Sua atribuição pode ser ambígua e dependente da ordem. Se ela se tornasse core sob outra configuração, então poderia conectar regiões antes separadas.

### Exercício 11 — Autovalores da PCA

**Enunciado:** uma covariância tem autovalores 5, 2 e 1. Qual proporção é retida em duas componentes? Qual o erro total de reconstrução de uma matriz centralizada com n = 10?

**Resolução:** a proporção é `7/8=87,5%`. O erro quadrático total é `(10−1)×1=9`. A soma de autovalores omitidos mede variância perdida; o fator n−1 a converte para soma total de quadrados.

### Exercício 12 — Coordenadas da Kernel PCA

**Enunciado:** para um autovetor unitário a e autovalor κ = 9 da Gram centralizada, quais são os scores de treinamento dessa componente?

**Resolução:** `z=√κ a=3a`. Usar 9a confundiria autovalor com sua raiz. A direção no espaço de características é normalizada pelo fator `1/√κ`.

### Exercício 13 — Perplexidade

**Enunciado:** qual a perplexidade de uma distribuição uniforme sobre quatro vizinhos? E de uma distribuição concentrada em um só?

**Resolução:** as entropias são 2 bits e zero. As perplexidades são 4 e 1. Isso explica a noção de número efetivo, sem transformar perplexidade em quantidade de clusters.

### Exercício 14 — Sinal do gradiente de t-SNE

**Enunciado:** um par tem p > q. Um passo de descida tende a aproximá-lo ou afastá-lo?

**Resolução:** sua contribuição ao gradiente é um múltiplo positivo de `zᵢ−zⱼ`. Como a descida subtrai o gradiente, o movimento tende a aproximar i de j. O movimento real soma contribuições de todos os pares.

### Exercício 15 — União fuzzy no UMAP

**Enunciado:** os pesos dirigidos são 0,6 e 0,7. Calcule a união.

**Resolução:** `0,6+0,7−0,6×0,7=0,88`. Ela fica entre o maior peso individual, 0,7, e um. Não se normaliza a linha dessa matriz como se fossem probabilidades de espécies.

### Exercício 16 — Força de um par UMAP

**Enunciado:** a = b = 1, s = 1 e w = 0,8. Calcule o coeficiente do gradiente que multiplica `zᵢ−zⱼ`.

**Resolução:** q = 1/2 e `2b(w−q)/s=0,6`. A contribuição de descida é −0,6 vezes o deslocamento, isto é, atrativa. Clipping e amostragem podem modificar a dinâmica numérica efetiva.

### Exercício 17 — Silhueta

**Enunciado:** a = 3 e b = 2. Qual a silhueta e o que ela indica?

**Resolução:** `s=(2−3)/3=−1/3`. O ponto está, em média, mais próximo do grupo alternativo escolhido que do próprio grupo. Isso não implica necessariamente um erro segundo uma espécie externa, pois a métrica não consulta esse rótulo.

### Exercício 18 — ARI e nomes dos grupos

**Enunciado:** compare as partições `[0,0,1,1]` e `[8,8,3,3]`.

**Resolução:** os pares juntos e separados coincidem. A tabela, após reordenar colunas, é diagonal, e ARI = 1. Os identificadores não têm significado ordinal.

### Exercício 19 — Penalidade local

**Enunciado:** h = 10. Dois vizinhos artificiais de um ponto tinham rankings originais 11 e 30. Quanto esse ponto acrescenta à soma de penalidades de trustworthiness?

**Resolução:** `(11−10)+(30−10)=21`. Na Iris, essa contribuição isolada reduz T em `42/403500≈0,00010409`. O valor global soma também as contribuições de todas as demais observações.

### Exercício 20 — Seleção experimental

**Enunciado:** para k = 3, a execução A tem menor objetivo K-Means, mas B tem maior silhueta. Qual deve seguir para a comparação entre valores de k no protocolo do projeto?

**Resolução:** A. A melhor tentativa para k fixo é escolhida primeiro pelo objetivo do método. Comparar diretamente todas as sementes pela silhueta mudaria a regra experimental. No GMM, o sentido do objetivo se inverte: escolhe-se a maior log-verossimilhança.

## 18. Fontes e alcance

### 18.1. Evidência da implementação utilizada

Os detalhes do projeto vêm de:

- [codigo/algoritmos.py](codigo/algoritmos.py): objetivos, parâmetros, conversões crisp, seleção, métricas, PAM, UPGMA e DBSCAN.
- [codigo/questoes.py](codigo/questoes.py): fluxo experimental e configurações das quatro projeções.
- [codigo/requirements.txt](codigo/requirements.txt): versões declaradas do ambiente.
- [resultados/metadados_questao_1.json](resultados/metadados_questao_1.json) e [metadados_questao_2.json](resultados/metadados_questao_2.json): configuração registrada.
- [resultados/execucoes_questao_1.json](resultados/execucoes_questao_1.json), [metricas_por_k.csv](resultados/metricas_por_k.csv) e [contingencias.json](resultados/contingencias.json): resultados de agrupamento.
- [resultados/execucoes_questao_2.json](resultados/execucoes_questao_2.json): saídas das projeções.
- [Artigo revisado](docs/artigo/artigo_ieee_revisado.pdf): narrativa experimental, discussão e bibliografia acadêmica do projeto.

Foram inspecionados os métodos locais de `fcmeans.FCM` e `fcmeans.KFCM`, a documentação local de `kmedoids.pam` e os módulos `umap/umap_.py` e `umap/layouts.py`. Isso permite explicitar variantes e detalhes que uma descrição genérica de “fuzzy” ou “kernel” poderia omitir.

### 18.2. Fontes primárias e documentação consultadas

- [Scikit-learn: agrupamento e avaliação](https://scikit-learn.org/stable/modules/clustering.html).
- [Scikit-learn: KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).
- [Scikit-learn: misturas gaussianas](https://scikit-learn.org/stable/modules/mixture.html).
- [Scikit-learn: DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html).
- [SciPy: linkage, average/UPGMA e matriz de ligações](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html).
- [Scikit-learn: PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html).
- [Scikit-learn: KernelPCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html).
- [Scikit-learn: TSNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html).
- [Van der Maaten e Hinton, 2008: Visualizing Data using t-SNE](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf), em especial seção 3 e apêndice A.
- [Documentação UMAP: How UMAP Works](https://umap-learn.readthedocs.io/en/latest/how_umap_works.html).
- [McInnes, Healy e Melville: UMAP, versão 3, 2020](https://arxiv.org/html/1802.03426v3), em especial seções de construção e otimização.
- [Scikit-learn: trustworthiness](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.trustworthiness.html).

As páginas online podem acompanhar versões diferentes das instaladas. O código local e os metadados prevalecem na descrição do experimento.

As derivações são exposições algébricas desenvolvidas para estudo, a partir das definições e dos objetivos explicitados. As fontes apoiam os conceitos e contratos indicados; não se afirma leitura integral de todas as referências da bibliografia do artigo. Esta apostila não reexecutou os ajustes, não introduz novos resultados na Iris e não certifica ótimo global ou correção de toda implementação de terceiros.
