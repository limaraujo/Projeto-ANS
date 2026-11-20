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
dbscan_grid = pd.read_csv(R / 'tunagem/dbscan.csv')
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

# Tunagem dos métodos com escolhas diretamente comparáveis por curvas.
fig, axs = plt.subplots(1, 3, figsize=(16, 4.5), sharex=True, sharey=True)
fig.subplots_adjust(left=.065, bottom=.22, top=.82, right=.985, wspace=.18)
panels = [
    ('k-means', 'K-Means', 'init'),
    ('fuzzy-k-means', 'FCM', 'm'),
    ('k-medoids', 'K-Medoids', 'init')
]
for ax, (key, title, field) in zip(axs, panels):
    data = perfis[perfis.algoritmo == key]
    for j, (value, group) in enumerate(data.groupby(field, dropna=False)):
        selected = bool(group.configuracao_selecionada.iloc[0])
        if field == 'm':
            label = f'm = {str(value).replace(".", ",")}'
        else:
            label = str(value)
        ax.plot(group.k, group.silhueta, marker=['s','o','^'][j % 3], ms=7,
                lw=3 if selected else 2, color=YELLOW if selected else [WHITE, '#66D9EF', '#E8A4D8'][j % 3],
                linestyle='-' if selected else '--', label=label)
    ax.set_title(title, fontsize=25)
    ax.set(xticks=[2,3,4,5], ylim=(.30,.61))
    ax.grid(alpha=.14)
    ax.legend(frameon=False, fontsize=18, labelcolor=WHITE, loc='lower left')
    ax.xaxis.set_major_formatter(decimal_formatter)
    ax.yaxis.set_major_formatter(decimal_formatter)
axs[0].set_ylabel('Silhueta')
fig.supxlabel('Número de grupos (k)', y=.04, fontsize=22)
save(fig, 'tunagem_particionais')

# Tunagem de Kernel FCM, GMM e DBSCAN: mapas compactos e compromisso com cobertura.
fig, axs = plt.subplots(1, 3, figsize=(16, 4.5))
fig.subplots_adjust(left=.065, bottom=.22, top=.80, right=.985, wspace=.30)

kernel_grid = (perfis[perfis.algoritmo == 'kernel-fuzzy-k-means']
               .drop_duplicates(['m','gamma'])
               .pivot(index='m', columns='gamma', values='silhueta_media')
               .sort_index(ascending=False).sort_index(axis=1))
im = axs[0].imshow(kernel_grid.values, cmap='viridis', vmin=.17, vmax=.46, aspect='auto')
axs[0].set(title='Kernel FCM', xlabel='gamma', ylabel='m',
           xticks=range(len(kernel_grid.columns)),
           xticklabels=[str(x).replace('.', ',') for x in kernel_grid.columns],
           yticks=range(len(kernel_grid.index)),
           yticklabels=[str(x).replace('.', ',') for x in kernel_grid.index])
for i in range(kernel_grid.shape[0]):
    for j in range(kernel_grid.shape[1]):
        axs[0].text(j, i, f'{kernel_grid.iloc[i,j]:.3f}'.replace('.', ','),
                    ha='center', va='center', fontsize=16, color=WHITE)
sel_kernel = perfis[(perfis.algoritmo == 'kernel-fuzzy-k-means') & perfis.configuracao_selecionada].iloc[0]
ki = list(kernel_grid.index).index(sel_kernel['m'])
kj = list(kernel_grid.columns).index(sel_kernel['gamma'])
axs[0].add_patch(plt.Rectangle((kj-.48,ki-.48),.96,.96,fill=False,edgecolor=YELLOW,lw=3))

gmm_grid = (perfis[perfis.algoritmo == 'gaussian-mixture']
            .drop_duplicates(['covariance_type','reg_covar'])
            .pivot(index='covariance_type', columns='reg_covar', values='silhueta_media')
            .reindex(['full','tied','diag','spherical']).sort_index(axis=1))
axs[1].imshow(gmm_grid.values, cmap='viridis', vmin=.17, vmax=.46, aspect='auto')
axs[1].set(title='GMM/EM', xlabel='regularização',
           xticks=range(len(gmm_grid.columns)),
           xticklabels=['10⁻⁶','10⁻⁴','10⁻²'],
           yticks=range(len(gmm_grid.index)), yticklabels=gmm_grid.index)
for i in range(gmm_grid.shape[0]):
    for j in range(gmm_grid.shape[1]):
        axs[1].text(j, i, f'{gmm_grid.iloc[i,j]:.3f}'.replace('.', ','),
                    ha='center', va='center', fontsize=15, color=WHITE)
sel_gmm = perfis[(perfis.algoritmo == 'gaussian-mixture') & perfis.configuracao_selecionada].iloc[0]
gi = list(gmm_grid.index).index(sel_gmm['covariance_type'])
gj = list(gmm_grid.columns).index(sel_gmm['reg_covar'])
axs[1].add_patch(plt.Rectangle((gj-.48,gi-.48),.96,.96,fill=False,edgecolor=YELLOW,lw=3))

for minimum, marker in [(3,'o'),(5,'s'),(10,'^')]:
    d = dbscan_grid[(dbscan_grid.min_samples == minimum) & dbscan_grid.silhueta.notna()]
    axs[2].scatter(d.cobertura_pct, d.silhueta, s=58, marker=marker,
                   label=f'min = {minimum}', alpha=.85)
chosen = dbscan_grid[dbscan_grid.selecionado].iloc[0]
axs[2].scatter(chosen.cobertura_pct, chosen.silhueta, s=155, facecolors='none',
               edgecolors=YELLOW, linewidths=3, zorder=5)
axs[2].axvline(95, color=YELLOW, lw=2, ls='--')
axs[2].set(title='DBSCAN', xlabel='Cobertura (%)', ylabel='Silhueta',
           xlim=(10,101), ylim=(.12,.68))
axs[2].grid(alpha=.14)
axs[2].legend(frameon=False, fontsize=16, labelcolor=WHITE, loc='lower left')
for ax in axs:
    ax.tick_params(labelsize=17)
save(fig, 'tunagem_complexos')

# GMM: compara o perfil selecionado ao perfil full de maior ARI na tunagem.
fig, ax = plt.subplots(figsize=(16, 4.5))
fig.subplots_adjust(left=.11, bottom=.27, top=.90, right=.97)
labels = ['Esférica selecionada\nreg = 10⁻²', 'Completa na tunagem\nreg = 10⁻²']
sil = [0.4568295013461273, 0.3684745512544146]
ari = [0.6199243317810601, 0.9222414299226981]
x = np.arange(2)
for offset, values, label, color in [(-.18, sil, 'Silhueta', WHITE), (.18, ari, 'ARI', YELLOW)]:
    bars = ax.bar(x + offset, values, .32, label=label, color=color)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x()+bar.get_width()/2, value+.025, fmt(value),
                ha='center', fontsize=23, color=color)
ax.set(xticks=x, xticklabels=labels, ylim=(0,1.08), yticks=[0,.25,.5,.75,1])
ax.yaxis.set_major_formatter(decimal_formatter)
ax.grid(alpha=.14, axis='y')
ax.legend(frameon=False, fontsize=23, labelcolor=WHITE, ncol=2, loc='upper left')
save(fig, 'gmm_tunagem')

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
     'subtitle':'Busca de hiperparâmetros e avaliação comparativa\nFátima Araújo e Rodrigo Gomes · Equipe 08',
     'notes':'Abertura (30 s). A separação geométrica coincide com as três espécies? O estudo compara sete agrupadores, incluindo sensibilidade aos hiperparâmetros, e quatro projeções.'},
    cols('Três espécies; quantos grupos?', 'BASE IRIS',
        ['150 flores; 50 por espécie.','Quatro medidas em centímetros.','Arquivo Iris da UCI explicitado.'],
        'PREPARAÇÃO', ['Z-score: z = (x − μ) / σ.','μ e σ populacionais por atributo.','Rótulos usados somente depois.'], ['ART','EXP'],
        'Tempo: 1 min. Usou-se codigo/iris/iris.data, correspondente à edição da UCI. As linhas 35 e 38 diferem de load_iris do scikit-learn; por isso a origem do arquivo precisa ser explicitada. Para cada atributo, μ é a média das 150 observações e σ é o desvio-padrão populacional. Os rótulos de espécie não entram no ajuste nem na seleção.'),
    cols('Sete métodos, cinco perspectivas','PARTIÇÕES',
        ['K-Means: centroides.','FCM e Kernel FCM: pertinências.','K-Medoids: flores como representantes.'],
        'OUTRAS ESTRUTURAS',['GMM/EM: mistura probabilística.','UPGMA: hierarquia de grupos.','DBSCAN: densidade e ruído.'],['ART'],
        f'Tempo: 1 min. O Kernel FCM usa protótipos no espaço de entrada e kernel RBF. K-Medoids usa PAM e Euclidiana. UPGMA usa ligação média com Manhattan. Perfis selecionados: {perfil_notas}.'),
    {'layout':'DiagramSlide','title':'Tunagem e rodada final são separadas',
     'steps':['TUNAGEM\n1.120 part.\n+ 24 DBSCAN',
              '42–51\nperfil pela\nmédia S₂…₅',
              'FINAL\n250 part.\n+ árvore + DBSCAN',
              '52–61\nobjetivo →\nk por silhueta'],
     'takeaway':"1.144 na tunagem + 252 na rodada final = 1.396 ajustes.",
     'mainFlow':[0,1,2], 'citations':['EXP','ART'],
     'notes':f"Tempo: 1,5 min. A tunagem inclui {contagens['ajustes_particionais']} ajustes particionais em k de 2 a 5 e {contagens['ajustes_dbscan']} candidatos do DBSCAN: 1.144 ajustes. Em cada configuração e k, a melhor execução é escolhida pela função objetivo. O perfil fixado maximiza a média das quatro silhuetas, sem escolher k nessa etapa. A rodada final usa novas sementes, 52 a 61, nos cinco valores de k. Só então k é escolhido pela silhueta. UPGMA usa uma árvore; DBSCAN, a configuração elegível com pelo menos {contagens['cobertura_minima_dbscan_pct']}% de cobertura. O ARI não orienta nenhuma escolha."},
    cols('Silhueta e ARI respondem a perguntas distintas','SILHUETA',
        ['Coesão e separação geométrica.','Define k após selecionar o ajuste.','k = 1: valor indefinido.'],
        'ARI',['Concordância com as espécies.','Desconta o acordo ao acaso.','Avaliação externa; não escolhe k.'],['ART','EXP'],
        'Tempo: 1 min. Silhueta s(i)=(b(i)−a(i))/max(a(i),b(i)): a é distância média ao próprio grupo; b é a menor distância média a outro grupo. Usa-se distância euclidiana para todos, inclusive para avaliar a árvore Manhattan. ARI=1 indica partições equivalentes; próximo de zero, acordo esperado ao acaso; pode ser negativo. ARI não é percentual de acerto.'),
    figure('Rodada final: silhueta favorece k = 2' if particao_comum else 'Silhueta dos perfis selecionados','silhuetas',
        (f'Seis métodos em k = 2. Silhueta {perfil_final[0][3]} e ARI {perfil_final[0][4]}.'
         if particao_comum else 'Curvas por número de grupos. Em k = 1, a silhueta é indefinida.'), ['EXP'],
        'Tempo: 1 min. Cada ponto usa a execução de melhor objetivo no perfil escolhido e no respectivo k. ' + particao_nota),
    figure('Tunagem: inicialização e difusividade','tunagem_particionais',
        'Perfis em amarelo foram escolhidos pela média das silhuetas em k = 2…5.', ['EXP','ART'],
        'Tempo: 1,5 min. K-Means comparou random e k-means++; a diferença média foi pequena e k-means++ foi selecionado. No FCM, m = 2 venceu a média; m controla a difusividade das pertinências. No K-Medoids, a inicialização build foi superior à random na média. Cada ponto representa a melhor das dez execuções pela função objetivo, usando sementes 42–51.'),
    figure('Kernel, GMM e DBSCAN na tunagem','tunagem_complexos',
        'Contorno amarelo: perfil escolhido; no DBSCAN, a linha marca 95% de cobertura.', ['EXP','ART'],
        'Tempo: 2 min. Kernel FCM avaliou nove pares de m e gamma; m = 2 e gamma = 0,05 maximizou a silhueta média. O GMM cruzou quatro estruturas de covariância com três regularizações; venceu spherical com regularização 0,01. O DBSCAN avaliou 24 pares de epsilon e min_samples. O círculo amarelo identifica epsilon = 0,6943 e min_samples = 3; pontos à esquerda de 95% eram inelegíveis, mesmo com silhueta maior.'),
    figure('GMM: critério interno não maximiza ARI','gmm_tunagem',
        'k = 3: o perfil esférico foi selecionado; o perfil full teve maior ARI apenas na tunagem.', ['EXP','ART'],
        'Tempo: 1,5 min. O perfil selecionado pela silhueta média foi spherical com regularização 0,01. Em k=3, ele obteve silhueta 0,4568 e ARI 0,6199. Na tunagem, full com a mesma regularização obteve silhueta menor, 0,3685, e ARI maior, 0,9222. Não são duas execuções do mesmo perfil. O ARI não participou da seleção; por isso a alternativa full não definiu o experimento final.'),
    figure('UPGMA: ARI 0,7184 no corte k = 3','dendrograma',
        'A árvore usa Manhattan; em k = 3, ARI = 0,7184 e silhueta = 0,4517.', ['EXP','ART','DIAG'],
        'Tempo: 1 min. O UPGMA usa ligação média e distância Manhattan para construir uma única árvore. O dendrograma mostra as 12 subárvores finais; as linhas marcam cortes em dois e três grupos. A silhueta oficial, calculada com Euclidiana no espaço padronizado, é 0,5802 em k=2 e 0,4517 em k=3. Neste segundo corte, o ARI é 0,7184.'),
    cols('DBSCAN avalia os pontos retidos','CONFIGURAÇÃO',
        [f"ε = {dbscan['eps']} · mínimo = {dbscan['min_samples']}.",
         f"{dbscan['grupos']} grupos e {dbscan['ruido']} pontos de ruído.",
         f"{dbscan['n']} flores retidas · {dbscan['cobertura']}% da base."],
        'SILHUETA × COBERTURA',[f"Escolhida: S = {dbscan['silhueta']} · ARI = {dbscan['ari']}.",
         f"Maior S da grade: {extremo_dbscan[5]}.",
         f"Mas cobria só {extremo_dbscan[4]}% da base."],['EXP','ART'],
        f'Tempo: 1 min. Excluir os rótulos −1 do DBSCAN reduz a amostra de ambas as métricas. '
        f'O mínimo de {dbscan["min_samples"]} inclui o próprio ponto. A maior silhueta da grade foi {extremo_dbscan[5]} com cobertura de {extremo_dbscan[4]}%. ' + amostra_nota),
    figure('PCA retém 95,80% em dois eixos','pca',
        'Setosa se separa; versicolor e virginica mantêm uma região de sobreposição.', ['EXP','ART'],
        'Tempo: 1,5 min. A PCA foi ajustada com quatro componentes e SVD completa. Valores singulares: 20,8955, 11,7551, 4,7014 e 1,7582. A média de entrada é numericamente próxima de zero após o z-score. PC1 explica 72,7705% e PC2 23,0305%. Os maiores loadings da PC1 estão em comprimento e largura de pétala (0,9950 e 0,9682). PC2 enfatiza largura de sépala (0,8913). As cores e os símbolos indicam as espécies conhecidas.'),
    figure('Kernel PCA muda a geometria','kernel_pca',
        'A fração retida se refere ao espectro do kernel centralizado.', ['EXP','ART','DIAG'],
        'Tempo: 1 min. Usa-se RBF com gamma=0,25, duas componentes e solver denso. Os autovalores 39,1321 e 17,7924 representam 39,8394% e 18,1140% do traço completo (98,2247). O percentual acumulado descreve a variância no espaço de características do RBF. Gamma foi fixado antes do ajuste. As cores e os símbolos indicam espécies.'),
    figure('t-SNE e UMAP enfatizam vizinhanças','tsne_umap',
        't-SNE: perp. 30 · UMAP: 15 viz., min_dist 0,1 · seed 42.', ['EXP','ART'],
        'Tempo: 1,5 min. t-SNE: perplexidade 30, inicialização PCA, semente 42, máximo de 1.000 iterações, KL final 0,1642 e taxa efetiva 50. O atributo n_iter_ registrou 999. UMAP: 15 vizinhos, min_dist=0,1, spread=1, inicialização espectral, semente 42 e uma thread. A saída 150 × 2 variou de −5,8964 a 10,1182 no eixo 1 e de 2,2188 a 9,0128 no eixo 2. A curva de similaridade usa a=1,5769 e b=0,8951. Cada técnica teve uma execução, com eixos sem unidade física.'),
    {'layout':'ResultsSlide','title':'Maior preservação local: t-SNE',
     'labels':['PCA','Kernel PCA','t-SNE','UMAP'],
     'values':[round(q2[k]['trustworthiness_10'],4) for k in ['pca','kernel_pca','tsne','umap']],
     'unit':'Trustworthiness · 10 vizinhos',
     'caption':'Diagnóstico desta configuração; não é acurácia nem avaliação global.',
     'highlightIndex':2,'citations':['EXP','ART'],
     'notes':'Tempo: 1 min. Trustworthiness penaliza vizinhos artificiais introduzidos pela projeção comparando o espaço padronizado 4D com o 2D, usando dez vizinhos e distância euclidiana. PCA=0,978156, Kernel PCA=0,932238, t-SNE=0,988813 e UMAP=0,978349. PCA e UMAP são muito próximos neste índice. Os valores não demonstram superioridade universal nem estabilidade entre sementes. O gráfico tem origem zero e valores numéricos explícitos.'},
    cols('O alcance das conclusões é descritivo','O QUE SUSTENTA',
        ['Tunagem e rodada final separadas.','Novas sementes na rodada final.','Sensibilidade documentada nas grades.'],
        'O QUE LIMITA',['10 sementes ≠ 10 amostras independentes.','Grade discreta; uma única base.','Cobertura afeta o DBSCAN.'],['ART','EXP'],
        'Tempo: 1 min. As sementes medem sensibilidade da otimização nas mesmas 150 flores, não variabilidade amostral. A busca discreta não prova otimalidade fora da grade. As configurações dependem do critério interno e, no DBSCAN, do piso de cobertura. Cada projeção foi executada uma vez, portanto sua estabilidade visual não foi estimada.'),
    {'layout':'ConclusionSlide','title':'Grupos geométricos diferem de espécies',
     'windowTitle':'CONCLUSÕES',
     'bullets':['Seis métodos escolheram k = 2 pela silhueta.',
        f"Entre os perfis escolhidos, {agrupamento['maior_ari_k3']['nome']} teve ARI {agrupamento['maior_ari_k3']['ari']} em k = 3.",
        'DBSCAN reteve 96%; inicializações afetaram k = 3.',
        'Silhueta e ARI avaliam propriedades distintas.'],
     'citations':['ART','EXP'],
     'notes':'Fechamento (45 s). ' + particao_nota + ' ' + amostra_nota + ' Retomar a comparação com as três espécies e o papel das projeções.'},
    {'layout':'ReferencesSlide','title':'Fontes e rastreabilidade','ids':['ART','EXP','DIAG'],
     'notes':'Material de apoio. ART corresponde ao artigo e à bibliografia. EXP corresponde às grades, métricas e projeções em resultados/. DIAG corresponde às tabelas e aos diagnósticos produzidos para o artigo.'}
]
spec = {'title':'Iris: agrupamento e redução de dimensionalidade',
    'plan':{'objective':'Apresentar protocolo, resultados e limites da comparação na Iris.',
    'audience':'Turma do CIn/UFPE · 2026.2', 'minutes':22,'slideCount':len(slides),
    'depth':'intermediária','language':'pt-BR','profile':'retroui-pixel',
    'narrative':'Pergunta → métodos → protocolo → evidências → projeções → limites → conclusão.',
    'assumptions':['Tema retro solicitado: retroui-pixel, 16:9, pt-BR.',
        'Fonte principal definida pelo usuário: artigo_iris_ieee_paginacao_corrigida.pdf.',
        '18 slides, cerca de 22 minutos, reservando 8 minutos para discussão.',
        'Artefatos existentes são a evidência; nenhum ajuste foi reexecutado.',
        'Fontes Pixelify Sans e JetBrains Mono podem usar Liberation Mono como fallback.',
        'Texto, diagramas e barras permanecem editáveis; figuras são imagens com SVG-fonte adicional.'],
    'analysis':{'centralTheme':'Separação geométrica e classes biológicas respondem a critérios diferentes.',
        'concepts':['Silhueta interna','ARI externo','Seleção por função objetivo','Padronização','Projeções 2D'],
        'arguments':['O perfil é fixado na tunagem antes de selecionar k na rodada final.',
            'Silhueta maior não implica maior ARI.','A projeção não é prova de novas classes.'],
        'results':['1.144 ajustes na tunagem e 252 na rodada final: 1.396 no total.',particao_nota,
            'Entre os perfis selecionados, UPGMA atinge ARI 0,7184 em k=3.', amostra_nota,
            'PCA 2D retém 95,80%; Kernel PCA retém 57,95% no espaço RBF; t-SNE tem trustworthiness=0,9888.'],
        'visualOpportunities':['Fluxo de seleção','Curvas por k','Mapas de tunagem', 'Contraste GMM','Árvore armazenada',
            'Quatro projeções com cores e símbolos','Barras de preservação local']},
    'sources':[{'path':'artigo_iris_ieee_paginacao_corrigida.pdf','author':'Fátima Araújo e Rodrigo Gomes',
        'consulted':True,'sections':'PDF integral; oito páginas; métodos, protocolo, resultados, discussão e conclusão.'},
        {'path':'resultados/','consulted':True,'sections':'Métricas Q1, metadados, contingências, árvore e coordenadas Q2.'},
        {'path':'docs/artigo/diagnosticos_revisao.json','consulted':True,'sections':'Resultados, sensibilidade, amostra comum, UPGMA e espectro RBF.'}],
    'limitations':['Referências teóricas consultadas por meio do artigo local; sem nova revisão externa.',
        'Revisão da apresentação verifica fidelidade aos registros; não substitui auditoria dos experimentos.']},
    'visual':{'grid':True,'gridOpacity':.28,'gridSpacing':.4,'logoInFooter':True},
    'slides':slides,'references':[
        {'id':'ART','text':'Fátima Araújo e Rodrigo Gomes. Agrupamento e Redução de Dimensionalidade na Base Iris: Busca de Hiperparâmetros e Avaliação Comparativa. UFPE, 2026.',
         'url':'file:artigo_iris_ieee_paginacao_corrigida.pdf'},
        {'id':'EXP','text':'Equipe 08. Questões 1 e 2: métricas, partições, hierarquia, parâmetros e coordenadas. Registros do projeto, 2026.',
         'url':'file:resultados/'},
        {'id':'DIAG','text':'Equipe 08. Diagnósticos de agrupamento, sensibilidade e projeção, 2026.',
         'url':'file:docs/artigo/diagnosticos_revisao.json'}]}
(OUT / 'deck.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
print(f'Gerado: {OUT / "deck.json"} ({len(slides)} slides)')
