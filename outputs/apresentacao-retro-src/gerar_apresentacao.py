"""Compõe a apresentação a partir dos artefatos existentes, sem refazer ajustes.

Uso, na raiz do projeto: MPLCONFIGDIR=/tmp/mpl-slides .venv/bin/python
outputs/apresentacao-retro-src/gerar_apresentacao.py
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ASSETS = OUT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
R = ROOT / 'resultados'
q1 = json.loads((R / 'execucoes_questao_1.json').read_text())
q2 = json.loads((R / 'execucoes_questao_2.json').read_text())
diagnostics = json.loads((ROOT / 'docs/artigo/diagnosticos_revisao.json').read_text())
metrics = pd.read_csv(R / 'metricas_por_k.csv')
BG, WHITE, YELLOW, GRAY = '#141414', '#F5F5F5', '#FFD400', '#AAAAAA'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 26,
    'text.color': WHITE, 'axes.labelcolor': WHITE, 'axes.edgecolor': GRAY,
    'axes.facecolor': BG, 'figure.facecolor': BG, 'xtick.color': WHITE,
    'ytick.color': WHITE, 'axes.spines.top': False, 'axes.spines.right': False,
    'savefig.facecolor': BG, 'svg.fonttype': 'none', 'axes.titleweight': 'bold'})
fmt = lambda x: f'{x:.4f}'.replace('.', ',')
decimal_formatter = FuncFormatter(lambda value, _: f'{value:g}'.replace('-', '−').replace('.', ','))
def save(fig, name):
    fig.savefig(ASSETS / f'{name}.png', dpi=180)
    fig.savefig(ASSETS / f'{name}.svg')
    plt.close(fig)
def axes_style(ax):
    ax.grid(alpha=.16, axis='y')
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=26)
    ax.yaxis.set_major_formatter(decimal_formatter)

# As seis séries usam as melhores execuções por objetivo já registradas.
fig, ax = plt.subplots(figsize=(16, 4.5))
fig.subplots_adjust(left=.085, bottom=.22, top=.93, right=.69)
names = {'k-means':'K-Means', 'fuzzy-k-means':'FCM',
    'kernel-fuzzy-k-means':'Kernel FCM', 'k-medoids':'K-Medoids',
    'gaussian-mixture':'GMM/EM', 'upgma':'UPGMA'}
for i, (key, name) in enumerate(names.items()):
    d = metrics[(metrics.algoritmo == key) & (metrics.k > 1)]
    ax.plot(d.k, d.silhueta, label=name, lw=2.8, marker=['s','o','^','D','x','v'][i],
        ms=8, color=[YELLOW, WHITE, '#66D9EF', '#E8A4D8', '#A8D88D', '#FFAE70'][i],
        linestyle=['-','--',':','-.','-','--'][i])
ax.set(xticks=[2,3,4,5], xlabel='Número de grupos (k)', ylabel='Silhueta', ylim=(.1,.65))
ax.legend(loc='center left', bbox_to_anchor=(1.02,.5), frameon=False, fontsize=25, labelcolor=WHITE)
axes_style(ax)
save(fig, 'silhuetas')

# Contraste entre critério interno e avaliação externa para o GMM.
gmm = metrics[(metrics.algoritmo == 'gaussian-mixture') & metrics.k.isin([2,3])].sort_values('k')
fig, ax = plt.subplots(figsize=(16,4.5))
fig.subplots_adjust(left=.08, right=.95, top=.92, bottom=.22)
x = np.arange(2)
for j, (k, color) in enumerate([(2,WHITE),(3,YELLOW)]):
    row = gmm[gmm.k == k].iloc[0]
    vals = [row.silhueta, row.ari]
    bars = ax.bar(x + (j-.5)*.3, vals, .28, label=f'k = {k}', color=color)
    for b,v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, v+.025, fmt(v), ha='center', fontsize=27, color=color)
ax.set(xticks=x, xticklabels=['Silhueta', 'ARI'], ylim=(0,1.09), yticks=[0,.5,1])
ax.legend(loc='upper left', frameon=False, ncol=2, labelcolor=WHITE, fontsize=26)
axes_style(ax)
save(fig, 'gmm_comparacao')

# Usa a árvore armazenada, sem recalcular a hierarquia.
stored = q1['upgma']['2']
if isinstance(stored, list):
    stored = stored[0]
Z = np.asarray(stored['hierarquia'])
assert Z.shape == (149,4)
fig, ax = plt.subplots(figsize=(16,4.5))
fig.subplots_adjust(left=.09,right=.98,bottom=.24,top=.93)
dendrogram(Z, truncate_mode='lastp', p=12, leaf_font_size=24,
    color_threshold=0, above_threshold_color=WHITE, ax=ax)
for k, color in [(2, YELLOW), (3, '#66D9EF')]:
    cut = (Z[-k + 1, 2] + Z[-k, 2]) / 2
    ax.axhline(cut, color=color, linestyle='--', lw=2)
    ax.text(118, cut + .07, f'{k} grupos', color=color, ha='right', fontsize=24,
            bbox={'facecolor': BG, 'edgecolor': 'none', 'pad': 2})
ax.set(xlabel='Subárvores finais: contagem entre parênteses', ylabel='Dist. Manhattan')
axes_style(ax)
save(fig, 'dendrograma')

species = [('Iris-setosa', YELLOW, 's'),('Iris-versicolor',WHITE,'o'),('Iris-virginica','#66D9EF','^')]
def scatter(ax, key, title=None):
    data = pd.read_csv(R / f'coordenadas_{key}.csv')
    for sp, color, marker in species:
        d = data[data.especie == sp]
        ax.scatter(d.componente_1, d.componente_2, label=sp.removeprefix('Iris-'),
            s=50, color=color, marker=marker, alpha=.85, linewidths=.5, edgecolors=BG)
    ax.tick_params(labelsize=24)
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    ax.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax.xaxis.set_major_formatter(decimal_formatter)
    ax.yaxis.set_major_formatter(decimal_formatter)
    ax.grid(alpha=.12)
    if title: ax.set_title(title, fontsize=27, pad=12)
    return data

kernel = diagnostics['kernel_pca']
kernel_share = f"{100 * sum(kernel['fractions']):.2f}".replace('.', ',')
for key, note, xl, yl in [
    ('pca', '95,80%\nda variância\n\nPC1: 72,77%\nPC2: 23,03%', 'PC1', 'PC2'),
    ('kernel_pca', f'RBF · gamma = 0,25\n\n{kernel_share}% da variância\nno espaço RBF', 'Comp. 1', 'Comp. 2')]:
    fig, ax = plt.subplots(figsize=(16,4.5))
    fig.subplots_adjust(left=.10,right=.62,bottom=.24,top=.95)
    scatter(ax,key)
    ax.set(xlabel=xl, ylabel=yl)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.66,1.0),
        frameon=False,fontsize=24,labelcolor=WHITE)
    fig.text(.68,.10,note,fontsize=24,color=YELLOW,linespacing=1.2)
    save(fig,key)

fig, axs = plt.subplots(1,2,figsize=(16,4.5))
fig.subplots_adjust(left=.10,right=.985,bottom=.34,top=.82,wspace=.30)
for ax,key,title in zip(axs,['tsne','umap'],['t-SNE | perplexidade 30','UMAP | 15 vizinhos']):
    scatter(ax,key,title)
    ax.set_xlabel('Dim. 1',fontsize=25)
    ax.set_ylabel('Dim. 2',fontsize=25)
handles, labels = axs[0].get_legend_handles_labels()
fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,-.035),ncol=3,
    frameon=False,fontsize=24,labelcolor=WHITE)
save(fig,'tsne_umap')

def cols(title, left, lb, right, rb, refs, notes):
    return {'layout':'TwoColumnSlide','title':title,'columns':[
        {'title':left,'bullets':lb},{'title':right,'bullets':rb}],
        'citations':refs,'notes':notes}
def figure(title, name, caption, refs, notes):
    return {'layout':'figure','title':title,'path':f'assets/{name}.png',
        'alt':caption,'caption':caption,'attribution':'Fonte: artefatos da Equipe 08. Gráfico autoral; dados originais preservados.',
        'citations':refs,'notes':notes}

slides = [
    {'layout':'CoverSlide','title':'Iris: grupos e projeções','duck':False,
     'coverLogo':'assets/logo-branco.png',
     'subtitle':'Agrupamento e redução de dimensionalidade\nFátima Araújo e Rogrigo Gomes · Equipe 08',
     'notes':'Abertura (30 s). O estudo compara sete agrupadores e quatro projeções. Pergunta guia: a separação geométrica coincide com as três espécies? A apresentação sintetiza a revisão de 18/11/2026 e os resultados registrados.'},
    cols('Três espécies; quantos grupos?', 'BASE IRIS',
        ['150 flores; 50 por espécie.','Quatro medidas em centímetros.','Sépalas e pétalas: comprimento e largura.'],
        'PREPARAÇÃO', ['Z-score: z = (x − μ) / σ.','μ e σ populacionais por atributo.','Espécies usadas após o ajuste.'], ['ART','EXP'],
        'Tempo: 1 min. Usou-se codigo/iris/iris.data. Para cada atributo, μ é a média das 150 observações e σ é a raiz da média dos desvios quadráticos em relação a μ. A análise é descritiva da base completa. Os rótulos de espécie servem à avaliação externa e à identificação visual.'),
    cols('Sete métodos, cinco perspectivas','PARTIÇÕES',
        ['K-Means: centroides.','FCM e Kernel FCM: pertinências.','K-Medoids: flores como representantes.'],
        'OUTRAS ESTRUTURAS',['GMM/EM: mistura probabilística.','UPGMA: hierarquia de grupos.','DBSCAN: densidade e ruído.'],['ART'],
        'Tempo: 1 min. K-Means minimiza distâncias quadráticas. FCM e Kernel FCM usam m=2. A variante de Zhang e Chen (2004) usa protótipos no espaço de entrada e RBF com gamma=0,25, igual ao inverso dos quatro atributos. Em k=3, FCM e Kernel FCM coincidiram na partição exclusiva (ARI entre partições = 1). K-Medoids usa PAM e distância euclidiana, com ARI externo de 0,6765 em k=3. GMM usa covariâncias completas. UPGMA usa ligação média com Manhattan. DBSCAN usa distância euclidiana.'),
    {'layout':'DiagramSlide','title':'O protocolo separa ajuste e avaliação',
     'steps':['Padronizar X','10 sementes por k','Selecionar pelo objetivo','Escolher k por silhueta'],
     'takeaway':'5 métodos × 5 valores de k × 10 ajustes + UPGMA + DBSCAN = 252.',
     'mainFlow':[0,1,2], 'citations':['EXP','ART'],
     'notes':'Tempo: 1,5 min. k varia de 1 a 5, sementes de 42 a 51. Há um único ajuste por chamada; K-Means e GMM usam n_init=1. Para cada método e k seleciona-se o menor objetivo, ou a maior log-verossimilhança no GMM. Objetivos não são comparados entre métodos. Fuzzy vira crisp pelo argmax das pertinências; GMM pela maior probabilidade posterior. UPGMA tem uma árvore e cinco cortes, não cinco novos ajustes. Após escolher k pela silhueta, calcula-se ARI com as espécies.'},
    cols('Silhueta e ARI respondem a perguntas distintas','SILHUETA',
        ['Coesão e separação geométrica.','Define k após selecionar o ajuste.','k = 1: valor indefinido.'],
        'ARI',['Concordância com as espécies.','Desconta o acordo ao acaso.','Avaliação externa; não escolhe k.'],['ART','EXP'],
        'Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.'),
    figure('A silhueta favorece dois grupos','silhuetas',
        'Os seis métodos atingem o máximo em k = 2; k = 1 é indefinido.', ['EXP'],
        'Tempo: 1 min. Cada ponto corresponde à melhor execução do método naquele k, escolhida primeiro por sua função objetivo. Todas as séries coincidem em k=2 (0,580184). A subdivisão do bloco versicolor/virginica reduz a silhueta. Valores extraídos diretamente de metricas_por_k.csv.'),
    cols('Seis métodos chegam à mesma partição','ESTRUTURA COMUM',
        ['Grupo A: 50 setosas.','Grupo B: 50 versicolors + 50 virginicas.','Mesmos grupos; identificadores podem mudar.'],
        'RESULTADO EM k = 2',['Silhueta: 0,5802.','ARI: 0,5681.','Separação geométrica difere das três espécies.'],['EXP','ART'],
        'Tempo: 1 min. K-Means, FCM, Kernel FCM, K-Medoids, GMM e UPGMA produzem a mesma partição selecionada, salvo permutações. As contingências confirmam 50/100. Isso explica a igualdade das métricas, sem implicar centros, pertinências ou funções objetivo iguais.'),
    figure('No GMM, três grupos elevam o ARI','gmm_comparacao',
        'O BIC favorece dois grupos (797,6857).', ['EXP','ART','DIAG'],
        'Tempo: 1,5 min. Para k=2, silhueta 0,580184, ARI 0,568116 e BIC 797,6857. Para k=3, silhueta 0,372773, ARI 0,903874 e BIC 804,5072. Em três componentes: 50 setosas, 45 versicolors e 50 virginicas + cinco versicolors. O BIC foi calculado nos cinco modelos selecionados por log-verossimilhança e também favoreceu k=2. Em k=5, uma componente tem peso de 0,0604 e autovalor mínimo da covariância de 0,00000381, compatível com um ajuste muito estreito.'),
    figure('Uma árvore permite vários cortes','dendrograma',
        'A silhueta Manhattan também favorece k = 2 (0,6192).', ['EXP','ART','DIAG'],
        'Tempo: 1 min. UPGMA com ligação média e Manhattan. O dendrograma usa as 12 subárvores finais, com contagens de folhas entre parênteses. As linhas marcam os cortes em dois e três grupos. A avaliação principal usa distância euclidiana. O diagnóstico com Manhattan retorna 0,6192, 0,5024, 0,4084 e 0,3770 para k de 2 a 5. Em k=3, o ARI externo é 0,7184.'),
    cols('DBSCAN encontra dois grupos e ruído','CONFIGURAÇÃO',
        ['eps = 0,8; min_samples = 5.','Dois grupos e quatro ruídos (2,67%).','Ruído: uma setosa e três virginicas.'],
        'MÉTRICAS E SENSIBILIDADE',['Silhueta: 0,5963 em 146 flores.','ARI: 0,5518 em 150 flores.','eps 0,8 e 0,9 excluem 4 flores.'],['EXP','ART','DIAG'],
        'Tempo: 1 min. Os grupos têm 49 setosas e 97 flores (50 versicolors + 47 virginicas). O próprio ponto conta em min_samples. O ARI inclui o rótulo −1 do ruído. Com min_samples=5, os cinco raios de 0,6 a 1,0 produziram dois grupos, com 26, 8, 4, 4 e 3 pontos de ruído. A silhueta de 0,6405 em eps=0,6 usa apenas 124 flores. Os raios 0,8 e 0,9 produziram as mesmas contagens e silhueta, um patamar observado após a escolha inicial.'),
    figure('PCA retém 95,80% em dois eixos','pca',
        'Setosa se separa; versicolor e virginica mantêm uma região de sobreposição.', ['EXP','ART'],
        'Tempo: 1,5 min. A PCA foi ajustada com quatro componentes e SVD completa. Valores singulares: 20,8955, 11,7551, 4,7014 e 1,7582. A média de entrada é numericamente próxima de zero após o z-score. PC1 explica 72,7705% e PC2 23,0305%. Os maiores loadings da PC1 estão em comprimento e largura de pétala (0,9950 e 0,9682). PC2 enfatiza largura de sépala (0,8913). As cores e os símbolos indicam as espécies conhecidas.'),
    figure('Kernel PCA muda a geometria','kernel_pca',
        'A fração retida se refere ao espectro do kernel centralizado.', ['EXP','ART','DIAG'],
        'Tempo: 1 min. Usa-se RBF com gamma=0,25, duas componentes e solver denso. Os autovalores 39,1321 e 17,7924 representam 39,8394% e 18,1140% do traço completo (98,2247). O percentual acumulado descreve a variância no espaço de características do RBF. Gamma foi fixado antes do ajuste. As cores e os símbolos indicam espécies.'),
    figure('t-SNE e UMAP enfatizam vizinhanças','tsne_umap',
        'Setosa permanece isolada; a posição entre ilhas não mede distância original.', ['EXP','ART'],
        'Tempo: 1,5 min. t-SNE: perplexidade 30, inicialização PCA, semente 42, máximo de 1.000 iterações, KL final 0,1642 e taxa efetiva 50. O atributo n_iter_ registrou 999. UMAP: 15 vizinhos, min_dist=0,1, spread=1, inicialização espectral, semente 42 e uma thread. A saída 150 × 2 variou de −5,8964 a 10,1182 no eixo 1 e de 2,2188 a 9,0128 no eixo 2. A curva de similaridade usa a=1,5769 e b=0,8951. Cada técnica teve uma execução, com eixos sem unidade física.'),
    {'layout':'ResultsSlide','title':'t-SNE preservou mais vizinhos locais',
     'labels':['PCA','Kernel PCA','t-SNE','UMAP'],
     'values':[round(q2[k]['trustworthiness_10'],4) for k in ['pca','kernel_pca','tsne','umap']],
     'unit':'Trustworthiness · 10 vizinhos',
     'caption':'Diagnóstico desta configuração; não é acurácia nem avaliação global.',
     'highlightIndex':2,'citations':['EXP','ART'],
     'notes':'Tempo: 1 min. Trustworthiness penaliza vizinhos artificiais introduzidos pela projeção comparando o espaço padronizado 4D com o 2D, usando dez vizinhos e distância euclidiana. PCA=0,978156, Kernel PCA=0,932238, t-SNE=0,988813 e UMAP=0,978349. PCA e UMAP são muito próximos neste índice. Os valores não demonstram superioridade universal nem estabilidade entre sementes. O gráfico tem origem zero e valores numéricos explícitos.'},
    cols('O alcance das conclusões é descritivo','O QUE SUSTENTA',
        ['Mesma base e mesma padronização.','Dez sementes por método e k.','Parâmetros e resultados registrados.'],
        'O QUE LIMITA',['Uma execução por projeção.','Uma base e uma padronização.','Testes de sensibilidade: eps e inicializações.'],['ART','EXP','DIAG'],
        'Tempo: 1 min. Como diagnóstico separado, o K-Means com k=3, semente 42 e 100 inicializações obteve objetivo 140,9658, ARI 0,6201 e silhueta 0,4590. O melhor objetivo do protocolo principal foi 140,9684, uma redução de 0,0018%. O diagnóstico complementa as dez sementes originais e a varredura de eps. Gamma, perplexidade e número de vizinhos ficaram fixos. As métricas de agrupamento são do espaço padronizado de quatro atributos.'),
    {'layout':'ConclusionSlide','title':'Grupos geométricos diferem de espécies',
     'windowTitle':'CONCLUSÕES',
     'bullets':['A silhueta selecionou dois grupos nos seis métodos.',
        'GMM em k = 3 recuperou melhor as espécies pelo ARI.',
        'PCA explica a variância; t-SNE destaca a vizinhança local.',
        'Interprete métrica, projeção e objetivo em conjunto.'],
     'citations':['ART','EXP'],
     'notes':'Fechamento (45 s). Responder à pergunta inicial: a geometria favoreceu setosa versus demais, enquanto a referência botânica tem três espécies. Essa diferença explica o contraste silhueta/ARI. Projeções complementam a leitura, preservando aspectos diferentes da estrutura. Abrir para perguntas.'},
    {'layout':'ReferencesSlide','title':'Fontes e rastreabilidade','ids':['ART','EXP','DIAG'],
     'notes':'Material de apoio. ART: artigo revisado em 18/11/2026 e bibliografia. EXP: arquivos da Questão 1 e da Questão 2 em resultados/. DIAG: diagnósticos complementares da revisão.'}
]
spec = {'title':'Iris: agrupamento e redução de dimensionalidade',
    'plan':{'objective':'Apresentar protocolo, resultados e limites da comparação na Iris.',
    'audience':'Turma do CIn/UFPE · 2026.2', 'minutes':18,'slideCount':len(slides),
    'depth':'intermediária','language':'pt-BR','profile':'retroui-pixel',
    'narrative':'Pergunta → métodos → protocolo → evidências → projeções → limites → conclusão.',
    'assumptions':['Tema retro solicitado: retroui-pixel, 16:9, pt-BR.',
        'Assumiu-se que a apresentação é sobre o projeto local e o artigo revisado mais recente.',
        '17 slides, cerca de 18 minutos; notas de apresentação incluídas.',
        'Artefatos existentes são a evidência; nenhum ajuste foi reexecutado.',
        'Fontes Pixelify Sans e JetBrains Mono podem usar Liberation Mono como fallback.',
        'Texto, diagramas e barras permanecem editáveis; figuras são imagens com SVG-fonte adicional.'],
    'analysis':{'centralTheme':'Separação geométrica e classes biológicas respondem a critérios diferentes.',
        'concepts':['Silhueta interna','ARI externo','Seleção por função objetivo','Padronização','Projeções 2D'],
        'arguments':['k deve ser selecionado após a melhor execução por objetivo.',
            'Silhueta maior não implica maior ARI.','A projeção não é prova de novas classes.'],
        'results':['252 ajustes nos registros.','Seis métodos selecionam k=2, Sil=0,5802 e ARI=0,5681.',
            'GMM em k=3 atinge ARI=0,9039; o BIC é mínimo em k=2.',
            'O DBSCAN obteve dois grupos nos cinco raios testados; a silhueta Manhattan do UPGMA favoreceu k=2.',
            'PCA 2D retém 95,80%; Kernel PCA retém 57,95% no espaço RBF; t-SNE tem trustworthiness=0,9888.'],
        'visualOpportunities':['Fluxo de seleção','Curvas por k','Contraste GMM','Árvore armazenada',
            'Quatro projeções com cores e símbolos','Barras de preservação local']},
    'sources':[{'path':'docs/artigo/artigo_ieee_revisado.pdf','author':'Equipe 08',
        'consulted':True,'sections':'Texto extraído; fonte Typst integral; seções de métodos, resultados e discussão.'},
        {'path':'resultados/','consulted':True,'sections':'Métricas Q1, metadados, contingências, árvore e coordenadas Q2.'},
        {'path':'docs/artigo/diagnosticos_revisao.json','consulted':True,'sections':'DBSCAN, K-Means, UPGMA, espectro RBF e modelos GMM.'}],
    'limitations':['Referências teóricas consultadas por meio do artigo local; sem nova revisão externa.',
        'Revisão da apresentação verifica fidelidade aos registros; não substitui auditoria dos experimentos.']},
    'visual':{'grid':True,'gridOpacity':.28,'gridSpacing':.4,'logoInFooter':True},
    'slides':slides,'references':[
        {'id':'ART','text':'Fátima Araújo e Rogrigo Gomes. Agrupamento e redução de dimensionalidade na base Iris. Revisão de 18/11/2026, UFPE.',
         'url':'file:docs/artigo/artigo_ieee_revisado.pdf'},
        {'id':'EXP','text':'Equipe 08. Questões 1 e 2: métricas, partições, hierarquia, parâmetros e coordenadas. Registros do projeto, 2026.',
         'url':'file:resultados/'},
        {'id':'DIAG','text':'Equipe 08. Diagnósticos complementares de agrupamento e projeção, 18/11/2026.',
         'url':'file:docs/artigo/diagnosticos_revisao.json'}]}
(OUT / 'deck.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
print(f'Gerado: {OUT / "deck.json"} ({len(slides)} slides)')
