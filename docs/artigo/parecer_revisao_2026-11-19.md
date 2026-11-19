# Parecer de revisão — artigo IEEE revisado

Arquivo analisado: `artigo_ieee_revisado.pdf`, com seis páginas, e seu fonte `artigo_ieee_revisado.typ`. Revisão realizada em 19/11/2026. O PDF e o fonte foram preservados.

O artigo apresenta um protocolo compreensível e resultados centrais consistentes com os artefatos locais. A distinção entre silhueta e ARI e a comparação dos agrupamentos na amostra comum do DBSCAN são pontos fortes. Antes da entrega, recomendo os ajustes abaixo, principalmente na discussão das escolhas e na documentação do experimento.

## 1. Explicar o contraste entre o GMM selecionado e a alternativa com maior ARI

**Prioridade alta — páginas 3 e 5; seções V-B, V-C e VIII.**

A Tabela V apresenta ARI de 0,6199 para o GMM esférico em três grupos, enquanto a Tabela VI apresenta 0,9222 para covariância completa e regularização de 0,01 na tunagem. A afirmação de que UPGMA tem o maior ARI está corretamente restrita aos perfis selecionados. Ainda assim, o leitor precisa entender por que a configuração com ARI maior não foi escolhida.

Sugestão de acréscimo à discussão:

> A seleção pela média das silhuetas favoreceu o GMM com covariância esférica. Na análise de sensibilidade da tunagem, o GMM com covariância completa, regularização de 0,01 e três componentes obteve ARI de 0,9222, mas silhueta de 0,3685. Assim, a configuração selecionada pelo critério interno não foi a que melhor recuperou as espécies. O maior ARI do UPGMA em três grupos se refere à comparação entre os perfis selecionados para o experimento final.

Os valores das Tabelas V e VI também vêm de conjuntos distintos de sementes. Convém preservar essa distinção ao discuti-los. Não é necessário trocar o critério de seleção retrospectivamente.

## 2. Delimitar o significado das novas sementes

**Prioridade alta — páginas 2 e 5; seções IV-A e VII.**

As sementes 42–51 e 52–61 distinguem as inicializações, mas a tunagem e o experimento usam a mesma matriz de 150 flores. A redação atual não afirma uma avaliação em dados novos; vale tornar esse limite explícito para evitar essa interpretação.

Sugestão:

> A separação das sementes avalia o comportamento com novas inicializações sobre a mesma base. Como a tunagem e a avaliação utilizam as mesmas 150 observações, os resultados descrevem essa amostra e não estimam o desempenho em dados novos.

A frase de limitações sobre as dez sementes também deve considerar o PAM com inicialização `build`, que pode repetir a mesma solução sem variar a inicialização, e a busca exaustiva em k = 1, já documentada no método. Evitar apresentar as 250 chamadas como 250 soluções diferentes.

## 3. Completar os parâmetros de reprodução no próprio artigo

**Prioridade média — página 2; seção IV-B.**

O texto remete às versões e aos parâmetros em `resultados/`, mas alguns detalhes relevantes podem caber em uma frase ou tabela curta. O código registra:

- K-Means: `n_init=1`, com dez chamadas externas por k.
- FCM e Kernel FCM: `n_init=1`, `max_iter=300` e `error=1e-5`.
- PAM: limite de 300 iterações para k > 1.
- GMM: `n_init=1`, `init_params="random_from_data"` e `tol=1e-5`.

Explicitar `n_init=1` ajuda a entender a contagem dos ajustes. A fundamentação descreve covariâncias completas, mas o perfil final do GMM é esférico; acrescentar que o perfil selecionado usa uma variância por componente, compartilhada entre as direções daquele componente.

## 4. Corrigir a citação da base e melhorar as referências

**Prioridade média — páginas 1 e 6.**

A referência [3], relativa à base Iris, aparece na bibliografia sem chamada no corpo. Acrescentá-la na apresentação da base e renumerar as referências pela ordem da primeira citação, caso esse seja o padrão adotado. Hoje [2] é StandardScaler e [3] é Iris.

As referências eletrônicas usam links cujo texto visível é apenas “Online”. Os links funcionam no arquivo digital, mas o endereço não fica visível na impressão. Considerar apresentar “[Online]. Disponível em: URL”, com data de acesso quando requerida pelo formato da atividade. A referência [21] também contém a repetição “documentação online. Online”.

Este parecer não verifica os metadados bibliográficos em fontes externas nem certifica conformidade com um template oficial IEEE.

## 5. Fortalecer o resumo e a conclusão com o resultado principal

**Prioridade média — páginas 1 e 5.**

O resumo informa que foram selecionados dois grupos, mas pode especificar que os seis métodos com escolha de k chegaram à mesma partição. A conclusão também pode recuperar esse achado e a comparação com o DBSCAN na amostra comum.

Sugestão de abertura para a conclusão:

> Nos seis métodos com escolha do número de grupos, a silhueta favoreceu a mesma partição: um grupo com as 50 flores de I. setosa e outro com as 100 flores das demais espécies. Nas 144 observações retidas pelo DBSCAN, os sete métodos produziram partições idênticas, salvo os identificadores dos grupos. Portanto, a maior silhueta do DBSCAN na comparação inicial acompanha a mudança de amostra, sem diferença nas atribuições sobre a amostra comum.

Manter a ressalva de que o maior trustworthiness do t-SNE vale para as configurações e a escala de dez vizinhos avaliadas. A diferença entre PCA e UMAP é pequena e não fundamenta uma conclusão de superioridade geral.

## 6. Ajustar linguagem e apresentação

**Prioridade baixa — ao longo do texto.**

- Substituir “média das silhuetas de quatro números de grupos”, no resumo, por “média das silhuetas para k de 2 a 5”. “Ajuste de hiperparâmetros” também pode substituir “tunagem”, por preferência editorial.
- Uniformizar a vírgula decimal em texto e tabelas: a Tabela III mostra `reg = 0.01`, enquanto o restante adota `0,01`. Preservar ponto decimal quando o trecho for uma expressão literal de código.
- Na Tabela VI, apresentar `1e-06` como potência de dez ou adotar uma notação uniforme para as três regularizações.
- Considerar “Dimensão 1” e “Dimensão 2” nos eixos do t-SNE e do UMAP, para distingui-los das componentes da PCA.
- A Tabela V exige consultar a legenda para saber a ordem das métricas. Se houver espaço, identificar “Sil./ARI” no cabeçalho.

As páginas 1, 3, 4 e 5 foram inspecionadas por rasterização. Nessas páginas não identifiquei cortes de conteúdo ou sobreposições que comprometam a leitura. As tabelas são densas, mas legíveis na inspeção. A revisão textual abrangeu as seis páginas.

## Conferências realizadas

Foi feito um recálculo independente, sem reexecutar os agrupadores ou alterar resultados:

- As silhuetas dos 24 resultados em k = 2–5 e os ARIs das 30 linhas em k = 1–5 de `metricas_por_k.csv` coincidem com os valores recalculados a partir dos rótulos salvos e da base padronizada.
- DBSCAN: 144 observações retidas, silhueta 0,6034547528 e ARI 0,5760482515, confirmando os valores publicados após arredondamento.
- Trustworthiness com dez vizinhos: PCA 0,9781561338; Kernel PCA 0,9322379182; t-SNE 0,9888128872; UMAP 0,9783494424. Todos conferem com os registros e o artigo.
- Os cinco ajustes GMM selecionados por objetivo, um por k, têm `converged=True` nos registros. Isso é uma consulta aos registros, não uma nova execução.
- A grade contém 28 perfis particionais: 2 + 3 + 9 + 2 + 12. Com quatro valores de k e dez sementes, são 1.120 chamadas na tunagem. Somadas às 24 do DBSCAN e às 252 do experimento, a contagem declarada é 1.396.

As verificações confirmam a consistência entre o artigo e os artefatos salvos; não demonstram, por si só, a reprodução integral das execuções históricas.
