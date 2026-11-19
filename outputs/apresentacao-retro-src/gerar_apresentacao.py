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
perfis = pd.read_csv(R / 'tunagem/particionais.csv')
agrupamento = diagnostics['agrupamento']
dbscan = agrupamento['dbscan']
mesma_amostra = agrupamento['mesma_amostra']
contagens = agrupamento['contagens']
particao_comum = agrupamento['particao_comum'] and agrupamento['estrutura_setosa']
empate_amostra = agrupamento['amostra_igual']
perfil_final = agrupamento['resumo']
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

# Faixas por configuração em k=3. Os pontos marcam o perfil selecionado.
fig, axs = plt.subplots(1, 2, figsize=(16, 4.5), sharey=True)
fig.subplots_adjust(left=.15, bottom=.19, top=.84, right=.97, wspace=.12)
k3 = perfis[perfis.k == 3]
rotulos = [names[key] for key in list(names)[:-1]]
for ax, coluna, titulo in zip(axs, ['silhueta', 'ari'], ['Silhueta', 'ARI']):
    for i, key in enumerate(list(names)[:-1]):
        valores = k3[k3.algoritmo == key][coluna].dropna()
        selecionado = metrics[(metrics.algoritmo == key) & (metrics.k == 3)].iloc[0][coluna]
        ax.hlines(i, valores.min(), valores.max(), colors=WHITE, lw=4)
        ax.scatter(selecionado, i, s=112, color=YELLOW, zorder=3)
    ax.set(yticks=range(len(rotulos)), yticklabels=rotulos, title=titulo,
           ylim=(len(rotulos) - .5, -.5))
    ax.tick_params(labelsize=24)
    ax.xaxis.set_major_formatter(decimal_formatter)
    ax.grid(alpha=.14, axis='x')
save(fig, 'sensibilidade')

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
gmm_k2, gmm_k3 = gmm.itertuples(index=False)

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

particao_nota = (
    'Os seis métodos selecionaram a mesma partição em k=2. Um grupo reúne as '
    '50 setosas. O outro contém 50 versicolors e 50 virginicas. '
    f'Silhueta {perfil_final[0][3]} e ARI {perfil_final[0][4]} em 150 flores.'
    if particao_comum else 'Os perfis selecionados podem produzir partições distintas. '
    'A tabela comparativa do artigo reúne as métricas de cada método.'
)
sensibilidade_notas = ' '.join(
    f'{nome}: extremos {minimo} e {maximo}; ARI {faixa}.'
    for nome, minimo, maximo, faixa in agrupamento['sensibilidade_k3']
)
amostra_nota = (
    f"As sete partições coincidem nas {dbscan['n']} flores retidas, com silhueta "
    f"{dbscan['silhueta']} e ARI {dbscan['ari']}."
    if empate_amostra else 'Na amostra comum, ver silhuetas, ARIs e concordância entre '
    'as partições na tabela do artigo.'
)
perfil_notas = '. '.join(f'{nome}: {params}, k={k}'
                        for nome, params, k, *_ in perfil_final)
extremo_dbscan = dbscan['tabela'][2]
slides = [
    {'layout':'CoverSlide','title':'Iris: grupos e projeções','duck':False,
     'coverLogo':'assets/logo-branco.png',
     'subtitle':'Agrupamento e redução de dimensionalidade\nFátima Araújo e Rogrigo Gomes · Equipe 08',
     'notes':'Abertura (30 s). A separação geométrica coincide com as três espécies? O estudo compara sete agrupadores, incluindo sensibilidade aos hiperparâmetros, e quatro projeções.'},
    cols('Três espécies; quantos grupos?', 'BASE IRIS',
        ['150 flores; 50 por espécie.','Quatro medidas em centímetros.','Sépalas e pétalas: comprimento e largura.'],
        'PREPARAÇÃO', ['Z-score: z = (x − μ) / σ.','μ e σ populacionais por atributo.','Espécies usadas após o ajuste.'], ['ART','EXP'],
        'Tempo: 1 min. Usou-se codigo/iris/iris.data. Para cada atributo, μ é a média das 150 observações e σ é a raiz da média dos desvios quadráticos em relação a μ. A análise é descritiva da base completa. Os rótulos de espécie servem à avaliação externa e à identificação visual.'),
    cols('Sete métodos, cinco perspectivas','PARTIÇÕES',
        ['K-Means: centroides.','FCM e Kernel FCM: pertinências.','K-Medoids: flores como representantes.'],
        'OUTRAS ESTRUTURAS',['GMM/EM: mistura probabilística.','UPGMA: hierarquia de grupos.','DBSCAN: densidade e ruído.'],['ART'],
        f'Tempo: 1 min. O Kernel FCM usa protótipos no espaço de entrada e kernel RBF. K-Medoids usa PAM e Euclidiana. UPGMA usa ligação média com Manhattan. Perfis selecionados: {perfil_notas}.'),
    {'layout':'DiagramSlide','title':'O protocolo separa ajuste e avaliação',
     'steps':['Padronizar X','10 sementes por perfil e k','Selecionar pelo objetivo','Escolher pela silhueta'],
     'takeaway':f"{contagens['ajustes_totais']} ajustes ao todo · 252 registros no protocolo final.",
     'mainFlow':[0,1,2], 'citations':['EXP','ART'],
     'notes':f"Tempo: 1,5 min. A grade inclui {contagens['ajustes_particionais']} ajustes nos métodos particionais em k de 2 a 5 e {contagens['ajustes_dbscan']} candidatos no DBSCAN. Em cada perfil e k, escolhe-se a melhor execução pela função objetivo. Silhueta seleciona perfil e k, com desempate por menor k e ordem da grade. Os perfis escolhidos acrescentam dez execuções em k=1. UPGMA usa cinco cortes da mesma árvore. O DBSCAN escolhe a maior silhueta válida com pelo menos {contagens['cobertura_minima_dbscan_pct']}% de cobertura. O ARI é calculado depois das escolhas."},
    cols('Silhueta e ARI respondem a perguntas distintas','SILHUETA',
        ['Coesão e separação geométrica.','Define k após selecionar o ajuste.','k = 1: valor indefinido.'],
        'ARI',['Concordância com as espécies.','Desconta o acordo ao acaso.','Avaliação externa; não escolhe k.'],['ART','EXP'],
        'Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.'),
    figure('A silhueta favorece dois grupos' if particao_comum else 'Silhueta dos perfis selecionados','silhuetas',
        (f'Seis métodos em k = 2. Silhueta {perfil_final[0][3]} e ARI {perfil_final[0][4]}.'
         if particao_comum else 'Curvas por número de grupos. Em k = 1, a silhueta é indefinida.'), ['EXP'],
        'Tempo: 1 min. Cada ponto usa a execução de melhor objetivo no perfil escolhido e no respectivo k. ' + particao_nota),
    figure('Hiperparâmetros afetam as métricas','sensibilidade',
        'Faixas entre perfis em k = 3. O ponto marca o perfil escolhido pela busca.', ['EXP','ART'],
        'Tempo: 1,5 min. Cada extremo usa a melhor execução por objetivo da sua configuração. ' + sensibilidade_notas),
    figure('GMM em dois e três componentes','gmm_comparacao',
        'Silhueta mede a geometria dos grupos. ARI mede concordância com espécies.', ['EXP','ART'],
        f'Tempo: 1,5 min. Em k=2, silhueta {fmt(gmm_k2.silhueta)} e ARI {fmt(gmm_k2.ari)}. Em k=3, silhueta {fmt(gmm_k3.silhueta)} e ARI {fmt(gmm_k3.ari)}. Comparamos o mesmo perfil em k distintos. A silhueta orientou a escolha; o ARI descreve a concordância com as espécies.'),
    figure('Uma árvore permite vários cortes','dendrograma',
        'A silhueta Manhattan também favorece k = 2 (0,6192).', ['EXP','ART','DIAG'],
        'Tempo: 1 min. UPGMA com ligação média e Manhattan. O dendrograma usa as 12 subárvores finais, com contagens de folhas entre parênteses. As linhas marcam os cortes em dois e três grupos. A avaliação principal usa distância euclidiana. O diagnóstico com Manhattan retorna 0,6192, 0,5024, 0,4084 e 0,3770 para k de 2 a 5. Em k=3, o ARI externo é 0,7184.'),
    cols('DBSCAN avalia os pontos retidos','CONFIGURAÇÃO',
        [f"ε = {dbscan['eps']} · mínimo = {dbscan['min_samples']}.",
         f"{dbscan['grupos']} grupos e {dbscan['ruido']} pontos de ruído.",
         f"{dbscan['n']} flores retidas · {dbscan['cobertura']}% da base."],
        'MÉTRICAS SEM RUÍDO',[f"Silhueta {dbscan['silhueta']} · ARI {dbscan['ari']}.",
        (f"Mesma partição dos outros seis em {dbscan['n']} flores." if empate_amostra
         else f"Comparação restrita às mesmas {dbscan['n']} flores.")],['EXP','ART'],
        f'Tempo: 1 min. Excluir os rótulos −1 do DBSCAN reduz a amostra de ambas as métricas. '
        f'O mínimo de {dbscan["min_samples"]} inclui o próprio ponto. A maior silhueta da grade foi {extremo_dbscan[5]} com cobertura de {extremo_dbscan[4]}%. ' + amostra_nota),
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
        ['Mesma base e mesma padronização.','Dez sementes por perfil e k.','Sensibilidade documentada nas grades.'],
        'O QUE LIMITA',['Uma execução por projeção.','Uma única base de dados.','Cobertura afeta os índices do DBSCAN.'],['ART','EXP'],
        'Tempo: 1 min. As sementes variam a inicialização com as mesmas observações. As configurações vencedoras dependem da grade e, para DBSCAN, do mínimo de cobertura. Na Questão 2, cada projeção usa uma configuração. As métricas de agrupamento são calculadas no espaço padronizado de quatro atributos.'),
    {'layout':'ConclusionSlide','title':'Grupos geométricos diferem de espécies',
     'windowTitle':'CONCLUSÕES',
     'bullets':['A silhueta orientou a escolha dos perfis e de k.',
        f"Entre os perfis escolhidos, {agrupamento['maior_ari_k3']['nome']} obteve ARI {agrupamento['maior_ari_k3']['ari']} em k = 3.",
        'PCA explica a variância; t-SNE destaca a vizinhança local.',
        'Interprete métrica, projeção e objetivo em conjunto.'],
     'citations':['ART','EXP'],
     'notes':'Fechamento (45 s). ' + particao_nota + ' ' + amostra_nota + ' Retomar a comparação com as três espécies e o papel das projeções.'},
    {'layout':'ReferencesSlide','title':'Fontes e rastreabilidade','ids':['ART','EXP','DIAG'],
     'notes':'Material de apoio. ART corresponde ao artigo e à bibliografia. EXP corresponde às grades, métricas e projeções em resultados/. DIAG corresponde às tabelas e aos diagnósticos produzidos para o artigo.'}
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
        'results':[f"{contagens['ajustes_totais']} ajustes e 252 registros no protocolo final.",particao_nota,
            f'O perfil escolhido de GMM atinge ARI {fmt(gmm_k3.ari)} em k=3.', amostra_nota,
            'PCA 2D retém 95,80%; Kernel PCA retém 57,95% no espaço RBF; t-SNE tem trustworthiness=0,9888.'],
        'visualOpportunities':['Fluxo de seleção','Curvas por k','Faixas de sensibilidade', 'Contraste GMM','Árvore armazenada',
            'Quatro projeções com cores e símbolos','Barras de preservação local']},
    'sources':[{'path':'docs/artigo/artigo_ieee_revisado.pdf','author':'Equipe 08',
        'consulted':True,'sections':'Texto extraído; fonte Typst integral; seções de métodos, resultados e discussão.'},
        {'path':'resultados/','consulted':True,'sections':'Métricas Q1, metadados, contingências, árvore e coordenadas Q2.'},
        {'path':'docs/artigo/diagnosticos_revisao.json','consulted':True,'sections':'Resultados, sensibilidade, amostra comum, UPGMA e espectro RBF.'}],
    'limitations':['Referências teóricas consultadas por meio do artigo local; sem nova revisão externa.',
        'Revisão da apresentação verifica fidelidade aos registros; não substitui auditoria dos experimentos.']},
    'visual':{'grid':True,'gridOpacity':.28,'gridSpacing':.4,'logoInFooter':True},
    'slides':slides,'references':[
        {'id':'ART','text':'Fátima Araújo e Rogrigo Gomes. Agrupamento e redução de dimensionalidade na base Iris. UFPE, 2026.',
         'url':'file:docs/artigo/artigo_ieee_revisado.pdf'},
        {'id':'EXP','text':'Equipe 08. Questões 1 e 2: métricas, partições, hierarquia, parâmetros e coordenadas. Registros do projeto, 2026.',
         'url':'file:resultados/'},
        {'id':'DIAG','text':'Equipe 08. Diagnósticos de agrupamento, sensibilidade e projeção, 2026.',
         'url':'file:docs/artigo/diagnosticos_revisao.json'}]}
(OUT / 'deck.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
print(f'Gerado: {OUT / "deck.json"} ({len(slides)} slides)')
