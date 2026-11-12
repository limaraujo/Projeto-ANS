"""Adapta o relatório validado ao estilo de artigo IEEE em duas colunas."""
from pathlib import Path
import re
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram

ROOT = Path(__file__).parent.parent
out = ROOT/'artigo'/'figuras'/'ieee'
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family':'serif', 'font.size':8, 'axes.labelsize':8,
                     'xtick.labelsize':7, 'ytick.labelsize':7, 'legend.fontsize':6.5})
m = pd.read_csv(ROOT/'resultados/metricas_por_k.csv')
for nome, linhas in m.groupby('algoritmo', sort=False):
    fig, ax=plt.subplots(figsize=(3.45,2.15))
    ax.plot(linhas.k,linhas.silhueta,'o-',lw=1,ms=3)
    best=linhas.loc[linhas.silhueta.idxmax()]
    ax.axvline(best.k,ls='--',color='#b32c34',lw=1,label=f'k* = {int(best.k)}')
    ax.set(xlabel='Número de grupos (k)',ylabel='Silhueta média',xticks=range(1,6))
    ax.text(1,0.04,'indefinida',rotation=90,transform=ax.get_xaxis_transform(),fontsize=7)
    ax.grid(alpha=.2); ax.legend(); fig.tight_layout(pad=.5)
    fig.savefig(out/f"silhueta_{nome.replace('-','_')}.pdf"); plt.close(fig)
q1=json.loads((ROOT/'resultados/execucoes_questao_1.json').read_text())
fig,ax=plt.subplots(figsize=(3.45,2.15))
dendrogram(np.array(q1['upgma']['2']['hierarquia']),no_labels=True,color_threshold=0,ax=ax)
ax.set(xlabel='Observações',ylabel='Distância Manhattan')
fig.tight_layout(pad=.5);fig.savefig(out/'dendrograma_upgma.pdf');plt.close(fig)
for nome in ['pca','kernel_pca','tsne','umap']:
    df=pd.read_csv(ROOT/f'resultados/coordenadas_{nome}.csv')
    fig,ax=plt.subplots(figsize=(3.45,2.35))
    for especie,cor,marker in zip(df.especie.unique(),['#2676a1','#c55b26','#438745'],['o','x','s']):
        d=df[df.especie==especie]
        ax.scatter(d.componente_1,d.componente_2,s=9,c=cor,marker=marker,label=especie.replace('Iris-',''),linewidths=.5)
    ax.set(xlabel='Componente 1',ylabel='Componente 2')
    if nome=='pca': ax.set(xlabel='PC1 (72,77%)',ylabel='PC2 (23,03%)')
    ax.legend(loc='best',framealpha=.85); ax.grid(alpha=.15)
    fig.tight_layout(pad=.5);fig.savefig(out/f'{nome}.pdf');plt.close(fig)

s=(ROOT/'relatorio.typ').read_text()
s=s[s.index('= Objetivo e aderência ao enunciado'):]
s=s.replace('= Objetivo e aderência ao enunciado','= Introdução')
start=s.index('A única fonte dos requisitos')
end=s.index('= Dados e preparação')
s=s[:start]+'''A análise não supervisionada pode revelar estruturas geométricas que não coincidem com classes conhecidas. Na base Iris, essa distinção permite comparar a seleção interna de agrupamentos com sua concordância externa com espécies botânicas. Este artigo avalia sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade, seguindo o protocolo atribuído à Equipe 08 no enunciado do projeto [1].

O objetivo é investigar quais partições são favorecidas pela silhueta, como elas se relacionam com as três espécies e quais estruturas são evidenciadas nas projeções bidimensionais. Foram realizados 252 ajustes principais: 250 ajustes particionais, uma hierarquia UPGMA e um DBSCAN. As projeções incluem PCA, Kernel PCA, t-SNE e UMAP. Os rótulos das espécies são utilizados apenas após os ajustes, para interpretação e avaliação externa.

As contribuições deste estudo são a comparação sob um protocolo comum, o registro completo das execuções e a interpretação conjunta de silhueta, índice de Rand ajustado e projeções. Padronização, sementes e hiperparâmetros são escolhas metodológicas; os requisitos experimentais decorrem exclusivamente de [1].

'''+s[end:]
s=s.replace('= Dados e preparação','= Base de dados e preparação').replace('= Questão 1: protocolo e métodos','= Metodologia de agrupamento')
s=s.replace('== Resultados consolidados','= Resultados de agrupamento\n== Comparação das partições selecionadas')
s=s.replace('= Questão 2: redução de dimensionalidade','= Redução de dimensionalidade')
s=s.replace('= Limitações e conclusão','= Discussão e limitações')
s=s.replace('A principal conclusão dos agrupamentos','= Conclusão\nA principal conclusão dos agrupamentos')
start=s.index('= Reprodutibilidade e artefatos')
s=s[:start]+'''= Reprodutibilidade
O código em Python separa os algoritmos (`algoritmos.py`), a execução das questões (`questoes.py`) e a interface (`main.py`). As versões utilizadas incluem NumPy 2.5.4, SciPy 1.18.1, scikit-learn 1.9.1, fuzzy-c-means 2.3.1, kmedoids 0.5.5 e umap-learn 0.5.12. As dependências completas são fixadas em `requirements.txt`.

Os artefatos incluem rótulos por execução, objetivos, parâmetros, sementes, pertinências e probabilidades posteriores. As métricas por k, contingências, coordenadas das projeções, componentes e loadings foram exportados em CSV ou JSON. A auditoria verificou as 252 execuções principais, a seleção por objetivo, silhuetas e ARI recalculados, normalização e conversão crisp, além da finitude das quatro projeções. O hash dos dados e as versões foram registrados para rastreabilidade. A auditoria verifica consistência dos resultados, sem garantir otimalidade global.

#heading(numbering: none)[Referências]
#block[
#set par(first-line-indent: 0pt, hanging-indent: 1.2em)
[1] F. de A. T. de Carvalho, “Projeto AM-NS 2026-2,” Centro de Informática, Universidade Federal de Pernambuco, Recife, Brasil, enunciado de projeto, 2026, pp. 2–7. Arquivo fornecido: `Projeto-AMG-NS-2026-2.pdf`.
]
'''
s=s.replace('width: 72%','width: 100%').replace('width: 90%','width: 100%')
s=re.sub(r'image\("figuras/([^".]+)\.png"',r'image("figuras/ieee/\1.pdf"',s)
# Legendas e numeração de tabelas no estilo IEEE.
pattern=r'#table\(.*?\n\)'
captions=['Estatísticas dos atributos antes da padronização','Resultados das partições selecionadas',
          'Silhueta das melhores execuções por k','Avaliação complementar com três grupos',
          'Espectro e variância explicada da PCA','Coeficientes das componentes principais',
          'Loadings da PCA','Autovalores da Kernel PCA','Saídas do t-SNE','Preservação local das projeções']
idx=iter(captions)
def wrap(match):
    tab=match.group().replace('inset: 5pt, stroke: .35pt','inset: (x: 2pt, y: 3pt), stroke: .3pt')
    tab=tab.replace('[Kernel Fuzzy K-Means]','[Kernel FCM]').replace('[Fuzzy K-Means]','[FCM]')
    tab=tab.replace('[automático]','[auto.]')
    for a,b in [('sepal\\_length','Comp. sépala'),('sepal\\_width','Larg. sépala'),('petal\\_length','Comp. pétala'),('petal\\_width','Larg. pétala')]: tab=tab.replace(a,b)
    return '#figure(kind: table, supplement: [TABELA], numbering: "I", caption: ['+next(idx)+'], [\n#set text(size: 8pt)\n'+tab+'\n])'
s=re.sub(pattern,wrap,s,flags=re.S)
header='''// Artigo acadêmico em estilo IEEE conference (A4), implementado em Typst.
// Compilar a partir da raiz: typst compile artigo/artigo_ieee.typ artigo/artigo_ieee.pdf
#set document(title: "Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa", author: "Equipe 08")
#set page(paper: "a4", margin: (top: 19mm, bottom: 43mm, x: 13mm), numbering: none)
#set text(font: "Nimbus Roman", size: 10pt, lang: "pt")
#set par(justify: true, leading: .45em, spacing: .55em, first-line-indent: 1em)
#set heading(numbering: "I.A.")
#set figure(gap: 5pt)
#show figure.caption: set text(size: 8pt)
#show figure.caption.where(kind: image): set figure.caption(separator: [. ])
#show figure.caption.where(kind: table): set figure.caption(separator: linebreak())
#show figure.where(kind: table): set figure.caption(position: top)
#show heading.where(level: 1): it => block(width: 100%, above: 1em, below: .6em)[
#set par(justify: false, first-line-indent: 0pt)
#align(center)[#text(weight: "regular", size: 10pt)[#if it.numbering != none {counter(heading).display("I."); h(.4em)}#upper(it.body)]]
]
#show heading.where(level: 2): it => block(above: .8em, below: .4em)[
#text(size: 10pt, weight: "regular", style: "italic")[#context numbering("A.", counter(heading).get().at(1)) #it.body]
]
#show figure.where(kind: image): set figure(supplement: [Fig.])
#align(center)[
#text(size: 24pt)[Agrupamento e redução de dimensionalidade na base Iris: uma avaliação comparativa]
#v(.7em)
#text(size: 11pt)[Equipe 08]
#linebreak()
#text(size: 10pt, style: "italic")[Centro de Informática — Universidade Federal de Pernambuco \\ Recife, Brasil]
#v(.8em)
]
#columns(2, gutter: 4.22mm)[
#block[
#set par(first-line-indent: 0pt)
#text(size: 9pt, weight: "bold")[Resumo—Este artigo compara sete algoritmos de agrupamento e quatro técnicas de redução de dimensionalidade na base Iris padronizada. Foram realizados 250 ajustes particionais, uma hierarquia UPGMA e uma execução DBSCAN. A melhor inicialização de cada número de grupos foi selecionada pela função objetivo, e o número de grupos pela silhueta. Os seis métodos com seleção de k escolheram dois grupos, com silhueta de 0,5802 e índice de Rand ajustado (ARI) de 0,5681. O DBSCAN encontrou dois grupos e quatro pontos de ruído. Em análise complementar, a mistura gaussiana com três componentes atingiu ARI de 0,9039, evidenciando a diferença entre separação geométrica e concordância com espécies. As duas primeiras componentes da PCA retiveram 95,80% da variância. Kernel PCA, t-SNE e UMAP complementaram a análise visual; t-SNE apresentou a maior preservação local de vizinhanças na configuração avaliada. Os resultados destacam os limites da seleção interna e a necessidade de interpretar projeções em conjunto com métricas.]

#text(size: 9pt, weight: "bold", style: "italic")[Palavras-chave—agrupamento, Iris, silhueta, índice de Rand ajustado, redução de dimensionalidade.]
]
'''
(ROOT/'artigo'/'artigo_ieee.typ').write_text(header+s+'\n]\n')
print('Artigo IEEE e figuras vetoriais gerados.')
